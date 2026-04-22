<template>
  <div class="app-provider">
    <slot />
    <Sonner />
  </div>
</template>

<script setup lang="ts">
import { Sonner } from "@/components/ui/sonner";
</script>
