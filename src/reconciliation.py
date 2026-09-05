import json
import time


# ---------------- Load Data ----------------

def load_transactions():
    with open("data/transactions.json", "r") as file:
        return json.load(file)


def load_pricing_policy():
    with open("policies/pricing_policy.json", "r") as file:
        return json.load(file)


# ---------------- Calculate Expected Price ----------------

def calculate_expected_price(transaction, pricing_policy):

    plan = transaction["plan"]
    country = transaction["billing_country"]

    try:
        return pricing_policy["plans"][plan][country]

    except KeyError:
        return None


# ---------------- Reconcile Transaction ----------------

def reconcile_transaction(transaction, pricing_policy):

    expected_price = calculate_expected_price(
        transaction,
        pricing_policy
    )

    order_amount = transaction["order_amount"]
    payment_amount = transaction["payment_amount"]

    fee_amount = transaction["fee_amount"]
    refund_amount = transaction["refund_amount"]

    actual_settlement = transaction["settlement_amount"]

    billing_country = transaction["billing_country"]
    card_country = transaction["card_country"]
    ip_country = transaction["ip_country"]

    # ---------------- Pricing Check ----------------

    if expected_price is None:

        return {
            "transaction_id": transaction["transaction_id"],
            "status": "UNRESOLVED",
            "reason": "Pricing policy unavailable"
        }

    pricing_difference = (
        payment_amount - expected_price
    )

    # ---------------- Order vs Payment ----------------

    payment_difference = (
        payment_amount - order_amount
    )

    # ---------------- Expected Settlement ----------------
    #
    # Finance system calculates what SHOULD have
    # been settled based on the payment, fee and refund.

    expected_settlement = (
        payment_amount
        - fee_amount
        - refund_amount
    )

    # ---------------- Actual Settlement ----------------

    settlement_difference = (
        actual_settlement
        - expected_settlement
    )

    # ---------------- Regional Signals ----------------

    location_conflict = (
        billing_country != card_country
        or billing_country != ip_country
        or card_country != ip_country
    )

    # ---------------- Determine Status ----------------

    if abs(pricing_difference) > 0:

        status = "PRICING_MISMATCH"

        reason = (
            "Payment amount does not match "
            "the applicable pricing policy"
        )

    elif abs(payment_difference) > 0:

        status = "PAYMENT_MISMATCH"

        reason = (
            "Payment amount does not match "
            "the order amount"
        )

    elif abs(settlement_difference) > 0:

        status = "SETTLEMENT_MISMATCH"

        reason = (
            "Actual settlement does not match "
            "the calculated expected settlement"
        )

    elif refund_amount > 0:

        status = "REFUND_ADJUSTMENT"

        reason = (
            "Transaction contains a refund "
            "that affects settlement"
        )

    elif location_conflict:

        status = "REGIONAL_REVIEW"

        reason = (
            "Billing, card and IP country "
            "signals conflict"
        )

    else:

        status = "MATCH"

        reason = (
            "Transaction reconciled successfully"
        )

    return {

        "transaction_id":
            transaction["transaction_id"],

        "status":
            status,

        "reason":
            reason,

        "order_amount":
            order_amount,

        "expected_price":
            expected_price,

        "payment_amount":
            payment_amount,

        "fee_amount":
            fee_amount,

        "refund_amount":
            refund_amount,

        "expected_settlement":
            round(
                expected_settlement,
                2
            ),

        "actual_settlement":
            actual_settlement,

        "pricing_difference":
            round(
                pricing_difference,
                2
            ),

        "payment_difference":
            round(
                payment_difference,
                2
            ),

        "settlement_difference":
            round(
                settlement_difference,
                2
            ),

        "billing_country":
            billing_country,

        "card_country":
            card_country,

        "ip_country":
            ip_country
    }


# ---------------- Run Reconciliation ----------------

