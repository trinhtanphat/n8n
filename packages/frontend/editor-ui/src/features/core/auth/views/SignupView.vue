<script lang="ts" setup>
import { computed, nextTick, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import AuthView from './AuthView.vue';

import type { IFormBoxConfig } from '@/Interface';
import { VIEWS } from '@/app/constants';
import { useToast } from '@/app/composables/useToast';
import { useSettingsStore } from '@/app/stores/settings.store';
import { useUsersStore } from '@/features/settings/users/users.store';
import { useI18n } from '@n8n/i18n';

const usersStore = useUsersStore();
const settingsStore = useSettingsStore();

const toast = useToast();
const i18n = useI18n();
const router = useRouter();
const route = useRoute();

const loading = ref(false);
const inviter = ref<null | { firstName: string; lastName: string }>(null);
const token = ref<string | undefined>(undefined);
const isPublicSignup = ref(false);
const turnstileWidgetId = ref<string | null>(null);

const turnstileSiteKey = computed(() => settingsStore.userManagement.turnstileSiteKey);

const inviteMessage = computed(() => {
	if (!inviter.value) {
		return '';
	}

	return i18n.baseText('settings.signup.signUpInviterInfo', {
		interpolate: { firstName: inviter.value.firstName, lastName: inviter.value.lastName },
	});
});

const formConfig = computed<IFormBoxConfig>(() => {
	if (isPublicSignup.value) {
		return {
			title: 'Create your VNSO account',
			buttonText: 'Create account',
			inputs: [
				{
					name: 'email',
					properties: {
						label: i18n.baseText('auth.email'),
						type: 'email',
						required: true,
						validationRules: [{ name: 'VALID_EMAIL' }],
						autocomplete: 'email',
						focusInitially: true,
					},
				},
				{
					name: 'firstName',
					properties: {
						label: i18n.baseText('auth.firstName'),
						maxlength: 32,
						required: true,
						autocomplete: 'given-name',
						capitalize: true,
					},
				},
				{
					name: 'lastName',
					properties: {
						label: i18n.baseText('auth.lastName'),
						maxlength: 32,
						required: true,
						autocomplete: 'family-name',
						capitalize: true,
					},
				},
				{
					name: 'password',
					properties: {
						label: i18n.baseText('auth.password'),
						type: 'password',
						validationRules: [{ name: 'DEFAULT_PASSWORD_RULES' }],
						required: true,
						infoText: i18n.baseText('auth.defaultPasswordRequirements'),
						autocomplete: 'new-password',
						capitalize: true,
					},
				},
				{
					name: 'agree',
					properties: {
						label: i18n.baseText('auth.agreement.label'),
						type: 'checkbox',
					},
				},
			],
		};
	}

	return {
		title: i18n.baseText('auth.signup.setupYourAccount'),
		buttonText: i18n.baseText('auth.signup.finishAccountSetup'),
		inputs: [
			{
				name: 'firstName',
				properties: {
					label: i18n.baseText('auth.firstName'),
					maxlength: 32,
					required: true,
					autocomplete: 'given-name',
					capitalize: true,
					focusInitially: true,
				},
			},
			{
				name: 'lastName',
				properties: {
					label: i18n.baseText('auth.lastName'),
					maxlength: 32,
					required: true,
					autocomplete: 'family-name',
					capitalize: true,
				},
			},
			{
				name: 'password',
				properties: {
					label: i18n.baseText('auth.password'),
					type: 'password',
					validationRules: [{ name: 'DEFAULT_PASSWORD_RULES' }],
					required: true,
					infoText: i18n.baseText('auth.defaultPasswordRequirements'),
					autocomplete: 'new-password',
					capitalize: true,
				},
			},
			{
				name: 'agree',
				properties: {
					label: i18n.baseText('auth.agreement.label'),
					type: 'checkbox',
				},
			},
		],
	};
});

onMounted(async () => {
	const tokenParam = getQueryParameter('token');

	if (!tokenParam) {
		if (!settingsStore.userManagement.publicSignupEnabled) {
			toast.showError(new Error('Public signup is disabled'), 'Sign up is not available');
			void router.replace({ name: VIEWS.SIGNIN });
			return;
		}

		isPublicSignup.value = true;
		await nextTick();
		await initializeTurnstile();
		return;
	}

	try {
		token.value = tokenParam;
		const invite = await usersStore.validateSignupToken({ token: token.value });
		inviter.value = invite.inviter as { firstName: string; lastName: string };
	} catch (e) {
		toast.showError(e, i18n.baseText('auth.signup.tokenValidationError'));
		void router.replace({ name: VIEWS.SIGNIN });
	}
});

async function onSubmit(values: { [key: string]: string | boolean }) {
	try {
		loading.value = true;

		if (isPublicSignup.value) {
			const email = String(values.email ?? '');
			const turnstileToken = getTurnstileToken();

			await usersStore.publicSignup({
				email,
				firstName: String(values.firstName ?? ''),
				lastName: String(values.lastName ?? ''),
				password: String(values.password ?? ''),
				turnstileToken: turnstileToken || undefined,
			});

			if (values.agree === true) {
				try {
					await usersStore.submitContactEmail(email, true);
				} catch {}
			}

			await router.push({ name: VIEWS.HOMEPAGE });
			return;
		}

		if (!token.value) {
			throw new Error(i18n.baseText('auth.signup.tokenValidationError'));
		}

		await usersStore.acceptInvitation({
			...values,
			token: token.value,
		} as {
			token: string;
			firstName: string;
			lastName: string;
			password: string;
		});

		if (values.agree === true) {
			try {
				await usersStore.submitContactEmail(
					String(values.email ?? usersStore.currentUser?.email ?? ''),
					true,
				);
			} catch {}
		}

		await router.push({ name: VIEWS.HOMEPAGE });
	} catch (error) {
		toast.showError(
			error,
			isPublicSignup.value
				? 'Failed to create account'
				: i18n.baseText('auth.signup.setupYourAccountError'),
		);
	} finally {
		loading.value = false;
	}
}

async function initializeTurnstile() {
	if (!isPublicSignup.value || !turnstileSiteKey.value) return;

	if (!(window as unknown as { turnstile?: unknown }).turnstile) {
		await new Promise<void>((resolve, reject) => {
			const script = document.createElement('script');
			script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
			script.async = true;
			script.defer = true;
			script.onload = () => resolve();
			script.onerror = () => reject(new Error('Failed to load Turnstile script'));
			document.head.appendChild(script);
		});
	}

	await nextTick();
	const el = document.getElementById('turnstile-widget');
	const turnstile = (
		window as unknown as {
			turnstile?: {
				render: (target: HTMLElement, options: { sitekey: string; theme: string }) => string;
			};
		}
	).turnstile;
	if (!el || !turnstile) return;

	turnstileWidgetId.value = turnstile.render(el, {
		sitekey: turnstileSiteKey.value,
		theme: 'light',
	});
}

function getTurnstileToken(): string {
	if (!turnstileSiteKey.value) return '';

	const turnstile = (
		window as unknown as {
			turnstile?: { getResponse: (id?: string) => string };
		}
	).turnstile;
	if (!turnstile) return '';

	const token = turnstile.getResponse(turnstileWidgetId.value ?? undefined);
	return typeof token === 'string' ? token : '';
}

function getQueryParameter(key: 'token'): string | null {
	return !route.query[key] || typeof route.query[key] !== 'string' ? null : route.query[key];
}
</script>

<template>
	<AuthView
		:form="formConfig"
		:form-loading="loading"
		:subtitle="isPublicSignup ? 'Join VNSO workflow automation platform' : inviteMessage"
		@submit="onSubmit"
	>
		<div v-if="isPublicSignup && turnstileSiteKey" :class="$style.turnstile">
			<div id="turnstile-widget" />
		</div>
	</AuthView>
</template>

<style lang="scss" module>
.turnstile {
	margin-top: var(--spacing--2xs);
	display: flex;
	justify-content: center;
}
</style>
