import './globals.css'

export const metadata = {
  title: 'Taggle Lite',
  description: 'Simple, local‑only bookmark manager'
}

export default function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-100 min-h-screen">{children}</body>
    </html>
  )
}