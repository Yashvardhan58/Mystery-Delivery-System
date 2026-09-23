#!/usr/bin/env python3
"""Automated batch test runner for FastBox logistics simulator.

Validates the simulation engine across:
  - base_case.json
  - test_case_1.json through test_case_10.json
"""

import os
import glob
import sys
from simulator.parser import load_simulation_data
from simulator.engine import execute_simulation


def run_all_test_cases(data_dir: str = "data") -> bool:
    print("=" * 95)
    print("                 FASTBOX LOGISTICS SIMULATOR - BATCH TEST SUITE                 ")
    print("=" * 95)

    if not os.path.exists(data_dir):
        print(f"[ERROR] Data directory '{data_dir}' does not exist.")
        return False

    # Collect files
    test_files = []
    base_file = os.path.join(data_dir, "base_case.json")
    if os.path.exists(base_file):
        test_files.append(base_file)

    # Add test cases sorted numerically
    numbered_cases = glob.glob(os.path.join(data_dir, "test_case_*.json"))
    numbered_cases.sort(key=lambda x: int("".join(filter(str.isdigit, os.path.basename(x))) or 0))
    test_files.extend(numbered_cases)

    if not test_files:
        print("[ERROR] No test JSON files found in data directory.")
        return False

    print(f"Found {len(test_files)} test suite datasets to execute.\n")
    print(f"{'Test Case File':<20} | {'Wh':<4} | {'Ag':<4} | {'Pkgs':<6} | {'Delivered':<10} | {'Total Dist (km)':<16} | {'Best Agent':<10} | {'Status':<6}")
    print("-" * 95)

    all_passed = True

    for file_path in test_files:
        filename = os.path.basename(file_path)
        try:
            warehouses, agents, packages = load_simulation_data(file_path)
            report, steps = execute_simulation(warehouses, agents, packages)

            # Verification Assertions
            expected_pkgs = len(packages)
            delivered_pkgs = report.total_packages_delivered
            has_best_agent = report.best_agent is not None if expected_pkgs > 0 else True
            valid_distance = report.total_distance_all_agents >= 0.0

            passed = (delivered_pkgs == expected_pkgs) and has_best_agent and valid_distance

            status_str = "PASS" if passed else "FAIL"
            if not passed:
                all_passed = False

            print(
                f"{filename:<20} | {len(warehouses):<4} | {len(agents):<4} | "
                f"{expected_pkgs:<6} | {delivered_pkgs:<10} | "
                f"{report.total_distance_all_agents:<16.2f} | "
                f"{str(report.best_agent):<10} | {status_str:<6}"
            )

        except Exception as e:
            all_passed = False
            print(f"{filename:<20} | ERROR: {e}")

    print("=" * 95)
    if all_passed:
        print(">> ALL TEST SUITES PASSED PERFECTLY (100% Package Delivery & Integrity Verified) <<")
    else:
        print(">> ONE OR MORE TEST SUITES FAILED VALIDATION. <<")
    print("=" * 95)

    return all_passed


if __name__ == "__main__":
    success = run_all_test_cases()
    sys.exit(0 if success else 1)
