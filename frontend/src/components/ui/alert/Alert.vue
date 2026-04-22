<template>
  <div
    :class="cn(
      'relative w-full rounded-lg border p-4 text-sm',
      variant === 'default' && 'bg-gray-50 text-gray-900 border-gray-200',
      variant === 'destructive' && 'bg-red-50 text-red-700 border-red-200',
      variant === 'info' && 'bg-blue-50 text-blue-700 border-blue-200',
      variant === 'warning' && 'bg-amber-50 text-amber-700 border-amber-200',
      variant === 'success' && 'bg-green-50 text-green-700 border-green-200',
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
