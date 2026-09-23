"""CSV Exporter for FastBox logistics simulation results and top performers."""

import csv
from typing import List, Optional
from ..models import SimulationReport, DeliveryStep


def export_top_performers_csv(
    report: SimulationReport,
    output_path: str = "top_performers.csv"
) -> str:
    """Exports agent performance rankings and efficiency metrics to a CSV file.

    Columns:
      - Rank: 1-indexed rank based on efficiency (lower is better)
      - Agent_ID: Unique agent identifier
      - Packages_Delivered: Count of completed deliveries
      - Total_Distance_KM: Total travel distance in km
      - Efficiency_Score: Distance per delivery (lower = better)
      - Is_Best_Agent: Flag indicating the top performer

    Args:
        report: SimulationReport object.
        output_path: Target CSV file path.

    Returns:
        str: Written CSV path.
    """
    # Sort agents by efficiency
    agent_entries = []
    for a_id, rep in report.agent_reports.items():
        if rep.packages_delivered > 0:
            agent_entries.append((rep.efficiency, -rep.packages_delivered, rep.total_distance, a_id, rep))
        else:
            # Idle agents at bottom
            agent_entries.append((float('inf'), 0, rep.total_distance, a_id, rep))

    agent_entries.sort()

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Rank",
            "Agent_ID",
            "Packages_Delivered",
            "Total_Distance_KM",
            "Efficiency_Score",
            "Is_Best_Agent"
        ])

        for rank, item in enumerate(agent_entries, 1):
            a_id = item[3]
            rep = item[4]
            is_best = "YES (Top Performer)" if a_id == report.best_agent else "NO"
            writer.writerow([
                rank,
                a_id,
                rep.packages_delivered,
                f"{rep.total_distance:.2f}",
                f"{rep.efficiency:.2f}" if rep.packages_delivered > 0 else "N/A",
                is_best
            ])

    return output_path


def export_delivery_logs_csv(
    delivery_steps: List[DeliveryStep],
    output_path: str = "delivery_logs.csv"
) -> str:
    """Exports step-by-step movement logs for auditing."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Step_Number",
            "Agent_ID",
            "Package_ID",
            "Start_Pos",
            "Warehouse_ID",
            "Warehouse_Pos",
            "Pickup_Dist_KM",
            "Destination_Pos",
            "Delivery_Dist_KM",
            "Step_Total_Dist_KM",
            "Cumulative_Dist_KM"
        ])

        for idx, s in enumerate(delivery_steps, 1):
            writer.writerow([
                idx,
                s.agent_id,
                s.package_id,
                f"({s.from_location[0]:.1f}, {s.from_location[1]:.1f})",
                s.to_warehouse_id,
                f"({s.warehouse_location[0]:.1f}, {s.warehouse_location[1]:.1f})",
                f"{s.pickup_distance:.2f}",
                f"({s.destination_location[0]:.1f}, {s.destination_location[1]:.1f})",
                f"{s.delivery_distance:.2f}",
                f"{s.step_total_distance:.2f}",
                f"{s.cumulative_distance_after_step:.2f}"
            ])

    return output_path
