import { useEffect, useState } from "react";
import {
  Brain,
  RefreshCw,
  Warehouse,
  AlertTriangle,
  CheckCircle,
  Activity,
  TrendingUp,
  Package,
  Users,
  Network,
  Lightbulb,
  ShieldAlert,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import "./App.css";

const API = "http://127.0.0.1:8002";

const COLORS = ["#16a34a", "#eab308", "#f97316", "#dc2626"];

function App() {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // SUPPLY_CHAIN_INTERACTIVE_FEATURES_V1
  const [assistantQuestion, setAssistantQuestion] = useState("");
  const [assistantAnswer, setAssistantAnswer] = useState("");
  const [assistantError, setAssistantError] = useState("");
  const [assistantLoading, setAssistantLoading] = useState(false);
  const [scenario, setScenario] = useState({ demand_change_pct: 15, lead_time_change_pct: 20, inventory_change_pct: -10 });
  const [scenarioResult, setScenarioResult] = useState(null);
  const [scenarioError, setScenarioError] = useState("");
  const [scenarioLoading, setScenarioLoading] = useState(false);

  async function loadData() {
    setLoading(true);
    setError("");

    const endpoints = {
      decision: "/api/decision-intelligence",
      forecast: "/api/demand-forecast",
      supplier: "/api/supplier-risk",
      inventory: "/api/inventory-optimization",
      workforce: "/api/workforce-intelligence",
      risk: "/api/risk-propagation",
    };

    try {
      const results = await Promise.all(
        Object.entries(endpoints).map(async ([key, endpoint]) => {
          const response = await fetch(`${API}${endpoint}`);
          if (!response.ok) {
            throw new Error(`${endpoint} returned ${response.status}`);
          }
          return [key, await response.json()];
        })
      );

      setData(Object.fromEntries(results));
    } catch (err) {
      console.error(err);
      setError(
        "Could not load all AI agents. Check that FastAPI is running on port 8002."
      );
    } finally {
      setLoading(false);
    }
  }

  // SUPPLY_CHAIN_INTERACTIVE_FEATURES_V1
  async function askAssistant() {
    const question = assistantQuestion.trim();
    if (!question) { setAssistantError("Enter a question first."); setAssistantAnswer(""); return; }
    setAssistantLoading(true); setAssistantError(""); setAssistantAnswer("");
    try {
      const response = await fetch(`${API}/api/assistant`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `Assistant request failed (${response.status}).`);
      setAssistantAnswer(payload.answer || "The assistant returned no answer.");
    } catch (err) { setAssistantError(err.message || "Could not contact the assistant API."); }
    finally { setAssistantLoading(false); }
  }

  async function runWhatIf() {
    setScenarioLoading(true); setScenarioError(""); setScenarioResult(null);
    try {
      const requestBody = {
        demand_change_pct: Number(scenario.demand_change_pct),
        lead_time_change_pct: Number(scenario.lead_time_change_pct),
        inventory_change_pct: Number(scenario.inventory_change_pct),
      };
      const response = await fetch(`${API}/api/what-if`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || `Simulation failed (${response.status}).`);
      setScenarioResult(payload);
    } catch (err) { setScenarioError(err.message || "Could not run the what-if simulation."); }
    finally { setScenarioLoading(false); }
  }
  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <Brain size={42} />
        <h2>Supply Chain AI Control Tower</h2>
        <p>Connecting to your AI agents...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-screen">
        <ShieldAlert size={42} />
        <h2>Backend Connection Error</h2>
        <p>{error}</p>
        <button onClick={loadData}>
          <RefreshCw size={16} /> Retry Connection
        </button>
      </div>
    );
  }

  const decisions = data.decision?.decisions || [];
  const suppliers = data.supplier?.suppliers || [];
  const inventory = data.inventory?.inventory || [];
  const workforce = data.workforce?.workforce || [];
  const risks = data.risk?.risk_propagation || [];

  const inventorySummary = data.inventory?.status_summary || {};
  const workforceSummary = data.workforce?.status_summary || {};
  const prioritySummary = data.decision?.priority_summary || {};
  const riskSummary = data.risk?.risk_summary || {};

  const supplierChart = suppliers.map((s) => ({
    name: s.Supplier_ID,
    risk: Number(s.Risk_Score || 0),
  }));

  const inventoryChart = Object.entries(inventorySummary).map(
    ([name, value]) => ({ name, value })
  );

  const workforceChart = Object.entries(workforceSummary).map(
    ([name, value]) => ({ name, value })
  );

  const decisionChart = decisions.map((d) => ({
    name: d.Warehouse_ID,
    score: Number(d.Decision_Priority_Score || 0),
  }));

  const riskChart = risks.map((r) => ({
    name: r.Warehouse_ID,
    score: Number(r.Propagated_Risk_Score || 0),
  }));

  const formatNumber = (value) =>
    Number(value || 0).toLocaleString();

  const forecastEvaluation = data.forecast?.evaluation || {};

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>
            <Brain size={32} />
            Supply Chain AI Control Tower
          </h1>
          <p>
            Intelligent demand, supplier, inventory, workforce and risk
            analytics
          </p>
        </div>

        <div className="connection">
          <span className="connection-dot" />
          <CheckCircle size={17} />
          AI Backend Connected
        </div>
      </header>

      <main className="dashboard">
        <section className="section">
          <div className="section-title">
            <div>
              <h2>
                <Activity size={22} /> Control Tower Overview
              </h2>
              <p>Operational intelligence across your supply chain</p>
            </div>

            <button className="refresh-button" onClick={loadData}>
              <RefreshCw size={16} /> Refresh Data
            </button>
          </div>

          <div className="cards">
            <MetricCard
              icon={<Warehouse />}
              label="Warehouses"
              value={data.decision?.warehouses_analyzed ?? decisions.length}
            />
            <MetricCard
              icon={<AlertTriangle />}
              label="High Priority"
              value={prioritySummary["High Priority"] || 0}
              type="danger"
            />
            <MetricCard
              icon={<Activity />}
              label="Monitor"
              value={prioritySummary.Monitor || 0}
              type="warning"
            />
            <MetricCard
              icon={<CheckCircle />}
              label="Normal"
              value={prioritySummary.Normal || 0}
              type="success"
            />
          </div>
        </section>

        <section className="section">
          <div className="section-title">
            <div>
              <h2>
                <Brain size={22} /> AI Agent Intelligence
              </h2>
              <p>Results returned by your six backend agents</p>
            </div>
          </div>

          <div className="agent-grid">
            <AgentCard
              icon={<TrendingUp />}
              title="Demand Forecasting"
              description="Predicts future demand and evaluates forecast accuracy."
              value={formatNumber(data.forecast?.rows)}
              label="Records analyzed"
            />

            <AgentCard
              icon={<ShieldAlert />}
              title="Supplier Risk"
              description="Ranks suppliers according to risk and selection scores."
              value={formatNumber(data.supplier?.suppliers_analyzed)}
              label="Suppliers analyzed"
            />

            <AgentCard
              icon={<Package />}
              title="Inventory Optimization"
              description="Identifies stock conditions and replenishment needs."
              value={formatNumber(data.inventory?.locations_analyzed)}
              label="Locations analyzed"
            />

            <AgentCard
              icon={<Users />}
              title="Workforce Intelligence"
              description="Analyzes demand, staffing requirements and workload."
              value={formatNumber(data.workforce?.days_analyzed)}
              label="Daily records analyzed"
            />

            <AgentCard
              icon={<Network />}
              title="Risk Propagation"
              description="Combines operational signals into warehouse risk scores."
              value={formatNumber(data.risk?.warehouses_analyzed)}
              label="Warehouses analyzed"
            />

            <AgentCard
              icon={<Lightbulb />}
              title="Decision Intelligence"
              description="Prioritizes warehouses and recommends operational actions."
              value={formatNumber(decisions.length)}
              label="Decisions generated"
            />
          </div>
        </section>

        <section className="section">
          <div className="section-title">
            <div>
              <h2>
                <TrendingUp size={22} /> Demand Forecast Evaluation
              </h2>
              <p>Model evaluation metrics returned by the backend</p>
            </div>
          </div>

          <div className="cards">
            <MetricCard
              icon={<Activity />}
              label="MAE"
              value={forecastEvaluation.MAE?.toFixed(2) ?? "—"}
            />
            <MetricCard
              icon={<TrendingUp />}
              label="RMSE"
              value={forecastEvaluation.RMSE?.toFixed(2) ?? "—"}
            />
            <MetricCard
              icon={<Brain />}
              label="R² Score"
              value={forecastEvaluation.R2?.toFixed(3) ?? "—"}
            />
            <MetricCard
              icon={<CheckCircle />}
              label="Forecast Quality"
              value={forecastEvaluation.Forecast_Quality || "—"}
            />
          </div>
        </section>

        <div className="chart-grid">
          <ChartCard title="Inventory Status Distribution">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={inventoryChart}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label
                >
                  {inventoryChart.map((entry, index) => (
                    <Cell
                      key={entry.name}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Supplier Risk Rankings">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={supplierChart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="risk" name="Risk Score" fill="#e879f9" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Workforce Status">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={workforceChart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" name="Records" fill="#16a34a" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Warehouse Decision Priority Scores">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={decisionChart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" name="Priority Score" fill="#f97316" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Propagated Risk by Warehouse">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={riskChart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" name="Risk Score" fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <section className="section">
          <div className="section-title">
            <div>
              <h2>
                <Package size={22} /> Inventory Replenishment Alerts
              </h2>
              <p>Inventory records flagged for attention by the agent</p>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Warehouse</th>
                  <th>Current Stock</th>
                  <th>Reorder Point</th>
                  <th>Recommended Order</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {inventory
                  .filter((item) =>
                    ["Critical", "Reorder", "Monitor"].includes(
                      item.Inventory_Status
                    )
                  )
                  .slice(0, 15)
                  .map((item, index) => (
                    <tr key={`${item.SKU_ID}-${item.Warehouse_ID}-${index}`}>
                      <td>{item.SKU_ID}</td>
                      <td>{item.Warehouse_ID}</td>
                      <td>{formatNumber(item.Current_Inventory)}</td>
                      <td>
                        {Number(
                          item.Recommended_Reorder_Point || 0
                        ).toFixed(2)}
                      </td>
                      <td>{formatNumber(item.Recommended_Order_Qty)}</td>
                      <td>
                        <StatusBadge status={item.Inventory_Status} />
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="section">
          <div className="section-title">
            <div>
              <h2>
                <Warehouse size={22} /> Warehouse Decisions
              </h2>
              <p>Priorities and recommended actions from Decision Intelligence</p>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Warehouse</th>
                  <th>Priority</th>
                  <th>Priority Score</th>
                  <th>Risk Level</th>
                  <th>Confidence</th>
                  <th>Recommended Action</th>
                </tr>
              </thead>
              <tbody>
                {decisions.map((item) => (
                  <tr key={item.Warehouse_ID}>
                    <td>
                      <strong>{item.Warehouse_ID}</strong>
                    </td>
                    <td>
                      <StatusBadge status={item.Decision_Priority} />
                    </td>
                    <td>
                      {Number(item.Decision_Priority_Score || 0).toFixed(2)}
                    </td>
                    <td>
                      <StatusBadge status={item.Overall_Risk_Level} />
                    </td>
                    <td>{item.Decision_Confidence ?? "—"}%</td>
                    <td className="action">{item.Action_Plan || "Continue monitoring."}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="section">
          <div className="section-title">
            <div>
              <h2>
                <Lightbulb size={22} /> AI Decision Explanations
              </h2>
              <p>Why each warehouse received its decision priority</p>
            </div>
          </div>

          <div className="explanation-grid">
            {decisions.map((item) => (
              <div className="explanation-card" key={item.Warehouse_ID}>
                <div className="explanation-header">
                  <strong>{item.Warehouse_ID}</strong>
                  <StatusBadge status={item.Decision_Priority} />
                </div>
                <p>{item.Why_This_Decision || "No explanation supplied."}</p>
                <div className="recommendation">
                  <span>Recommended Action</span>
                  <strong>{item.Action_Plan || "Continue monitoring."}</strong>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* SUPPLY_CHAIN_INTERACTIVE_FEATURES_V1 */}
        <section className="section">
          <div className="section-title"><div><h2><Brain size={22} /> Supply Chain Assistant</h2><p>Ask questions about your project data using the rule-based, data-grounded assistant.</p></div></div>
          <div className="feature-panel">
            <label className="feature-label" htmlFor="assistant-question">Your question</label>
            <textarea id="assistant-question" className="feature-textarea" rows={3} value={assistantQuestion} onChange={(event) => setAssistantQuestion(event.target.value)} placeholder="Example: Why is WH_4 high priority?" />
            <div className="feature-actions"><button className="refresh-button" type="button" onClick={askAssistant} disabled={assistantLoading}>{assistantLoading ? "Checking data..." : "Ask assistant"}</button><span className="feature-note">Answers use the project's CSV outputs and predefined rules.</span></div>
            {assistantError && <p className="feature-error">{assistantError}</p>}
            {assistantAnswer && <div className="feature-result"><h3>Assistant response</h3><p className="feature-prewrap">{assistantAnswer}</p></div>}
          </div>
        </section>

        <section className="section">
          <div className="section-title"><div><h2><Activity size={22} /> What-If Scenario Simulator</h2><p>Change demand, supplier lead time, and inventory to estimate operational impact.</p></div></div>
          <div className="feature-panel">
            <div className="scenario-input-grid">
              <div><label className="feature-label" htmlFor="demand-change">Demand change (%)</label><input id="demand-change" className="feature-input" type="number" min="-100" max="500" step="1" value={scenario.demand_change_pct} onChange={(event) => setScenario({ ...scenario, demand_change_pct: event.target.value })} /></div>
              <div><label className="feature-label" htmlFor="lead-time-change">Supplier lead-time change (%)</label><input id="lead-time-change" className="feature-input" type="number" min="-90" max="500" step="1" value={scenario.lead_time_change_pct} onChange={(event) => setScenario({ ...scenario, lead_time_change_pct: event.target.value })} /></div>
              <div><label className="feature-label" htmlFor="inventory-change">Inventory change (%)</label><input id="inventory-change" className="feature-input" type="number" min="-100" max="500" step="1" value={scenario.inventory_change_pct} onChange={(event) => setScenario({ ...scenario, inventory_change_pct: event.target.value })} /></div>
            </div>
            <div className="feature-actions"><button className="refresh-button" type="button" onClick={runWhatIf} disabled={scenarioLoading}>{scenarioLoading ? "Simulating..." : "Run simulation"}</button><span className="feature-note">Defaults: demand +15%, lead time +20%, inventory âˆ’10%.</span></div>
            {scenarioError && <p className="feature-error">{scenarioError}</p>}
            {scenarioResult && <div className="feature-result">
              <h3>Scenario results</h3>
              {scenarioResult.scenario && <p className="feature-note">Demand {scenarioResult.scenario.demand_change_pct}% | Lead time {scenarioResult.scenario.lead_time_change_pct}% | Inventory {scenarioResult.scenario.inventory_change_pct}%</p>}
              <h4>Inventory impact</h4><div className="feature-metrics-grid">{Object.entries(scenarioResult.inventory || {}).map(([key, value]) => <div className="feature-metric" key={`inventory-${key}`}><span>{key.replace(/_/g, " ")}</span><strong>{typeof value === "number" ? value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : (value && typeof value === "object" ? Object.entries(value).map(([key, count]) => key.replace(/_/g, " ") + ": " + count).join(", ") : String(value))}</strong></div>)}</div>
              <h4>Workforce impact</h4><div className="feature-metrics-grid">{Object.entries(scenarioResult.workforce || {}).map(([key, value]) => <div className="feature-metric" key={`workforce-${key}`}><span>{key.replace(/_/g, " ")}</span><strong>{typeof value === "number" ? value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : (value && typeof value === "object" ? Object.entries(value).map(([key, count]) => key.replace(/_/g, " ") + ": " + count).join(", ") : String(value))}</strong></div>)}</div>
              {Array.isArray(scenarioResult.recommendations) && scenarioResult.recommendations.length > 0 && <><h4>Recommendations</h4><ul className="feature-recommendations">{scenarioResult.recommendations.map((item, index) => <li key={`recommendation-${index}`}>{item}</li>)}</ul></>}
            </div>}
          </div>
        </section>
        <footer>
          <div>
            <Brain size={18} />
            <strong>AI Supply Chain Control Tower</strong>
          </div>
          <span>React + FastAPI + AI Agents</span>
        </footer>
      </main>
    </div>
  );
}

function MetricCard({ icon, label, value, type = "" }) {
  return (
    <div className={`card ${type}`}>
      <div className="card-icon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function AgentCard({ icon, title, description, value, label }) {
  return (
    <div className="agent-card">
      <div className="agent-header">
        <div className="agent-icon blue">{icon}</div>
        <div>
          <h3>{title}</h3>
          <span>{label}</span>
        </div>
      </div>
      <div className="agent-main-value">{value}</div>
      <div className="agent-description">{description}</div>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="chart-card">
      <h3>{title}</h3>
      {children}
    </div>
  );
}

function StatusBadge({ status }) {
  const value = String(status || "Unknown");
  const normalized = value.toLowerCase();

  let type = "normal";

  if (
    normalized.includes("high") ||
    normalized.includes("critical")
  ) {
    type = "high";
  } else if (
    normalized.includes("monitor") ||
    normalized.includes("reorder") ||
    normalized.includes("medium")
  ) {
    type = "monitor";
  } else if (
    normalized.includes("healthy") ||
    normalized.includes("adequate") ||
    normalized.includes("low") ||
    normalized.includes("normal")
  ) {
    type = "low";
  }

  return <span className={`badge ${type}`}>{value}</span>;
}

export default App;