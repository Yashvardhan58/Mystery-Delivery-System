"""Dynamic mid-day agent arrival and workload re-balancing module."""

from typing import Dict, List, Tuple
from ..models import Warehouse, Agent, Package, SimulationReport, DeliveryStep
from ..distance import calculate_delivery_trip_distance, euclidean_distance


def simulate_with_dynamic_agent(
    warehouses: Dict[str, Warehouse],
    agents: Dict[str, Agent],
    packages: List[Package],
    new_agent_id: str = "A_DYNAMIC",
    new_agent_location: Tuple[float, float] = (50.0, 50.0),
    join_after_package_count: int = 2
) -> Tuple[SimulationReport, List[DeliveryStep]]:
    """Simulates dynamic network adaptation where a new agent enters mid-day.

    Workflow:
      1. Initial packages are assigned and delivered under standard network conditions.
      2. When `join_after_package_count` packages have been delivered, a new agent joins at `new_agent_location`.
      3. Remaining unfulfilled packages are dynamically re-evaluated and assigned to the nearest agent
         (factoring in the new agent's entry location).
      4. Deliveries resume and a comprehensive updated report is produced.

    Args:
        warehouses: Warehouse dictionary.
        agents: Initial agents dictionary.
        packages: Full package list.
        new_agent_id: Identifier for newly joined agent.
        new_agent_location: Starting (x, y) coordinates for new agent.
        join_after_package_count: Threshold of completed deliveries before agent joins.

    Returns:
        Tuple of (SimulationReport, List[DeliveryStep]).
    """
    # Create working copies of agents
    active_agents = {
        a_id: Agent(id=a.id, location=a.initial_location)
        for a_id, a in agents.items()
    }
    delivery_history: List[DeliveryStep] = []

    # Phase 1: Initial dispatch
    from ..dispatcher import dispatch_packages_to_agents
    initial_assignments = dispatch_packages_to_agents(warehouses, active_agents, packages)

    completed_packages = set()
    total_delivered = 0

    # Execute phase 1 deliveries up to the join threshold
    for agent_id, pkg_list in initial_assignments.items():
        agent = active_agents[agent_id]
        for pkg in list(pkg_list):
            if total_delivered >= join_after_package_count:
                break
            wh = warehouses[pkg.warehouse_id]
            pickup_d, deliver_d, step_total = calculate_delivery_trip_distance(
                agent.location, wh.location, pkg.destination
            )
            agent.total_distance += step_total
            agent.packages_delivered += 1
            agent.location = pkg.destination

            delivery_history.append(DeliveryStep(
                package_id=pkg.id,
                agent_id=agent.id,
                from_location=agent.initial_location if agent.packages_delivered == 1 else delivery_history[-1].destination_location,
                to_warehouse_id=wh.id,
                warehouse_location=wh.location,
                destination_location=pkg.destination,
                pickup_distance=pickup_d,
                delivery_distance=deliver_d,
                step_total_distance=step_total,
                cumulative_distance_after_step=agent.total_distance,
            ))
            completed_packages.add(pkg.id)
            total_delivered += 1

    # Phase 2: Dynamic Agent Enters
    new_agent = Agent(id=new_agent_id, location=new_agent_location)
    active_agents[new_agent_id] = new_agent

    # Filter unfulfilled packages
    remaining_packages = [p for p in packages if p.id not in completed_packages]

    # Re-dispatch remaining packages with updated agent fleet
    re_assignments = dispatch_packages_to_agents(warehouses, active_agents, remaining_packages)

    # Phase 3: Deliver remaining packages
    for agent_id, pkg_list in re_assignments.items():
        agent = active_agents[agent_id]
        for pkg in pkg_list:
            wh = warehouses[pkg.warehouse_id]
            from_pos = agent.location
            pickup_d, deliver_d, step_total = calculate_delivery_trip_distance(
                from_pos, wh.location, pkg.destination
            )
            agent.total_distance += step_total
            agent.packages_delivered += 1
            agent.location = pkg.destination

            delivery_history.append(DeliveryStep(
                package_id=pkg.id,
                agent_id=agent.id,
                from_location=from_pos,
                to_warehouse_id=wh.id,
                warehouse_location=wh.location,
                destination_location=pkg.destination,
                pickup_distance=pickup_d,
                delivery_distance=deliver_d,
                step_total_distance=step_total,
                cumulative_distance_after_step=agent.total_distance,
            ))

    # Build final report
    from ..engine import SimulationEngine
    temp_engine = SimulationEngine(warehouses, active_agents, [])
    temp_engine.delivery_history = delivery_history
    report = temp_engine._generate_report()

    return report, delivery_history
