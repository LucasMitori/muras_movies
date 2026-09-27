import type { LibraryEntry, LibraryStatus, Paginated, Rating } from '~/types/api'

/**
 * Upsert helpers for the "one row per (user, media_item)" resources.
 * The API enforces the uniqueness; here we just look up whether a row
 * already exists to decide POST vs PATCH.
 */
export function useLibraryEntry(mediaItemId: number) {
  const api = useApi()
  const entry = ref<LibraryEntry | null>(null)
  const loading = ref(false)

  async function load() {
    loading.value = true
    try {
      const page = await api<Paginated<LibraryEntry>>('/entries/', { query: { media_item: mediaItemId } })
      entry.value = page.results[0] ?? null
    } finally {
      loading.value = false
    }
  }

  async function setStatus(status: LibraryStatus) {
    if (entry.value) {
      entry.value = await api<LibraryEntry>(`/entries/${entry.value.id}/`, { method: 'PATCH', body: { status } })
    } else {
      entry.value = await api<LibraryEntry>('/entries/', {
        method: 'POST',
        body: { media_item: mediaItemId, status },
      })
    }
  }

  return { entry, loading, load, setStatus }
}

export function useRating(mediaItemId: number) {
  const api = useApi()
  const rating = ref<Rating | null>(null)
  const loading = ref(false)

  async function load() {
    loading.value = true
    try {
      const page = await api<Paginated<Rating>>('/ratings/', { query: { media_item: mediaItemId } })
      rating.value = page.results[0] ?? null
    } finally {
      loading.value = false
    }
  }

  async function setStars(stars: number) {
    const value = Math.round(stars * 2)
    if (rating.value) {
      rating.value = await api<Rating>(`/ratings/${rating.value.id}/`, { method: 'PATCH', body: { value } })
    } else {
      rating.value = await api<Rating>('/ratings/', { method: 'POST', body: { media_item: mediaItemId, value } })
    }
  }

  return { rating, loading, load, setStars }
}
