export const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api'

export interface Bookmark {
  id: string
  url: string
  title?: string
  created_at: string
}

/**
 * Add a new bookmark (Free tier stores locally, but endpoint exists for Pro sync)
 */
export async function addBookmark(url: string, title?: string): Promise<Bookmark> {
  const resp = await fetch(`${API_BASE}/bookmarks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url, title })
  })
  if (!resp.ok) {
    const err = await resp.json()
    throw new Error(err.message || 'Failed to add bookmark')
  }
  return resp.json()
}

/**
 * Search bookmarks locally – placeholder for future server‑side search.
 */
export async function searchBookmarks(query: string): Promise<Bookmark[]> {
  const resp = await fetch(`${API_BASE}/bookmarks`)
  if (!resp.ok) {
    const err = await resp.json()
    throw new Error(err.message || 'Failed to fetch bookmarks')
  }
  const all: Bookmark[] = await resp.json()
  if (!query) return all
  const lower = query.toLowerCase()
  return all.filter(
    b => b.url.toLowerCase().includes(lower) || (b.title?.toLowerCase().includes(lower) ?? false)
  )
}

/**
 * Request AI‑generated tags for a URL.
 */
export async function generateTags(url: string, maxTags = 3): Promise<string[]> {
  const resp = await fetch(`${API_BASE}/generate-tags`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ url, max_tags: maxTags })
  })
  if (!resp.ok) {
    const err = await resp.json()
    throw new Error(err.message || 'Failed to generate tags')
  }
  const data = await resp.json()
  return data.tags as string[]
}
