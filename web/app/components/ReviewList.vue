<script setup lang="ts">
import type { Paginated, Review } from '~/types/api'

const props = defineProps<{ mediaItemId: number }>()
const auth = useAuthStore()
const api = useApi()

const { data, refresh } = await useAsyncData(`reviews-${props.mediaItemId}`, () =>
  api<Paginated<Review>>('/reviews/', { query: { media_item: props.mediaItemId } }),
)

const reviews = computed(() => data.value?.results ?? [])
const myReview = computed(() => reviews.value.find((r) => r.author.id === auth.user?.id) ?? null)

const draft = ref('')
const submitting = ref(false)
const errorMessage = ref('')

watchEffect(() => {
  draft.value = myReview.value?.body ?? ''
})

async function submit() {
  if (!draft.value.trim()) return
  submitting.value = true
  errorMessage.value = ''
  try {
    if (myReview.value) {
      await api(`/reviews/${myReview.value.id}/`, { method: 'PATCH', body: { body: draft.value } })
    } else {
      await api('/reviews/', { method: 'POST', body: { media_item: props.mediaItemId, body: draft.value } })
    }
    await refresh()
  } catch {
    errorMessage.value = 'Could not save your review. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div>
    <h2 class="text-h6 mb-3">Reviews</h2>

    <VCard v-if="auth.isAuthenticated" variant="tonal" class="mb-6">
      <VCardText>
        <VTextarea
          v-model="draft"
          :label="myReview ? 'Edit your review' : 'Write a review'"
          rows="3"
          auto-grow
          hide-details
        />
        <VAlert v-if="errorMessage" type="error" variant="tonal" density="compact" class="mt-2">
          {{ errorMessage }}
        </VAlert>
      </VCardText>
      <VCardActions>
        <VSpacer />
        <VBtn color="primary" :loading="submitting" @click="submit">
          {{ myReview ? 'Update review' : 'Post review' }}
        </VBtn>
      </VCardActions>
    </VCard>

    <VList v-if="reviews.length" lines="three">
      <VListItem v-for="review in reviews" :key="review.id">
        <VListItemTitle class="font-weight-medium">{{ review.author.username }}</VListItemTitle>
        <VListItemSubtitle style="white-space: normal">{{ review.body }}</VListItemSubtitle>
      </VListItem>
    </VList>
    <p v-else class="text-medium-emphasis">No reviews yet — be the first to write one.</p>
  </div>
</template>
