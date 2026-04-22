<template>
  <input
    :class="cn(
      'flex h-9 w-full rounded-md border border-gray-200 bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-50',
      $attrs.class ?? ''
    )"
    v-model="modelValue"
    v-bind="$attrs"
  />
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";

const modelValue = defineModel<string>();
</script>
