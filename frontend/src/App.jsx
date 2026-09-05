import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [metrics, setMetrics] = useState(null);
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedException, setSelectedException] = useState(null);
  const [investigation, setInvestigation] = useState(null);
  const [investigating, setInvestigating] = useState(false);
  const [report, setReport] = useState(null);
  const [policies, setPolicies] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    try {
      const [
        metricsResponse,
        exceptionsResponse,
        reportResponse,
        policiesResponse,
      ] = await Promise.all([
        fetch(`${API_URL}/metrics`),
        fetch(`${API_URL}/exceptions`),
        fetch(`${API_URL}/reports`),
        fetch(`${API_URL}/policies`),
      ]);

      const metricsData = await metricsResponse.json();
      const exceptionsData = await exceptionsResponse.json();
      const reportData = await reportResponse.json();
      const policiesData = await policiesResponse.json();

      setMetrics(metricsData);
      setExceptions(exceptionsData.exceptions || []);
      setReport(reportData);
      setPolicies(policiesData);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setLoading(false);
    }
  }

  async function investigate(transactionId) {
    setInvestigating(true);
    setInvestigation(null);

    try {
      const response = await fetch(
        `${API_URL}/investigate/${transactionId}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();
      setInvestigation(data);
    } catch (error) {
      console.error("AI investigation failed:", error);
    } finally {
      setInvestigating(false);
    }
  }

  function formatCurrency(value) {
    if (value === undefined || value === null) {
      return "₹0";
    }

    return `₹${Number(value).toLocaleString("en-IN")}`;
  }

  function statusLabel(status) {
    return status
      .replaceAll("_", " ")
      .toLowerCase()
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  function getStatusClass(status) {
    if (status === "PRICING_MISMATCH") return "status pricing";
    if (status === "SETTLEMENT_MISMATCH") return "status settlement";
    if (status === "REFUND_ADJUSTMENT") return "status refund";
    if (status === "REGIONAL_REVIEW") return "status regional";

    return "status";
  }

  const navigation = [
    {
      name: "Overview",
      icon: "▦",
    },
    {
      name: "Transactions",
      icon: "▤",
    },
    {
      name: "Exceptions",
      icon: "⚠",
    },
    {
      name: "AI Investigation",
      icon: "✦",
    },
    {
      name: "Reports",
      icon: "◫",
    },
    {
      name: "Policies",
      icon: "◈",
    },
  ];

  return (
    <div className="app">
      <style>{`
        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
          font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI",
            sans-serif;
          background: #f5f7fb;
          color: #172033;
        }

        button {
          font-family: inherit;
        }

        .app {
          min-height: 100vh;
          display: flex;
          background: #f5f7fb;
        }

        .sidebar {
          width: 250px;
          min-height: 100vh;
          background: #111827;
          color: white;
          padding: 24px 16px;
          position: fixed;
          left: 0;
          top: 0;
          bottom: 0;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 4px 12px 30px;
        }

        .brand-icon {
          width: 38px;
          height: 38px;
          border-radius: 10px;
          background: linear-gradient(135deg, #6d5dfc, #8b5cf6);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          font-weight: 700;
        }

        .brand-title {
          font-size: 15px;
          font-weight: 700;
          line-height: 1.2;
        }

        .brand-subtitle {
          color: #9ca3af;
          font-size: 11px;
          margin-top: 3px;
        }

        .nav-title {
          color: #6b7280;
          font-size: 10px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 1px;
          padding: 0 12px 10px;
        }

        .nav-item {
          width: 100%;
          border: none;
          background: transparent;
          color: #9ca3af;
          padding: 11px 12px;
          border-radius: 9px;
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 13px;
          text-align: left;
          cursor: pointer;
          margin-bottom: 4px;
        }

        .nav-item:hover {
          background: #1f2937;
          color: white;
        }

        .nav-item.active {
          background: #252044;
          color: white;
        }

        .nav-icon {
          width: 22px;
          text-align: center;
          font-size: 15px;
        }

        .main {
          margin-left: 250px;
          width: calc(100% - 250px);
          min-height: 100vh;
        }

        .topbar {
          height: 72px;
          background: white;
          border-bottom: 1px solid #e5e7eb;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 34px;
        }

        .page-title {
          font-size: 20px;
          font-weight: 700;
          color: #111827;
        }

        .page-description {
          color: #6b7280;
          font-size: 12px;
          margin-top: 3px;
        }

        .system-status {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          color: #4b5563;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #22c55e;
        }

        .content {
          padding: 30px 34px;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 18px;
          margin-bottom: 24px;
        }

        .metric-card {
          background: white;
          border: 1px solid #e6e9ef;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(17, 24, 39, 0.03);
        }

        .metric-label {
          color: #6b7280;
          font-size: 12px;
          font-weight: 500;
          margin-bottom: 10px;
        }

        .metric-value {
          color: #111827;
          font-size: 25px;
          font-weight: 750;
        }

        .metric-footer {
          color: #9ca3af;
          font-size: 11px;
          margin-top: 8px;
        }

        .dashboard-grid {
          display: grid;
          grid-template-columns: 1.6fr 1fr;
          gap: 20px;
        }

        .panel {
          background: white;
          border: 1px solid #e6e9ef;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(17, 24, 39, 0.03);
          overflow: hidden;
        }

        .panel-header {
          padding: 18px 20px;
          border-bottom: 1px solid #edf0f4;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .panel-title {
          font-size: 14px;
          font-weight: 700;
        }

        .panel-subtitle {
          color: #9ca3af;
          font-size: 11px;
          margin-top: 3px;
        }

        .view-button {
          border: none;
          background: #f3f1ff;
          color: #6657d9;
          border-radius: 7px;
          padding: 7px 10px;
          font-size: 11px;
          cursor: pointer;
          font-weight: 600;
        }

        .table-wrapper {
          overflow-x: auto;
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        th {
          text-align: left;
          color: #9ca3af;
          font-size: 10px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          padding: 12px 20px;
          background: #fafbfc;
        }

        td {
          padding: 14px 20px;
          border-top: 1px solid #f0f2f5;
          font-size: 12px;
        }

        .transaction-id {
          font-weight: 650;
          color: #374151;
        }

        .amount {
          font-weight: 600;
        }

        .status {
          display: inline-block;
          padding: 5px 8px;
          border-radius: 6px;
          background: #f3f4f6;
          color: #4b5563;
          font-size: 10px;
          font-weight: 650;
        }

        .status.pricing {
          background: #fff4e5;
          color: #b45309;
        }

        .status.settlement {
          background: #feecec;
          color: #b91c1c;
        }

        .status.refund {
          background: #edf7f1;
          color: #15803d;
        }

        .status.regional {
          background: #eef2ff;
          color: #4f46e5;
        }

        .exception-list {
          padding: 8px 0;
        }

        .exception-item {
          padding: 15px 20px;
          border-bottom: 1px solid #f0f2f5;
        }

        .exception-item:last-child {
          border-bottom: none;
        }

        .exception-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .exception-reason {
          color: #6b7280;
          font-size: 11px;
          line-height: 1.5;
        }

        .chart-container {
          padding: 20px;
        }

        .bar-row {
          margin-bottom: 17px;
        }

        .bar-info {
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          margin-bottom: 6px;
          color: #4b5563;
        }

        .bar-track {
          height: 8px;
          border-radius: 10px;
          background: #eef0f4;
          overflow: hidden;
        }

        .bar-fill {
          height: 100%;
          border-radius: 10px;
          background: #6d5dfc;
        }

        .empty-state {
          padding: 40px 20px;
          text-align: center;
          color: #9ca3af;
          font-size: 13px;
        }

        .loading {
          padding: 80px;
          text-align: center;
          color: #6b7280;
        }

        .investigation-layout {
          display: grid;
          grid-template-columns: 1fr 1.3fr;
          gap: 20px;
        }

        .exception-select {
          padding: 16px;
        }

        .select-card {
          border: 1px solid #e5e7eb;
          border-radius: 10px;
          padding: 14px;
          margin-bottom: 10px;
          cursor: pointer;
          background: white;
        }

        .select-card:hover {
          border-color: #8b7ff0;
        }

        .select-card.selected {
          border-color: #6d5dfc;
          background: #faf9ff;
        }

        .select-id {
          font-size: 12px;
          font-weight: 700;
          margin-bottom: 7px;
        }

        .select-reason {
          color: #6b7280;
          font-size: 11px;
        }

        .ai-panel {
          padding: 22px;
        }

        .ai-badge {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          background: #f3f1ff;
          color: #6657d9;
          border-radius: 7px;
          padding: 7px 10px;
          font-size: 11px;
          font-weight: 700;
          margin-bottom: 18px;
        }

        .ai-classification {
          font-size: 20px;
          font-weight: 750;
          margin-bottom: 8px;
        }

        .confidence {
          color: #6b7280;
          font-size: 12px;
          margin-bottom: 22px;
        }

        .ai-section {
          margin-top: 20px;
        }

        .ai-section-title {
          font-size: 11px;
          font-weight: 700;
          color: #374151;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 8px;
        }

        .ai-text {
          color: #4b5563;
          font-size: 13px;
          line-height: 1.7;
        }

        .evidence-item {
          color: #4b5563;
          font-size: 12px;
          margin-bottom: 7px;
          padding-left: 15px;
          position: relative;
        }

        .evidence-item:before {
          content: "•";
          position: absolute;
          left: 0;
          color: #6d5dfc;
        }

        .investigate-button {
          width: 100%;
          margin-top: 18px;
          border: none;
          background: #6d5dfc;
          color: white;
          padding: 11px;
          border-radius: 8px;
          font-size: 12px;
          font-weight: 700;
          cursor: pointer;
        }

        .investigate-button:hover {
          background: #5c4de0;
        }

        .investigate-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .action-button {
          border: none;
          background: #f3f1ff;
          color: #6657d9;
          padding: 7px 10px;
          border-radius: 7px;
          font-size: 11px;
          font-weight: 700;
          cursor: pointer;
        }

        .action-button:hover {
          background: #e9e5ff;
        }

        .notice {
          background: #fff8e8;
          border: 1px solid #f3dfad;
          border-radius: 9px;
          padding: 12px;
          color: #8a6518;
          font-size: 11px;
          line-height: 1.5;
          margin-bottom: 18px;
        }

        .agent-trace {
          margin-bottom: 20px;
          padding: 14px;
          border: 1px solid #e5e7eb;
          border-radius: 10px;
          background: #fafafa;
        }

        .agent-trace-title {
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 12px;
          color: #374151;
        }

        .agent-step {
          display: flex;
          gap: 10px;
          align-items: flex-start;
          margin-bottom: 10px;
        }

        .agent-step:last-child {
          margin-bottom: 0;
        }

        .agent-step-icon {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #edf7f1;
          color: #15803d;
          font-size: 11px;
          font-weight: 700;
          flex-shrink: 0;
        }

        .agent-step-name {
          font-size: 11px;
          font-weight: 700;
          color: #374151;
        }

        .agent-step-description {
          margin-top: 2px;
          font-size: 10px;
          color: #6b7280;
          line-height: 1.4;
        }

        @media (max-width: 1000px) {
          .metrics-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .dashboard-grid,
          .investigation-layout {
            grid-template-columns: 1fr;
          }
        }
      `}</style>

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <div className="brand-title">
              Finance Controller
            </div>

            <div className="brand-subtitle">
              Revenue Integrity
            </div>
          </div>
        </div>

        <div className="nav-title">
          Controller
        </div>

        {navigation.map((item) => (
          <button
            key={item.name}
            className={
              activePage === item.name
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => setActivePage(item.name)}
          >
            <span className="nav-icon">
              {item.icon}
            </span>

            {item.name}
          </button>
        ))}
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <div className="page-title">
              {activePage}
            </div>

            <div className="page-description">
              AI-powered financial reconciliation and exception control
            </div>
          </div>

          <div className="system-status">
            <span className="status-dot"></span>
            Controller online
          </div>
        </header>

        <section className="content">

          {loading ? (
            <div className="loading">
              Loading finance controller...
            </div>
          ) : activePage === "Overview" ? (
            <>
              <div className="metrics-grid">

                <div className="metric-card">
                  <div className="metric-label">
                    Total Transactions
                  </div>

                  <div className="metric-value">
                    {metrics?.total_transactions ?? 0}
                  </div>

                  <div className="metric-footer">
                    Processed in current batch
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">
                    Match Rate
                  </div>

                  <div className="metric-value">
                    {metrics?.match_rate ?? 0}%
                  </div>

                  <div className="metric-footer">
                    Automatically reconciled
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">
                    Exceptions
                  </div>

                  <div className="metric-value">
                    {metrics?.exceptions ?? 0}
                  </div>

                  <div className="metric-footer">
                    Require investigation
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">
                    Processing Time
                  </div>

                  <div className="metric-value">
                    {metrics?.processing_time_seconds ?? 0}s
                  </div>

                  <div className="metric-footer">
                    Deterministic reconciliation
                  </div>
                </div>

              </div>

              <div className="dashboard-grid">

                <div className="panel">

                  <div className="panel-header">
                    <div>
                      <div className="panel-title">
                        Recent Exceptions
                      </div>

                      <div className="panel-subtitle">
                        Financial discrepancies detected by the controller
                      </div>
                    </div>

                    <button
                      className="view-button"
                      onClick={() => setActivePage("Exceptions")}
                    >
                      View all
                    </button>
                  </div>

                  <div className="table-wrapper">
                    <table>
                      <thead>
                        <tr>
                          <th>Transaction</th>
                          <th>Type</th>
                          <th>Impact</th>
                        </tr>
                      </thead>

                      <tbody>
                        {exceptions
                          .slice(0, 7)
                          .map((exception) => (
                            <tr key={exception.transaction_id}>
                              <td>
                                <span className="transaction-id">
                                  {exception.transaction_id}
                                </span>
                              </td>

                              <td>
                                <span
                                  className={getStatusClass(
                                    exception.status
                                  )}
                                >
                                  {statusLabel(exception.status)}
                                </span>
                              </td>

                              <td className="amount">
                                {formatCurrency(
                                  Math.abs(
                                    exception.financial_impact || 0
                                  )
                                )}
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>

                </div>

                <div className="panel">

                  <div className="panel-header">
                    <div>
                      <div className="panel-title">
                        Exception Breakdown
                      </div>

                      <div className="panel-subtitle">
                        Current reconciliation batch
                      </div>
                    </div>
                  </div>

                  <div className="chart-container">

                    <div className="bar-row">
                      <div className="bar-info">
                        <span>Pricing mismatch</span>
                        <span>
                          {metrics?.pricing_mismatches ?? 0}
                        </span>
                      </div>

                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${
                              ((metrics?.pricing_mismatches || 0) /
                                Math.max(metrics?.exceptions || 1, 1)) *
                              100
                            }%`,
                          }}
                        ></div>
                      </div>
                    </div>

                    <div className="bar-row">
                      <div className="bar-info">
                        <span>Settlement mismatch</span>
                        <span>
                          {metrics?.settlement_mismatches ?? 0}
                        </span>
                      </div>

                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${
                              ((metrics?.settlement_mismatches || 0) /
                                Math.max(metrics?.exceptions || 1, 1)) *
                              100
                            }%`,
                          }}
                        ></div>
                      </div>
                    </div>

                    <div className="bar-row">
                      <div className="bar-info">
                        <span>Refund adjustment</span>
                        <span>
                          {metrics?.refund_adjustments ?? 0}
                        </span>
                      </div>

                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${
                              ((metrics?.refund_adjustments || 0) /
                                Math.max(metrics?.exceptions || 1, 1)) *
                              100
                            }%`,
                          }}
                        ></div>
                      </div>
                    </div>

                    <div className="bar-row">
                      <div className="bar-info">
                        <span>Regional review</span>
                        <span>
                          {metrics?.regional_reviews ?? 0}
                        </span>
                      </div>

                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${
                              ((metrics?.regional_reviews || 0) /
                                Math.max(metrics?.exceptions || 1, 1)) *
                              100
                            }%`,
                          }}
                        ></div>
                      </div>
                    </div>

                  </div>

                </div>

              </div>
            </>
          ) : activePage === "Exceptions" ? (
            <div className="panel">

              <div className="panel-header">
                <div>
                  <div className="panel-title">
                    Exception Queue
                  </div>

                  <div className="panel-subtitle">
                    {exceptions.length} exceptions detected
                  </div>
                </div>
              </div>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Transaction</th>
                      <th>Customer</th>
                      <th>Type</th>
                      <th>Order</th>
                      <th>Payment</th>
                      <th>Impact</th>
                    </tr>
                  </thead>

                  <tbody>
                    {exceptions.map((exception) => (
                      <tr key={exception.transaction_id}>
                        <td className="transaction-id">
                          {exception.transaction_id}
                        </td>

                        <td>
                          {exception.customer_id}
                        </td>

                        <td>
                          <span
                            className={getStatusClass(
                              exception.status
                            )}
                          >
                            {statusLabel(exception.status)}
                          </span>
                        </td>

                        <td>
                          {formatCurrency(exception.order_amount)}
                        </td>

                        <td>
                          {formatCurrency(exception.payment_amount)}
                        </td>

                        <td className="amount">
                          {formatCurrency(
                            Math.abs(
                              exception.financial_impact || 0
                            )
                          )}
                        </td>

                        <td>
                          <button
                            className="action-button"
                            onClick={() => {
                              setSelectedException(exception);
                              setInvestigation(null);
                              setActivePage("AI Investigation");
                            }}
                          >
                            Investigate
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>
          ) : activePage === "AI Investigation" ? (
            <div className="investigation-layout">

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <div className="panel-title">
                      Exception Queue
                    </div>

                    <div className="panel-subtitle">
                      Select a case to investigate
                    </div>
                  </div>
                </div>

                <div className="exception-select">
                  {exceptions.map((exception) => (
                    <div
                      key={exception.transaction_id}
                      className={
                        selectedException?.transaction_id ===
                        exception.transaction_id
                          ? "select-card selected"
                          : "select-card"
                      }
                      onClick={() => {
                        setSelectedException(exception);
                        setInvestigation(null);
                      }}
                    >
                      <div className="select-id">
                        {exception.transaction_id}
                      </div>

                      <div className="select-reason">
                        {exception.reason}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="panel">

                <div className="ai-panel">

                  <div className="ai-badge">
                    ✦ AI Finance Investigator
                  </div>
                  <div className="agent-trace">
                    <div className="agent-trace-title">Investigation Workflow</div>
                    {(investigation?.investigation_steps || []).map((step) => (
                      <div className="agent-step" key={step.step}>
                        <div className="agent-step-icon">✓</div>
                        <div>
                          <div className="agent-step-name">{step.name}</div>
                          <div className="agent-step-description">
                            {step.description}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>


                  <div className="notice">
                    AI analysis is based on transaction,
                    reconciliation, and pricing-policy evidence.
                    Financial arithmetic remains deterministic.
                  </div>

                  {!selectedException ? (
                    <div className="empty-state">
                      Select an exception from the queue to begin
                      an AI investigation.
                    </div>
                  ) : (
                    <>
                      <div className="ai-classification">
                        {investigation?.ai_investigation
                          ?.classification ||
                          "Ready for investigation"}
                      </div>

                      {investigation ? (
                        <>
                          <div className="confidence">
                            Confidence:{" "}
                            {Math.round(
                              (investigation.ai_investigation
                                ?.confidence || 0) * 100
                            )}
                            %
                          </div>

                          <div className="ai-section">
                            <div className="ai-section-title">
                              Explanation
                            </div>

                            <div className="ai-text">
                              {
                                investigation.ai_investigation
                                  ?.explanation
                              }
                            </div>
                          </div>

                          <div className="ai-section">
                            <div className="ai-section-title">
                              Financial Impact
                            </div>

                            <div className="ai-text">
                              {formatCurrency(
                                Math.abs(
                                  investigation.ai_investigation
                                    ?.financial_impact || 0
                                )
                              )}
                            </div>
                          </div>

                          <div className="ai-section">
                            <div className="ai-section-title">
                              Evidence
                            </div>

                            {(
                              investigation.ai_investigation
                                ?.evidence || []
                            ).map((item, index) => (
                              <div
                                className="evidence-item"
                                key={index}
                              >
                                {item}
                              </div>
                            ))}
                          </div>

                          <div className="ai-section">
                            <div className="ai-section-title">
                              Recommendation
                            </div>

                            <div className="ai-text">
                              {
                                investigation.ai_investigation
                                  ?.recommendation
                              }
                            </div>
                          </div>
                        </>
                      ) : (
                        <div className="ai-text">
                          This exception has not been investigated yet.
                        </div>
                      )}

                      <button
                        className="investigate-button"
                        disabled={investigating}
                        onClick={() =>
                          investigate(
                            selectedException.transaction_id
                          )
                        }
                      >
                        {investigating
                          ? "Investigating with AI..."
                          : "Investigate with AI"}
                      </button>
                    </>
                  )}

                </div>

              </div>

            </div>
          ) : activePage === "Reports" ? (
            <div>
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-label">Evaluation Accuracy</div>
                  <div className="metric-value">
                    {report?.accuracy ?? 0}%
                  </div>
                  <div className="metric-footer">
                    Deterministic reconciliation evaluation
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">Total Test Records</div>
                  <div className="metric-value">
                    {report?.total_records ?? report?.total ?? report?.total_transactions ?? 0}
                  </div>
                  <div className="metric-footer">
                    Synthetic evaluation dataset
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">Correct</div>
                  <div className="metric-value">{report?.correct_predictions ?? report?.correct ?? 0}</div>
                  <div className="metric-footer">Correct classifications</div>
                </div>

                <div className="metric-card">
                  <div className="metric-label">Incorrect</div>
                  <div className="metric-value">{report?.incorrect_predictions ?? report?.incorrect ?? 0}</div>
                  <div className="metric-footer">Incorrect classifications</div>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <div className="panel-title">Evaluation Report</div>
                    <div className="panel-subtitle">
                      Reconciliation performance by exception category
                    </div>
                  </div>
                </div>

                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Category</th>
                        <th>Precision</th>
                        <th>Recall</th>
                        <th>TP</th>
                        <th>FP</th>
                        <th>FN</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(
                        report?.class_metrics || report?.categories || report?.category_metrics || {}
                      ).map(([category, values]) => (
                        <tr key={category}>
                          <td className="transaction-id">
                            {category.replaceAll("_", " ")}
                          </td>
                          <td>{values?.precision ?? 0}%</td>
                          <td>{values?.recall ?? 0}%</td>
                          <td>{values?.true_positive ?? values?.TP ?? values?.tp ?? 0}</td>
                          <td>{values?.false_positive ?? values?.FP ?? values?.fp ?? 0}</td>
                          <td>{values?.false_negative ?? values?.FN ?? values?.fn ?? 0}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="notice" style={{ marginTop: "20px" }}>
                These metrics evaluate the deterministic reconciliation engine
                against synthetic ground truth. They should not be presented as
                a measurement of LLM accuracy.
              </div>
            </div>
          ) : activePage === "Policies" ? (
            <div className="panel">
              <div className="panel-header">
                <div>
                  <div className="panel-title">Pricing Policies</div>
                  <div className="panel-subtitle">
                    Regional pricing rules used by the reconciliation controller
                  </div>
                </div>
              </div>

              <div className="notice" style={{ margin: "20px" }}>
                Currency: {policies?.currency || "INR"}. Regional differences are
                review signals, not automatic fraud decisions.
              </div>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Plan</th>
                      <th>India</th>
                      <th>United States</th>
                      <th>Germany</th>
                      <th>United Kingdom</th>
                      <th>Singapore</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(policies?.plans || {}).map(
                      ([planName, countryPrices]) => (
                        <tr key={planName}>
                          <td className="transaction-id">
                            {planName.charAt(0).toUpperCase() + planName.slice(1)}
                          </td>
                          <td>{formatCurrency(countryPrices?.IN)}</td>
                          <td>{formatCurrency(countryPrices?.US)}</td>
                          <td>{formatCurrency(countryPrices?.DE)}</td>
                          <td>{formatCurrency(countryPrices?.GB)}</td>
                          <td>{formatCurrency(countryPrices?.SG)}</td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ) : activePage === "Transactions" ? (
            <div className="panel">

              <div className="panel-header">
                <div>
                  <div className="panel-title">
                    Transaction Ledger
                  </div>

                  <div className="panel-subtitle">
                    All transactions processed by the controller
                  </div>
                </div>
              </div>

              <TransactionsTable
                formatCurrency={formatCurrency}
              />

            </div>
          ) : (
            <div className="panel">
              <div className="empty-state">
                <div
                  style={{
                    fontSize: "25px",
                    marginBottom: "12px",
                  }}
                >
                  ✦
                </div>

                <div
                  style={{
                    color: "#374151",
                    fontWeight: 700,
                    marginBottom: "5px",
                  }}
                >
                  {activePage}
                </div>

                This module is ready for integration.
              </div>
            </div>
          )}

        </section>
      </main>
    </div>
  );
}

function TransactionsTable({ formatCurrency }) {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/transactions")
      .then((response) => response.json())
      .then((data) => {
        setTransactions(data.transactions || []);
      })
      .catch((error) => {
        console.error(
          "Failed to load transactions:",
          error
        );
      });
  }, []);

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Transaction</th>
            <th>Product</th>
            <th>Plan</th>
            <th>Order Amount</th>
            <th>Payment</th>
            <th>Billing Country</th>
          </tr>
        </thead>

        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.transaction_id}>
              <td className="transaction-id">
                {transaction.transaction_id}
              </td>

              <td>
                {transaction.product}
              </td>

              <td>
                {transaction.plan}
              </td>

              <td>
                {formatCurrency(
                  transaction.order_amount
                )}
              </td>

              <td>
                {formatCurrency(
                  transaction.payment_amount
                )}
              </td>

              <td>
                {transaction.billing_country}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;