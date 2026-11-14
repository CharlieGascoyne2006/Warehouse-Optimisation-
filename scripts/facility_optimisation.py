import pandas as pd
import pulp
import time
import os

from datetime import datetime

# ========================================
# SCRIPT START
# ========================================

script_start = time.time()

# ========================================
# SETTINGS
# ========================================

OUTPUT_FOLDER = "output"

TIME_LIMIT_SECONDS = 600

GAP_TOLERANCE = 0.001

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

# ========================================
# LOAD DATA
# ========================================

print("Loading datasets...")

distance_matrix = pd.read_csv(
    "distance_matrix_kdtree.csv"
)

warehouse_data = pd.read_csv(
    "candidate_warehouses_clean.csv"
)

warehouse_data.columns = (
    warehouse_data.columns
    .str.strip()
    .str.lower()
)

print(
    f"Distance Records: "
    f"{len(distance_matrix):,}"
)

# ========================================
# VALIDATION
# ========================================

required_distance_cols = [
    "msoa",
    "warehouse",
    "distance_km",
    "population"
]

required_warehouse_cols = [
    "warehouse",
    "capacity"
]

for col in required_distance_cols:

    if col not in distance_matrix.columns:

        raise ValueError(
            f"Missing distance column: {col}"
        )

for col in required_warehouse_cols:

    if col not in warehouse_data.columns:

        raise ValueError(
            f"Missing warehouse column: {col}"
        )

# ========================================
# COST COLUMN
# ========================================

distance_matrix["cost"] = (
    distance_matrix["population"]
    *
    distance_matrix["distance_km"]
)

print(
    "Cost column created successfully"
)

# ========================================
# USER INPUT
# ========================================

NUMBER_OF_WAREHOUSES = int(
    input(
        "How many warehouses would you like to open? "
    )
)

print(
    f"\nOptimising for "
    f"{NUMBER_OF_WAREHOUSES} warehouses"
)

# ========================================
# CREATE LISTS
# ========================================

msoas = sorted(
    distance_matrix["msoa"]
    .unique()
    .tolist()
)

warehouses = sorted(
    distance_matrix["warehouse"]
    .unique()
    .tolist()
)

print(f"MSOAs: {len(msoas):,}")
print(f"Warehouses: {len(warehouses):,}")

# ========================================
# POPULATION LOOKUP
# ========================================

population_lookup = dict(

    distance_matrix[
        ["msoa", "population"]
    ]
    .drop_duplicates()

    .values

)

# ========================================
# CAPACITY LOOKUP
# ========================================

capacity_dict = dict(

    zip(

        warehouse_data[
            "warehouse"
        ],

        warehouse_data[
            "capacity"
        ]

    )

)

total_population = sum(
    population_lookup.values()
)

total_capacity = (
    warehouse_data[
        "capacity"
    ].sum()
)

print(
    f"\nTotal Population: "
    f"{total_population:,.0f}"
)

print(
    f"Total Capacity: "
    f"{total_capacity:,.0f}"
)

# ========================================
# COST LOOKUP
# ========================================

cost_dict = {}

for _, row in distance_matrix.iterrows():

    cost_dict[(
        row["msoa"],
        row["warehouse"]
    )] = row["cost"]

# ========================================
# MODEL
# ========================================

model = pulp.LpProblem(
    "Capacitated_Facility_Location",
    pulp.LpMinimize
)

# ========================================
# VARIABLES
# ========================================

open_wh = pulp.LpVariable.dicts(

    "OpenWarehouse",

    warehouses,

    cat="Binary"

)

assign = pulp.LpVariable.dicts(

    "Assign",

    [

        (m, w)

        for m in msoas

        for w in warehouses

    ],

    cat="Binary"

)

# ========================================
# OBJECTIVE
# ========================================

model += pulp.lpSum(

    cost_dict[(m, w)]

    *

    assign[(m, w)]

    for m in msoas

    for w in warehouses

)

# ========================================
# EVERY MSOA ASSIGNED ONCE
# ========================================

for m in msoas:

    model += (

        pulp.lpSum(

            assign[(m, w)]

            for w in warehouses

        )

        == 1

    )

# ========================================
# ONLY ASSIGN TO OPEN WAREHOUSE
# ========================================

for m in msoas:

    for w in warehouses:

        model += (

            assign[(m, w)]

            <=

            open_wh[w]

        )

# ========================================
# CAPACITY CONSTRAINTS
# ========================================

for w in warehouses:

    model += (

        pulp.lpSum(

            population_lookup[m]

            *

            assign[(m, w)]

            for m in msoas

        )

        <=

        capacity_dict[w]

    )

