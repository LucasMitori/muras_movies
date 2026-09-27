import type { LibraryEntry, Paginated, PublicDiaryEntry, PublicUser } from '~/types/api'
import { ApiError } from '~/composables/useApi'

/**
 * Loads a public profile plus the parts of it this viewer is allowed to see.
 *
 * The server decides visibility; this only reacts to it. `can_view_library`
 * tells us whether to ask for the library at all, which keeps the common case
 * from firing a request that is certain to come back 403. A 403 is still
 * handled, because the flag and the list are two separate requests and the
 * owner could tighten the setting between them.
 */
export function useUserProfile(username: string) {
  const api = useApi()

  const follow = async (target: PublicUser, shouldFollow: boolean) => {
    await api(`/accounts/users/${encodeURIComponent(target.username)}/follow/`, {
      method: shouldFollow ? 'POST' : 'DELETE',
    })
  }

  const block = async (target: PublicUser, shouldBlock: boolean) => {
    await api(`/accounts/users/${encodeURIComponent(target.username)}/block/`, {
      method: shouldBlock ? 'POST' : 'DELETE',
    })
  }

  const loadProfile = () => api<PublicUser>(`/accounts/users/${encodeURIComponent(username)}/`)

  const loadLibrary = async (user: PublicUser | null) => {
    if (!user?.can_view_library) return []
    try {
      const page = await api<Paginated<LibraryEntry>>(
        `/accounts/users/${encodeURIComponent(user.username)}/library/`,
        { query: { limit: 60 } },
      )
      return page.results
    } catch (error) {
      if (error instanceof ApiError && error.status === 403) return []
      throw error
    }
  }

  const loadDiary = async (user: PublicUser | null) => {
    if (!user?.can_view_library) return []
    try {
      const page = await api<Paginated<PublicDiaryEntry>>(
        `/accounts/users/${encodeURIComponent(user.username)}/diary/`,
        { query: { limit: 30 } },
      )
      return page.results
    } catch (error) {
      if (error instanceof ApiError && error.status === 403) return []
      throw error
    }
  }

  return { loadProfile, loadLibrary, loadDiary, follow, block }
}
