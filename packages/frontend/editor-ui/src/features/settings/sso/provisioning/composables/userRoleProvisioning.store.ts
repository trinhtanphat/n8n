import { ref, readonly } from 'vue';
import { defineStore } from 'pinia';
import { useRootStore } from '@n8n/stores/useRootStore';
import * as provisioningApi from '@n8n/rest-api-client/api/provisioning';
import type { ProvisioningConfig } from '@n8n/rest-api-client/api/provisioning';
import { useSettingsStore } from '@/app/stores/settings.store';
import { EnterpriseEditionFeature } from '@/app/constants';

/**
 * Composable to load and save provisioning config
 */
export const useUserRoleProvisioningStore = defineStore('userRoleProvisioning', () => {
	const rootStore = useRootStore();
	const settingsStore = useSettingsStore();

	const provisioningConfig = ref<ProvisioningConfig | undefined>();

	const isProvisioningLicensed = () =>
		Boolean(settingsStore.isEnterpriseFeatureEnabled[EnterpriseEditionFeature.Provisioning]);

	const getProvisioningConfig = async () => {
		if (!isProvisioningLicensed()) {
			provisioningConfig.value = undefined;
			return undefined;
		}

		try {
			const config = await provisioningApi.getProvisioningConfig(rootStore.restApiContext);
			provisioningConfig.value = config;
			return config;
		} catch (error) {
			console.error('Failed to fetch provisioning config:', error);
			throw error;
		}
	};

	const saveProvisioningConfig = async (config: Partial<ProvisioningConfig>) => {
		if (!isProvisioningLicensed()) {
			return provisioningConfig.value;
		}

		try {
			const updatedConfig = await provisioningApi.saveProvisioningConfig(
				rootStore.restApiContext,
				config,
			);
			provisioningConfig.value = updatedConfig;
			return updatedConfig;
		} catch (error) {
			console.error('Failed to save provisioning config:', error);
			throw error;
		}
	};

	return {
		provisioningConfig: readonly(provisioningConfig),
		getProvisioningConfig,
		saveProvisioningConfig,
	};
});
