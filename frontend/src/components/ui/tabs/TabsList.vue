<template>
  <TabsList
    :class="cn(
      'inline-flex h-9 items-center justify-center rounded-lg bg-gray-100 p-1 text-gray-500',
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
