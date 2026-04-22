<template>
  <div class="app-layout" :class="{ 'app-layout--immersive': isImmersiveRoute }">
    <header
      v-if="!isImmersiveRoute"
      class="app-layout__header"
    >
      <div class="app-layout__brand">
        <img class="app-layout__logo" src="/icon-192.png" alt="初华的书" />
        <div>
          <div class="app-layout__title">初华的书</div>
          <div class="app-layout__subtitle">个人在线阅读器</div>
        </div>
      </div>

      <div class="app-layout__actions">
        <div class="app-layout__nav-actions">
          <Button
            :variant="route.name === 'books' ? 'default' : 'secondary'"
            size="sm"
            @click="goTo('books')"
          >
            书架
          </Button>
          <Button
            :variant="route.name === 'rules' ? 'default' : 'secondary'"
            size="sm"
            @click="goTo('rules')"
          >
            目录规则
          </Button>
          <Button variant="secondary" size="sm" @click="backendModalVisible = true">
            切换后端
          </Button>
          <Button variant="secondary" size="sm" @click="handleToggleTheme">
            {{ themeToggleLabel }}
          </Button>
        </div>

        <div class="app-layout__user">
          <div class="app-layout__user-meta">
            <span class="app-layout__username">{{ authStore.user?.username }}</span>
            <span class="app-layout__backend">{{ backendSummary }}</span>
          </div>
          <Button variant="ghost" size="sm" @click="handleLogout">退出登录</Button>
        </div>
      </div>
    </header>

    <main class="app-layout__content" :class="{ 'app-layout__content--immersive': isImmersiveRoute }">
      <router-view />
    </main>

    <backend-switch-modal v-model:show="backendModalVisible" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { Button } from "@/components/ui/button";
import BackendSwitchModal from "../components/BackendSwitchModal.vue";
import { useAuthStore } from "../stores/auth";
import { useAppThemeStore } from "../stores/app-theme";
import { usePreferencesStore } from "../stores/preferences";
import { getBackendDisplaySummary } from "../utils/backend";

const authStore = useAuthStore();
const appThemeStore = useAppThemeStore();
const preferencesStore = usePreferencesStore();
const route = useRoute();
const router = useRouter();
const backendModalVisible = ref(false);
const isImmersiveRoute = computed(() => route.meta.immersive === true);
const backendSummary = computed(() => getBackendDisplaySummary());
const themeToggleLabel = computed(() => (appThemeStore.theme === "dark" ? "日间模式" : "夜间模式"));

function goTo(name: "books" | "rules") {
  void router.push({ name });
}

function handleLogout() {
  authStore.logout();
  void router.push({ name: "login" });
}

function handleToggleTheme() {
  const nextTheme = appThemeStore.theme === "dark" ? "light" : "dark";
  appThemeStore.setTheme(nextTheme, true);

  if (preferencesStore.initialized) {
    preferencesStore.patchReader({ theme: nextTheme }, 0);
    return;
  }

  void preferencesStore.ensureReady().then(() => {
    preferencesStore.patchReader({ theme: nextTheme }, 0);
  }).catch(() => {
    // 全局主题已经本地生效，这里只是不让 reader 偏好同步失败打断交互。
  });
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: transparent;
}

.app-layout--immersive {
  background: transparent;
}

.app-layout__header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  padding: 16px 24px;
  backdrop-filter: blur(12px);
  background: var(--surface-header-bg);
}

.app-layout__brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.app-layout__logo {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  object-fit: cover;
  box-shadow: 0 12px 24px rgba(74, 159, 217, 0.28);
}

.app-layout__title {
  font-size: 18px;
  font-weight: 700;
}

.app-layout__subtitle {
  font-size: 13px;
  color: var(--text-secondary);
}

.app-layout__actions {
  display: flex;
  align-items: center;
  gap: 18px;
}

.app-layout__nav-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  max-width: 100%;
}

.app-layout__user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-layout__user-meta {
  display: grid;
  gap: 2px;
}

.app-layout__content {
  padding: 24px;
}

.app-layout__content--immersive {
  padding: 0;
}

.app-layout__username {
  max-width: min(240px, 40vw);
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-layout__backend {
  max-width: min(280px, 44vw);
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 780px) {
  .app-layout__header {
    flex-direction: column;
    align-items: stretch;
  }

  .app-layout__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .app-layout__content {
    padding: 16px;
  }

  .app-layout__content--immersive {
    padding: 0;
  }

  .app-layout__user {
    justify-content: space-between;
  }

  .app-layout__username,
  .app-layout__backend {
    max-width: 100%;
  }
}
</style>
