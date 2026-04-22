<template>
  <DialogDescription :class="cn('text-sm text-gray-500', $attrs.class ?? '')">
    <slot />
  </DialogDescription>
</template>

<script setup lang="ts">
import { DialogDescription } from "reka-ui";
import { cn } from "@/lib/utils";
</script>
