<script setup lang="ts">
import type { LibraryEntry, Paginated } from '~/types/api'

definePageMeta({ middleware: 'auth' })
useHead({ title: 'My library — Muratori', meta: [{ name: 'robots', content: 'noindex, nofollow' }] })

const { data } = await useAsyncData('my-library-entries', () =>
  useApi()<Paginated<LibraryEntry>>('/entries/', { query: { limit: 100 } }),
)

const entries = computed(() => data.value?.results ?? [])

const groups: { title: string; status: LibraryEntry['status'] }[] = [
  { title: 'Watching', status: 'watching' },
  { title: 'Planned', status: 'planned' },
  { title: 'Completed', status: 'completed' },
  { title: 'Dropped', status: 'dropped' },
]
</script>

<template>
  <div>
    <h1 class="text-h4 mb-6">My library</h1>

    <VEmptyState
      v-if="!entries.length"
      icon="mdi-bookmark-outline"
      title="Nothing tracked yet"
      text="Rate or track a title from its page to see it here."
    />

    <div v-for="group in groups" :key="group.status" class="mb-8">
      <template v-if="entries.some((e) => e.status === group.status)">
        <h2 class="text-h6 mb-3">{{ group.title }}</h2>
        <VRow>
          <VCol
            v-for="entry in entries.filter((e) => e.status === group.status)"
            :key="entry.id"
            cols="6"
            sm="4"
            md="3"
            lg="2"
          >
            <MovieCard :item="entry.media_item_detail" />
          </VCol>
        </VRow>
      </template>
    </div>
  </div>
</template>
