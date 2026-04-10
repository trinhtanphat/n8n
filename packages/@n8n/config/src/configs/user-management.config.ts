import { z } from 'zod';

import { Config, Env, Nested } from '../decorators';
import { PasswordConfig } from './password.config';

@Config
class SmtpAuth {
	/** SMTP login username */
	@Env('N8N_SMTP_USER')
	user: string = '';

	/** SMTP login password */
	@Env('N8N_SMTP_PASS')
	pass: string = '';

	/** SMTP OAuth Service Client */
	@Env('N8N_SMTP_OAUTH_SERVICE_CLIENT')
	serviceClient: string = '';

	/** SMTP OAuth Private Key */
	@Env('N8N_SMTP_OAUTH_PRIVATE_KEY')
	privateKey: string = '';
}

@Config
class SmtpConfig {
	/** SMTP server host */
	@Env('N8N_SMTP_HOST')
	host: string = '';

	/** SMTP server port */
	@Env('N8N_SMTP_PORT')
	port: number = 465;

	/** Whether to use SSL for SMTP */
	@Env('N8N_SMTP_SSL')
	secure: boolean = true;

	/** Whether to use STARTTLS for SMTP when SSL is disabled */
	@Env('N8N_SMTP_STARTTLS')
	startTLS: boolean = true;

	/** How to display sender name */
	@Env('N8N_SMTP_SENDER')
	sender: string = '';

	@Nested
	auth: SmtpAuth;
}

@Config
export class TemplateConfig {
	/** Overrides default HTML template for inviting new people (use full path) */
	@Env('N8N_UM_EMAIL_TEMPLATES_INVITE')
	'user-invited': string = '';

	/** Overrides default HTML template for resetting password (use full path) */
	@Env('N8N_UM_EMAIL_TEMPLATES_PWRESET')
	'password-reset-requested': string = '';

	/** Overrides default HTML template for notifying that a workflow was shared (use full path) */
	@Env('N8N_UM_EMAIL_TEMPLATES_WORKFLOW_SHARED')
	'workflow-shared': string = '';

	/** Overrides default HTML template for notifying that a workflow was deactivated (use full path) */
	@Env('N8N_UM_EMAIL_TEMPLATES_WORKFLOW_AUTODEACTIVATED')
	'workflow-deactivated': string = '';

	/** Overrides default HTML template for notifying that credentials were shared (use full path) */
	@Env('N8N_UM_EMAIL_TEMPLATES_CREDENTIALS_SHARED')
	'credentials-shared': string = '';

	/** Overrides default HTML template for notifying that credentials were shared (use full path) */
	@Env('N8N_UM_EMAIL_TEMPLATES_PROJECT_SHARED')
	'project-shared': string = '';

	/** Overrides default HTML template for notifying that a workflow failed in production (use full path) */
	@Env('N8N_UM_EMAIL_TEMPLATES_WORKFLOW_FAILURE')
	'workflow-failure': string = '';
}

const emailModeSchema = z.enum(['', 'smtp']);
type EmailMode = z.infer<typeof emailModeSchema>;

@Config
class EmailConfig {
	/** Email delivery method: `smtp` or empty (disabled). */
	@Env('N8N_EMAIL_MODE', emailModeSchema)
	mode: EmailMode = 'smtp';

	@Nested
	smtp: SmtpConfig;

	@Nested
	template: TemplateConfig;
}

@Config
class PublicSignupConfig {
	/** Whether unauthenticated users can create accounts directly. */
	@Env('N8N_PUBLIC_SIGNUP_ENABLED')
	enabled: boolean = false;

	/** Cloudflare Turnstile site key used by public signup page. */
	@Env('N8N_PUBLIC_SIGNUP_TURNSTILE_SITE_KEY')
	turnstileSiteKey: string = '';

	/** Cloudflare Turnstile secret key used by backend verification. */
	@Env('N8N_PUBLIC_SIGNUP_TURNSTILE_SECRET_KEY')
	turnstileSecretKey: string = '';
}

@Config
class GoogleSocialLoginConfig {
	@Env('N8N_SOCIAL_LOGIN_GOOGLE_ENABLED')
	enabled: boolean = false;

	@Env('N8N_SOCIAL_LOGIN_GOOGLE_CLIENT_ID')
	clientId: string = '';

	@Env('N8N_SOCIAL_LOGIN_GOOGLE_CLIENT_SECRET')
	clientSecret: string = '';
}

@Config
class GithubSocialLoginConfig {
	@Env('N8N_SOCIAL_LOGIN_GITHUB_ENABLED')
	enabled: boolean = false;

	@Env('N8N_SOCIAL_LOGIN_GITHUB_CLIENT_ID')
	clientId: string = '';

	@Env('N8N_SOCIAL_LOGIN_GITHUB_CLIENT_SECRET')
	clientSecret: string = '';
}

@Config
class FacebookSocialLoginConfig {
	@Env('N8N_SOCIAL_LOGIN_FACEBOOK_ENABLED')
	enabled: boolean = false;

	@Env('N8N_SOCIAL_LOGIN_FACEBOOK_CLIENT_ID')
	clientId: string = '';

	@Env('N8N_SOCIAL_LOGIN_FACEBOOK_CLIENT_SECRET')
	clientSecret: string = '';
}

@Config
class SocialLoginConfig {
	@Nested
	google: GoogleSocialLoginConfig;

	@Nested
	github: GithubSocialLoginConfig;

	@Nested
	facebook: FacebookSocialLoginConfig;
}

const INVALID_JWT_REFRESH_TIMEOUT_WARNING =
	'N8N_USER_MANAGEMENT_JWT_REFRESH_TIMEOUT_HOURS needs to be smaller than N8N_USER_MANAGEMENT_JWT_DURATION_HOURS. Setting N8N_USER_MANAGEMENT_JWT_REFRESH_TIMEOUT_HOURS to 0.';

@Config
export class UserManagementConfig {
	@Nested
	emails: EmailConfig;

	@Nested
	password: PasswordConfig;

	@Nested
	publicSignup: PublicSignupConfig;

	@Nested
	socialLogin: SocialLoginConfig;

	/** JWT secret to use. If unset, n8n will generate its own. */
	@Env('N8N_USER_MANAGEMENT_JWT_SECRET')
	jwtSecret: string = '';

	/** How long (in hours) before the JWT expires. */
	@Env('N8N_USER_MANAGEMENT_JWT_DURATION_HOURS')
	jwtSessionDurationHours: number = 168;

	/**
	 * Security Control: Invite Link Exposure Prevention
	 *
	 * When enabled, prevents exposure of invite URLs in API responses to users
	 * with 'user:create' permission, mitigating account takeover risks via
	 * invite link leakage (e.g., compromised admin accounts, network interception).
	 */
	@Env('N8N_INVITE_LINKS_EMAIL_ONLY')
	inviteLinksEmailOnly: boolean = false;

	/**
	 * How long (in hours) before expiration to automatically refresh it.
	 * - `0` means 25% of `N8N_USER_MANAGEMENT_JWT_DURATION_HOURS`.
	 * - `-1` means it will never refresh. This forces users to log back in after expiration.
	 */
	@Env('N8N_USER_MANAGEMENT_JWT_REFRESH_TIMEOUT_HOURS')
	jwtRefreshTimeoutHours: number = 0;

	sanitize() {
		if (this.jwtRefreshTimeoutHours >= this.jwtSessionDurationHours) {
			console.warn(INVALID_JWT_REFRESH_TIMEOUT_WARNING);
			this.jwtRefreshTimeoutHours = 0;
		}
	}
}
