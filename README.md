# halcyon-motors-billing

# Halcyon Motors -- Contract-to-Billing Configuration

Take-home exercise for Hologram's GTM Engineer, Post-Sales role. Translates the signed
order form (00002891, org 90342) into a structured billing configuration, computable
billing logic, and go-live QA.

## Repo structure

| File | Section | What it is |
|---|---|---|
| `billing_config.json` | A | Structured billing config for every billable term in the contract |
| `SECTION_A_NOTES.md` | A.2 | System-of-record mapping (CRM vs. billing platform) |
| `billing_calculator.py` | B | Billing logic + the worked Month 8 example |
| `SECTION_C.md` | C | Contract ambiguities, the one escalation message, and the automation call |

## How to run

```
python3 billing_calculator.py
```

Runs the Month 8 example (150 active SIMs, 2,400MB pooled usage) and prints the full
breakdown plus a step-by-step trace. No dependencies beyond the Python standard library.

## Assumptions

- **Month 12 minimum-spend tier**: the contract's schedule overlaps at month 12 (listed
  under both "Months 7-12" and "Months 12-24"). Resolved as $600/month (the earlier
  tier) rather than guessing -- flagged explicitly in `SECTION_C.md`.
- **Test Mode -> Active proration**: assumed a SIM that transitions mid-month is billed
  a full month's MRC starting the month of transition, since the contract doesn't state
  a proration rule.
- **SIM hardware frequency**: assumed one-time at purchase, since it's the only line
  item without an explicit frequency label (unlike MRC's "Monthly" and overage's "Pay
  as you go").
- **Outbound SMS in the worked example**: the prompt didn't specify an SMS count for
  Month 8, so it's assumed to be 0 in the worked example.
- **Unmigrated G1 SIMs**: no rate is specified in this order form for SIMs that fail
  migration to G3, so they're excluded from this config and flagged as an open item.

## AI usage disclosure

I used Claude (Anthropic) to help draft this repo -- specifically:
- Structuring the JSON schema for `billing_config.json` from the raw contract text
- Drafting the initial Python logic in `billing_calculator.py`, which I then verified
  by hand-checking the Month 8 example against the contract terms myself
- Drafting the language in `SECTION_C.md`

I reviewed and verified all dollar figures and logic against the signed order form
directly -- the reasoning and the choice of what to flag as ambiguous is my own.
