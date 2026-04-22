<template>
  <SelectValue v-bind="$attrs" :class="cn('text-sm', $attrs.class ?? '')">
    <slot />
  </SelectValue>
</template>

<script setup lang="ts">
import { SelectValue } from "reka-ui";
import { cn } from "@/lib/utils";
</script>
