import Link from 'next/link'

export function ParticipantHeader() {
  return (
    <header className="border-b border-border" aria-label="HumanOS participant header">
      <div className="mx-auto flex min-h-20 max-w-6xl items-center justify-between gap-6 px-5 sm:px-8">
        <Link
          href="#main-content"
          className="font-sans text-lg font-semibold tracking-tight text-foreground focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring"
        >
          Human<span className="text-primary">OS</span>
        </Link>
        <nav aria-label="Page links" className="flex items-center gap-5 text-sm">
          <Link
            href="#accessibility"
            className="text-muted-foreground underline-offset-4 hover:text-foreground hover:underline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring"
          >
            Accessibility
          </Link>
          <Link
            href="#leaving"
            className="hidden text-muted-foreground underline-offset-4 hover:text-foreground hover:underline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring sm:inline"
          >
            Leaving is always your choice
          </Link>
        </nav>
      </div>
    </header>
  )
}
