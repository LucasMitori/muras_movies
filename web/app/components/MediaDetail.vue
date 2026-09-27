<script setup lang="ts">
import type { MediaItemDetail } from '~/types/api'

const props = defineProps<{ item: MediaItemDetail }>()
const auth = useAuthStore()

const { entry, load: loadEntry, setStatus } = useLibraryEntry(props.item.id)
const { rating, load: loadRating, setStars } = useRating(props.item.id)

if (auth.isAuthenticated) {
  await Promise.all([loadEntry(), loadRating()])
}

const statusOptions: { title: string; value: string }[] = [
  { title: 'Planned', value: 'planned' },
  { title: 'Watching', value: 'watching' },
  { title: 'Completed', value: 'completed' },
  { title: 'Dropped', value: 'dropped' },
]

const savingStatus = ref(false)
const savingRating = ref(false)

async function onStatusChange(status: string) {
  savingStatus.value = true
  try {
    await setStatus(status as never)
  } finally {
    savingStatus.value = false
  }
}

async function onRatingChange(stars: number) {
  savingRating.value = true
  try {
    await setStars(stars)
  } finally {
    savingRating.value = false
  }
}

const myStars = computed(() => (rating.value ? rating.value.value / 2 : null))
const muratoriStars = computed(() =>
  props.item.muratori_rating_average ? Number(props.item.muratori_rating_average) / 2 : null,
)
const runtimeLabel = computed(() => {
  const minutes = props.item.movie_details?.runtime_minutes
  if (!minutes) return null
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`
})
</script>

<template>
  <div>
    <div
      v-if="item.backdrop_url"
      class="rounded-lg mb-6"
      :style="{
        backgroundImage: `linear-gradient(to top, rgba(0,0,0,.65), rgba(0,0,0,.1)), url(${item.backdrop_url})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        aspectRatio: '16/6',
      }"
    />

    <VRow>
      <VCol cols="12" sm="4" md="3">
        <VImg :src="item.poster_url ?? undefined" aspect-ratio="2/3" cover class="rounded-lg bg-surface-variant" />
      </VCol>

      <VCol cols="12" sm="8" md="9">
        <h1 class="text-h4 mb-1">{{ item.title }}</h1>
        <div class="text-medium-emphasis mb-3">
          <span v-if="item.movie_details?.release_date">{{ item.movie_details.release_date.slice(0, 4) }}</span>
          <span v-if="item.series_details?.first_air_date">{{ item.series_details.first_air_date.slice(0, 4) }}</span>
          <span v-if="runtimeLabel"> · {{ runtimeLabel }}</span>
          <span v-if="item.series_details?.number_of_seasons">
            · {{ item.series_details.number_of_seasons }} season(s)
          </span>
        </div>

        <div class="d-flex flex-wrap mb-4" style="gap: 6px">
          <VChip v-for="genre in item.genres" :key="genre.id" size="small" variant="tonal">
            {{ genre.name }}
          </VChip>
        </div>

        <p class="text-body-1 mb-6" style="max-width: 60ch">{{ item.synopsis || 'No synopsis available yet.' }}</p>

        <VRow>
          <VCol cols="12" sm="6" md="4">
            <div class="text-caption text-medium-emphasis mb-1">Muratori rating</div>
            <div class="d-flex align-center" style="gap: 8px">
              <RatingStars :model-value="muratoriStars" readonly />
              <span v-if="item.muratori_rating_count" class="text-caption text-medium-emphasis">
                {{ item.muratori_rating_count }} rating(s)
              </span>
              <span v-else class="text-caption text-medium-emphasis">Unrated</span>
            </div>
            <div v-if="item.external_vote_average" class="text-caption text-medium-emphasis mt-1">
              TMDB: {{ Number(item.external_vote_average).toFixed(1) }}/10
              <span v-if="item.external_vote_count">({{ item.external_vote_count }} votes)</span>
            </div>
          </VCol>

          <VCol v-if="auth.isAuthenticated" cols="12" sm="6" md="4">
            <div class="text-caption text-medium-emphasis mb-1">Your rating</div>
            <RatingStars :model-value="myStars" :disabled="savingRating" @update:model-value="onRatingChange" />
          </VCol>

          <VCol v-if="auth.isAuthenticated" cols="12" sm="6" md="4">
            <VSelect
              :model-value="entry?.status ?? null"
              :items="statusOptions"
              label="Library status"
              variant="outlined"
              density="comfortable"
              :loading="savingStatus"
              hide-details
              clearable
              @update:model-value="(value: string | null) => value && onStatusChange(value)"
            />
          </VCol>
        </VRow>

        <VAlert v-if="!auth.isAuthenticated" type="info" variant="tonal" class="mt-4">
          <NuxtLink to="/login">Log in</NuxtLink> to track, rate, or review this title.
        </VAlert>
      </VCol>
    </VRow>

    <VDivider class="my-8" />

    <ReviewList :media-item-id="item.id" />
  </div>
</template>
