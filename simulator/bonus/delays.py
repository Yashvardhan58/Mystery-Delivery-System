"""Random delivery delays and stochastic traffic simulation module."""

import random
from dataclasses import dataclass
from typing import Dict, List
from ..models import DeliveryStep


@dataclass
class DelayReport:
    """Summary of simulated traffic delays and operational delivery durations."""
    agent_id: str
    total_travel_time_minutes: float
    total_delay_time_minutes: float
    total_operating_time_minutes: float
    average_delay_per_delivery_minutes: float
    delays_by_package: Dict[str, float]


def simulate_with_traffic_delays(
    delivery_steps: List[DeliveryStep],
    base_speed_kmh: float = 40.0,
    random_seed: int = 42
) -> Dict[str, DelayReport]:
    """Simulates delivery times with stochastic traffic conditions, loading delays, and weather.

    Physics & Operational Delay Model:
      - Ideal Travel Time = (Distance / Base Speed) * 60 minutes
      - Loading Delay (Warehouse pickup) = Uniform(3.0, 10.0) minutes
      - Traffic Congestion Delay = Distance * Uniform(0.05, 0.20) minutes
      - Customer Delivery Handoff = Uniform(2.0, 5.0) minutes

    Args:
        delivery_steps: Recorded delivery movements from simulation.
        base_speed_kmh: Average agent transit speed in kilometers per hour.
        random_seed: Seed for reproducible stochastic simulation.

    Returns:
        Dict[str, DelayReport]: Per-agent delay and operational duration analysis.
    """
    rng = random.Random(random_seed)
    by_agent: Dict[str, List[DeliveryStep]] = {}
    for step in delivery_steps:
        by_agent.setdefault(step.agent_id, []).append(step)

    reports: Dict[str, DelayReport] = {}

    for agent_id, steps in sorted(by_agent.items()):
        total_travel_min = 0.0
        total_delay_min = 0.0
        package_delays: Dict[str, float] = {}

        for step in steps:
            # Ideal transit duration
            pure_travel_min = (step.step_total_distance / base_speed_kmh) * 60.0
            total_travel_min += pure_travel_min

            # Stochastic delay factors
            loading_delay = rng.uniform(3.0, 10.0)
            traffic_delay = step.step_total_distance * rng.uniform(0.05, 0.20)
            handoff_delay = rng.uniform(2.0, 5.0)

            step_delay = loading_delay + traffic_delay + handoff_delay
            total_delay_min += step_delay
            package_delays[step.package_id] = round(step_delay, 2)

        total_op_time = total_travel_min + total_delay_min
        avg_delay = (total_delay_min / len(steps)) if steps else 0.0

        reports[agent_id] = DelayReport(
            agent_id=agent_id,
            total_travel_time_minutes=round(total_travel_min, 2),
            total_delay_time_minutes=round(total_delay_min, 2),
            total_operating_time_minutes=round(total_op_time, 2),
            average_delay_per_delivery_minutes=round(avg_delay, 2),
            delays_by_package=package_delays,
        )

    return reports
