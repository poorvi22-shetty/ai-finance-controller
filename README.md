AI Revenue Integrity & Reconciliation Controller

An AI-powered finance controller that detects financial discrepancies across payments, pricing, refunds, fees and settlements, and uses an LLM to investigate exceptions.

Built for the Razorpay AI Buildathon 2026 — AI Finance Controller Track.

Problem Statement

Fintech businesses process large volumes of payments, refunds, fees and settlements across different systems. Manually checking these records can be time-consuming and can result in missed discrepancies.

Regional pricing also adds complexity because billing country, card country and IP-based location may not always match.

This project automates the reconciliation process and uses AI to investigate exceptions that require further analysis.

Objectives

• Automatically reconcile financial transactions

• Detect payment and pricing mismatches

• Detect settlement discrepancies

• Identify refund and adjustment differences

• Use billing country, card country and IP country as regional signals

• Retrieve the pricing policy relevant to a transaction

• Use an LLM to investigate exceptions

• Generate explanations, confidence scores and recommendations

• Calculate the financial impact of discrepancies

• Store investigation results for audit and review

System Workflow

Transaction Data
      ↓
Deterministic Reconciliation
      ↓
Exception Detection
      ↓
Relevant Policy Retrieval
      ↓
Financial Evidence Collection
      ↓
Groq LLM Investigation
      ↓
Classification + Explanation
      ↓
Recommendation + Audit Result

Reconciliation Engine

The reconciliation engine performs deterministic checks before any AI investigation.

Checks include:

• Payment amount vs expected price

• Pricing policy differences

• Payment status

• Fees

• Refunds

• Expected settlement vs actual settlement

• Settlement differences

• Billing country vs card country

• Billing country vs IP country

The core financial calculations are handled by deterministic rules rather than the LLM.

AI Investigation

Exceptions detected by the reconciliation engine can be investigated using Groq.

The AI receives:

• Transaction data

• Reconciliation result

• Relevant pricing policy

The AI generates:

• Exception classification

• Explanation

• Confidence score

• Financial impact

• Supporting evidence

• Recommendation

The LLM is used for investigation and explanation. It does not replace the deterministic financial calculations.

Policy Retrieval

The system contains regional pricing policies for different plans and countries.

Example:

Starter Plan

• India: ₹1,000

• Singapore: ₹1,800

• Germany: ₹2,200

• United Kingdom: ₹2,100

• United States: ₹2,500

The relevant policy is retrieved based on the transaction's plan and billing country and provided to the AI as part of the investigation evidence.

Example 1 — Pricing Mismatch

Transaction: TXN0001

• Plan: Starter

• Billing Country: GB

• Expected Price: ₹2,100

• Payment Received: ₹1,470

• Difference: ₹630

The reconciliation engine detects the pricing mismatch.

The AI investigates the transaction using the pricing policy and transaction evidence. It identifies the ₹630 shortfall and recommends checking for an approved discount, promotional code or manual adjustment before taking corrective action.

Example 2 — Settlement Mismatch

Transaction: TXN0011

• Expected Settlement: ₹15,680

• Actual Settlement: ₹15,380

• Difference: ₹300

• Adjustment Amount: ₹300

The AI identifies that the ₹300 adjustment exactly explains the settlement difference.

Instead of automatically treating the transaction as fraud, it recommends confirming that the adjustment was authorized and correctly applied.

Dataset

The project uses synthetic financial transaction data.

100 transactions were generated for testing:

• Normal: 60

• Pricing Mismatch: 10

• Settlement Mismatch: 10

• Refund Adjustment: 10

• Ambiguous Location: 10

Total: 100

No real Razorpay customer data is used.

Evaluation

The deterministic reconciliation engine was evaluated against a separate synthetic ground-truth dataset.

• Total Records: 100

• Correct Predictions: 100

• Incorrect Predictions: 0

• Accuracy: 100%

Class-level evaluation:

• Normal — Precision: 100%, Recall: 100%

• Pricing Mismatch — Precision: 100%, Recall: 100%

• Settlement Mismatch — Precision: 100%, Recall: 100%

• Refund Adjustment — Precision: 100%, Recall: 100%

• Ambiguous Location — Precision: 100%, Recall: 100%

Important:

The 100% accuracy reported here is for the deterministic reconciliation engine against synthetic ground truth. It is not an evaluation of the LLM.

Technology Stack

Backend

• Python

• FastAPI

• OpenAI Python SDK

AI

• Groq API

• openai/gpt-oss-120b

Frontend

• React

• Vite

• JavaScript

• CSS

Data

• JSON

• Synthetic transaction dataset

• Synthetic ground-truth dataset

• Pricing policy data

Project Structure

ai-finance-controller/

• data/
  • transactions.json
  • ground_truth.json

• policies/
  • pricing_policy.json

• reports/
  • ai_investigations.json
  • evaluation_report.json

• src/
  • ai/
    • __init__.py
    • investigator.py
  • create_ground_truth.py
  • evaluation.py
  • generate_data.py
  • main.py
  • reconciliation.py

• frontend/
  • src/
    • App.jsx
    • App.css
    • main.jsx
  • package.json
  • vite.config.js

• .gitignore

• README.md

Running the Project

Backend

Create a virtual environment:

python -m venv venv

Activate it:

Windows:

.\venv\Scripts\activate

Install dependencies:

pip install fastapi uvicorn openai python-dotenv

Create a .env file:

GROQ_API_KEY=your_api_key

Start the backend:

uvicorn src.main:app --reload

Backend runs at:

http://127.0.0.1:8000

Frontend

Open another terminal:

cd frontend

Install dependencies:

npm install

Start the frontend:

npm run dev

Frontend runs at:

http://localhost:5173

API Endpoints

• GET /transactions — Returns transaction data

• GET /metrics — Returns reconciliation metrics

• GET /exceptions — Returns detected exceptions

• GET /policies — Returns pricing policies

• GET /reports — Returns evaluation results

• POST /investigate/{transaction_id} — Investigates an exception using the AI pipeline

Important Design Decisions

• Financial calculations are deterministic.

• The LLM is used for investigation and explanation.

• Policy information is retrieved and provided as evidence to the AI.

• Regional differences are treated as review signals and are not automatically classified as fraud.

• AI-generated financial impact is supported by deterministic reconciliation results.

• Investigation results are persisted for audit and review.

Limitations

• The current dataset is synthetic.

• The project is a prototype and is not connected to real payment or settlement systems.

• AI investigation is currently performed for individual exceptions.

• Production use would require authentication, database persistence and additional monitoring.

• More extensive LLM evaluation would be required before production use.

Buildathon

Built for the Razorpay AI Buildathon 2026.

Track: AI Finance Controller

The project focuses on closing a finance-operations reconciliation loop across a batch of financial transactions, automatically resolving matches and surfacing exceptions that require investigation.
