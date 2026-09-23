# 📦 FastBox Mystery Delivery System — Logistics Simulator

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-pep8-green.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

A modular, production-ready logistics simulation engine developed for **FastBox**. The system models multi-warehouse operations, nearest-agent dispatching via Euclidean geometry, real-world delivery simulation, operational efficiency scoring, and comprehensive reporting.

---

## 📑 Table of Contents
- [Architecture & Design](#-architecture--design)
- [Explicitly Documented Engineering Assumptions](#-explicitly-documented-engineering-assumptions)
- [Project Directory Structure](#-project-directory-structure)
- [Prerequisites & Installation](#-prerequisites--installation)
- [Usage & CLI Options](#-usage--cli-options)
- [Automated Verification & Test Cases](#-automated-verification--test-cases)
- [Bonus Extensions](#-bonus-extensions)
- [Unit Testing](#-unit-testing)
- [Output Format](#-output-format)

---

## 🏛 Architecture & Design

The simulation is built using clean, modular domain layers following SOLID principles:

```
┌─────────────────────────────────────────────────────────────┐
│                       CLI / Main Entry                      │
│                    (main.py / test_runner.py)               │
└──────────────────────────────┬──────────────────────────────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       ▼                       ▼                        ▼
┌──────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ JSON Parser  │ ───► │ Dispatch Engine │ ───► │Simulation Engine│
│ (parser.py)  │      │ (dispatcher.py) │      │   (engine.py)   │
└──────────────┘      └─────────────────┘      └────────┬────────┘
                                                        │
                      ┌─────────────────────────────────┼────────────────────────┐
                      ▼                                 ▼                        ▼
             ┌─────────────────┐               ┌─────────────────┐      ┌─────────────────┐
             │ ASCII Visualizer│               │ Traffic Delays  │      │  CSV Exporter   │
             │ (ascii_viz.py)  │               │   (delays.py)   │      │(csv_exporter.py)│
             └─────────────────┘               └─────────────────┘      └─────────────────┘
```

---

## 🔍 Explicitly Documented Engineering Assumptions

Per the assignment brief and engineering guidelines, the following explicit assumptions and edge-case handling rules were implemented:

1. **Dual Schema Normalization**:
   - The parser seamlessly handles both standard assignment JSON formats:
     - **Dictionary Schema** (e.g. `test_case_*.json`): `{"warehouses": {"W1": [x, y]}, "agents": {"A1": [x, y]}, "packages": [...]}`
     - **List Schema** (e.g. `base_case.json`): `{"warehouses": [{"id": "W1", "location": [x, y]}], ...}`
   - Supports key variants: `warehouse` vs. `warehouse_id`, `destination` vs. `dest`.

2. **Nearest-Agent Dispatch Logic**:
   - Each package is assigned to an agent by minimizing the **Euclidean Distance** from the agent's initial location $A(x_1, y_1)$ to the package's pickup warehouse $W(x_2, y_2)$:
     $$\text{Distance} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$
   - **Tie-Breaking Hierarchy**:
     1. Lowest Euclidean distance to warehouse.
     2. Least loaded agent (fewer assigned packages for balanced workload).
     3. Lexicographical Agent ID (`"A1"` before `"A2"`).

3. **Delivery Simulation Movement Model**:
   - Agents fulfill assigned packages sequentially.
   - For each delivery:
     $$\text{Agent Current Position} \xrightarrow{\text{Pickup Leg}} \text{Warehouse Position} \xrightarrow{\text{Delivery Leg}} \text{Package Destination}$$
   - After delivery handoff, the agent's new position becomes the package destination coordinate.
   - Total trip distance accumulates precisely across all legs.

4. **Operational Efficiency & Best Agent Selection**:
   - $\text{Efficiency} = \frac{\text{Total Distance (km)}}{\text{Packages Delivered}}$
   - Lower numerical value indicates superior efficiency (less transit required per delivery).
   - **Best Agent**: Chosen as the agent with the lowest non-zero efficiency score. Ties are broken by the agent who delivered more packages, followed by lowest total distance.

---

## 📁 Project Directory Structure

```
Mystery-Delivery-System/
├── simulator/                      # Core domain package
│   ├── __init__.py                 # Package declaration
│   ├── models.py                   # Dataclasses: Warehouse, Agent, Package, DeliveryStep
│   ├── distance.py                 # Euclidean math and trip leg calculations
│   ├── parser.py                   # Robust dual-schema JSON parser & validator
│   ├── dispatcher.py               # Nearest-agent dispatch & multi-tier tie-breaking
│   ├── engine.py                   # Delivery simulator & JSON report generator
│   └── bonus/                      # Bonus feature modules
│       ├── __init__.py
│       ├── ascii_viz.py            # 2D ASCII spatial map & step route renderer
│       ├── delays.py               # Stochastic traffic, loading & handoff simulator
│       ├── dynamic_agent.py        # Mid-day dynamic agent arrival & rebalancing
│       └── csv_exporter.py         # Top performer & trip audit CSV exporter
├── data/                           # Dataset repository
│   ├── base_case.json              # Baseline example dataset
│   ├── test_case_1.json            # Test Case 1 (5 warehouses, 4 agents, 12 packages)
│   ├── ...
│   └── test_case_10.json           # Test Case 10 (5 warehouses, 4 agents, 11 packages)
├── tests/                          # Automated test suite
│   ├── __init__.py
│   └── test_simulator.py           # Unit tests (math, parsing, dispatch, simulation)
├── main.py                         # Unified CLI entrypoint with feature flags
├── test_runner.py                  # Batch verification script across all 11 test suites
├── report.json                     # Generated simulation report
├── top_performers.csv              # Exported rankings CSV
├── delivery_logs.csv               # Exported delivery audit log CSV
├── .gitignore                      # Python gitignore configuration
└── README.md                       # Comprehensive documentation
```

---

## ⚡ Prerequisites & Installation

- **Python**: Version `3.8` or higher (Pure standard library implementation, no mandatory external dependencies).
- **Clone Repository**:
  ```bash
  git clone https://github.com/Yashvardhan58/Mystery-Delivery-System.git
  cd Mystery-Delivery-System
  ```

---

## 🚀 Usage & CLI Options

### 1. Basic Simulation (Standard Run)
```bash
python main.py
```
*Runs the simulation on `data/base_case.json` and outputs `report.json`.*

### 2. Custom Input & Output Path
```bash
python main.py --input data/test_case_1.json --output my_report.json
```

### 3. Run with All 4 Bonus Extensions
```bash
python main.py --input data/base_case.json --all-bonus
```

### 4. CLI Flags Reference
| Flag | Short | Description |
|---|---|---|
| `--input <path>` | `-i` | Input JSON dataset path (default: `data/base_case.json`) |
| `--output <path>` | `-o` | Output JSON report path (default: `report.json`) |
| `--visualize` | `-v` | Render 2D ASCII network map and route traces |
| `--delays` | `-d` | Simulate stochastic traffic congestion & handling delays |
| `--dynamic-agent` | | Simulate mid-day arrival of new agent and route rebalancing |
| `--csv` | | Export `top_performers.csv` and `delivery_logs.csv` |
| `--all-bonus` | | Enable all 4 bonus features simultaneously |

---

## 🧪 Automated Verification & Test Cases

Execute the automated batch test runner across all **11 test suites**:

```bash
python test_runner.py
```

### Batch Test Results Matrix:
| Test Case File | Warehouses | Agents | Packages | Delivered | Total Dist (km) | Best Agent | Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `base_case.json` | 3 | 3 | 5 | 5 | 214.56 | A3 | **PASS** |
| `test_case_1.json` | 5 | 4 | 12 | 12 | 288.18 | A1 | **PASS** |
| `test_case_2.json` | 3 | 3 | 10 | 10 | 534.05 | A1 | **PASS** |
| `test_case_3.json` | 4 | 4 | 6 | 6 | 159.53 | A3 | **PASS** |
| `test_case_4.json` | 5 | 5 | 12 | 12 | 306.99 | A3 | **PASS** |
| `test_case_5.json` | 5 | 5 | 10 | 10 | 301.59 | A3 | **PASS** |
| `test_case_6.json` | 4 | 4 | 9 | 9 | 202.93 | A3 | **PASS** |
| `test_case_7.json` | 4 | 4 | 10 | 10 | 204.38 | A3 | **PASS** |
| `test_case_8.json` | 5 | 4 | 11 | 11 | 359.59 | A1 | **PASS** |
| `test_case_9.json` | 3 | 4 | 8 | 8 | 190.06 | A3 | **PASS** |
| `test_case_10.json` | 5 | 4 | 11 | 11 | 267.54 | A4 | **PASS** |

*All 11 test suites achieve 100% package delivery verification.*

---

## 🌟 Bonus Extensions

### 1. 🗺️ 2D ASCII Grid & Route Visualizer (`simulator/bonus/ascii_viz.py`)
Renders a scaled 2D spatial map of the logistics network and step-by-step route logs:
```
============================================
  FastBox Network Map (Bounds: [0,0] to [105,90])
============================================
  ^ Y (max: 90)
  |..........................P.............|
  |...............P...W....................|
  |......................A.................|
  |...........P............................|
  |...................................A....|
  |.....................................W..|
  |.......................................P|
  |....P...................................|
  |..A.....................................|
  |W.......................................|
  +========================================+> X (max: 105)
  Legend: [W] Warehouse  |  [A] Agent Start  |  [P] Package Dest  |  [.] Empty
```

### 2. ⏱️ Stochastic Traffic & Handling Delays (`simulator/bonus/delays.py`)
Models real-world factors:
- Warehouse loading times: `Uniform(3.0, 10.0)` minutes
- Transit traffic variance: `Distance * Uniform(0.05, 0.20)` minutes
- Customer delivery handoff: `Uniform(2.0, 5.0)` minutes

### 3. 🔄 Dynamic Mid-Day Agent Arrival (`simulator/bonus/dynamic_agent.py`)
Simulates real-time fleet flexibility:
- A new agent (`A_DYNAMIC`) enters mid-shift.
- Unfulfilled packages are dynamically re-routed to optimize remaining distance.

### 4. 📊 CSV Metrics Exporter (`simulator/bonus/csv_exporter.py`)
Generates structured CSV exports:
- `top_performers.csv`: Agent rankings, deliveries, total distance, and efficiency.
- `delivery_logs.csv`: Complete audit trace of every trip coordinate and leg distance.

---

## 🔬 Unit Testing

Run the unit test suite covering domain models, geometric calculations, parser validation, dispatcher tie-breaking, simulation engine, and bonus extensions:

```bash
python -m unittest discover -s tests
```

---

## 📄 Output Format

Sample generated `report.json`:
```json
{
  "A1": {
    "packages_delivered": 2,
    "total_distance": 121.21,
    "efficiency": 60.61
  },
  "A2": {
    "packages_delivered": 2,
    "total_distance": 79.21,
    "efficiency": 39.6
  },
  "A3": {
    "packages_delivered": 1,
    "total_distance": 14.14,
    "efficiency": 14.14
  },
  "best_agent": "A3"
}
```

---

## 👤 Author
- **Name**: Yashvardhan Sawant
- **GitHub**: [@Yashvardhan58](https://github.com/Yashvardhan58)
- **Email**: [yashvardhansawantcollege@gmail.com](mailto:yashvardhansawantcollege@gmail.com)
