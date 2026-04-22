<template>
  <TabsTrigger
    :value="value"
    :disabled="disabled"
    :class="cn(
      'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary-color)] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-white data-[state=active]:text-[var(--text-primary)] data-[state=active]:shadow-sm',
      $attrs.class ?? ''
    )"
  >
    <slot />
  </TabsTrigger>
</template>

<script setup lang="ts">
import { TabsTrigger } from "reka-ui";
import { cn } from "@/lib/utils";

interface Props {
  value: string;
  disabled?: boolean;
}

defineProps<Props>();
</script>
