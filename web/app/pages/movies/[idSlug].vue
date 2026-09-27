<script setup lang="ts">
const { data: item } = await useMediaItem()
useHead({ title: () => (item.value ? `${item.value.title} — Muratori` : 'Muratori') })
</script>

<template>
  <MediaDetail v-if="item" :item="item" />
</template>
