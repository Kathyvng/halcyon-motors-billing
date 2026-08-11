# Section A.2 -- System of Record Mapping

`billing_config.json` is the structured source of truth once it's built, but it shouldn't
live only as a file in a repo -- it needs a home in the actual systems Hologram runs on:

- **CRM (Salesforce)**: `order_form.org_id`, `order_form.order_form_number`, `start_date`,
  `initial_term_months`, `renewal_term_months`, and `payment_terms` map to the Opportunity/
  Contract object as the commercial system of record -- this is what Sales, Finance, and
  Deal Desk all reference when a customer asks "what did we sign up for?"
- **Billing platform**: `rate_plan`, `sim_hardware`, `sms`, `support_package`,
  `test_mode`, and `minimum_spend_schedule` map to the billing system's rate plan / SKU
  configuration -- this is what actually generates the invoice.

**What has to be right for downstream reporting and invoices to stay clean:**
`org_id`, the rate plan's included-data amount and MRC, and the minimum-spend tier
boundaries. If the org ID is mistyped or the tier boundaries are off by even one month
(see the Month 12 overlap in `billing_config.json`), every invoice for that org is wrong
until someone notices -- and by then it's a customer-facing billing dispute, not an
internal config fix.
