<template>
  <Toaster
    position="top-center"
    :toast-options="{
      classes: {
        toast: 'bg-white border border-gray-200 text-gray-900 shadow-lg',
        title: 'text-sm font-medium',
        description: 'text-sm text-gray-500',
      },
    }"
  />
</template>

<script setup lang="ts">
import { Toaster } from "vue-sonner";
</script>
