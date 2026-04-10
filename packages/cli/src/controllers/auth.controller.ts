import {
	LoginRequestDto,
	PublicSignupRequestDto,
	ResolveSignupTokenQueryDto,
} from '@n8n/api-types';
import { Logger } from '@n8n/backend-common';
import { GlobalConfig } from '@n8n/config';
import { Time } from '@n8n/constants';
import type { User, PublicUser, AuthProviderType } from '@n8n/db';
import {
	AuthIdentityRepository,
	UserRepository,
	AuthenticatedRequest,
	GLOBAL_MEMBER_ROLE,
	GLOBAL_OWNER_ROLE,
} from '@n8n/db';
import {
	Body,
	createBodyKeyedRateLimiter,
	Get,
	Param,
	Post,
	Query,
	RestController,
} from '@n8n/decorators';
import { isEmail } from 'class-validator';
import { Response } from 'express';
import { randomUUID } from 'crypto';

import { AuthHandlerRegistry } from '@/auth/auth-handler.registry';
import { AuthService } from '@/auth/auth.service';
import { RESPONSE_ERROR_MESSAGES } from '@/constants';
import { AuthError } from '@/errors/response-errors/auth.error';
import { BadRequestError } from '@/errors/response-errors/bad-request.error';
import { ForbiddenError } from '@/errors/response-errors/forbidden.error';
import { InternalServerError } from '@/errors/response-errors/internal-server.error';
import { EventService } from '@/events/event.service';
import { License } from '@/license';
import { MfaService } from '@/mfa/mfa.service';
import { PostHogClient } from '@/posthog';
import { AuthlessRequest } from '@/requests';
import { OwnershipService } from '@/services/ownership.service';
import { PasswordUtility } from '@/services/password.utility';
import { UrlService } from '@/services/url.service';
import { UserService } from '@/services/user.service';
import {
	getCurrentAuthenticationMethod,
	isOidcCurrentAuthenticationMethod,
	isSamlCurrentAuthenticationMethod,
	isSsoCurrentAuthenticationMethod,
} from '@/sso.ee/sso-helpers';
import '../auth/handlers/email.auth-handler';

const SOCIAL_STATE_COOKIE_NAME = 'n8n-social-state';

type SocialProvider = 'google' | 'github' | 'facebook';

@RestController()
export class AuthController {
	constructor(
		private readonly logger: Logger,
		private readonly globalConfig: GlobalConfig,
		private readonly authService: AuthService,
		private readonly mfaService: MfaService,
		private readonly userService: UserService,
		private readonly license: License,
		private readonly userRepository: UserRepository,
		private readonly authIdentityRepository: AuthIdentityRepository,
		private readonly eventService: EventService,
		private readonly authHandlerRegistry: AuthHandlerRegistry,
		private readonly passwordUtility: PasswordUtility,
		private readonly ownershipService: OwnershipService,
		private readonly urlService: UrlService,
		private readonly postHog?: PostHogClient,
	) {}

	/** Log in a user */
	@Post('/login', {
		skipAuth: true,
		// Two layered rate limit to ensure multiple users can login from the same
		// IP address but aggressive per email limit.
		ipRateLimit: {
			limit: 1000,
			windowMs: 5 * Time.minutes.toMilliseconds,
		},
		keyedRateLimit: createBodyKeyedRateLimiter<LoginRequestDto>({
			limit: 5,
			windowMs: 1 * Time.minutes.toMilliseconds,
			field: 'emailOrLdapLoginId',
		}),
	})
	async login(
		req: AuthlessRequest,
		res: Response,
		@Body payload: LoginRequestDto,
	): Promise<PublicUser | undefined> {
		const { emailOrLdapLoginId, password, mfaCode, mfaRecoveryCode } = payload;

		const currentAuthenticationMethod = getCurrentAuthenticationMethod();
		this.validateEmailFormat(currentAuthenticationMethod, emailOrLdapLoginId);

		const emailHandler = this.authHandlerRegistry.get('email', 'password');
		if (!emailHandler) {
			this.logger.error('Email authentication handler is not registered');
			throw new InternalServerError('Email authentication method not available');
		}

		const preliminaryUser = await emailHandler.handleLogin(emailOrLdapLoginId, password);
		this.validateSsoRestrictions(preliminaryUser);

		const { user, usedAuthenticationMethod } = await this.authenticateWithPassword(
			currentAuthenticationMethod,
			emailOrLdapLoginId,
			password,
			preliminaryUser,
		);

		await this.validateMfa(user, mfaCode, mfaRecoveryCode);

		this.authService.issueCookie(res, user, user.mfaEnabled, req.browserId);

		this.eventService.emit('user-logged-in', {
			user,
			authenticationMethod: usedAuthenticationMethod,
		});

		return await this.userService.toPublic(user, {
			posthog: this.postHog,
			withScopes: true,
			mfaAuthenticated: user.mfaEnabled,
		});
	}

