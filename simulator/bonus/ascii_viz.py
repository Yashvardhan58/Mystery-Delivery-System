"""ASCII route and 2D spatial grid visualizer for FastBox logistics network."""

from typing import Dict, List, Tuple
from ..models import Warehouse, Agent, Package, DeliveryStep


def render_ascii_map(
    warehouses: Dict[str, Warehouse],
    agents: Dict[str, Agent],
    packages: List[Package],
    grid_width: int = 40,
    grid_height: int = 15
) -> str:
    """Renders a scaled 2D ASCII grid displaying Warehouses, Agents, and Package Destinations.

    Legend:
      W = Warehouse
      A = Agent Starting Location
      P = Package Destination
      . = Empty space
    """
    # Determine coordinate bounds
    all_x = [w.location[0] for w in warehouses.values()] + \
            [a.initial_location[0] for a in agents.values()] + \
            [p.destination[0] for p in packages]
    all_y = [w.location[1] for w in warehouses.values()] + \
            [a.initial_location[1] for a in agents.values()] + \
            [p.destination[1] for p in packages]

    min_x, max_x = (min(all_x), max(all_x)) if all_x else (0, 100)
    min_y, max_y = (min(all_y), max(all_y)) if all_y else (0, 100)

    # Avoid zero division
    span_x = max(1.0, max_x - min_x)
    span_y = max(1.0, max_y - min_y)

    def to_grid(x: float, y: float) -> Tuple[int, int]:
        gx = int(round((x - min_x) / span_x * (grid_width - 1)))
        gy = int(round((y - min_y) / span_y * (grid_height - 1)))
        # Invert y for terminal rendering (top is max_y)
        gy_inverted = (grid_height - 1) - gy
        return gx, gy_inverted

    # Initialize empty grid
    grid = [["." for _ in range(grid_width)] for _ in range(grid_height)]

    # Plot Package Destinations
    for pkg in packages:
        gx, gy = to_grid(*pkg.destination)
        grid[gy][gx] = "P"

    # Plot Warehouses
    for w in warehouses.values():
        gx, gy = to_grid(*w.location)
        grid[gy][gx] = "W"

    # Plot Agents (highest priority on map)
    for a in agents.values():
        gx, gy = to_grid(*a.initial_location)
        grid[gy][gx] = "A"

    lines = []
    lines.append("=" * (grid_width + 4))
    lines.append(f"  FastBox Network Map (Bounds: [{min_x:.0f},{min_y:.0f}] to [{max_x:.0f},{max_y:.0f}])")
    lines.append("=" * (grid_width + 4))
    lines.append(f"  ^ Y (max: {max_y:.0f})")

    for r_idx, row in enumerate(grid):
        lines.append(f"  |{''.join(row)}|")

    lines.append(f"  +{'=' * grid_width}+> X (max: {max_x:.0f})")
    lines.append("  Legend: [W] Warehouse  |  [A] Agent Start  |  [P] Package Dest  |  [.] Empty")
    lines.append("=" * (grid_width + 4))

    return "\n".join(lines)


def render_ascii_routes(delivery_steps: List[DeliveryStep]) -> str:
    """Renders a chronological step-by-step route and trip diagram in ASCII."""
    if not delivery_steps:
        return "No delivery steps recorded."

    lines = [
        "================================================================================",
        "                       FASTBOX AGENT ROUTE EXECUTION LOG                        ",
        "================================================================================",
    ]

    # Group by agent
    by_agent: Dict[str, List[DeliveryStep]] = {}
    for step in delivery_steps:
        by_agent.setdefault(step.agent_id, []).append(step)

    for agent_id, steps in sorted(by_agent.items()):
        lines.append(f"\n[Agent: {agent_id}] - Total Trips: {len(steps)}")
        lines.append("  " + "-" * 74)
        for i, s in enumerate(steps, 1):
            from_str = f"({s.from_location[0]:.0f},{s.from_location[1]:.0f})"
            wh_str = f"{s.to_warehouse_id}({s.warehouse_location[0]:.0f},{s.warehouse_location[1]:.0f})"
            dest_str = f"Dest[{s.package_id}]({s.destination_location[0]:.0f},{s.destination_location[1]:.0f})"
            
            lines.append(
                f"  Trip #{i}: {from_str} --[{s.pickup_distance:.1f} km]--> {wh_str} "
                f"--[{s.delivery_distance:.1f} km]--> {dest_str} | Step: {s.step_total_distance:.2f} km (Cumul: {s.cumulative_distance_after_step:.2f} km)"
            )
        lines.append("  " + "-" * 74)

    lines.append("================================================================================")
    return "\n".join(lines)
