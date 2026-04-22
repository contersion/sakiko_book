<template>
  <div :class="cn('animate-pulse rounded-md bg-gray-200', $attrs.class ?? '')" />
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";
</script>
