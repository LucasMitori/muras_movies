// Mirrors the DRF serializers in backend/apps/*/serializers.py. Keep in
// sync by hand until the OpenAPI-generated client (drf-spectacular) lands.

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiErrorBody {
  detail: string
  code: string
  errors: Record<string, string[]> | null
}

export interface Profile {
  display_name: string
  bio: string
  avatar: string | null
  library_visibility: 'public' | 'followers' | 'private'
  diary_dates_visibility: 'public' | 'followers' | 'private'
  show_on_public_leaderboards: boolean
}

export interface AuthUser {
  id: number
  username: string
  email: string
  date_joined: string
  profile: Profile
}

/** The subset of a Profile that anyone may see (no visibility settings). */
export interface PublicProfile {
  display_name: string
  bio: string
  avatar: string | null
}

/**
 * Another user as the current requester sees them. The relationship and
 * can_view_* flags are computed per requester on the server, so the client
 * never has to re-derive the privacy rule.
 */
export interface PublicUser {
  id: number
  username: string
  date_joined: string
  profile: PublicProfile
  followers_count: number
  following_count: number
  ratings_count: number
  reviews_count: number
  is_self: boolean
  is_following: boolean
  is_followed_by: boolean
  has_blocked: boolean
  can_view_library: boolean
  can_view_diary_dates: boolean
}

export interface Genre {
  id: number
  name: string
  slug: string
}

export type MediaType = 'movie' | 'series'

export interface MediaItemSummary {
  id: number
  slug: string
  media_type: MediaType
  title: string
  poster_url: string | null
  genres: Genre[]
  external_vote_average: string | null
  muratori_rating_average: string | null
  muratori_rating_count: number
}

export interface MovieDetails {
  release_date: string | null
  runtime_minutes: number | null
}

export interface SeriesDetails {
  first_air_date: string | null
  last_air_date: string | null
  status: string
  number_of_seasons: number | null
  number_of_episodes: number | null
}

export interface MediaItemDetail extends MediaItemSummary {
  original_title: string
  original_language: string
  synopsis: string
  backdrop_url: string | null
  external_vote_count: number | null
  movie_details: MovieDetails | null
  series_details: SeriesDetails | null
}

export type LibraryStatus = 'planned' | 'watching' | 'completed' | 'dropped'

export interface LibraryEntry {
  id: number
  media_item: number
  media_item_detail: MediaItemSummary
  status: LibraryStatus
  created_at: string
  updated_at: string
}

/** Someone else's diary entry: watched_on is null when they withhold dates. */
export interface PublicDiaryEntry {
  id: number
  media_item: number
  media_item_detail: MediaItemSummary
  watched_on: string | null
  is_rewatch: boolean
  note: string
  created_at: string
}

export interface Rating {
  id: number
  media_item: number
  value: number
  stars: number
  created_at: string
  updated_at: string
}

export interface ReviewAuthor {
  id: number
  username: string
}

export interface Review {
  id: number
  media_item: number
  author: ReviewAuthor
  body: string
  contains_spoilers: boolean
  created_at: string
  updated_at: string
}
