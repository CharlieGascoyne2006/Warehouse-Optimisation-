import pandas as pd
import matplotlib.pyplot as plt

# ========================================
# LOAD RESULTS
# ========================================

results = pd.read_csv(
    "output/all_runs.csv"
)

# ========================================
# CLEAN DATA
# ========================================

results = results.sort_values(
    "warehouses"
)

# ========================================
# CHART 1
# AVERAGE DISTANCE
# ========================================

plt.figure(figsize=(10, 6))

plt.plot(

    results["warehouses"],

    results["average_distance_km"],

    marker="o",
    linewidth=2

)

for _, row in results.iterrows():

    plt.annotate(

        f"{row['average_distance_km']:.1f}",

        (
            row["warehouses"],
            row["average_distance_km"]
        ),

        textcoords="offset points",

        xytext=(0, 8),

        ha="center"

    )

plt.title(
    "Average Distance vs Number of Warehouses"
)

plt.xlabel(
    "Number of Warehouses"
)

plt.ylabel(
    "Average Population-Weighted Distance (km)"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "output/average_distance_vs_warehouses.png",
    dpi=300
)

# ========================================
# CHART 2
# OBJECTIVE VALUE
# ========================================

plt.figure(figsize=(10, 6))

plt.plot(

    results["warehouses"],

    results["objective"] / 1_000_000_000,

    marker="o",

    linewidth=2

)

for _, row in results.iterrows():

    plt.annotate(

        f"{row['objective']/1_000_000_000:.2f}",

        (
            row["warehouses"],
            row["objective"] / 1_000_000_000
        ),

        textcoords="offset points",

        xytext=(0, 8),

        ha="center"

    )

plt.title(
    "Objective Cost vs Number of Warehouses"
)

plt.xlabel(
    "Number of Warehouses"
)

plt.ylabel(
    "Objective Cost (Billions)"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "output/objective_vs_warehouses.png",
    dpi=300
)

# ========================================
# CHART 3
# RUN TIME
# ========================================

plt.figure(figsize=(10, 6))

plt.plot(

    results["warehouses"],

    results["runtime_minutes"],

    marker="o",

    linewidth=2

)

for _, row in results.iterrows():

    plt.annotate(

        f"{row['runtime_minutes']:.1f}",

        (
            row["warehouses"],
            row["runtime_minutes"]
        ),

        textcoords="offset points",

        xytext=(0, 8),

        ha="center"

    )

plt.title(
    "Runtime vs Number of Warehouses"
)

plt.xlabel(
    "Number of Warehouses"
)

plt.ylabel(
    "Runtime (Minutes)"
)

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "output/runtime_vs_warehouses.png",
    dpi=300
)

print(
    "\nCharts saved:"
)

print(
    "output/average_distance_vs_warehouses.png"
)

print(
    "output/objective_vs_warehouses.png"
)

print(
    "output/runtime_vs_warehouses.png"
)