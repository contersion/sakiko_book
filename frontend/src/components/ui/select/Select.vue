<template>
  <SelectRoot v-bind="$attrs">
    <slot />
  </SelectRoot>
</template>

<script setup lang="ts">
import { SelectRoot } from "reka-ui";
</script>
