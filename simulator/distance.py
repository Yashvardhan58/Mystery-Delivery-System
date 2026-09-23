"""Euclidean distance and geometric calculation utilities for logistics simulation."""

import math
from typing import Sequence, Tuple
from .models import Coordinate


def euclidean_distance(p1: Sequence[float], p2: Sequence[float]) -> float:
    """Calculates the 2D Euclidean distance between two points: p1 and p2.

    Formula:
        d = sqrt((x2 - x1)^2 + (y2 - y1)^2)

    Args:
        p1: First coordinate sequence [x1, y1].
        p2: Second coordinate sequence [x2, y2].

    Returns:
        float: The precise Euclidean distance between the two points.

    Raises:
        ValueError: If either point does not have at least 2 coordinate dimensions.
    """
    if len(p1) < 2 or len(p2) < 2:
        raise ValueError(f"Invalid points provided: p1={p1}, p2={p2}. Must have 2 dimensions.")
    dx = float(p2[0]) - float(p1[0])
    dy = float(p2[1]) - float(p1[1])
    return math.hypot(dx, dy)


def calculate_delivery_trip_distance(
    agent_current_pos: Coordinate,
    warehouse_pos: Coordinate,
    destination_pos: Coordinate
) -> Tuple[float, float, float]:
    """Calculates the two legs of a single delivery trip and total trip distance.

    Leg 1: Agent Current Location -> Warehouse Location (Pickup)
    Leg 2: Warehouse Location -> Destination Location (Delivery)

    Args:
        agent_current_pos: Current (x, y) location of the agent.
        warehouse_pos: (x, y) location of the source warehouse.
        destination_pos: (x, y) destination of the package.

    Returns:
        Tuple of (pickup_distance, delivery_distance, total_trip_distance).
    """
    pickup_dist = euclidean_distance(agent_current_pos, warehouse_pos)
    delivery_dist = euclidean_distance(warehouse_pos, destination_pos)
    total_trip_dist = pickup_dist + delivery_dist
    return pickup_dist, delivery_dist, total_trip_dist
