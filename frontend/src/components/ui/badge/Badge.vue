<template>
  <div :class="cn(badgeVariants({ variant }), $attrs.class ?? '')">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";
import { badgeVariants } from "./index";
import type { BadgeVariants } from "./index";

interface Props {
  variant?: BadgeVariants["variant"];
}

defineProps<Props>();
</script>
