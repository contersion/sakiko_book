<template>
  <hr :class="cn('shrink-0 bg-gray-200', orientation === 'horizontal' ? 'h-[1px] w-full' : 'h-full w-[1px]', $attrs.class ?? '')" />
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";

interface Props {
  orientation?: "horizontal" | "vertical";
}

withDefaults(defineProps<Props>(), {
  orientation: "horizontal",
});
</script>