	private validateEmailFormat(authMethod: AuthProviderType, emailOrLdapLoginId: string): void {
		if (authMethod === 'email' && !isEmail(emailOrLdapLoginId)) {
			throw new BadRequestError('Invalid email address');
		}
	}

	private validateSsoRestrictions(preliminaryUser: User | undefined): void {
		const shouldBlockSsoUser =
			(isSamlCurrentAuthenticationMethod() || isOidcCurrentAuthenticationMethod()) &&
			preliminaryUser?.role.slug !== GLOBAL_OWNER_ROLE.slug &&
			!preliminaryUser?.settings?.allowSSOManualLogin;

		if (shouldBlockSsoUser) {
			throw new AuthError('SSO is enabled, please log in with SSO');
		}
	}

	private async authenticateWithPassword(
		getCurrentAuthenticationMethod: AuthProviderType,
		emailOrLdapLoginId: string,
		password: string,
		preliminaryUser: User | undefined,
	): Promise<{ user: User; usedAuthenticationMethod: AuthProviderType }> {
		let user = preliminaryUser;
		let usedAuthenticationMethod: AuthProviderType = 'email';

		const shouldTryAlternativeAuth =
			getCurrentAuthenticationMethod !== 'email' &&
			preliminaryUser?.role.slug !== GLOBAL_OWNER_ROLE.slug;

		if (shouldTryAlternativeAuth) {
			const authHandler = this.authHandlerRegistry.get(getCurrentAuthenticationMethod, 'password');
			if (authHandler) {
				user = await authHandler.handleLogin(emailOrLdapLoginId, password);
				usedAuthenticationMethod = getCurrentAuthenticationMethod;
			}
		}

		if (!user) {
			this.eventService.emit('user-login-failed', {
				authenticationMethod: usedAuthenticationMethod,
				userEmail: emailOrLdapLoginId,
				reason: 'wrong credentials',
			});
			throw new AuthError('Wrong username or password. Do you have caps lock on?');
		}

		return { user, usedAuthenticationMethod };
	}

	private async validateMfa(
		user: User,
		mfaCode: string | undefined,
		mfaRecoveryCode: string | undefined,
	): Promise<void> {
		if (!user.mfaEnabled) {
			return;
		}

		if (!mfaCode && !mfaRecoveryCode) {
			throw new AuthError('MFA Error', 998);
		}

		const isMfaCodeOrMfaRecoveryCodeValid = await this.mfaService.validateMfa(
			user.id,
			mfaCode,
			mfaRecoveryCode,
		);

		if (!isMfaCodeOrMfaRecoveryCodeValid) {
			throw new AuthError('Invalid mfa token or recovery code');
		}
	}

	/** Check if the user is already logged in */
	@Get('/login', {
		skipAuth: true,
		allowSkipMFA: true,
	})
	async currentUser(req: AuthenticatedRequest | AuthlessRequest): Promise<PublicUser | null> {
		if (!('user' in req) || !req.user) {
			return null;
		}

		// We need auth identities to determine signInType in toPublic method
		const user = await this.userService.findUserWithAuthIdentities(req.user.id);

		return await this.userService.toPublic(user, {
			posthog: this.postHog,
			withScopes: true,
			mfaAuthenticated: req.authInfo?.usedMfa,
		});
	}

