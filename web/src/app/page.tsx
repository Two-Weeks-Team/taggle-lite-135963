"use client"

import { BookmarkForm } from '@/components/BookmarkForm'
import { BookmarkList } from '@/components/BookmarkList'

export default function HomePage() {
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Taggle Lite</h1>
      <BookmarkForm />
      <BookmarkList />
    </main>
  )
}