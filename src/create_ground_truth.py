import json


# ---------------- Load Transactions ----------------

with open(
    "data/transactions.json",
    "r"
) as file:

    transactions = json.load(file)


# ---------------- Create Ground Truth ----------------

ground_truth = []

for transaction in transactions:

    transaction_id = transaction["transaction_id"]

    number = int(
        transaction_id.replace("TXN", "")
    )

    if 1 <= number <= 10:

        case_type = "pricing_mismatch"

    elif 11 <= number <= 20:

        case_type = "settlement_mismatch"

    elif 21 <= number <= 30:

        case_type = "refund_adjustment"

    elif 31 <= number <= 40:

        case_type = "ambiguous_location"

    else:

        case_type = "normal"

    ground_truth.append({

        "transaction_id":
            transaction_id,

        "case_type":
            case_type
    })


# ---------------- Save Ground Truth ----------------

with open(
    "data/ground_truth.json",
    "w"
) as file:

    json.dump(
        ground_truth,
        file,
        indent=4
    )


print(
    f"Created ground truth for "
    f"{len(ground_truth)} transactions."
)