	/** Validate invite token to enable invitee to set up their account */
	@Get('/resolve-signup-token', { skipAuth: true })
	async resolveSignupToken(
		_req: AuthlessRequest,
		_res: Response,
		@Query payload: ResolveSignupTokenQueryDto,
	) {
		if (isSsoCurrentAuthenticationMethod()) {
			this.logger.debug(
				'Invite links are not supported on this system, please use single sign on instead.',
			);
			throw new BadRequestError(
				'Invite links are not supported on this system, please use single sign on instead.',
			);
		}

		if (!payload.token) {
			this.logger.debug('Request to resolve signup token failed because token is missing');
			throw new BadRequestError('Token is required');
		}

		const { inviterId, inviteeId } = await this.userService.getInvitationIdsFromPayload(
			payload.token,
		);

		const isWithinUsersLimit = this.license.isWithinUsersLimit();

		if (!isWithinUsersLimit) {
			this.logger.debug('Request to resolve signup token failed because of users quota reached', {
				inviterId,
				inviteeId,
			});
			throw new ForbiddenError(RESPONSE_ERROR_MESSAGES.USERS_QUOTA_REACHED);
		}

		const users = await this.userRepository.findManyByIds([inviterId, inviteeId], {
			includeRole: true,
		});

		if (users.length !== 2) {
			this.logger.debug(
				'Request to resolve signup token failed because the ID of the inviter and/or the ID of the invitee were not found in database',
				{ inviterId, inviteeId },
			);
			throw new BadRequestError('Invalid invite URL');
		}

		const invitee = users.find((user) => user.id === inviteeId);
		if (!invitee || invitee.password) {
			this.logger.error('Invalid invite URL - invitee already setup', {
				inviterId,
				inviteeId,
			});
			throw new BadRequestError('The invitation was likely either deleted or already claimed');
		}

		const inviter = users.find((user) => user.id === inviterId);
		if (!inviter?.email) {
			this.logger.error(
				'Request to resolve signup token failed because inviter does not exist or is not set up',
				{
					inviterId: inviter?.id,
				},
			);
			throw new BadRequestError('Invalid request');
		}

		this.eventService.emit('user-invite-email-click', { inviter, invitee });

		const { firstName, lastName } = inviter;
		return { inviter: { firstName, lastName } };
	}

	@Post('/public/signup', {
		skipAuth: true,
		ipRateLimit: {
			limit: 100,
			windowMs: 5 * Time.minutes.toMilliseconds,
		},
		keyedRateLimit: createBodyKeyedRateLimiter<PublicSignupRequestDto>({
			limit: 5,
			windowMs: 10 * Time.minutes.toMilliseconds,
			field: 'email',
		}),
	})
	async publicSignup(
		req: AuthlessRequest,
		res: Response,
		@Body payload: PublicSignupRequestDto,
	): Promise<PublicUser> {
		if (!this.globalConfig.userManagement.publicSignup.enabled) {
			throw new ForbiddenError('Public signup is disabled');
		}

		if (!(await this.ownershipService.hasInstanceOwner())) {
			throw new BadRequestError('Owner account is not set up yet');
		}

		if (!this.license.isWithinUsersLimit()) {
			throw new ForbiddenError(RESPONSE_ERROR_MESSAGES.USERS_QUOTA_REACHED);
		}

		if (!isEmail(payload.email)) {
			throw new BadRequestError('Invalid email address');
		}

		await this.verifyTurnstile(req, payload.turnstileToken);

		const existing = await this.userRepository.findOne({
			where: { email: payload.email },
			relations: ['role', 'authIdentities'],
		});

		if (existing?.password) {
			throw new BadRequestError('Email already registered');
		}

		const hashedPassword = await this.passwordUtility.hash(payload.password);
		let user: User;

		if (existing) {
			existing.firstName = payload.firstName;
			existing.lastName = payload.lastName;
			existing.password = hashedPassword;
			user = await this.userRepository.save(existing, { transaction: false });
		} else {
			const created = await this.userRepository.createUserWithProject({
				email: payload.email,
				firstName: payload.firstName,
				lastName: payload.lastName,
				password: hashedPassword,
				role: GLOBAL_MEMBER_ROLE,
			});
			user = created.user;
		}

		this.authService.issueCookie(res, user, false, req.browserId);

		this.eventService.emit('user-signed-up', {
			user,
			userType: 'email',
			wasDisabledLdapUser: false,
		});

		return await this.userService.toPublic(user, {
			posthog: this.postHog,
			withScopes: true,
		});
	}

