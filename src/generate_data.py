import json
import random
from datetime import datetime, timedelta


# ---------------- Configuration ----------------

NUM_TRANSACTIONS = 100

COUNTRIES = ["IN", "US", "DE", "GB", "SG"]

PLANS = ["starter", "pro", "enterprise"]

PRICING = {
    "starter": {
        "IN": 1000,
        "US": 2500,
        "DE": 2200,
        "GB": 2100,
        "SG": 1800
    },
    "pro": {
        "IN": 2500,
        "US": 6000,
        "DE": 5500,
        "GB": 5200,
        "SG": 4500
    },
    "enterprise": {
        "IN": 8000,
        "US": 18000,
        "DE": 16500,
        "GB": 16000,
        "SG": 14000
    }
}


# ---------------- Generate Transaction ----------------

def generate_transaction(index):

    customer_country = random.choice(COUNTRIES)
    plan = random.choice(PLANS)

    expected_price = PRICING[plan][customer_country]

    order_amount = expected_price
    payment_amount = expected_price

    fee_amount = round(
        payment_amount * 0.02,
        2
    )

    refund_amount = 0
    adjustment_amount = 0

    payment_status = "success"
    settlement_status = "settled"

    billing_country = customer_country
    card_country = customer_country
    ip_country = customer_country

    case_type = "normal"


    # ==================================================
    # CASE 1: PRICING MISMATCH
    # ==================================================

    if 1 <= index <= 10:

        payment_amount = round(
            expected_price * 0.70,
            2
        )

        fee_amount = round(
            payment_amount * 0.02,
            2
        )

        case_type = "pricing_mismatch"


    # ==================================================
    # CASE 2: SETTLEMENT MISMATCH
    # ==================================================

    elif 11 <= index <= 20:

        case_type = "settlement_mismatch"

        payment_amount = expected_price

        fee_amount = round(
            payment_amount * 0.02,
            2
        )

        adjustment_amount = 300


    # ==================================================
    # CASE 3: REFUND ADJUSTMENT
    # ==================================================

    elif 21 <= index <= 30:

        case_type = "refund_adjustment"

        payment_amount = expected_price

        fee_amount = round(
            payment_amount * 0.02,
            2
        )

        refund_amount = round(
            payment_amount * 0.20,
            2
        )


    # ==================================================
    # CASE 4: AMBIGUOUS REGIONAL SIGNALS
    # ==================================================

    elif 31 <= index <= 40:

        case_type = "ambiguous_location"

        payment_amount = expected_price

        fee_amount = round(
            payment_amount * 0.02,
            2
        )

        card_country = random.choice(
            [
                country
                for country in COUNTRIES
                if country != customer_country
            ]
        )

        ip_country = random.choice(
            [
                country
                for country in COUNTRIES
                if country != customer_country
            ]
        )


    # ==================================================
    # CASE 5: NORMAL TRANSACTION
    # ==================================================

    else:

        case_type = "normal"


    # ==================================================
    # EXPECTED SETTLEMENT
    # ==================================================

    expected_settlement = (
        payment_amount
        - fee_amount
        - refund_amount
    )


    # ==================================================
    # ACTUAL SETTLEMENT
    # ==================================================

    actual_settlement = expected_settlement

    if case_type == "settlement_mismatch":

        actual_settlement = (
            expected_settlement - 300
        )


    # ==================================================
    # CREATE TRANSACTION
    # ==================================================

    return {

        "transaction_id":
            f"TXN{index:04d}",

        "customer_id":
            f"CUS{random.randint(1000, 9999)}",

        "product":
            "SaaS Platform",

        "plan":
            plan,

        "order_amount":
            order_amount,

        "payment_amount":
            payment_amount,

        "payment_status":
            payment_status,

        "fee_amount":
            fee_amount,

        "refund_amount":
            refund_amount,

        "adjustment_amount":
            adjustment_amount,

        "expected_settlement":
            round(
                expected_settlement,
                2
            ),

        "settlement_amount":
            round(
                actual_settlement,
                2
            ),

        "settlement_status":
            settlement_status,

        "currency":
            "INR",

        "billing_country":
            billing_country,

        "card_country":
            card_country,

        "ip_country":
            ip_country,

        "timestamp":
            (
                datetime.now()
                - timedelta(
                    days=random.randint(0, 30)
                )
            ).isoformat()
    }


# ---------------- Generate Dataset ----------------

def generate_dataset():

    transactions = []

    for index in range(
        1,
        NUM_TRANSACTIONS + 1
    ):

        transaction = generate_transaction(
            index
        )

        transactions.append(
            transaction
        )

    return transactions


# ---------------- Save Dataset ----------------

if __name__ == "__main__":

    transactions = generate_dataset()

    with open(
        "data/transactions.json",
        "w"
    ) as file:

        json.dump(
            transactions,
            file,
            indent=4
        )

    print(
        f"Generated {len(transactions)} "
        "synthetic transactions successfully."
    )