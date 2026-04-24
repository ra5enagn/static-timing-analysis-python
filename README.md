# Static Timing Analysis (STA) Tool – Work in Progress

## Overview

This is a Python-based Static Timing Analysis (STA) tool that parses gate-level netlists (`.bench`) and NLDM Liberty files (`.lib`) to compute:

* Gate delays using interpolation from LUTs
* Slew propagation across the circuit
* Arrival times at each node
* Slack values for all gates
* Total circuit delay
* One critical path through the circuit

This project is still a **work in progress** and is actively being debugged and refined.

---

## Current Status

* Working correctly for **8 out of 10 tested benchmark cases**
* Remaining **2 test cases fail due to edge cases in traversal / timing propagation**
* Code structure is stable, but improvements are ongoing in:

  * Topological traversal logic
  * Boundary conditions in delay/slew interpolation
  * Robustness for complex fan-in/fan-out scenarios

---

## Features

* Parses `.bench` netlists and builds a node-based graph representation
* Reads NLDM timing data (delay and slew LUTs)
* Computes fan-in / fan-out relationships
* Calculates load capacitance dynamically
* Performs:

  * Forward traversal → delay + slew propagation
  * Backward traversal → slack computation
* Outputs:

  * Circuit details
  * Delay LUT
  * Slew LUT
  * Critical path and slack report

---

## File Structure

```
.
├── main_sta.py
├── README.md
├── requirements.txt
└── outputs (generated during runtime)
    ├── ckt_details.txt
    ├── delay_LUT.txt
    ├── slew_LUT.txt
    └── ckt_traversal.txt
```

---

## Requirements

This project uses only standard Python libraries:

```
argparse
re
time
```

No external installations are required.

---

## How to Run

### 1. Read Netlist

```
python main_sta.py --read_ckt <path_to_bench_file>
```

### 2. Read NLDM File

```
python main_sta.py --read_nldm <path_to_lib_file>
```

### 3. Extrac
