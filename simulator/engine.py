"""Simulation engine for FastBox delivery logistics."""

import json
from typing import Dict, List, Tuple, Optional, Any
from .models import Warehouse, Agent, Package, DeliveryStep, AgentReport, SimulationReport
from .distance import calculate_delivery_trip_distance
from .dispatcher import dispatch_packages_to_agents


class SimulationEngine:
    """Executes logistics simulation, tracking movement paths and performance metrics."""

    def __init__(
        self,
        warehouses: Dict[str, Warehouse],
        agents: Dict[str, Agent],
        packages: List[Package]
    ) -> None:
        self.warehouses = warehouses
        self.agents = agents
        self.packages = packages
        self.delivery_history: List[DeliveryStep] = []

    def run(self) -> SimulationReport:
        """Executes full assignment and delivery simulation across the network.

        Returns:
            SimulationReport: Summary report containing per-agent metrics and best agent.
        """
        # Step 1: Assign packages to nearest agents
        assignments = dispatch_packages_to_agents(self.warehouses, self.agents, self.packages)

        # Step 2: Execute deliveries for each agent
        for agent_id, assigned_packages in assignments.items():
            agent = self.agents[agent_id]
            for package in assigned_packages:
                warehouse = self.warehouses[package.warehouse_id]
                from_pos = agent.location
                wh_pos = warehouse.location
                dest_pos = package.destination

                pickup_d, deliver_d, step_total = calculate_delivery_trip_distance(
                    from_pos, wh_pos, dest_pos
                )

                agent.total_distance += step_total
                agent.packages_delivered += 1
                agent.location = dest_pos  # Agent finishes at the delivery location

                # Log detailed step
                step = DeliveryStep(
                    package_id=package.id,
                    agent_id=agent.id,
                    from_location=from_pos,
                    to_warehouse_id=warehouse.id,
                    warehouse_location=wh_pos,
                    destination_location=dest_pos,
                    pickup_distance=pickup_d,
                    delivery_distance=deliver_d,
                    step_total_distance=step_total,
                    cumulative_distance_after_step=agent.total_distance,
                )
                self.delivery_history.append(step)

        # Step 3: Build and return report
        return self._generate_report()

    def _generate_report(self) -> SimulationReport:
        """Constructs the SimulationReport and determines the best performing agent."""
        agent_reports: Dict[str, AgentReport] = {}
        active_candidates: List[Tuple[float, int, float, str]] = []

        total_packages = 0
        total_dist_all = 0.0

        for agent_id, agent in sorted(self.agents.items()):
            rep = AgentReport(
                packages_delivered=agent.packages_delivered,
                total_distance=round(agent.total_distance, 2),
                efficiency=agent.efficiency,
            )
            agent_reports[agent_id] = rep
            total_packages += agent.packages_delivered
            total_dist_all += agent.total_distance

            # Candidate tuple for best agent:
            # (efficiency [lower is better], -packages_delivered [more is better], total_distance [lower is better], agent_id)
            if agent.packages_delivered > 0:
                active_candidates.append((
                    agent.efficiency,
                    -agent.packages_delivered,
                    agent.total_distance,
                    agent_id
                ))

        best_agent: Optional[str] = None
        if active_candidates:
            active_candidates.sort()
            best_agent = active_candidates[0][3]

        return SimulationReport(
            agent_reports=agent_reports,
            best_agent=best_agent,
            total_packages_delivered=total_packages,
            total_distance_all_agents=round(total_dist_all, 2),
        )


def execute_simulation(
    warehouses: Dict[str, Warehouse],
    agents: Dict[str, Agent],
    packages: List[Package]
) -> Tuple[SimulationReport, List[DeliveryStep]]:
    """Convenience helper to run simulation and return both summary and step logs."""
    engine = SimulationEngine(warehouses, agents, packages)
    report = engine.run()
    return report, engine.delivery_history


def save_report(report: SimulationReport, output_path: str = "report.json") -> str:
    """Exports simulation report to a formatted JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)
    return output_path
