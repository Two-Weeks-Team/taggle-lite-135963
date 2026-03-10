"use client"

import { useEffect, useState } from 'react'
import { getAllBookmarks, deleteBookmarkFromIDB } from '@/lib/idb'

export function BookmarkList() {
  const [bookmarks, setBookmarks] = useState<Array<{ id: string; url: string; title?: string }>>([])
  const [filter, setFilter] = useState('')

  const load = async () => {
    const all = await getAllBookmarks()
    setBookmarks(all)
  }

  useEffect(() => {
    load()
  }, [])

  const handleDelete = async (id: string) => {
    await deleteBookmarkFromIDB(id)
    setBookmarks(prev => prev.filter(b => b.id !== id))
  }

  const filtered = bookmarks.filter(b => {
    const q = filter.toLowerCase()
    return b.url.toLowerCase().includes(q) || (b.title?.toLowerCase().includes(q) ?? false)
  })

  return (
    <section>
      <input
        type="text"
        placeholder="Search bookmarks..."
        value={filter}
        onChange={e => setFilter(e.target.value)}
        className="w-full p-2 border rounded mb-4"
      />
      {filtered.length === 0 ? (
        <p className="text-gray-500">No bookmarks found.</p>
      ) : (
        <ul className="space-y-2">
          {filtered.map(b => (
            <li key={b.id} className="p-2 border rounded flex justify-between items-center">
              <div>
                <a href={b.url} target="_blank" rel="noopener noreferrer" className="font-medium text-blue-600">
                  {b.title || b.url}
                </a>
                <div className="text-sm text-gray-500">{b.url}</div>
              </div>
              <button
                onClick={() => handleDelete(b.id)}
                className="text-red-500 hover:underline"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
