from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import json
import os
import sys


# ---------------- Add src Directory ----------------

sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


from reconciliation import (
    run_reconciliation
)

from ai.investigator import (
    investigate_exception,
    save_single_investigation,
    retrieve_relevant_policy
)


# ---------------- Create FastAPI App ----------------

app = FastAPI(
    title="AI Revenue Integrity & Reconciliation Controller",
    description=(
        "AI-powered financial reconciliation and "
        "exception investigation system."
    ),
    version="1.0.0"
)


# ---------------- Enable CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Helper Functions ----------------

def load_transactions():

    with open(
        "data/transactions.json",
        "r"
    ) as file:

        return json.load(file)


def load_pricing_policy():

    with open(
        "policies/pricing_policy.json",
        "r"
    ) as file:

        return json.load(file)


def load_ai_investigations():

    file_path = (
        "reports/ai_investigations.json"
    )

    if not os.path.exists(file_path):

        return []

    with open(
        file_path,
        "r"
    ) as file:

        return json.load(file)


def load_evaluation_report():

    file_path = (
        "reports/evaluation_report.json"
    )

    if not os.path.exists(file_path):

        return {
            "available": False,
            "message":
                "Evaluation report has not been generated yet."
        }

    with open(
        file_path,
        "r"
    ) as file:

        report = json.load(file)

    report["available"] = True

    return report


# ---------------- Root Endpoint ----------------

@app.get("/")
def root():

    return {
        "message":
            "AI Finance Controller API is running",

        "status":
            "healthy"
    }


# ---------------- Transactions Endpoint ----------------

@app.get("/transactions")
def get_transactions():

    transactions = load_transactions()

    return {
        "total":
            len(transactions),

        "transactions":
            transactions
    }


# ---------------- Policies Endpoint ----------------

@app.get("/policies")
def get_policies():

    policy = load_pricing_policy()

    return {
        "policy_name":
            "Regional Pricing Policy",

        "currency":
            policy.get(
                "currency",
                "INR"
            ),

        "plans":
            policy.get(
                "plans",
                {}
            )
    }


# ---------------- AI Investigations Endpoint ----------------

@app.get("/investigations")
def get_investigations():

    investigations = load_ai_investigations()

    return {
        "total":
            len(investigations),

        "investigations":
            investigations
    }


# ---------------- Metrics Endpoint ----------------

@app.get("/metrics")
def get_metrics():

    results, processing_time = (
        run_reconciliation()
    )

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

    match_rate = (
        (matched / total) * 100
        if total > 0
        else 0
    )

    return {
        "total_transactions":
            total,

        "matched_transactions":
            matched,

        "exceptions":
            total - matched,

        "match_rate":
            round(
                match_rate,
                2
            ),

        "pricing_mismatches":
            pricing_mismatch,

        "payment_mismatches":
            payment_mismatch,

        "settlement_mismatches":
            settlement_mismatch,

        "refund_adjustments":
            refund_adjustment,

        "regional_reviews":
            regional_review,

        "processing_time_seconds":
            round(
                processing_time,
                6
            )
    }


# ---------------- Exceptions Endpoint ----------------

@app.get("/exceptions")
def get_exceptions():

    transactions = load_transactions()

    results, processing_time = (
        run_reconciliation()
    )

    exceptions = []

    for index, result in enumerate(results):

        if result["status"] == "MATCH":
            continue

        transaction = transactions[index]

        # Determine financial impact

        financial_impact = 0

        if result["status"] == "PRICING_MISMATCH":

            financial_impact = abs(
                result.get(
                    "pricing_difference",
                    0
                )
            )

        elif result["status"] == "SETTLEMENT_MISMATCH":

            financial_impact = abs(
                result.get(
                    "settlement_difference",
                    0
                )
            )

        elif result["status"] == "REFUND_ADJUSTMENT":

            financial_impact = abs(
                transaction.get(
                    "refund_amount",
                    0
                )
            )

        exceptions.append({

            "transaction_id":
                transaction["transaction_id"],

            "customer_id":
                transaction["customer_id"],

            "product":
                transaction["product"],

            "plan":
                transaction["plan"],

            "order_amount":
                transaction["order_amount"],

            "payment_amount":
                transaction["payment_amount"],

            "settlement_amount":
                transaction["settlement_amount"],

            "status":
                result["status"],

            "reason":
                result["reason"],

            "financial_impact":
                financial_impact
        })

    return {

        "total_exceptions":
            len(exceptions),

        "processing_time_seconds":
            round(
                processing_time,
                6
            ),

        "exceptions":
            exceptions
    }


