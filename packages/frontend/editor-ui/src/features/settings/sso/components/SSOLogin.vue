<script lang="ts" setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

import { useI18n } from '@n8n/i18n';
import { N8nButton } from '@n8n/design-system';

import { useToast } from '@/app/composables/useToast';
import { useSettingsStore } from '@/app/stores/settings.store';
import { useSSOStore } from '../sso.store';

const i18n = useI18n();
const ssoStore = useSSOStore();
const settingsStore = useSettingsStore();
const toast = useToast();
const route = useRoute();

const socialLogin = computed(() => settingsStore.userManagement.socialLogin);
const publicSignupEnabled = computed(() => settingsStore.userManagement.publicSignupEnabled);

const hasSocialProviders = computed(
	() =>
		socialLogin.value.google.enabled ||
		socialLogin.value.github.enabled ||
		socialLogin.value.facebook.enabled,
);

const shouldShowAuthOptions = computed(
	() => ssoStore.showSsoLoginButton || hasSocialProviders.value || publicSignupEnabled.value,
);

const getRedirectQuery = () =>
	typeof route.query?.redirect === 'string'
		? `?redirect=${encodeURIComponent(route.query.redirect)}`
		: '';

const onSSOLogin = async () => {
	try {
		const redirectUrl = ssoStore.isDefaultAuthenticationSaml
			? await ssoStore.getSSORedirectUrl(
					typeof route.query?.redirect === 'string' ? route.query.redirect : '',
				)
			: ssoStore.oidc.loginUrl;
		window.location.href = redirectUrl ?? '';
	} catch (error) {
		toast.showError(error, 'Error', error.message);
	}
};

const onSocialLogin = (provider: 'google' | 'github' | 'facebook') => {
	const providerConfig = socialLogin.value[provider];
	if (!providerConfig.enabled || !providerConfig.loginUrl) return;

	window.location.href = `${providerConfig.loginUrl}${getRedirectQuery()}`;
};
</script>

<template>
	<div v-if="shouldShowAuthOptions" :class="$style.ssoLogin">
		<div :class="$style.divider">
			<span>{{ i18n.baseText('sso.login.divider') }}</span>
		</div>

		<N8nButton
			v-if="ssoStore.showSsoLoginButton"
			variant="outline"
			size="large"
			:label="i18n.baseText('sso.login.button')"
			@click="onSSOLogin"
		/>

		<div v-if="hasSocialProviders" :class="$style.socialButtons">
			<N8nButton
				v-if="socialLogin.google.enabled"
				variant="outline"
				size="large"
				label="Continue with Google"
				@click="onSocialLogin('google')"
			/>
			<N8nButton
				v-if="socialLogin.github.enabled"
				variant="outline"
				size="large"
				label="Continue with GitHub"
				@click="onSocialLogin('github')"
			/>
			<N8nButton
				v-if="socialLogin.facebook.enabled"
				variant="outline"
				size="large"
				label="Continue with Facebook"
				@click="onSocialLogin('facebook')"
			/>
		</div>

		<router-link v-if="publicSignupEnabled" to="/signup" :class="$style.signupLink">
			Create a VNSO customer account
		</router-link>
	</div>
</template>

<style lang="scss" module>
.ssoLogin {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	text-align: center;
}

.divider {
	width: 100%;
	position: relative;
	text-transform: uppercase;

	&::before {
		content: '';
		position: absolute;
		top: 50%;
		left: 0;
		width: 100%;
		height: 1px;
		background-color: var(--color--foreground);
	}

	span {
		position: relative;
		display: inline-block;
		margin: var(--spacing--2xs) auto;
		padding: var(--spacing--lg);
		background: var(--color--background--light-3);
	}
}

.socialButtons {
	display: grid;
	gap: var(--spacing--2xs);
	width: 100%;
	margin-top: var(--spacing--2xs);
}

.signupLink {
	margin-top: var(--spacing--2xs);
	font-size: var(--font-size-2s);
	color: var(--color-primary);
	text-decoration: none;
}

.signupLink:hover {
	text-decoration: underline;
}
</style>
