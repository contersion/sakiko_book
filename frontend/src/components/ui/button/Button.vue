<template>
  <button :class="cn(buttonVariants({ variant, size }), $attrs.class ?? '')" v-bind="$attrs">
    <slot />
  </button>
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";
import { buttonVariants } from "./index";
import type { ButtonVariants } from "./index";

interface Props {
  variant?: ButtonVariants["variant"];
  size?: ButtonVariants["size"];
}

defineProps<Props>();
</script>
