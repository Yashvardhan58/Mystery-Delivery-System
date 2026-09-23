"""Unit test suite for FastBox logistics simulator."""

import unittest
import math
from simulator.models import Warehouse, Agent, Package
from simulator.distance import euclidean_distance, calculate_delivery_trip_distance
from simulator.parser import parse_warehouses, parse_agents, parse_packages, load_simulation_data, DataParsingError
from simulator.dispatcher import find_nearest_agent_for_warehouse, dispatch_packages_to_agents
from simulator.engine import execute_simulation, SimulationEngine
from simulator.bonus import (
    render_ascii_map,
    render_ascii_routes,
    simulate_with_traffic_delays,
    simulate_with_dynamic_agent,
    export_top_performers_csv
)


class TestEuclideanDistance(unittest.TestCase):
    def test_basic_distance(self):
        # 3-4-5 triangle
        self.assertAlmostEqual(euclidean_distance((0, 0), (3, 4)), 5.0)

    def test_zero_distance(self):
        self.assertEqual(euclidean_distance((10, 20), (10, 20)), 0.0)

    def test_trip_legs(self):
        # Agent at (0,0), Warehouse at (0,3), Destination at (4,3)
        pickup_d, deliv_d, total_d = calculate_delivery_trip_distance((0, 0), (0, 3), (4, 3))
        self.assertAlmostEqual(pickup_d, 3.0)
        self.assertAlmostEqual(deliv_d, 4.0)
        self.assertAlmostEqual(total_d, 7.0)


class TestParser(unittest.TestCase):
    def test_parse_dict_and_list_format(self):
        dict_data = {
            "warehouses": {"W1": [0, 0]},
            "agents": {"A1": [5, 5]},
            "packages": [{"id": "P1", "warehouse": "W1", "destination": [10, 10]}]
        }
        w, a, p = load_simulation_data(dict_data)
        self.assertEqual(len(w), 1)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(p), 1)
        self.assertEqual(w["W1"].location, (0.0, 0.0))

        list_data = {
            "warehouses": [{"id": "W1", "location": [0, 0]}],
            "agents": [{"id": "A1", "location": [5, 5]}],
            "packages": [{"id": "P1", "warehouse_id": "W1", "destination": [10, 10]}]
        }
        w2, a2, p2 = load_simulation_data(list_data)
        self.assertEqual(len(w2), 1)
        self.assertEqual(len(a2), 1)
        self.assertEqual(len(p2), 1)

    def test_invalid_warehouse_reference(self):
        bad_data = {
            "warehouses": {"W1": [0, 0]},
            "agents": {"A1": [5, 5]},
            "packages": [{"id": "P1", "warehouse": "W_NON_EXISTENT", "destination": [10, 10]}]
        }
        with self.assertRaises(DataParsingError):
            load_simulation_data(bad_data)


class TestDispatcher(unittest.TestCase):
    def test_nearest_agent_assignment(self):
        w = {"W1": Warehouse("W1", (0, 0))}
        a = {
            "A1": Agent("A1", (5, 5)),    # dist = sqrt(50) = 7.07
            "A2": Agent("A2", (50, 50))  # dist = sqrt(5000) = 70.7
        }
        pkgs = [Package("P1", "W1", (10, 10))]
        assignments = dispatch_packages_to_agents(w, a, pkgs)
        self.assertEqual(len(assignments["A1"]), 1)
        self.assertEqual(len(assignments["A2"]), 0)
        self.assertEqual(assignments["A1"][0].id, "P1")


class TestSimulationEngine(unittest.TestCase):
    def test_base_case_simulation(self):
        warehouses, agents, packages = load_simulation_data("data/base_case.json")
        report, steps = execute_simulation(warehouses, agents, packages)

        # 5 packages total delivered
        self.assertEqual(report.total_packages_delivered, 5)
        self.assertEqual(len(steps), 5)
        self.assertIn(report.best_agent, ["A1", "A2", "A3"])

        # Check report dict keys
        rep_dict = report.to_dict()
        self.assertIn("A1", rep_dict)
        self.assertIn("A2", rep_dict)
        self.assertIn("A3", rep_dict)
        self.assertIn("best_agent", rep_dict)


class TestBonusFeatures(unittest.TestCase):
    def test_ascii_map_and_routes(self):
        w, a, p = load_simulation_data("data/base_case.json")
        rep, steps = execute_simulation(w, a, p)
        ascii_map = render_ascii_map(w, a, p)
        ascii_routes = render_ascii_routes(steps)
        self.assertIn("FastBox Network Map", ascii_map)
        self.assertIn("FASTBOX AGENT ROUTE EXECUTION LOG", ascii_routes)

    def test_traffic_delays(self):
        w, a, p = load_simulation_data("data/base_case.json")
        rep, steps = execute_simulation(w, a, p)
        delays = simulate_with_traffic_delays(steps)
        self.assertIn("A1", delays)
        self.assertGreater(delays["A1"].total_travel_time_minutes, 0)
        self.assertGreater(delays["A1"].total_delay_time_minutes, 0)

    def test_dynamic_agent(self):
        w, a, p = load_simulation_data("data/base_case.json")
        dyn_rep, dyn_steps = simulate_with_dynamic_agent(w, a, p, new_agent_id="A_NEW", join_after_package_count=2)
        self.assertEqual(dyn_rep.total_packages_delivered, 5)
        self.assertIn("A_NEW", dyn_rep.agent_reports)


if __name__ == "__main__":
    unittest.main()
