<template>
  <TabsList
    :class="cn(
      'inline-flex h-9 items-center justify-center rounded-lg bg-[var(--button-secondary-bg)] p-1 text-[var(--text-secondary)]',
      $attrs.class ?? ''
    )"
  >
    <slot />
  </TabsList>
</template>

<script setup lang="ts">
import { TabsList } from "reka-ui";
import { cn } from "@/lib/utils";
</script>
