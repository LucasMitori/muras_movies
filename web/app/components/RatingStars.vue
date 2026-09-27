<script setup lang="ts">
const props = defineProps<{ modelValue: number | null; readonly?: boolean; disabled?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

// VRating's half-increments give us the 0.5..5.0 step scale directly.
function onUpdate(value: number) {
  if (props.readonly) return
  emit('update:modelValue', value)
}
</script>

<template>
  <VRating
    :model-value="modelValue ?? 0"
    half-increments
    density="comfortable"
    color="warning"
    :readonly="readonly"
    :disabled="disabled"
    :aria-label="readonly ? 'Rating' : 'Rate this title, half-star steps from 0.5 to 5'"
    @update:model-value="onUpdate"
  />
</template>
