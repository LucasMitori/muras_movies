/** Cosmetic slug for /movies/[id]-[slug] routes. The id is what's resolved; the slug is decorative. */
export function slugifyTitle(title: string): string {
  return title
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

/** Parses the leading numeric id off a "[id]-[slug]" route param. */
export function idFromRouteParam(param: string): number | null {
  const match = /^(\d+)/.exec(param)
  return match ? Number(match[1]) : null
}
