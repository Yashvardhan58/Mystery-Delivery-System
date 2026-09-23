#!/usr/bin/env python3
"""FastBox Logistics Simulation - Main CLI Entrypoint.

Usage Examples:
    python main.py
    python main.py --input data/test_case_1.json
    python main.py --input data/base_case.json --all-bonus
    python main.py -i data/test_case_2.json -v --csv
"""

import argparse
import sys
import os
import json
from simulator.parser import load_simulation_data, DataParsingError
from simulator.engine import execute_simulation, save_report
from simulator.bonus import (
    render_ascii_map,
    render_ascii_routes,
    simulate_with_traffic_delays,
    simulate_with_dynamic_agent,
    export_top_performers_csv,
    export_delivery_logs_csv,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FastBox Logistics Simulator: Multi-Warehouse Delivery & Agent Efficiency Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input data/base_case.json
  python main.py -i data/test_case_1.json --all-bonus
  python main.py -i data/test_case_3.json --visualize --csv
        """
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        default="data/base_case.json",
        help="Path to the simulation input JSON dataset (default: data/base_case.json)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="report.json",
        help="Path to save the output JSON report (default: report.json)"
    )
    parser.add_argument(
        "-v", "--visualize",
        action="store_true",
        help="Render 2D ASCII network map and step-by-step agent route diagrams."
    )
    parser.add_argument(
        "-d", "--delays",
        action="store_true",
        help="Simulate stochastic delivery and traffic delays."
    )
    parser.add_argument(
        "--dynamic-agent",
        action="store_true",
        help="Simulate dynamic mid-day agent arrival and workload re-balancing."
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Export top performer rankings to 'top_performers.csv' and audit logs to 'delivery_logs.csv'."
    )
    parser.add_argument(
        "--all-bonus",
        action="store_true",
        help="Enable all 4 bonus extensions simultaneously."
    )
    return parser.parse_args()


def print_banner() -> None:
    print("=" * 80)
    print("                    FASTBOX LOGISTICS SIMULATION ENGINE                    ")
    print("=" * 80)


def main() -> int:
    args = parse_arguments()
    print_banner()

    # Handle --all-bonus flag
    visualize = args.visualize or args.all_bonus
    delays = args.delays or args.all_bonus
    dynamic_agent = args.dynamic_agent or args.all_bonus
    export_csv = args.csv or args.all_bonus

    # 1. Load and Parse Input Dataset
    print(f"[*] Loading simulation input dataset: '{args.input}'")
    try:
        warehouses, agents, packages = load_simulation_data(args.input)
    except (FileNotFoundError, DataParsingError) as e:
        print(f"[ERROR] Failed to load data: {e}", file=sys.stderr)
        return 1

    print(f"    - Warehouses: {len(warehouses)} ({', '.join(sorted(warehouses.keys()))})")
    print(f"    - Agents:     {len(agents)} ({', '.join(sorted(agents.keys()))})")
    print(f"    - Packages:   {len(packages)}")
    print("-" * 80)

    # 2. Execute Primary Simulation
    print("[*] Running core delivery simulation and distance optimization...")
    report, delivery_steps = execute_simulation(warehouses, agents, packages)

    # 3. Save Report
    save_report(report, args.output)
    print(f"[+] Simulation report generated and saved to '{args.output}'")
    print("-" * 80)

    # 4. Display Formatted Results Summary
    print("                         SIMULATION RESULTS SUMMARY                         ")
    print("-" * 80)
    print(f"{'Agent ID':<10} | {'Packages Delivered':<20} | {'Total Distance (km)':<20} | {'Efficiency (km/pkg)':<20}")
    print("-" * 80)
    for agent_id, a_rep in sorted(report.agent_reports.items()):
        eff_str = f"{a_rep.efficiency:.2f}" if a_rep.packages_delivered > 0 else "N/A"
        print(f"{agent_id:<10} | {a_rep.packages_delivered:<20} | {a_rep.total_distance:<20.2f} | {eff_str:<20}")
    print("-" * 80)
    print(f"[BEST AGENT] Top Performer (Best Efficiency): {report.best_agent}")
    print(f"[TOTAL PKGS] Packages Delivered:               {report.total_packages_delivered}/{len(packages)}")
    print(f"[TOTAL DIST] Fleet Travel Distance:            {report.total_distance_all_agents:.2f} km")
    print("=" * 80)

    # 5. Bonus: ASCII Map & Route Visualization
    if visualize:
        print("\n" + "=" * 80)
        print("                    BONUS: 2D ASCII NETWORK MAP & ROUTES                    ")
        print("=" * 80)
        print(render_ascii_map(warehouses, agents, packages))
        print("\n" + render_ascii_routes(delivery_steps))

    # 6. Bonus: Stochastic Delays & Traffic Analysis
    if delays:
        print("\n" + "=" * 80)
        print("                BONUS: STOCHASTIC TRAFFIC & HANDLING DELAYS                 ")
        print("=" * 80)
        delay_reports = simulate_with_traffic_delays(delivery_steps)
        print(f"{'Agent ID':<10} | {'Travel Time (min)':<18} | {'Delay Time (min)':<18} | {'Total Time (min)':<18} | {'Avg Delay/Trip':<15}")
        print("-" * 80)
        for a_id, d_rep in sorted(delay_reports.items()):
            print(
                f"{a_id:<10} | {d_rep.total_travel_time_minutes:<18.2f} | "
                f"{d_rep.total_delay_time_minutes:<18.2f} | "
                f"{d_rep.total_operating_time_minutes:<18.2f} | "
                f"{d_rep.average_delay_per_delivery_minutes:<15.2f}"
            )
        print("=" * 80)

    # 7. Bonus: Dynamic Mid-Day Agent Arrival
    if dynamic_agent:
        print("\n" + "=" * 80)
        print("                BONUS: DYNAMIC MID-DAY AGENT RE-BALANCING                   ")
        print("=" * 80)
        # Re-load fresh data for dynamic scenario
        w_dyn, a_dyn, p_dyn = load_simulation_data(args.input)
        dyn_report, dyn_steps = simulate_with_dynamic_agent(
            w_dyn, a_dyn, p_dyn, new_agent_id="A_DYNAMIC", new_agent_location=(50.0, 50.0)
        )
        print(f"[*] New Agent 'A_DYNAMIC' joined mid-day at location (50.0, 50.0).")
        print(f"    - Baseline Fleet Distance:        {report.total_distance_all_agents:.2f} km")
        print(f"    - Dynamic Fleet Distance:         {dyn_report.total_distance_all_agents:.2f} km")
        delta = report.total_distance_all_agents - dyn_report.total_distance_all_agents
        print(f"    - Network Efficiency Impact:      {delta:+.2f} km ({'Improvement' if delta > 0 else 'Workload Distributed'})")
        print(f"    - Post-Arrival Best Agent:        {dyn_report.best_agent}")
        print("=" * 80)

    # 8. Bonus: CSV Exporter
    if export_csv:
        print("\n" + "=" * 80)
        print("                        BONUS: CSV METRICS EXPORT                           ")
        print("=" * 80)
        top_csv = export_top_performers_csv(report, "top_performers.csv")
        log_csv = export_delivery_logs_csv(delivery_steps, "delivery_logs.csv")
        print(f"[+] Exported top performers summary to '{top_csv}'")
        print(f"[+] Exported step-by-step audit logs to  '{log_csv}'")
        print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
