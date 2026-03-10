"use client"

import { useState } from 'react'
import { addBookmark, generateTags } from '@/lib/api'
import { addBookmarkToIDB } from '@/lib/idb'
import { v4 as uuidv4 } from 'uuid'

export function BookmarkForm() {
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [suggestedTags, setSuggestedTags] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url) return
    setLoading(true)
    try {
      const newBookmark = {
        id: uuidv4(),
        url,
        title: title || undefined,
        created_at: new Date().toISOString()
      }
      await addBookmarkToIDB(newBookmark)
      await addBookmark(url, title)
      setUrl('')
      setTitle('')
      setSuggestedTags([])
    } catch (err) {
      console.error(err)
      alert('Failed to save bookmark')
    } finally {
      setLoading(false)
    }
  }

  const fetchTags = async () => {
    if (!url) return
    try {
      const tags = await generateTags(url)
      setSuggestedTags(tags)
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 mb-6">
      <input
        type="url"
        placeholder="https://example.com"
        value={url}
        onChange={e => setUrl(e.target.value)}
        onBlur={fetchTags}
        required
        className="p-2 border rounded"
      />
      <input
        type="text"
        placeholder="Optional title"
        value={title}
        onChange={e => setTitle(e.target.value)}
        className="p-2 border rounded"
      />
      {suggestedTags.length > 0 && (
        <div className="text-sm text-gray-600">
          Suggested tags: {suggestedTags.join(', ')}
        </div>
      )}
      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
      >
        {loading ? 'Saving...' : 'Add Bookmark'}
      </button>
    </form>
  )
}
