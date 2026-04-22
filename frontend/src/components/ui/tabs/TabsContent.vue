<template>
  <TabsContent
    :value="value"
    :class="cn(
      'mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 focus-visible:ring-offset-2',
      $attrs.class ?? ''
    )"
  >
    <slot />
  </TabsContent>
</template>

<script setup lang="ts">
import { TabsContent } from "reka-ui";
import { cn } from "@/lib/utils";

interface Props {
  value: string;
}

defineProps<Props>();
</script>
