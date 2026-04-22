<template>
  <div :class="cn('rounded-lg border border-gray-200 bg-white text-gray-900 shadow-none', $attrs.class ?? '')">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";
</script>