	@Get('/public/oauth/:provider/login', { skipAuth: true })
	async socialLogin(
		_resReq: AuthlessRequest,
		res: Response,
		@Param('provider') providerParam: string,
		@Query payload: { redirect?: string },
	) {
		const provider = this.validateSocialProvider(providerParam);
		const config = this.getSocialProviderConfig(provider);

		if (!config.enabled) {
			throw new ForbiddenError(`${provider} login is disabled`);
		}

		const state = randomUUID();
		const { samesite, secure } = this.globalConfig.auth.cookie;
		const redirect = this.resolveSafeRedirect(payload.redirect);

		res.cookie(SOCIAL_STATE_COOKIE_NAME, JSON.stringify({ state, provider, redirect }), {
			maxAge: 15 * Time.minutes.toMilliseconds,
			httpOnly: true,
			sameSite: samesite,
			secure,
		});

		const callbackUrl = this.getSocialCallbackUrl(provider);
		const authUrl = this.buildProviderAuthUrl(provider, config.clientId, callbackUrl, state);

		res.redirect(authUrl.toString());
	}

	@Get('/public/oauth/:provider/callback', { skipAuth: true })
	async socialCallback(
		req: AuthlessRequest,
		res: Response,
		@Param('provider') providerParam: string,
		@Query payload: { code?: string; state?: string },
	) {
		const provider = this.validateSocialProvider(providerParam);
		const config = this.getSocialProviderConfig(provider);

		if (!config.enabled) {
			throw new ForbiddenError(`${provider} login is disabled`);
		}

		if (!payload.code || !payload.state) {
			throw new BadRequestError('Missing OAuth callback parameters');
		}

		const cookieValue = req.cookies[SOCIAL_STATE_COOKIE_NAME];
		res.clearCookie(SOCIAL_STATE_COOKIE_NAME);

		if (typeof cookieValue !== 'string') {
			throw new BadRequestError('Missing OAuth state cookie');
		}

		let statePayload: { state: string; provider: SocialProvider; redirect: string };
		try {
			statePayload = JSON.parse(cookieValue) as {
				state: string;
				provider: SocialProvider;
				redirect: string;
			};
		} catch {
			throw new BadRequestError('Invalid OAuth state payload');
		}

		if (statePayload.state !== payload.state || statePayload.provider !== provider) {
			throw new BadRequestError('Invalid OAuth state');
		}

		const callbackUrl = this.getSocialCallbackUrl(provider);
		const profile = await this.fetchSocialProfile(provider, config, payload.code, callbackUrl);

		if (!profile.email || !isEmail(profile.email)) {
			throw new BadRequestError('A valid email is required from the social provider');
		}

		const providerIdentity = `${provider}:${profile.providerUserId}`;
		const existingIdentity = await this.authIdentityRepository.findOne({
			where: {
				providerType: 'oidc',
				providerId: providerIdentity,
			},
			relations: { user: { role: true, authIdentities: true } },
		});

		let user: User | undefined = existingIdentity?.user;

		if (!user) {
			const existingUser = await this.userRepository.findOne({
				where: { email: profile.email },
				relations: ['role', 'authIdentities'],
			});
			user = existingUser ?? undefined;
		}

		if (!user) {
			if (!this.license.isWithinUsersLimit()) {
				throw new ForbiddenError(RESPONSE_ERROR_MESSAGES.USERS_QUOTA_REACHED);
			}

			const created = await this.userRepository.createUserWithProject({
				email: profile.email,
				firstName: profile.firstName,
				lastName: profile.lastName,
				password: 'no password set',
				role: GLOBAL_MEMBER_ROLE,
			});
			user = created.user;
		}

		const alreadyLinked = user.authIdentities?.some(
			(identity) => identity.providerType === 'oidc' && identity.providerId === providerIdentity,
		);

		if (!alreadyLinked) {
			await this.authIdentityRepository.save(
				this.authIdentityRepository.create({
					providerType: 'oidc',
					providerId: providerIdentity,
					userId: user.id,
				}),
			);
		}

		this.authService.issueCookie(res, user, false, req.browserId);
		this.eventService.emit('user-logged-in', {
			user,
			authenticationMethod: 'oidc',
		});

		return res.redirect(statePayload.redirect);
	}

