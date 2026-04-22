<template>
  <SliderRoot
    :model-value="sliderValue"
    @update:model-value="handleUpdate"
    :class="cn('relative flex w-full touch-none select-none items-center', $attrs.class ?? '')"
  >
    <SliderTrack class="relative h-1.5 w-full grow overflow-hidden rounded-full bg-gray-200">
      <SliderRange class="absolute h-full bg-gray-900" />
    </SliderTrack>
    <SliderThumb
      class="block h-4 w-4 rounded-full border border-gray-200 bg-white shadow transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gray-400 disabled:pointer-events-none disabled:opacity-50"
    />
  </SliderRoot>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { SliderRoot, SliderTrack, SliderRange, SliderThumb } from "reka-ui";
import { cn } from "@/lib/utils";

const modelValue = defineModel<number>();

const sliderValue = computed(() => [modelValue.value ?? 0]);

function handleUpdate(val: number[] | undefined) {
  modelValue.value = val?.[0] ?? 0;
}
</script>
