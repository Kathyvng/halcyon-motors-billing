# Section C -- Go-Live QA & Customer Communication

## C.1 -- Things I would not silently guess on before go-live

1. **Month 12 falls in two tiers at once.** The minimum-spend schedule lists "Months
   7-12" at $600/month and "Months 12-24" at $1,200/month -- month 12 is in both. That's
   a $600 swing for one month, times however many customers share this template. I
   resolved it as $600 in the config (first-listed tier wins) but flagged it rather than
   guessing silently.
2. **No stated proration rule for Test Mode -> Active mid-month.** If a SIM converts on
   day 17 of a 30-day month, does it owe a full month's MRC or a partial one? The
   contract is silent. I assumed full-month MRC starting the month of transition, but
   this should be confirmed before the first invoice run.
3. **SIM hardware has no stated billing frequency.** MRC is explicitly "Monthly" and
   overage is explicitly "Pay as you go" -- SIM hardware has neither label. I assumed
   one-time at purchase, which is standard for hardware, but it's not stated.
4. **Unmigrated G1 SIMs fall back to "one of Hologram's standard plans... with the
   associated rates" -- unnamed.** If any of Halcyon's SIMs fail migration, there's no
   rate in this order form to bill them against.
5. **"Active SIM count" isn't defined for a fleet that changes size mid-month.** If SIMs
   are added or removed mid-month, is pool sizing based on an end-of-month snapshot, a
   daily average, or SIM-days? This directly changes the pool total and therefore the
   overage calculation.

## C.2 -- The message I'd send to get one resolved

**To:** Deal Desk (internal, before this goes near the customer)
**Subject:** Halcyon Motors (Org 90342) -- Month 12 minimum-spend tier is ambiguous, need a ruling before go-live

> Hey team -- reviewing the Halcyon Motors order form (00002891) for go-live and the
> minimum-spend schedule has an overlap: Month 12 is listed under both "Months 7-12"
> ($600/mo) and "Months 12-24" ($1,200/mo). That's a $600 difference for a single
> invoice, and I don't want to guess which one the deal desk intended when this
> template was built.
>
> Can you confirm which rate applies to month 12 specifically? I've defaulted the
> config to $600 (treating "Months 7-12" as inclusive and "Months 12-24" as starting
> at month 13) so I can keep moving, but I want that confirmed -- or corrected -- before
> the first invoice generates. Happy to hop on a call if faster.

## C.3 -- What I'd automate first, and what I'd cut

**Automate first:** generating `billing_config.json` directly from the signed order
form instead of a human re-reading the PDF each time. The order form is structured
enough (consistent tables for rate plan, hardware, SMS, test mode, minimum spend) that
an AI-assisted extraction step could produce a first-pass config automatically, with a
human only reviewing the fields flagged as ambiguous or out of pattern -- which turns
this exercise from a 90-minute manual read into a 10-minute review.

**Eliminate:** re-deriving the minimum-spend tier lookup by hand on every renewal. Once
the schedule is captured once as structured data, the "which tier applies to which
month" question should never require a human to re-read the contract again -- it's a
lookup, not a judgment call, and treating it as a judgment call is exactly where the
Month 12 overlap becomes a real invoicing risk instead of a documentation footnote.
