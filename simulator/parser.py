"""JSON input parser and schema normalizer for FastBox logistics simulation."""

import json
import os
from typing import Dict, List, Tuple, Any, Union
from .models import Warehouse, Agent, Package, Coordinate


class DataParsingError(Exception):
    """Raised when the input JSON data is malformed or violates schema expectations."""
    pass


def _parse_coordinate(val: Any, field_name: str) -> Coordinate:
    """Validates and converts coordinate inputs into a (float, float) tuple."""
    if not isinstance(val, (list, tuple)) or len(val) != 2:
        raise DataParsingError(f"Field '{field_name}' must be a 2D coordinate [x, y], got {val}")
    try:
        x = float(val[0])
        y = float(val[1])
        return (x, y)
    except (ValueError, TypeError) as e:
        raise DataParsingError(f"Invalid coordinate numbers in '{field_name}': {val}") from e


def parse_warehouses(raw_warehouses: Any) -> Dict[str, Warehouse]:
    """Parses warehouses from either a dictionary format or a list of objects.

    Supported Formats:
      - Dict: {"W1": [0, 0], "W2": [50, 75]}
      - List: [{"id": "W1", "location": [0, 0]}, {"id": "W2", "location": [50, 75]}]
    """
    warehouses: Dict[str, Warehouse] = {}
    if isinstance(raw_warehouses, dict):
        for w_id, loc in raw_warehouses.items():
            coord = _parse_coordinate(loc, f"warehouse.{w_id}")
            warehouses[str(w_id)] = Warehouse(id=str(w_id), location=coord)
    elif isinstance(raw_warehouses, list):
        for idx, item in enumerate(raw_warehouses):
            if not isinstance(item, dict) or "id" not in item:
                raise DataParsingError(f"Warehouse at index {idx} missing 'id' key: {item}")
            w_id = str(item["id"])
            loc_val = item.get("location") or item.get("coordinates") or item.get("pos")
            if loc_val is None:
                raise DataParsingError(f"Warehouse '{w_id}' missing 'location' coordinate: {item}")
            coord = _parse_coordinate(loc_val, f"warehouse.{w_id}")
            warehouses[w_id] = Warehouse(id=w_id, location=coord)
    else:
        raise DataParsingError(f"'warehouses' must be a dictionary or list, got {type(raw_warehouses)}")

    if not warehouses:
        raise DataParsingError("Input dataset must contain at least one warehouse.")
    return warehouses


def parse_agents(raw_agents: Any) -> Dict[str, Agent]:
    """Parses agents from either a dictionary format or a list of objects.

    Supported Formats:
      - Dict: {"A1": [5, 5], "A2": [60, 60]}
      - List: [{"id": "A1", "location": [5, 5]}, {"id": "A2", "location": [60, 60]}]
    """
    agents: Dict[str, Agent] = {}
    if isinstance(raw_agents, dict):
        for a_id, loc in raw_agents.items():
            coord = _parse_coordinate(loc, f"agent.{a_id}")
            agents[str(a_id)] = Agent(id=str(a_id), location=coord)
    elif isinstance(raw_agents, list):
        for idx, item in enumerate(raw_agents):
            if not isinstance(item, dict) or "id" not in item:
                raise DataParsingError(f"Agent at index {idx} missing 'id' key: {item}")
            a_id = str(item["id"])
            loc_val = item.get("location") or item.get("coordinates") or item.get("pos")
            if loc_val is None:
                raise DataParsingError(f"Agent '{a_id}' missing 'location' coordinate: {item}")
            coord = _parse_coordinate(loc_val, f"agent.{a_id}")
            agents[a_id] = Agent(id=a_id, location=coord)
    else:
        raise DataParsingError(f"'agents' must be a dictionary or list, got {type(raw_agents)}")

    if not agents:
        raise DataParsingError("Input dataset must contain at least one agent.")
    return agents


def parse_packages(raw_packages: Any, valid_warehouse_ids: set) -> List[Package]:
    """Parses packages list and validates destination coordinates and warehouse references."""
    if not isinstance(raw_packages, list):
        raise DataParsingError(f"'packages' must be a list of package items, got {type(raw_packages)}")

    packages: List[Package] = []
    seen_ids = set()

    for idx, item in enumerate(raw_packages):
        if not isinstance(item, dict) or "id" not in item:
            raise DataParsingError(f"Package at index {idx} missing 'id' key: {item}")
        p_id = str(item["id"])
        if p_id in seen_ids:
            raise DataParsingError(f"Duplicate package ID detected: '{p_id}'")
        seen_ids.add(p_id)

        # Handle warehouse key variants: 'warehouse' or 'warehouse_id'
        w_id = item.get("warehouse") or item.get("warehouse_id")
        if not w_id:
            raise DataParsingError(f"Package '{p_id}' missing warehouse identifier: {item}")
        w_id_str = str(w_id)
        if w_id_str not in valid_warehouse_ids:
            raise DataParsingError(
                f"Package '{p_id}' references unknown warehouse '{w_id_str}'. "
                f"Available warehouses: {sorted(list(valid_warehouse_ids))}"
            )

        dest_val = item.get("destination") or item.get("dest")
        if dest_val is None:
            raise DataParsingError(f"Package '{p_id}' missing 'destination' coordinate: {item}")
        dest_coord = _parse_coordinate(dest_val, f"package.{p_id}.destination")

        packages.append(Package(id=p_id, warehouse_id=w_id_str, destination=dest_coord))

    return packages


def load_simulation_data(file_path_or_content: Union[str, Dict[str, Any]]) -> Tuple[Dict[str, Warehouse], Dict[str, Agent], List[Package]]:
    """Loads and validates simulation data from a JSON file path or raw dictionary.

    Args:
        file_path_or_content: Filepath string or pre-loaded dictionary.

    Returns:
        Tuple of (warehouses_dict, agents_dict, packages_list).
    """
    if isinstance(file_path_or_content, str):
        if not os.path.exists(file_path_or_content):
            raise FileNotFoundError(f"Simulation input file not found: '{file_path_or_content}'")
        with open(file_path_or_content, "r", encoding="utf-8") as f:
            try:
                raw_data = json.load(f)
            except json.JSONDecodeError as e:
                raise DataParsingError(f"Invalid JSON syntax in '{file_path_or_content}': {e}") from e
    elif isinstance(file_path_or_content, dict):
        raw_data = file_path_or_content
    else:
        raise DataParsingError(f"Expected file path string or dict, got {type(file_path_or_content)}")

    if not isinstance(raw_data, dict):
        raise DataParsingError("Root JSON structure must be an object/dict containing 'warehouses', 'agents', and 'packages'.")

    if "warehouses" not in raw_data:
        raise DataParsingError("Missing required key 'warehouses' in input JSON.")
    if "agents" not in raw_data:
        raise DataParsingError("Missing required key 'agents' in input JSON.")
    if "packages" not in raw_data:
        raise DataParsingError("Missing required key 'packages' in input JSON.")

    warehouses = parse_warehouses(raw_data["warehouses"])
    agents = parse_agents(raw_data["agents"])
    packages = parse_packages(raw_data["packages"], set(warehouses.keys()))

    return warehouses, agents, packages
