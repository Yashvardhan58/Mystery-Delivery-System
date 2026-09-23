"""Dispatcher module: assigns packages to delivery agents based on warehouse proximity."""

from typing import Dict, List, Tuple
from .models import Warehouse, Agent, Package
from .distance import euclidean_distance


def find_nearest_agent_for_warehouse(
    warehouse: Warehouse,
    agents: Dict[str, Agent],
    current_workloads: Dict[str, int] = None
) -> str:
    """Finds the optimal nearest agent for a given warehouse location.

    Assignment & Tie-breaking Strategy:
      1. Primary: Euclidean distance from Agent's initial location to Warehouse.
      2. Secondary: Load-balancing tie breaker (agent with fewer assigned packages).
      3. Tertiary: Deterministic alphabetical Agent ID order (e.g. 'A1' before 'A2').

    Args:
        warehouse: The source warehouse object.
        agents: Dictionary of all available Agent objects.
        current_workloads: Optional dictionary tracking number of packages currently assigned.

    Returns:
        str: ID of the selected agent.
    """
    if not agents:
        raise ValueError("Cannot assign packages: No agents available in network.")

    if current_workloads is None:
        current_workloads = {a_id: 0 for a_id in agents.keys()}

    best_agent_id = None
    best_criteria = None

    for agent_id, agent in agents.items():
        dist = euclidean_distance(agent.initial_location, warehouse.location)
        workload = current_workloads.get(agent_id, 0)
        criteria = (dist, workload, agent_id)

        if best_criteria is None or criteria < best_criteria:
            best_criteria = criteria
            best_agent_id = agent_id

    return best_agent_id


def dispatch_packages_to_agents(
    warehouses: Dict[str, Warehouse],
    agents: Dict[str, Agent],
    packages: List[Package]
) -> Dict[str, List[Package]]:
    """Dispatches a list of packages to the nearest agents based on Euclidean distance to warehouse.

    Args:
        warehouses: Mapping of warehouse ID to Warehouse object.
        agents: Mapping of agent ID to Agent object.
        packages: List of Package objects to be assigned.

    Returns:
        Dict[str, List[Package]]: Mapping of agent ID to their list of assigned packages.
    """
    # Initialize container for all registered agents
    assignments: Dict[str, List[Package]] = {agent_id: [] for agent_id in sorted(agents.keys())}
    workloads: Dict[str, int] = {agent_id: 0 for agent_id in agents.keys()}

    for package in packages:
        warehouse = warehouses[package.warehouse_id]
        chosen_agent_id = find_nearest_agent_for_warehouse(warehouse, agents, workloads)
        assignments[chosen_agent_id].append(package)
        workloads[chosen_agent_id] += 1

    return assignments
