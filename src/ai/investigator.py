import json
import os
import sys
import time

from dotenv import load_dotenv
from openai import OpenAI


# ---------------- Add src Directory ----------------

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


from reconciliation import (
    run_reconciliation,
    load_transactions,
    load_pricing_policy
)


# ---------------- Load Environment Variables ----------------

load_dotenv()


# ---------------- Groq Client ----------------

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# ---------------- Retrieve Relevant Pricing Policy ----------------

def retrieve_relevant_policy(
    transaction,
    pricing_policy
):

    plan = transaction["plan"]

    billing_country = transaction["billing_country"]

    plan_policy = pricing_policy.get(
        "plans",
        {}
    ).get(
        plan,
        {}
    )

    expected_price = plan_policy.get(
        billing_country
    )

    return {
        "plan": plan,
        "billing_country": billing_country,
        "expected_price": expected_price,
        "currency": pricing_policy.get(
            "currency",
            "INR"
        )
    }


# ---------------- Build Investigation Prompt ----------------

def build_investigation_prompt(
    transaction,
    reconciliation_result,
    pricing_policy
):

    relevant_policy = retrieve_relevant_policy(
        transaction,
        pricing_policy
    )

    evidence = {
        "transaction": transaction,
        "reconciliation_result": reconciliation_result,
        "relevant_policy": relevant_policy
    }

    prompt = f"""
You are an AI Finance Controller investigating
a financial transaction exception.

Analyze the transaction using ONLY the evidence provided.

Your responsibilities:

1. Identify the type of financial exception.

2. Explain why the transaction was flagged.

3. Determine whether the discrepancy appears legitimate
   or requires further review.

4. Identify the financial impact.

5. Consider regional signals carefully.

6. Do NOT automatically classify regional differences as fraud.

7. Provide a confidence score between 0 and 1.

8. State what additional evidence would be useful
   if the case cannot be resolved.

Return ONLY valid JSON in this structure:

{{
    "classification": "MATCH | PRICING_MISMATCH | PAYMENT_MISMATCH | SETTLEMENT_MISMATCH | REFUND_ADJUSTMENT | REGIONAL_REVIEW | UNRESOLVED",
    "explanation": "Clear explanation of the finding",
    "financial_impact": 0,
    "confidence": 0.0,
    "evidence": [],
    "recommendation": "Recommended next action"
}}

IMPORTANT:

- Do not use hidden labels or ground-truth information.
- Reason only from the financial evidence provided.
- Do not invent missing information.
- If the evidence is insufficient, classify the case as
  UNRESOLVED and explain what evidence is missing.

FINANCIAL EVIDENCE:

{json.dumps(evidence, indent=4)}
"""

    return prompt


# ---------------- Investigate One Exception ----------------

