<template>
  <TabsRoot v-bind="$attrs">
    <slot />
  </TabsRoot>
</template>

<script setup lang="ts">
import { TabsRoot } from "reka-ui";
</script>
