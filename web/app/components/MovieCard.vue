<script setup lang="ts">
import { slugifyTitle } from '~/utils/slug'
import type { MediaItemSummary } from '~/types/api'

const props = defineProps<{ item: MediaItemSummary }>()

const detailRoute = computed(() => {
  const base = props.item.media_type === 'series' ? 'series' : 'movies'
  return `/${base}/${props.item.id}-${slugifyTitle(props.item.title)}`
})

const stars = computed(() => {
  const avg = props.item.muratori_rating_average
  return avg ? (Number(avg) / 2).toFixed(1) : null
})
</script>

<template>
  <NuxtLink :to="detailRoute" class="text-decoration-none">
    <VCard>
      <VImg :src="item.poster_url ?? undefined" aspect-ratio="2/3" cover class="bg-surface-variant">
        <template v-if="!item.poster_url" #placeholder>
          <div class="d-flex align-center justify-center fill-height text-medium-emphasis">
            <VIcon icon="mdi-image-off-outline" size="40" />
          </div>
        </template>
      </VImg>
      <VCardText class="pb-2">
        <div class="text-body-2 font-weight-medium text-truncate" :title="item.title">
          {{ item.title }}
        </div>
        <div v-if="stars" class="text-caption text-medium-emphasis d-flex align-center" style="gap: 4px">
          <VIcon icon="mdi-star" size="14" color="warning" />
          {{ stars }} · {{ item.muratori_rating_count }}
        </div>
        <div v-else class="text-caption text-medium-emphasis">Not yet rated</div>
      </VCardText>
    </VCard>
  </NuxtLink>
</template>
