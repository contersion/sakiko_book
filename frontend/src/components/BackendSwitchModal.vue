<template>
  <Dialog :open="show" @update:open="handleModalVisibilityChange">
    <DialogContent class="max-w-lg">
      <DialogHeader>
        <DialogTitle>切换后端</DialogTitle>
      </DialogHeader>

      <div class="backend-switcher">
        <Alert variant="info">
          当前连接：<strong>{{ currentBackendSummary }}</strong>
        </Alert>

        <Alert v-if="formError" variant="destructive">
          {{ formError }}
        </Alert>

        <div class="backend-switcher__fields">
          <div class="backend-switcher__field">
            <label>连接模式</label>
            <div class="backend-switcher__radio-group">
              <label
                class="backend-switcher__radio"
                :class="{ 'backend-switcher__radio--active': draft.mode === 'local' }"
              >
                <input v-model="draft.mode" type="radio" value="local" class="sr-only" />
                <span>本地后端</span>
              </label>
              <label
                class="backend-switcher__radio"
                :class="{ 'backend-switcher__radio--active': draft.mode === 'remote' }"
              >
                <input v-model="draft.mode" type="radio" value="remote" class="sr-only" />
                <span>远程后端</span>
              </label>
            </div>
            <div class="backend-switcher__hint">
              本地模式会继续使用当前 Web 的同源 `/api` 行为，或使用本地环境变量里的覆盖地址。
            </div>
          </div>

          <div class="backend-switcher__field">
            <label>远程后端地址</label>
            <Input
              v-model="draft.remoteBaseUrl"
              :disabled="draft.mode !== 'remote' || submitting"
              placeholder="https://example.com"
            />
            <div class="backend-switcher__hint">
              这里只填写后端根地址，不要包含 `/api`。
            </div>
          </div>
        </div>
      </div>

      <div class="backend-switcher__footer">
        <Button variant="ghost" :disabled="submitting" @click="applyLocalDefault">
          恢复本地默认
        </Button>
        <div class="flex gap-2">
          <Button variant="ghost" :disabled="submitting" @click="closeModal">取消</Button>
          <Button :disabled="submitting" @click="submit">
            保存并重新登录
          </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert } from "@/components/ui/alert";
import { notify } from "@/utils/notify";

import { useAuthStore } from "../stores/auth";
import { usePreferencesStore } from "../stores/preferences";
import {
  type BackendConfig,
  type BackendMode,
  getBackendDisplaySummary,
  getBackendIdForConfig,
  getRemoteBaseUrlValidationMessage,
  isSameBackendConfig,
  loadBackendConfig,
  normalizeRemoteBaseUrl,
  saveBackendConfig,
  storeBackendNotice,
} from "../utils/backend";
import { authTokenStorage } from "../utils/token";

interface BackendDraftState {
  mode: BackendMode;
  remoteBaseUrl: string;
}

const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  (event: "update:show", value: boolean): void;
}>();

const router = useRouter();
const authStore = useAuthStore();
const preferencesStore = usePreferencesStore();
const submitting = ref(false);
const formError = ref<string | null>(null);
const currentConfig = ref<BackendConfig>(loadBackendConfig());
const draft = reactive<BackendDraftState>({
  mode: "local",
  remoteBaseUrl: "",
});

const currentBackendSummary = computed(() => getBackendDisplaySummary(currentConfig.value));

watch(
  () => props.show,
  (value) => {
    if (value) {
      syncDraftFromStorage();
    }
  },
);

function syncDraftFromStorage() {
  currentConfig.value = loadBackendConfig();
  draft.mode = currentConfig.value.mode;
  draft.remoteBaseUrl = currentConfig.value.remoteBaseUrl || "";
  formError.value = null;
}

function handleModalVisibilityChange(value: boolean) {
  emit("update:show", value);
}

function closeModal() {
  if (submitting.value) {
    return;
  }

  emit("update:show", false);
}

function applyLocalDefault() {
  draft.mode = "local";
  formError.value = null;
}

function buildNextConfig(): BackendConfig {
  if (draft.mode === "remote") {
    const validationMessage = getRemoteBaseUrlValidationMessage(draft.remoteBaseUrl);
    if (validationMessage) {
      throw new Error(validationMessage);
    }
  }

  return {
    mode: draft.mode,
    remoteBaseUrl: normalizeRemoteBaseUrl(draft.remoteBaseUrl),
  };
}

function clearBackendTokens(previousConfig: BackendConfig, nextConfig: BackendConfig) {
  const previousBackendId = getBackendIdForConfig(previousConfig);
  const nextBackendId = getBackendIdForConfig(nextConfig);

  authTokenStorage.clear(previousBackendId);
  authTokenStorage.clear(nextBackendId);
  authTokenStorage.clearLegacy();

  return nextBackendId;
}

async function submit() {
  formError.value = null;
  submitting.value = true;

  try {
    const nextConfig = buildNextConfig();

    if (isSameBackendConfig(currentConfig.value, nextConfig)) {
      notify.info("当前已经在使用这个后端。");
      closeModal();
      return;
    }

    const savedConfig = saveBackendConfig(nextConfig);
    const nextBackendId = clearBackendTokens(currentConfig.value, savedConfig);

    authStore.handleBackendSwitch(nextBackendId);
    preferencesStore.resetState();

    storeBackendNotice({
      type: "success",
      text: `已切换到${savedConfig.mode === "remote" ? "远程" : "本地"}后端，请重新登录。`,
    });

    closeModal();
    window.location.assign(router.resolve({ name: "login" }).href);
  } catch (error) {
    const messageText = error instanceof Error ? error.message : "切换后端失败，请稍后重试。";
    formError.value = messageText;
    notify.error(messageText);
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.backend-switcher {
  display: grid;
  gap: 16px;
}

.backend-switcher__fields {
  display: grid;
  gap: 16px;
}

.backend-switcher__field {
  display: grid;
  gap: 8px;
}

.backend-switcher__field label {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
}

.backend-switcher__radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.backend-switcher__radio {
  display: inline-flex;
  align-items: center;
  padding: 8px 14px;
  border: 1px solid var(--border-color-soft);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.6);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 160ms ease;
}

.backend-switcher__radio:hover {
  background: rgba(255, 255, 255, 0.8);
}

.backend-switcher__radio--active {
  border-color: var(--primary-color);
  background: rgba(244, 164, 180, 0.12);
  color: var(--primary-color);
  font-weight: 600;
}

.backend-switcher__radio input {
  position: absolute;
  opacity: 0;
}

.backend-switcher__hint {
  margin-top: 10px;
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.7;
}

.backend-switcher__footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-top: 16px;
}

@media (max-width: 640px) {
  .backend-switcher__footer {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
