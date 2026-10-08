import subprocess
import sys
from pathlib import Path


# ============================================================
# Multi-Agent Supply Chain Orchestrator
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PYTHON_EXECUTABLE = sys.executable


AGENTS = [
    {
        "name": "Demand Forecasting",
        "script": "backend/agents/demand_forecasting_agent.py",
    },
    {
        "name": "Supplier Risk & Selection",
        "script": "backend/agents/supplier_risk_agent.py",
    },
    {
        "name": "Inventory Optimization",
        "script": "backend/agents/inventory_optimization_agent.py",
    },
    {
        "name": "Workforce Intelligence",
        "script": "backend/agents/workforce_intelligence_agent.py",
    },
    {
        "name": "Risk Propagation",
        "script": "backend/agents/risk_propagation_agent.py",
    },
    {
        "name": "Decision Intelligence",
        "script": "backend/agents/decision_intelligence_agent.py",
    },
]


def run_agent(agent):
    """Run one intelligence agent."""

    name = agent["name"]
    script = PROJECT_ROOT / agent["script"]

    print("\n" + "=" * 70)
    print(f"RUNNING AGENT: {name}")
    print("=" * 70)

    if not script.exists():

        print(
            f"ERROR: Agent script not found: {script}"
        )

        return False

    try:

        result = subprocess.run(
            [
                PYTHON_EXECUTABLE,
                str(script),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        print(result.stdout)

        if result.returncode != 0:

            print(
                f"Agent failed: {name}"
            )

            print(
                result.stderr
            )

            return False

        print(
            f"Agent completed successfully: {name}"
        )

        return True

    except Exception as error:

        print(
            f"Unexpected error while running "
            f"{name}: {error}"
        )

        return False


def run_orchestration():

    print("\n")
    print("=" * 70)
    print("MULTI-AGENT SUPPLY CHAIN INTELLIGENCE SYSTEM")
    print("=" * 70)

    print(
        f"Project root: {PROJECT_ROOT}"
    )

    print(
        f"Python executable: {PYTHON_EXECUTABLE}"
    )

    print(
        f"Total agents: {len(AGENTS)}"
    )

    print("\nStarting coordinated intelligence pipeline...")

    successful_agents = 0

    # --------------------------------------------------------
    # Execute agents sequentially
    # --------------------------------------------------------

    for agent in AGENTS:

        success = run_agent(agent)

        if success:

            successful_agents += 1

        else:

            print(
                "\nOrchestration stopped because "
                "an agent failed."
            )

            break

    # --------------------------------------------------------
    # Final orchestration status
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("ORCHESTRATION SUMMARY")
    print("=" * 70)

    print(
        f"Agents completed: "
        f"{successful_agents}/{len(AGENTS)}"
    )

    if successful_agents == len(AGENTS):

        print(
            "STATUS: SUCCESS"
        )

        print(
            "\nAll intelligence agents completed successfully."
        )

        print(
            "The supply chain intelligence pipeline "
            "is ready for downstream applications."
        )

    else:

        print(
            "STATUS: FAILED"
        )

        print(
            "One or more agents did not complete."
        )

    print("=" * 70)


if __name__ == "__main__":

    run_orchestration()