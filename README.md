# Warehouse Location Optimisation for England and Wales

## Overview

This project applies Operations Research techniques to determine the optimal location of warehouse facilities across England and Wales.

A capacitated facility location model was developed using Mixed Integer Linear Programming (MILP) to minimise population-weighted transportation distance whilst satisfying warehouse capacity constraints.

To improve transportation realism, a bespoke route-aware distance estimation methodology was developed and validated against OpenStreetMap routing data.
To improve transportation realism, a bespoke route-aware distance estimation methodology was developed combining:

- Haversine distance calculations
- Rural-Urban Classification accessibility factors
- KDTree spatial indexing
- Adaptive route sampling
- OpenStreetMap validation

---

## Project Objectives

The project sought to answer three key questions:

1. How can warehouse locations be optimised across England and Wales whilst respecting capacity constraints?

2. Does incorporating route accessibility characteristics influence warehouse location decisions?

3. Can a KDTree-based route accessibility methodology provide an accurate approximation of road-network distance without requiring full network routing?

---

## Project Scale

| Metric | Value |
|----------|----------:|
| Demand Locations | 7,264 MSOAs |
| Candidate Warehouses | 20 |
| Warehouse-Demand Pairs | 145,280 |
| Validation Routes | 100 |

---

## Methodology

### Demand Data

- 7,264 MSOA demand locations
- Population-based demand representation
- England and Wales coverage

### Candidate Warehouses

- 20 candidate warehouse locations
- Major UK logistics corridors and distribution hubs

### Distance Estimation

The project developed a route-aware distance estimation methodology combining:

- Haversine distance calculations
- Rural Urban Classification accessibility factors
- Adaptive route sampling
- KDTree nearest-neighbour classification

Estimated road distance was calculated as:

```text
Estimated Distance = Crow Fly Distance × Route Factor
```

---

## Validation Results

The distance estimation methodology was validated against OpenStreetMap routing data.

| Metric | Result |
|----------|----------:|
| Mean Distance Error | 8.81% |
| Median Distance Error | 6.49% |
| Correlation | 0.993 |

---

## Optimisation Results

| Warehouses | Objective Cost |
|----------:|----------:|
| 7 | 4.55 bn |
| 8 | 3.51 bn |
| 9 | 3.40 bn |
| 10 | 3.37 bn |
| 14 | 3.16 bn |
| 20 | 3.12 bn |

Key findings:

- Warehouse capacity constraints materially influenced facility selection.
- Route-aware distance estimation improved transportation realism.
- The largest accessibility gains occurred between 7 and 10 facilities.
- Diminishing returns were observed beyond approximately 10–12 warehouses.
- Distance modelling assumptions influenced warehouse selection under constrained network scenarios.

---

## Key Technologies

- Python
- Pandas
- NumPy
- SciPy KDTree
- PuLP
- CBC Solver
- OpenStreetMap
- OSRM

---

## Repository Structure

```text
report/
    Warehouse_Optimisation_Report.pdf

scripts/
    optimisation scripts

figures/
    validation and optimisation visualisations

data/
    source datasets
```

---

## Full Report

The complete methodology, validation process and results are documented in:

```text
report/Warehouse_Optimisation_Report.pdf
```

---

## Author

Charlie Gascoyne

Data & Analytics | Operations Research | Supply Chain Optimisation | Spatial Analytics
