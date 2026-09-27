import type { MediaItemDetail } from '~/types/api'
import { idFromRouteParam } from '~/utils/slug'

/** Loads one title by the numeric id encoded at the front of the [idSlug] route param. */
export function useMediaItem() {
  const route = useRoute()
  const idSlug = route.params.idSlug as string
  const id = idFromRouteParam(idSlug)

  if (id === null) {
    throw createError({ statusCode: 404, statusMessage: 'Unknown title.' })
  }

  return useAsyncData(`media-item-${id}`, async () => {
    try {
      return await useApi()<MediaItemDetail>(`/media/${id}/`)
    } catch {
      throw createError({ statusCode: 404, statusMessage: 'This title could not be found.' })
    }
  })
}
