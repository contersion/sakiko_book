<template>
  <app-provider>
    <div class="app-shell" :class="appThemeClass">
      <router-view />

      <transition name="boot-fade">
        <div v-if="authStore.isRestoringSession" class="boot-screen" aria-live="polite">
          <div class="boot-screen__panel">
            <img class="boot-screen__logo" src="/icon-192.png" alt="祥子的书" />
            <svg class="animate-spin h-8 w-8 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <div class="boot-screen__title">正在恢复登录状态</div>
            <p class="boot-screen__description">正在确认你的账号信息与阅读入口，请稍候。</p>
          </div>
        </div>
      </transition>
    </div>
  </app-provider>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";
import { useRoute } from "vue-router";

import AppProvider from "./components/AppProvider.vue";
import { useAuthStore } from "./stores/auth";
import { useAppThemeStore } from "./stores/app-theme";
import { usePreferencesStore } from "./stores/preferences";

const authStore = useAuthStore();
const route = useRoute();
const appThemeStore = useAppThemeStore();
const preferencesStore = usePreferencesStore();
const appThemeClass = computed(() => `app-theme--${appThemeStore.theme}`);

watch(
  () => preferencesStore.reader.theme,
  (theme, previousTheme) => {
    if (
      !preferencesStore.initialized ||
      route.name !== "reader" ||
      theme === previousTheme ||
      theme === appThemeStore.theme
    ) {
      return;
    }

    appThemeStore.setTheme(theme, true);
  },
);
</script>

<style scoped>
.app-shell {
  min-height: 100dvh;
}

.boot-screen {
  position: fixed;
  inset: 0;
  z-index: 999;
  display: grid;
  place-items: center;
  padding: 24px;
  background: color-mix(in srgb, var(--app-shell-color) 78%, white 22%);
  backdrop-filter: blur(16px);
}

.boot-screen__panel {
  width: min(420px, 100%);
  display: grid;
  justify-items: center;
  gap: 18px;
  padding: 36px 28px;
  border: 1px solid var(--border-color);
  border-radius: 28px;
  background: color-mix(in srgb, var(--surface-color) 90%, white 10%);
  box-shadow: var(--surface-shadow);
  text-align: center;
}

.boot-screen__logo {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  object-fit: cover;
}

.boot-screen__title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
}

.boot-screen__description {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.boot-fade-enter-active,
.boot-fade-leave-active {
  transition: opacity 180ms ease;
}

.boot-fade-enter-from,
.boot-fade-leave-to {
  opacity: 0;
}
</style>
