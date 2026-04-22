<template>
  <div
    :class="cn(
      'relative w-full rounded-lg border p-4 text-sm',
      variant === 'default' && 'bg-[var(--alert-default-bg)] text-[var(--alert-default-text)] border-[var(--alert-default-border)]',
      variant === 'destructive' && 'bg-[var(--alert-destructive-bg)] text-[var(--alert-destructive-text)] border-[var(--alert-destructive-border)]',
      variant === 'info' && 'bg-[var(--alert-info-bg)] text-[var(--alert-info-text)] border-[var(--alert-info-border)]',
      variant === 'warning' && 'bg-[var(--alert-warning-bg)] text-[var(--alert-warning-text)] border-[var(--alert-warning-border)]',
      variant === 'success' && 'bg-[var(--alert-success-bg)] text-[var(--alert-success-text)] border-[var(--alert-success-border)]',
      $attrs.class ?? ''
    )"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";

interface Props {
  variant?: "default" | "destructive" | "info" | "warning" | "success";
}

withDefaults(defineProps<Props>(), {
  variant: "default",
});
</script>