def investigate_exception(
    transaction,
    reconciliation_result,
    pricing_policy
):

    prompt = build_investigation_prompt(
        transaction,
        reconciliation_result,
        pricing_policy
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a financial reconciliation "
                    "and revenue integrity investigator."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    response_text = (
        response.choices[0].message.content
    )

    return json.loads(response_text)


# ---------------- Investigate All Exceptions ----------------

def investigate_all_exceptions():

    transactions = load_transactions()

    pricing_policy = load_pricing_policy()

    results, reconciliation_time = run_reconciliation()

    investigations = []

    start_time = time.perf_counter()

    # Only investigate one exception at a time
    # to avoid hitting Groq rate limits.

    for index, reconciliation_result in enumerate(
        results[:1]
    ):

        if reconciliation_result["status"] == "MATCH":
            continue

        transaction = transactions[index]

        print(
            f"Investigating "
            f"{transaction['transaction_id']}..."
        )

        try:

            ai_result = investigate_exception(
                transaction,
                reconciliation_result,
                pricing_policy
            )

            investigations.append({
                "transaction_id":
                    transaction["transaction_id"],

                "initial_status":
                    reconciliation_result["status"],

                "initial_reason":
                    reconciliation_result["reason"],

                "ai_investigation":
                    ai_result
            })

        except Exception as error:

            print(
                f"ERROR for "
                f"{transaction['transaction_id']}: "
                f"{error}"
            )

            investigations.append({
                "transaction_id":
                    transaction["transaction_id"],

                "initial_status":
                    reconciliation_result["status"],

                "initial_reason":
                    reconciliation_result["reason"],

                "ai_investigation": {
                    "classification":
                        "UNRESOLVED",

                    "explanation":
                        "AI investigation failed.",

                    "financial_impact":
                        0,

                    "confidence":
                        0,

                    "evidence":
                        [],

                    "recommendation":
                        "Retry investigation manually.",

                    "error":
                        str(error)
                }
            })

    ai_processing_time = (
        time.perf_counter() - start_time
    )

    return (
        investigations,
        reconciliation_time,
        ai_processing_time
    )


# ---------------- Save Investigation Results ----------------

def save_investigations(
    investigations
):

    os.makedirs(
        "reports",
        exist_ok=True
    )

    with open(
        "reports/ai_investigations.json",
        "w"
    ) as file:

        json.dump(
            investigations,
            file,
            indent=4
        )

    print(
        "\nAI investigation results saved to "
        "reports/ai_investigations.json"
    )


# ---------------- Save Single Investigation ----------------

def save_single_investigation(
    transaction,
    reconciliation_result,
    ai_result
):

    os.makedirs(
        "reports",
        exist_ok=True
    )

    file_path = (
        "reports/ai_investigations.json"
    )

    investigations = []

    if os.path.exists(file_path):

        try:

            with open(
                file_path,
                "r"
            ) as file:

                investigations = json.load(file)

        except (
            json.JSONDecodeError,
            OSError
        ):

            investigations = []

    investigation_record = {

        "transaction_id":
            transaction["transaction_id"],

        "initial_status":
            reconciliation_result["status"],

        "initial_reason":
            reconciliation_result["reason"],

        "ai_investigation":
            ai_result
    }

    transaction_id = (
        transaction["transaction_id"]
    )

    updated = False

    for index, existing in enumerate(
        investigations
    ):

        if (
            existing.get("transaction_id")
            == transaction_id
        ):

            investigations[index] = (
                investigation_record
            )

            updated = True

            break

    if not updated:

        investigations.append(
            investigation_record
        )

    with open(
        file_path,
        "w"
    ) as file:

        json.dump(
            investigations,
            file,
            indent=4
        )

    return investigation_record


# ---------------- Main ----------------

if __name__ == "__main__":

    print(
        "\n=========================================="
    )

    print(
        "      AI FINANCE CONTROLLER"
    )

    print(
        "==========================================\n"
    )

    (
        investigations,
        reconciliation_time,
        ai_time
    ) = investigate_all_exceptions()

    save_investigations(
        investigations
    )

    print(
        "\n=========================================="
    )

    print(
        "        INVESTIGATION SUMMARY"
    )

    print(
        "==========================================\n"
    )

    print(
        f"Exceptions investigated : "
        f"{len(investigations)}"
    )

    print(
        f"Reconciliation time     : "
        f"{reconciliation_time:.4f} seconds"
    )

    print(
        f"AI investigation time   : "
        f"{ai_time:.4f} seconds"
    )

    print(
        "\n------------------------------------------"
    )

    for investigation in investigations:

        ai_result = (
            investigation["ai_investigation"]
        )

        print(
            f"\nTransaction : "
            f"{investigation['transaction_id']}"
        )

        print(
            f"Initial     : "
            f"{investigation['initial_status']}"
        )

        print(
            f"AI Result   : "
            f"{ai_result['classification']}"
        )

        print(
            f"Confidence  : "
            f"{ai_result['confidence']}"
        )

        print(
            f"Explanation : "
            f"{ai_result['explanation']}"
        )

        print(
            f"Recommendation : "
            f"{ai_result['recommendation']}"
        )