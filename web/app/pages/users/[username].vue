<script setup lang="ts">
import type { LibraryEntry, PublicDiaryEntry, PublicUser } from '~/types/api'
import { ApiError } from '~/composables/useApi'

const route = useRoute()
const username = computed(() => String(route.params.username))

const { loadProfile, loadLibrary, loadDiary, follow, block } = useUserProfile(username.value)
const auth = useAuthStore()

// One useAsyncData for all three: the library and diary requests depend on the
// profile's can_view_library flag, so they cannot be fetched in parallel with it.
const { data, error, refresh } = await useAsyncData(`profile-${username.value}`, async () => {
  const user = await loadProfile()
  const [library, diary] = await Promise.all([loadLibrary(user), loadDiary(user)])
  return { user, library, diary }
})

const user = computed<PublicUser | null>(() => data.value?.user ?? null)
const library = computed<LibraryEntry[]>(() => data.value?.library ?? [])
const diary = computed<PublicDiaryEntry[]>(() => data.value?.diary ?? [])

// A blocked user is served a 404 rather than a 403, so the page cannot be used
// to confirm that an account exists. Both land here as "not found".
if (error.value instanceof ApiError && error.value.status === 404) {
  throw createError({ statusCode: 404, statusMessage: 'User not found', fatal: true })
}

const displayName = computed(() => user.value?.profile.display_name || user.value?.username || '')

useHead(() => ({
  title: `${displayName.value} — Muratori`,
  // Profiles are public but thin; keep them out of the index until there is
  // enough on them to be worth a search result.
  meta: [{ name: 'robots', content: 'noindex, follow' }],
}))

const busy = ref(false)
const actionError = ref<string | null>(null)

async function toggleFollow() {
  if (!user.value) return
  busy.value = true
  actionError.value = null
  try {
    await follow(user.value, !user.value.is_following)
    await refresh()
  } catch (e) {
    actionError.value = e instanceof ApiError ? e.message : 'Could not update follow.'
  } finally {
    busy.value = false
  }
}

async function toggleBlock() {
  if (!user.value) return
  busy.value = true
  actionError.value = null
  const wasBlocked = user.value.has_blocked
  try {
    await block(user.value, !wasBlocked)
    // Blocking makes this profile invisible to us, so staying on the page would
    // only show a 404 on the next load. Send them somewhere that still exists.
    if (!wasBlocked) return await navigateTo('/')
    await refresh()
  } catch (e) {
    actionError.value = e instanceof ApiError ? e.message : 'Could not update block.'
  } finally {
    busy.value = false
  }
}

const statusLabels: Record<LibraryEntry['status'], string> = {
  watching: 'Watching',
  planned: 'Planned',
  completed: 'Completed',
  dropped: 'Dropped',
}
</script>

<template>
  <div v-if="user">
    <VCard class="mb-8" variant="tonal">
      <VCardText class="d-flex flex-wrap align-center" style="gap: 20px">
        <VAvatar :image="user.profile.avatar ?? undefined" size="88" color="surface-variant">
          <VIcon v-if="!user.profile.avatar" icon="mdi-account" size="44" />
        </VAvatar>

        <div class="flex-grow-1" style="min-width: 220px">
          <h1 class="text-h5">{{ displayName }}</h1>
          <div class="text-body-2 text-medium-emphasis">@{{ user.username }}</div>
          <p v-if="user.profile.bio" class="text-body-2 mt-2 mb-0">{{ user.profile.bio }}</p>

          <div class="d-flex flex-wrap text-body-2 text-medium-emphasis mt-3" style="gap: 16px">
            <span><strong>{{ user.followers_count }}</strong> followers</span>
            <span><strong>{{ user.following_count }}</strong> following</span>
            <span><strong>{{ user.ratings_count }}</strong> ratings</span>
            <span><strong>{{ user.reviews_count }}</strong> reviews</span>
          </div>
        </div>

        <div v-if="auth.isAuthenticated && !user.is_self" class="d-flex flex-column" style="gap: 8px">
          <VBtn
            :color="user.is_following ? 'surface-variant' : 'primary'"
            :loading="busy"
            :prepend-icon="user.is_following ? 'mdi-account-check' : 'mdi-account-plus'"
            @click="toggleFollow"
          >
            {{ user.is_following ? 'Following' : 'Follow' }}
          </VBtn>
          <VBtn
            variant="text"
            size="small"
            :loading="busy"
            :color="user.has_blocked ? 'warning' : undefined"
            @click="toggleBlock"
          >
            {{ user.has_blocked ? 'Unblock' : 'Block' }}
          </VBtn>
        </div>
      </VCardText>

      <VCardText v-if="actionError" class="pt-0">
        <VAlert type="error" variant="tonal" density="compact">{{ actionError }}</VAlert>
      </VCardText>
    </VCard>

    <VAlert
      v-if="!user.can_view_library"
      type="info"
      variant="tonal"
      icon="mdi-lock-outline"
      class="mb-6"
    >
      {{ displayName }} keeps their library private.
    </VAlert>

    <template v-else>
      <h2 class="text-h6 mb-3">Library</h2>
      <VEmptyState
        v-if="!library.length"
        icon="mdi-bookmark-outline"
        title="Nothing tracked yet"
        class="mb-6"
      />
      <VRow v-else class="mb-8">
        <VCol v-for="entry in library" :key="entry.id" cols="6" sm="4" md="3" lg="2">
          <MovieCard :item="entry.media_item_detail" />
          <div class="text-caption text-medium-emphasis mt-1">{{ statusLabels[entry.status] }}</div>
        </VCol>
      </VRow>

      <template v-if="diary.length">
        <h2 class="text-h6 mb-3">Diary</h2>
        <VList density="comfortable" class="mb-8">
          <VListItem v-for="entry in diary" :key="entry.id">
            <VListItemTitle>{{ entry.media_item_detail.title }}</VListItemTitle>
            <VListItemSubtitle>
              <template v-if="entry.watched_on">{{ entry.watched_on }}</template>
              <template v-else>Date not shared</template>
              <template v-if="entry.is_rewatch"> · rewatch</template>
            </VListItemSubtitle>
          </VListItem>
        </VList>
      </template>
    </template>
  </div>
</template>
