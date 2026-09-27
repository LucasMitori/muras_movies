<script setup lang="ts">
import type { MediaItemSummary, Paginated } from '~/types/api'

useHead({ title: 'Muratori — discover movies & series' })

const search = ref('')
const { data, status, refresh } = await useAsyncData(
  'catalog-list',
  () => useApi()<Paginated<MediaItemSummary>>('/media/', { query: { search: search.value || undefined } }),
  { watch: [search] },
)

const items = computed(() => data.value?.results ?? [])
</script>

<template>
  <div>
    <div class="d-flex align-center mb-6" style="gap: 12px">
      <h1 class="text-h4">Discover</h1>
      <VSpacer />
      <VTextField
        v-model="search"
        placeholder="Search titles..."
        prepend-inner-icon="mdi-magnify"
        density="comfortable"
        variant="outlined"
        hide-details
        style="max-width: 320px"
        clearable
      />
    </div>

    <VProgressLinear v-if="status === 'pending'" indeterminate color="primary" class="mb-4" />

    <VRow v-if="items.length">
      <VCol v-for="item in items" :key="item.id" cols="6" sm="4" md="3" lg="2">
        <MovieCard :item="item" />
      </VCol>
    </VRow>

    <VEmptyState
      v-else-if="status !== 'pending'"
      icon="mdi-movie-search-outline"
      title="No titles yet"
      :text="
        search
          ? `Nothing matched “${search}”.`
          : 'The catalog is empty. Import something with `manage.py import_tmdb_popular`.'
      "
    />

    <VBtn v-if="status === 'error'" variant="tonal" class="mt-4" @click="refresh()">Retry</VBtn>
  </div>
</template>
