"""Domain models and data structures for FastBox logistics simulator."""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional

# 2D Coordinate alias: [x, y]
Coordinate = Tuple[float, float]


@dataclass(frozen=True)
class Warehouse:
    """Represents a distribution warehouse location."""
    id: str
    location: Coordinate

    def __post_init__(self) -> None:
        if len(self.location) != 2:
            raise ValueError(f"Warehouse '{self.id}' location must be a 2D coordinate [x, y].")


@dataclass
class Agent:
    """Represents a delivery agent stationed in the logistics network."""
    id: str
    location: Coordinate
    initial_location: Coordinate = field(init=False)
    packages_delivered: int = 0
    total_distance: float = 0.0

    def __post_init__(self) -> None:
        if len(self.location) != 2:
            raise ValueError(f"Agent '{self.id}' location must be a 2D coordinate [x, y].")
        self.initial_location = (float(self.location[0]), float(self.location[1]))
        self.location = (float(self.location[0]), float(self.location[1]))

    @property
    def efficiency(self) -> float:
        """Computes efficiency as total distance divided by packages delivered.
        
        Lower value represents higher efficiency (less distance per delivery).
        Returns 0.0 if no packages were delivered.
        """
        if self.packages_delivered == 0:
            return 0.0
        return round(self.total_distance / self.packages_delivered, 2)


@dataclass(frozen=True)
class Package:
    """Represents a package to be picked up from a warehouse and delivered to a destination."""
    id: str
    warehouse_id: str
    destination: Coordinate

    def __post_init__(self) -> None:
        if len(self.destination) != 2:
            raise ValueError(f"Package '{self.id}' destination must be a 2D coordinate [x, y].")


@dataclass
class DeliveryStep:
    """Detailed log record of an individual delivery movement."""
    package_id: str
    agent_id: str
    from_location: Coordinate
    to_warehouse_id: str
    warehouse_location: Coordinate
    destination_location: Coordinate
    pickup_distance: float
    delivery_distance: float
    step_total_distance: float
    cumulative_distance_after_step: float


@dataclass
class AgentReport:
    """Summary metrics for an individual delivery agent."""
    packages_delivered: int
    total_distance: float
    efficiency: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "packages_delivered": self.packages_delivered,
            "total_distance": round(self.total_distance, 2),
            "efficiency": round(self.efficiency, 2),
        }


@dataclass
class SimulationReport:
    """Complete simulation report including all agents and the best performer."""
    agent_reports: Dict[str, AgentReport]
    best_agent: Optional[str]
    total_packages_delivered: int = 0
    total_distance_all_agents: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Converts report to exact JSON format specified in assignment schema."""
        output: Dict[str, Any] = {}
        for agent_id, report in sorted(self.agent_reports.items()):
            output[agent_id] = report.to_dict()
        output["best_agent"] = self.best_agent
        return output
