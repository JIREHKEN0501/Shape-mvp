import {
  CheckIcon,
  EyeIcon,
  HandIcon,
  MessageSquareTextIcon,
} from 'lucide-react'

import { ParticipantConsent } from '@/components/human-os/participant-consent'
import { ParticipantHeader } from '@/components/human-os/participant-header'

const principles = [
  {
    icon: EyeIcon,
    title: 'You will know what is happening',
    description:
      'Each part explains what it asks of you before you decide whether to continue.',
  },
  {
    icon: MessageSquareTextIcon,
    title: 'You will be addressed without judgement',
    description:
      'HumanOS communicates what has been observed. It does not label your character or intentions.',
  },
  {
    icon: HandIcon,
    title: 'You remain in control',
    description:
      'You may pause, ask for information, or leave. Continuing is always your decision.',
  },
]

const nextSteps = [
  'Read this introduction and review the participation information.',
  'Choose whether you wish to begin.',
  'Move through the experience at your own pace.',
]

export default function Page() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <ParticipantHeader />
      <main id="main-content">
        <section className="mx-auto grid max-w-6xl gap-12 px-5 py-16 sm:px-8 sm:py-24 lg:grid-cols-[minmax(0,1.15fr)_minmax(18rem,0.7fr)] lg:items-end lg:gap-20">
          <div>
            <p className="font-sans text-sm font-semibold uppercase tracking-widest text-primary">
              Welcome to HumanOS
            </p>
            <h1 className="mt-5 max-w-3xl font-serif text-5xl leading-[1.06] tracking-tight text-balance sm:text-6xl lg:text-7xl">
              A place to take part with clarity and choice.
            </h1>
          </div>
          <div className="border-t border-border pt-6 lg:border-t-0 lg:pt-0">
            <p className="text-lg leading-relaxed text-muted-foreground">
              HumanOS is a guided digital experience. It shares clear, governed observations without making unsupported conclusions about you.
            </p>
            <a
              href="#what-to-expect"
              className="mt-6 inline-flex min-h-11 items-center font-semibold text-primary underline decoration-primary/30 underline-offset-4 hover:decoration-primary focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring"
            >
              Understand what to expect
            </a>
          </div>
        </section>

        <section
          aria-labelledby="trust-heading"
          className="bg-muted"
        >
          <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-20">
            <div className="max-w-2xl">
              <p className="font-sans text-sm font-semibold uppercase tracking-widest text-primary">
                How you are treated
              </p>
              <h2 id="trust-heading" className="mt-3 font-serif text-3xl leading-tight text-balance sm:text-4xl">
                Trust starts with knowing the boundaries.
              </h2>
            </div>
            <div className="mt-10 grid gap-px overflow-hidden rounded-2xl border border-border bg-border md:grid-cols-3">
              {principles.map(({ icon: Icon, title, description }) => (
                <article key={title} className="bg-card p-6 sm:p-8">
                  <Icon className="size-5 text-primary" strokeWidth={1.75} aria-hidden="true" />
                  <h3 className="mt-8 font-sans text-lg font-semibold text-balance">{title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section
          id="what-to-expect"
          aria-labelledby="expect-heading"
          className="mx-auto grid max-w-6xl gap-12 px-5 py-16 sm:px-8 sm:py-24 lg:grid-cols-2 lg:gap-20"
        >
          <div>
            <p className="font-sans text-sm font-semibold uppercase tracking-widest text-primary">
              What happens next
            </p>
            <h2 id="expect-heading" className="mt-3 max-w-lg font-serif text-3xl leading-tight text-balance sm:text-4xl">
              A simple process, explained before it begins.
            </h2>
            <p className="mt-5 max-w-lg leading-relaxed text-muted-foreground">
              You do not need special knowledge to take part. Read each prompt, respond in the way that is right for you, and use the available controls whenever you need them.
            </p>
          </div>
          <ol className="flex flex-col gap-6" aria-label="The next three steps">
            {nextSteps.map((step, index) => (
              <li key={step} className="flex gap-4 border-b border-border pb-6 last:border-b-0">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted font-sans text-sm font-semibold text-primary" aria-hidden="true">
                  {index + 1}
                </span>
                <p className="pt-1 text-base leading-relaxed">{step}</p>
              </li>
            ))}
          </ol>
        </section>

        <section aria-labelledby="governance-heading" className="mx-auto max-w-6xl px-5 pb-16 sm:px-8 sm:pb-24">
          <div className="grid gap-10 rounded-2xl border border-border bg-card p-6 sm:p-10 lg:grid-cols-[0.8fr_1.2fr] lg:gap-16">
            <div>
              <p className="font-sans text-sm font-semibold uppercase tracking-widest text-primary">
                About your interaction
              </p>
              <h2 id="governance-heading" className="mt-3 font-serif text-3xl leading-tight text-balance">
                Clear information, protected boundaries.
              </h2>
            </div>
            <ul className="flex flex-col gap-5" aria-label="Interaction commitments">
              {[
                'Information shown to you is checked against the purpose of this experience.',
                'Changes in presentation do not change the meaning of the information you receive.',
                'Protected internal processes are not shown, but the information you need to make a choice is made clear.',
              ].map((item) => (
                <li key={item} className="flex gap-3 text-sm leading-relaxed text-muted-foreground">
                  <CheckIcon className="mt-0.5 size-5 shrink-0 text-primary" aria-hidden="true" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section id="accessibility" aria-labelledby="accessibility-heading" className="bg-muted">
          <div className="mx-auto grid max-w-6xl gap-6 px-5 py-12 sm:px-8 md:grid-cols-[1fr_auto] md:items-center">
            <div>
              <h2 id="accessibility-heading" className="font-sans text-lg font-semibold">
                Use the experience in the way that works for you.
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
                You may use browser zoom, keyboard navigation, or a screen reader. You can also take breaks and return when you are ready.
              </p>
            </div>
            <p className="text-sm font-medium text-primary">
              Browser controls remain available throughout.
            </p>
          </div>
        </section>

        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
          <ParticipantConsent />
        </div>
      </main>

      <footer id="leaving" className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-5 py-8 text-sm text-muted-foreground sm:px-8 md:flex-row md:items-center md:justify-between">
          <p>You may close this page at any time.</p>
          <p>HumanOS participant experience</p>
        </div>
      </footer>
    </div>
  )
}
