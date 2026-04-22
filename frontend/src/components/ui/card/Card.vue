<template>
  <div :class="cn('rounded-lg border border-[var(--dialog-border)] bg-white text-[var(--text-primary)] shadow-none', $attrs.class ?? '')">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";
</script>
