"""
Halcyon Motors -- Contract-to-Billing Calculator (Section B)

Loads billing_config.json (the structured Section A output) and computes
a given month's charge from three inputs: month number, active SIM count,
and total pooled data usage for the month.

Run directly to see the worked Month 8 example:
    python3 billing_calculator.py
"""

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "billing_config.json")


def load_config(path: str = CONFIG_PATH) -> dict:
    with open(path, "r") as f:
        return json.load(f)


CONFIG = load_config()
INCLUDED_MB_PER_SIM = CONFIG["rate_plan"]["included_data_mb_per_sim"]
MRC_RATE = CONFIG["rate_plan"]["mrc_per_sim_usd"]
OVERAGE_RATE = CONFIG["rate_plan"]["overage_rate_usd_per_mb"]
SMS_OUTBOUND_RATE = CONFIG["sms"]["outbound"]["rate_usd"]
MIN_SPEND_SCHEDULE = CONFIG["minimum_spend_schedule"]


def pool_included_mb(active_sims: int) -> float:
    """Each SIM in the pool contributes its included data to the shared pool."""
    return active_sims * INCLUDED_MB_PER_SIM


def data_overage_charge(total_pooled_usage_mb: float, active_sims: int) -> float:
    """
    Overage is assessed at month-end against the POOL total, not per-SIM.
    Only usage above the combined included amount is billed.
    """
    included = pool_included_mb(active_sims)
    overage_mb = max(0.0, total_pooled_usage_mb - included)
    return round(overage_mb * OVERAGE_RATE, 2)


def mrc_charge(active_sims: int) -> float:
    return round(active_sims * MRC_RATE, 2)


def outbound_sms_charge(outbound_sms_count: int) -> float:
    return round(outbound_sms_count * SMS_OUTBOUND_RATE, 2)


def get_minimum_spend(month_number: int) -> float:
    """
    Tiered minimum-spend lookup.

    NOTE: the contract's own schedule overlaps at month 12 (it appears in
    both "Months 7-12" and "Months 12-24"). This function resolves that by
    matching tiers in the order they're listed in billing_config.json,
    returning the FIRST match -- so month 12 resolves to the $600 tier.
    This is a documented assumption (see SECTION_C.md, ambiguity #1),
    not a silent guess.
    """
    for tier in MIN_SPEND_SCHEDULE:
        start = tier["start_month"]
        end = tier["end_month"] if tier["end_month"] is not None else float("inf")
        if start <= month_number <= end:
            return tier["amount_usd_per_month"]
    raise ValueError(f"No minimum spend tier configured for month {month_number}")


def qualifying_fees(active_sims: int, total_pooled_usage_mb: float, outbound_sms_count: int = 0):
    """
    Fees that count toward the minimum-spend comparison: MRC + data overage + SMS.
    Per the contract, SIM hardware, late fees, and setup/implementation charges
    are explicitly excluded from "Actual Spend" -- so they're not included here.
    """
    mrc = mrc_charge(active_sims)
    overage = data_overage_charge(total_pooled_usage_mb, active_sims)
    sms = outbound_sms_charge(outbound_sms_count)
    breakdown = {"mrc": mrc, "data_overage": overage, "outbound_sms": sms}
    return round(mrc + overage + sms, 2), breakdown


def compute_monthly_charge(month_number: int, active_sims: int,
                            total_pooled_usage_mb: float, outbound_sms_count: int = 0) -> dict:
    fees, breakdown = qualifying_fees(active_sims, total_pooled_usage_mb, outbound_sms_count)
    minimum = get_minimum_spend(month_number)
    final_charge = max(minimum, fees)

    return {
        "month": month_number,
        "active_sims": active_sims,
        "pool_included_mb": pool_included_mb(active_sims),
        "total_pooled_usage_mb": total_pooled_usage_mb,
        "charge_breakdown": breakdown,
        "qualifying_fees_total": fees,
        "minimum_spend_for_month": minimum,
        "final_charge": final_charge,
        "minimum_spend_applied": final_charge == minimum and fees < minimum,
    }


def is_sim_active(days_in_test_mode: int, data_used_kb: float, outbound_sms_sent: int) -> bool:
    """
    Section B.3 -- Test Mode -> Active transition.

    A SIM converts to ACTIVE the moment ANY ONE of these is true (first one wins,
    they are not cumulative requirements):
      - 90 days have elapsed in Test Mode, OR
      - the SIM has consumed 100KB of data, OR
      - the SIM has sent 10 outbound SMS messages
    Once ACTIVE, the SIM starts incurring MRC and data usage (pool + overage) charges.
    """
    tm = CONFIG["test_mode"]
    return (
        data_used_kb >= tm["data_threshold_kb"]
        or outbound_sms_sent >= tm["outbound_sms_threshold"]
        or days_in_test_mode >= tm["duration_days"]
    )


if __name__ == "__main__":
    print("=== Worked Example: Month 8, 150 active SIMs, 2,400 MB pooled usage ===\n")
    result = compute_monthly_charge(
        month_number=8,
        active_sims=150,
        total_pooled_usage_mb=2400,
        outbound_sms_count=0,  # not given in the prompt; assumed 0 -- documented in README
    )
    print(json.dumps(result, indent=2))

    print("\n--- Step-by-step ---")
    print(f"1. Pool included = 150 SIMs x 10MB = {result['pool_included_mb']} MB")
    print(f"2. Overage = max(0, 2400 - {result['pool_included_mb']}) x $0.75 "
          f"= {result['charge_breakdown']['data_overage']}")
    print(f"3. MRC = 150 x $2.43 = {result['charge_breakdown']['mrc']}")
    print(f"4. Qualifying fees = MRC + overage + SMS = {result['qualifying_fees_total']}")
    print(f"5. Month 8 falls in the 'Months 7-12' tier -> minimum = "
          f"${result['minimum_spend_for_month']}")
    print(f"6. Final charge = max(minimum, qualifying fees) = ${result['final_charge']}")
