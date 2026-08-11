'use client'

import { useState } from 'react'
import { ArrowRightIcon } from 'lucide-react'

import { Button } from '@/components/ui/button'

export function ParticipantConsent() {
  const [hasAgreed, setHasAgreed] = useState(false)
  const [hasBegun, setHasBegun] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function beginExperience() {
    if (isSubmitting || !hasAgreed) return

    setIsSubmitting(true)
    setError(null)

    try {
      const response = await fetch('/consent', {
        method: 'POST',
        credentials: 'include',
      })

      const result: { ok?: boolean } = await response.json()
      if (!response.ok || !result.ok) {
        throw new Error('Consent could not be recorded.')
      }

      setHasBegun(true)
      window.location.assign('/task/pattern_recognition_v1')
    } catch {
      setError('We could not record your choice. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section
      id="before-you-begin"
      aria-labelledby="consent-heading"
      className="rounded-2xl bg-primary px-6 py-8 text-primary-foreground sm:px-10 sm:py-10"
    >
      <div className="max-w-2xl">
        <p className="font-sans text-sm font-semibold uppercase tracking-widest text-primary-foreground/75">
          Your choice
        </p>
        <h2 id="consent-heading" className="mt-3 font-serif text-3xl leading-tight text-balance sm:text-4xl">
          Begin only when you feel informed and ready.
        </h2>
        <p className="mt-4 max-w-xl text-base leading-relaxed text-primary-foreground/80">
          Taking part is voluntary. You can pause or leave at any point. Choosing not to continue will not be treated as a judgement about you.
        </p>

        <label className="mt-7 flex cursor-pointer items-start gap-3 rounded-xl bg-primary-foreground/10 p-4 text-sm leading-relaxed">
          <input
            type="checkbox"
            checked={hasAgreed}
            onChange={(event) => setHasAgreed(event.target.checked)}
            className="mt-1 size-4 shrink-0 accent-current"
          />
          <span>I understand what this experience involves and choose to begin.</span>
        </label>

        <div className="mt-6 flex flex-col items-start gap-3 sm:flex-row sm:items-center">
          <Button
            size="lg"
            variant="secondary"
            disabled={!hasAgreed || hasBegun || isSubmitting}
            className="h-11 px-5"
            onClick={beginExperience}
          >
            {hasBegun ? 'Choice confirmed' : isSubmitting ? 'Confirming choice…' : 'Begin the experience'}
            {!hasBegun && <ArrowRightIcon data-icon="inline-end" aria-hidden="true" />}
          </Button>
          {!hasAgreed && (
            <p className="text-sm text-primary-foreground/70">
              Please confirm your choice to continue.
            </p>
          )}
          {hasBegun && (
            <p className="text-sm font-medium text-primary-foreground" role="status">
              You have chosen to begin.
            </p>
          )}
          {error && (
            <p className="text-sm font-medium text-primary-foreground" role="alert">
              {error}
            </p>
          )}
        </div>
      </div>
    </section>
  )
}