def run_reconciliation():

    transactions = load_transactions()

    pricing_policy = load_pricing_policy()

    start_time = time.perf_counter()

    results = []

    for transaction in transactions:

        result = reconcile_transaction(
            transaction,
            pricing_policy
        )

        results.append(result)

    end_time = time.perf_counter()

    processing_time = (
        end_time - start_time
    )

    return results, processing_time


# ---------------- Calculate Metrics ----------------

def calculate_metrics(
    results,
    processing_time
):

    total = len(results)

    matched = sum(
        1
        for result in results
        if result["status"] == "MATCH"
    )

    pricing_mismatch = sum(
        1
        for result in results
        if result["status"] == "PRICING_MISMATCH"
    )

    payment_mismatch = sum(
        1
        for result in results
        if result["status"] == "PAYMENT_MISMATCH"
    )

    settlement_mismatch = sum(
        1
        for result in results
        if result["status"] == "SETTLEMENT_MISMATCH"
    )

    refund_adjustment = sum(
        1
        for result in results
        if result["status"] == "REFUND_ADJUSTMENT"
    )

    regional_review = sum(
        1
        for result in results
        if result["status"] == "REGIONAL_REVIEW"
    )

    unresolved = sum(
        1
        for result in results
        if result["status"] == "UNRESOLVED"
    )

    match_rate = (
        matched / total * 100
        if total > 0
        else 0
    )

    total_pricing_variance = sum(
        abs(result["pricing_difference"])
        for result in results
        if "pricing_difference" in result
    )

    total_settlement_variance = sum(
        abs(result["settlement_difference"])
        for result in results
        if "settlement_difference" in result
    )

    return {

        "total_transactions":
            total,

        "matched":
            matched,

        "pricing_mismatch":
            pricing_mismatch,

        "payment_mismatch":
            payment_mismatch,

        "settlement_mismatch":
            settlement_mismatch,

        "refund_adjustment":
            refund_adjustment,

        "regional_review":
            regional_review,

        "unresolved":
            unresolved,

        "match_rate":
            round(
                match_rate,
                2
            ),

        "total_pricing_variance":
            round(
                total_pricing_variance,
                2
            ),

        "total_settlement_variance":
            round(
                total_settlement_variance,
                2
            ),

        "processing_time_seconds":
            round(
                processing_time,
                4
            )
    }


# ---------------- Main ----------------

if __name__ == "__main__":

    results, processing_time = (
        run_reconciliation()
    )

    metrics = calculate_metrics(
        results,
        processing_time
    )

    print(
        "\n========== "
        "AI FINANCE CONTROLLER "
        "==========\n"
    )

    print(
        f"Total transactions : "
        f"{metrics['total_transactions']}"
    )

    print(
        f"Matched             : "
        f"{metrics['matched']}"
    )

    print(
        f"Pricing mismatch    : "
        f"{metrics['pricing_mismatch']}"
    )

    print(
        f"Payment mismatch    : "
        f"{metrics['payment_mismatch']}"
    )

    print(
        f"Settlement mismatch : "
        f"{metrics['settlement_mismatch']}"
    )

    print(
        f"Refund adjustment   : "
        f"{metrics['refund_adjustment']}"
    )

    print(
        f"Regional review     : "
        f"{metrics['regional_review']}"
    )

    print(
        f"Unresolved          : "
        f"{metrics['unresolved']}"
    )

    print(
        f"Match rate          : "
        f"{metrics['match_rate']}%"
    )

    print(
        f"Pricing variance    : "
        f"₹{metrics['total_pricing_variance']}"
    )

    print(
        f"Settlement variance : "
        f"₹{metrics['total_settlement_variance']}"
    )

    print(
        f"Processing time     : "
        f"{metrics['processing_time_seconds']} seconds"
    )

    print("\n========== EXCEPTIONS ==========\n")

    for result in results:

        if result["status"] != "MATCH":

            print(
                f"{result['transaction_id']} | "
                f"{result['status']} | "
                f"{result['reason']}"
            )