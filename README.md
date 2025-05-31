# Beluga Challenge - A* Search Solver

A deterministic A* search-based solver for the Airbus Beluga XL logistics planning problem from the TUPLES consortium competition.

## Problem Description

The Beluga Challenge involves optimizing the storage and movement of aircraft parts transported by Airbus Beluga XL aircraft. The system manages:
- Aircraft parts held on jigs that can slide and be stored on racks
- A bidirectional multi-queue rack system
- Trailers for transferring jigs between Beluga and fixed racks
- Production lines that consume parts from jigs
- Flight schedules with incoming and outgoing requirements

## Installation

### Clone the project
```bash
git clone https://github.com/inquisitour/beluga-challange.git
```

## Usage

### Basic Solver
```bash
python scripts/run_solver.py instances/problem_4_s46_j23_r2_oc51_f6.json
```

### With Custom Parameters
```bash
python scripts/run_solver.py instances/problem_4_s46_j23_r2_oc51_f6.json --max-iterations 10000 --time-limit 60
```

### Save Output
```bash
python scripts/run_solver.py instances/problem_4_s46_j23_r2_oc51_f6.json --output outputs/plan.txt
```

### Debug Mode
```bash
python scripts/run_solver.py instances/problem_4_s46_j23_r2_oc51_f6.json --debug
```

## Project Structure

```
src/
├── core/           # Core data structures and problem representation
├── search/         # A* search algorithm and related components
└── utils/          # Utilities and verification tools

tests/              # Test files and debugging utilities
instances/          # Problem instance files
scripts/            # Main execution scripts
outputs/            # Generated plans and results
```

## Algorithm Overview

The solver uses A* search with:
- **State Representation**: Tracks jig positions, loading status, and flight progress
- **Action Space**: Move jigs between racks, send to production, process flights
- **Heuristic**: Estimates remaining steps based on unprocessed flights, unproduced parts, and blocked jigs
- **Goal Test**: Verifies all flights processed and production requirements met

## Testing

Run individual tests:
```bash
python -m tests.test_setup    # Test basic components
python -m tests.test_astar    # Test A* search
python -m tests.debug         # Debug action generation and heuristics
```

## Implementation Notes

This is a minimal implementation with the following limitations:
- Simplified handling of Beluga loading/unloading operations
- Basic heuristic function that may not be optimal for all instances
- Limited to small-medium instance sizes due to state space complexity

## Results

The solver successfully:
- Loads and parses problem instances
- Generates valid actions from any state
- Explores the search space systematically
- Verifies plan correctness

For the current test instance, the search explores up to 5/6 flights and produces partial solutions, indicating the framework is functional and sound but may require refinement for complete solutions on complex instances.