# ========================================
# EXACTLY N WAREHOUSES
# ========================================

model += (

    pulp.lpSum(

        open_wh[w]

        for w in warehouses

    )

    == NUMBER_OF_WAREHOUSES

)

# ========================================
# SOLVE
# ========================================

print(
    "\nSolving optimisation model..."
)

solver = pulp.PULP_CBC_CMD(

    timeLimit=TIME_LIMIT_SECONDS,

    gapRel=GAP_TOLERANCE,

    msg=True

)

solve_start = time.time()

model.solve(solver)

solve_end = time.time()

runtime = (
    solve_end
    -
    solve_start
)

# ========================================
# STATUS
# ========================================

status = pulp.LpStatus[
    model.status
]

print(
    f"\nSolver Status: {status}"
)

if status == "Infeasible":

    raise Exception(
        "Model is infeasible."
    )

if status == "Unbounded":

    raise Exception(
        "Model is unbounded."
    )

# ========================================
# SELECTED WAREHOUSES
# ========================================

selected_warehouses = [

    w

    for w in warehouses

    if pulp.value(
        open_wh[w]
    ) > 0.5

]

print("\nSelected Warehouses:")

for w in selected_warehouses:

    print(f"  - {w}")

# ========================================
# ASSIGNMENTS
# ========================================

assignments = []

for m in msoas:

    for w in warehouses:

        value = pulp.value(
            assign[(m, w)]
        )

        if value is not None and value > 0.5:

            assignments.append({

                "msoa":
                    m,

                "warehouse":
                    w,

                "population":
                    population_lookup[m]

            })

assignments_df = pd.DataFrame(
    assignments
)

# ========================================
# WAREHOUSE SUMMARY
# ========================================

warehouse_summary = (

    assignments_df

    .groupby("warehouse")

    .agg(

        assigned_population=(
            "population",
            "sum"
        ),

        msoa_count=(
            "msoa",
            "count"
        )

    )

    .reset_index()

)

warehouse_summary[
    "capacity"
] = warehouse_summary[
    "warehouse"
].map(
    capacity_dict
)

warehouse_summary[
    "utilisation_pct"
] = (

    warehouse_summary[
        "assigned_population"
    ]

    /

    warehouse_summary[
        "capacity"
    ]

) * 100

warehouse_summary[
    "unused_capacity"
] = (

    warehouse_summary[
        "capacity"
    ]

    -

    warehouse_summary[
        "assigned_population"
    ]

)

warehouse_summary = warehouse_summary.sort_values(

    "utilisation_pct",

    ascending=False

)

# ========================================
# TIMESTAMP
# ========================================

timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

# ========================================
# OUTPUT FILES
# ========================================

assignments_file = (
    f"{OUTPUT_FOLDER}/warehouse_assignments_{timestamp}.csv"
)

summary_file = (
    f"{OUTPUT_FOLDER}/warehouse_summary_{timestamp}.csv"
)

run_file = (
    f"{OUTPUT_FOLDER}/run_summary_{timestamp}.csv"
)

master_file = (
    f"{OUTPUT_FOLDER}/all_runs.csv"
)

# ========================================
# SAVE OUTPUTS
# ========================================

assignments_df.to_csv(
    assignments_file,
    index=False
)

warehouse_summary.to_csv(
    summary_file,
    index=False
)

average_distance = (
    pulp.value(model.objective)
    /
    total_population
)


results_summary = pd.DataFrame([{

    "warehouses":
        NUMBER_OF_WAREHOUSES,

    "objective":
        pulp.value(
            model.objective
        ),

    "average_distance_km":
        average_distance,


    "runtime_seconds":
        runtime,

    "runtime_minutes":
        runtime / 60,

    "status":
        status
    

}])

results_summary.to_csv(
    run_file,
    index=False
)

if os.path.exists(
    master_file
):

    existing = pd.read_csv(
        master_file
    )

    existing = pd.concat(

        [
            existing,
            results_summary
        ],

        ignore_index=True

    )

    existing.to_csv(
        master_file,
        index=False
    )

else:

    results_summary.to_csv(
        master_file,
        index=False
    )

# ========================================
# RESULTS
# ========================================

print(
    f"\nTotal Cost = "
    f"{pulp.value(model.objective):,.2f}"
)

print(
    f"Solver Runtime: "
    f"{runtime:.2f} seconds"
)

print(
    f"Solver Runtime: "
    f"{runtime/60:.2f} minutes"
)

script_end = time.time()

print(
    f"\nTotal Script Runtime: "
    f"{(script_end - script_start)/60:.2f} minutes"
)

print("\nOutputs saved:")

print(assignments_file)
print(summary_file)
print(run_file)
print(master_file)