# ---------------- Evaluation Report Endpoint ----------------

@app.get("/reports")
def get_reports():

    report = load_evaluation_report()

    return report


# ---------------- AI Investigation Endpoint ----------------

@app.post(
    "/investigate/{transaction_id}"
)
def investigate_transaction(
    transaction_id: str
):

    transactions = load_transactions()

    pricing_policy = load_pricing_policy()

    results, _ = (
        run_reconciliation()
    )


    # ==========================================================
    # AGENT INVESTIGATION TRACE
    # ==========================================================

    investigation_steps = []


    # ---------------- Step 1: Reconciliation ----------------

    investigation_steps.append({
        "step": 1,
        "name": "Deterministic Reconciliation",
        "status": "completed",
        "description":
            "Compared payment, pricing, refund, fee, "
            "settlement, and regional signals."
    })


    # ---------------- Find Transaction ----------------

    transaction_index = None

    for index, transaction in enumerate(
        transactions
    ):

        if (
            transaction["transaction_id"]
            == transaction_id
        ):

            transaction_index = index

            break


    if transaction_index is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )


    transaction = transactions[
        transaction_index
    ]

    reconciliation_result = results[
        transaction_index
    ]


    # ---------------- Only Investigate Exceptions ----------------

    if (
        reconciliation_result["status"]
        == "MATCH"
    ):

        return {

            "transaction_id":
                transaction_id,

            "message":
                "Transaction is already reconciled.",

            "classification":
                "MATCH",

            "confidence":
                1.0,

            "investigation_steps":
                investigation_steps
        }


    # ==========================================================
    # STEP 2: RETRIEVE RELEVANT POLICY
    # ==========================================================

    relevant_policy = retrieve_relevant_policy(
        transaction,
        pricing_policy
    )


    investigation_steps.append({

        "step": 2,

        "name":
            "Retrieve Relevant Policy",

        "status":
            "completed",

        "description":
            "Retrieved the regional pricing policy "
            "relevant to the transaction's plan and "
            "billing country."
    })


    # ==========================================================
    # STEP 3: GATHER EVIDENCE
    # ==========================================================

    investigation_steps.append({

        "step": 3,

        "name":
            "Gather Financial Evidence",

        "status":
            "completed",

        "description":
            "Collected transaction data, deterministic "
            "reconciliation results, and relevant policy "
            "evidence for investigation."
    })


    # ==========================================================
    # STEP 4: AI INVESTIGATION
    # ==========================================================

    ai_result = investigate_exception(

        transaction,

        reconciliation_result,

        pricing_policy
    )


    investigation_steps.append({

        "step": 4,

        "name":
            "AI Exception Investigation",

        "status":
            "completed",

        "description":
            "Groq AI analyzed the financial evidence "
            "and classified the exception with confidence, "
            "explanation, financial impact, and recommendation."
    })


    # ==========================================================
    # STEP 5: PERSIST AUDIT RESULT
    # ==========================================================

    save_single_investigation(

        transaction,

        reconciliation_result,

        ai_result
    )


    investigation_steps.append({

        "step": 5,

        "name":
            "Persist Audit Result",

        "status":
            "completed",

        "description":
            "Saved the investigation result for future "
            "audit and review."
    })


    # ==========================================================
    # FINAL RESPONSE
    # ==========================================================

    return {

        "transaction_id":
            transaction_id,

        "initial_status":
            reconciliation_result["status"],

        "initial_reason":
            reconciliation_result["reason"],

        "investigation_steps":
            investigation_steps,

        "ai_investigation":
            ai_result
    }