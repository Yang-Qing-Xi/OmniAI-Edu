'use client';

import { useEffect } from 'react';
import { useSettingsStore } from '@/lib/store/settings';

const API_MGMT_BASE_URL = 'http://127.0.0.1:5010';

/**
 * Fetches server-configured providers on mount and merges into settings store.
 * Also fetches from the unified API management service.
 * Renders nothing — purely a side-effect component.
 */
export function ServerProvidersInit() {
  const fetchServerProviders = useSettingsStore((state) => state.fetchServerProviders);

  useEffect(() => {
    fetchServerProviders();
    fetchApiMgmtProviders();
  }, [fetchServerProviders]);

  return null;
}

async function fetchApiMgmtProviders() {
  try {
    const res = await fetch(`${API_MGMT_BASE_URL}/api/openmaic/providers`, {
      signal: AbortSignal.timeout(3000),
    });
    if (!res.ok) return;

    const data = await res.json();
    const store = useSettingsStore.getState();

    if (data.providers && Object.keys(data.providers).length > 0) {
      const newProvidersConfig = { ...store.providersConfig } as Record<string, any>;
      for (const [pid, info] of Object.entries(data.providers) as [string, any][]) {
        if (newProvidersConfig[pid]) {
          newProvidersConfig[pid] = {
            ...newProvidersConfig[pid],
            isServerConfigured: true,
            serverModels: info.models,
            serverBaseUrl: info.baseUrl,
          };
        }
      }

      // Auto-select first available model if none is configured
      let updates: Record<string, any> = { providersConfig: newProvidersConfig as typeof store.providersConfig };
      if (!store.modelId) {
        for (const [pid, info] of Object.entries(data.providers) as [string, any][]) {
          const models = info.models as string[] | undefined;
          if (models && models.length > 0 && newProvidersConfig[pid]) {
            updates.providerId = pid as typeof store.providerId;
            updates.modelId = models[0];
            break;
          }
        }
      }

      useSettingsStore.setState(updates);
    }
  } catch {
    // API management service not available, silently skip
  }
}