	private resolveSafeRedirect(redirect?: string): string {
		if (!redirect) return '/';
		if (redirect.startsWith('/')) return redirect;

		try {
			const parsed = new URL(redirect);
			const base = new URL(this.urlService.getInstanceBaseUrl());
			if (parsed.origin === base.origin) {
				return `${parsed.pathname}${parsed.search}${parsed.hash}`;
			}
		} catch {}

		return '/';
	}

	private validateSocialProvider(provider: string): SocialProvider {
		if (provider === 'google' || provider === 'github' || provider === 'facebook') {
			return provider;
		}

		throw new BadRequestError('Unsupported social provider');
	}

	private getSocialProviderConfig(provider: SocialProvider) {
		const socialLogin = this.globalConfig.userManagement.socialLogin;
		const providerConfig = socialLogin[provider];

		if (!providerConfig.clientId || !providerConfig.clientSecret) {
			throw new BadRequestError(`${provider} OAuth credentials are not configured`);
		}

		return providerConfig;
	}

	private getSocialCallbackUrl(provider: SocialProvider): string {
		return `${this.urlService.getInstanceBaseUrl()}/${this.globalConfig.endpoints.rest}/public/oauth/${provider}/callback`;
	}

	private buildProviderAuthUrl(
		provider: SocialProvider,
		clientId: string,
		redirectUri: string,
		state: string,
	): URL {
		if (provider === 'google') {
			const url = new URL('https://accounts.google.com/o/oauth2/v2/auth');
			url.searchParams.set('client_id', clientId);
			url.searchParams.set('redirect_uri', redirectUri);
			url.searchParams.set('response_type', 'code');
			url.searchParams.set('scope', 'openid email profile');
			url.searchParams.set('state', state);
			url.searchParams.set('prompt', 'select_account');
			return url;
		}

		if (provider === 'github') {
			const url = new URL('https://github.com/login/oauth/authorize');
			url.searchParams.set('client_id', clientId);
			url.searchParams.set('redirect_uri', redirectUri);
			url.searchParams.set('scope', 'read:user user:email');
			url.searchParams.set('state', state);
			return url;
		}

		const url = new URL('https://www.facebook.com/v19.0/dialog/oauth');
		url.searchParams.set('client_id', clientId);
		url.searchParams.set('redirect_uri', redirectUri);
		url.searchParams.set('response_type', 'code');
		url.searchParams.set('scope', 'email,public_profile');
		url.searchParams.set('state', state);
		return url;
	}

	private async fetchSocialProfile(
		provider: SocialProvider,
		config: { clientId: string; clientSecret: string },
		code: string,
		redirectUri: string,
	): Promise<{ providerUserId: string; email: string; firstName: string; lastName: string }> {
		if (provider === 'google') {
			const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
				method: 'POST',
				headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
				body: new URLSearchParams({
					code,
					client_id: config.clientId,
					client_secret: config.clientSecret,
					redirect_uri: redirectUri,
					grant_type: 'authorization_code',
				}),
			});

			const token = (await tokenRes.json()) as { access_token?: string };
			if (!token.access_token) throw new BadRequestError('Failed to retrieve Google access token');

			const userRes = await fetch('https://openidconnect.googleapis.com/v1/userinfo', {
				headers: { Authorization: `Bearer ${token.access_token}` },
			});
			const user = (await userRes.json()) as {
				sub?: string;
				email?: string;
				given_name?: string;
				family_name?: string;
				name?: string;
			};

