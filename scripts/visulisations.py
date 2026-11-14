import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# =====================================================
# LOAD DATA
# =====================================================

df = pd.read_csv(
    "osm_validation_results.csv"
)

# Clean style

plt.style.use("default")

# =====================================================
# 1. PREDICTED VS OSM DISTANCE
# =====================================================

plt.figure(figsize=(8,6))

plt.scatter(
    df["osm_distance_km"],
    df["distance_km"],
    alpha=0.7
)

max_val = max(
    df["osm_distance_km"].max(),
    df["distance_km"].max()
)

plt.plot(
    [0, max_val],
    [0, max_val],
    color="red",
    linestyle="--",
    label="Perfect Fit"
)

plt.xlabel("OSM Distance (km)")
plt.ylabel("Predicted Distance (km)")
plt.title("Predicted vs Actual OSM Distance")
plt.legend()

plt.tight_layout()

plt.savefig(
    "01_predicted_vs_osm_distance.png",
    dpi=300
)

plt.close()

# =====================================================
# 2. ERROR BY BAND
# =====================================================

band_error = (
    df.groupby(
        "distance_band"
    )[
        "distance_error_pct"
    ]
    .mean()
)

plt.figure(figsize=(8,6))

band_error.plot(
    kind="bar"
)

plt.ylabel("Mean Error (%)")

plt.title(
    "Mean Error by Distance Band"
)

plt.tight_layout()

plt.savefig(
    "02_error_by_band.png",
    dpi=300
)

plt.close()

# =====================================================
# 3. ROUTE FACTOR COMPARISON
# =====================================================

factor_compare = (
    df.groupby(
        "distance_band"
    )[
        [
            "route_factor",
            "osm_factor"
        ]
    ]
    .mean()
)

factor_compare.plot(
    kind="bar",
    figsize=(8,6)
)

plt.ylabel("Factor")

plt.title(
    "Predicted vs OSM Factors"
)

plt.tight_layout()

plt.savefig(
    "03_factor_comparison.png",
    dpi=300
)

plt.close()

# =====================================================
# 4. ERROR DISTRIBUTION
# =====================================================

plt.figure(figsize=(8,6))

plt.hist(
    df["distance_error_pct"],
    bins=15
)

plt.xlabel("Distance Error (%)")
plt.ylabel("Frequency")

plt.title(
    "Distribution of Validation Errors"
)

plt.tight_layout()

plt.savefig(
    "04_error_distribution.png",
    dpi=300
)

plt.close()

# =====================================================
# 5. ERROR VS DISTANCE
# =====================================================

plt.figure(figsize=(8,6))

plt.scatter(
    df["osm_distance_km"],
    df["distance_error_pct"],
    alpha=0.7
)

plt.xlabel(
    "OSM Distance (km)"
)

plt.ylabel(
    "Distance Error (%)"
)

plt.title(
    "Error vs Journey Length"
)

plt.tight_layout()

plt.savefig(
    "05_error_vs_distance.png",
    dpi=300
)

plt.close()

# =====================================================
# 6. ROUTE COUNTS
# =====================================================

plt.figure(figsize=(8,6))

df["distance_band"].value_counts().plot(
    kind="bar"
)

plt.ylabel(
    "Number of Routes"
)

plt.title(
    "Validation Sample Composition"
)

plt.tight_layout()

plt.savefig(
    "06_validation_sample.png",
    dpi=300
)

plt.close()

# =====================================================
# 7. CORRELATION HEATMAP
# =====================================================

numeric_cols = [

    "crow_fly_km",

    "distance_km",

    "osm_distance_km",

    "route_factor",

    "osm_factor",

    "distance_error_pct"
]

corr = (
    df[
        numeric_cols
    ]
    .corr()
)

plt.figure(figsize=(8,6))

sns.heatmap(
    corr,
    annot=True,
    cmap="Blues"
)

plt.title(
    "Validation Correlation Matrix"
)

plt.tight_layout()

plt.savefig(
    "07_correlation_heatmap.png",
    dpi=300
)

plt.close()

# =====================================================
# 8. V1 VS V2 COMPARISON
# =====================================================

v1_error = 11.06
v2_error = 8.81

v1_corr = 0.988
v2_corr = 0.993

fig, ax = plt.subplots(
    1,
    2,
    figsize=(10,5)
)

ax[0].bar(
    ["V1","V2"],
    [v1_error,v2_error]
)

ax[0].set_title(
    "Mean Error (%)"
)

ax[1].bar(
    ["V1","V2"],
    [v1_corr,v2_corr]
)

ax[1].set_ylim(0.98, 1.00)

ax[1].set_title(
    "Correlation"
)

ax[1].set_ylabel(
    "Correlation Coefficient"
)

plt.tight_layout()

plt.savefig(
    "08_v1_vs_v2.png",
    dpi=300
)

plt.close()

# =====================================================
# SUMMARY TABLE
# =====================================================

summary = pd.DataFrame({

    "Metric":[

        "Mean Error",

        "Median Error",

        "Correlation",

        "Predicted Factor",

        "OSM Factor"
    ],

    "Value":[

        df["distance_error_pct"].mean(),

        df["distance_error_pct"].median(),

        df[
            [
                "distance_km",
                "osm_distance_km"
            ]
        ]
        .corr()
        .iloc[0,1],

        df["route_factor"].mean(),

        df["osm_factor"].mean()
    ]
})

summary.to_csv(
    "validation_summary.csv",
    index=False
)

print(
    "All visualisations created."
)