			return {
				providerUserId: user.sub ?? '',
				email: user.email ?? '',
				firstName: user.given_name ?? user.name?.split(' ')[0] ?? 'User',
				lastName: user.family_name ?? user.name?.split(' ').slice(1).join(' ') ?? '',
			};
		}

		if (provider === 'github') {
			const tokenRes = await fetch('https://github.com/login/oauth/access_token', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded',
					Accept: 'application/json',
				},
				body: new URLSearchParams({
					code,
					client_id: config.clientId,
					client_secret: config.clientSecret,
					redirect_uri: redirectUri,
				}),
			});

			const token = (await tokenRes.json()) as { access_token?: string };
			if (!token.access_token) throw new BadRequestError('Failed to retrieve GitHub access token');

			const headers = {
				Authorization: `Bearer ${token.access_token}`,
				Accept: 'application/vnd.github+json',
				'X-GitHub-Api-Version': '2022-11-28',
			};

			const userRes = await fetch('https://api.github.com/user', { headers });
			const user = (await userRes.json()) as { id?: number; email?: string; name?: string };

			let email = user.email ?? '';
			if (!email) {
				const emailRes = await fetch('https://api.github.com/user/emails', { headers });
				const emails = (await emailRes.json()) as Array<{
					email: string;
					primary: boolean;
					verified: boolean;
				}>;
				email = emails.find((entry) => entry.primary && entry.verified)?.email ?? '';
			}

			const fullName = user.name ?? 'User';
			return {
				providerUserId: String(user.id ?? ''),
				email,
				firstName: fullName.split(' ')[0] ?? 'User',
				lastName: fullName.split(' ').slice(1).join(' '),
			};
		}

		const tokenUrl = new URL('https://graph.facebook.com/v19.0/oauth/access_token');
		tokenUrl.searchParams.set('client_id', config.clientId);
		tokenUrl.searchParams.set('client_secret', config.clientSecret);
		tokenUrl.searchParams.set('redirect_uri', redirectUri);
		tokenUrl.searchParams.set('code', code);

		const tokenRes = await fetch(tokenUrl);
		const token = (await tokenRes.json()) as { access_token?: string };
		if (!token.access_token) throw new BadRequestError('Failed to retrieve Facebook access token');

		const userUrl = new URL('https://graph.facebook.com/me');
		userUrl.searchParams.set('fields', 'id,email,first_name,last_name,name');
		userUrl.searchParams.set('access_token', token.access_token);

		const userRes = await fetch(userUrl);
		const user = (await userRes.json()) as {
			id?: string;
			email?: string;
			first_name?: string;
			last_name?: string;
			name?: string;
		};

		return {
			providerUserId: user.id ?? '',
			email: user.email ?? '',
			firstName: user.first_name ?? user.name?.split(' ')[0] ?? 'User',
			lastName: user.last_name ?? user.name?.split(' ').slice(1).join(' ') ?? '',
		};
	}

	private async verifyTurnstile(req: AuthlessRequest, turnstileToken?: string): Promise<void> {
		const secret = this.globalConfig.userManagement.publicSignup.turnstileSecretKey;

		if (!secret) {
			return;
		}

		if (!turnstileToken) {
			throw new BadRequestError('Turnstile verification is required');
		}

		const verificationRes = await fetch(
			'https://challenges.cloudflare.com/turnstile/v0/siteverify',
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded',
				},
				body: new URLSearchParams({
					secret,
					response: turnstileToken,
					remoteip: req.ip ?? '',
				}),
			},
		);

		const verification = (await verificationRes.json()) as { success?: boolean };
		if (!verification.success) {
			throw new BadRequestError('Turnstile validation failed');
		}
	}

	/** Log out a user */
	@Post('/logout')
	async logout(req: AuthenticatedRequest, res: Response) {
		await this.authService.invalidateToken(req);
		this.authService.clearCookie(res);
		return { loggedOut: true };
	}
}
