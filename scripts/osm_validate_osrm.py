import pandas as pd
import numpy as np
import requests
import time

# =====================================================
# LOAD SAMPLE
# =====================================================

print("Loading validation sample...")

sample = pd.read_csv(
    "osm_validation_sample.csv"
)

print(sample["distance_band"].value_counts())

# TEST FIRST
sample = sample.head(100)

print(
    f"Routes to test: {len(sample)}"
)

# =====================================================
# FUNCTION
# =====================================================

def get_osrm_distance(
    start_lat,
    start_lon,
    end_lat,
    end_lon
):
    """
    Returns road distance in km from OSRM
    """

    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
        f"?overview=false"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    distance_m = data[
        "routes"
    ][0][
        "distance"
    ]

    return round(
        distance_m / 1000,
        2
    )

# =====================================================
# CALCULATE OSM DISTANCES
# =====================================================

osm_distances = []

for i, row in sample.iterrows():

    print(
        f"\nRoute {i+1}/{len(sample)}"
    )

    try:

        distance = get_osrm_distance(

            row["latitude"],
            row["longitude"],

            row["lat"],
            row["lon"]
        )

        osm_distances.append(
            distance
        )

        print(
            f"OSRM Distance: "
            f"{distance:.2f} km"
        )

        # polite delay

        time.sleep(1)

    except Exception as e:

        print(
            f"Failed: {e}"
        )

        osm_distances.append(
            np.nan
        )

# =====================================================
# RESULTS
# =====================================================

sample["osm_distance_km"] = osm_distances

sample = sample.dropna()

# =====================================================
# FACTORS
# =====================================================

sample["osm_factor"] = (
    sample["osm_distance_km"]
    /
    sample["crow_fly_km"]
)

# =====================================================
# ERRORS
# =====================================================

sample["distance_error_pct"] = (
    abs(
        sample["distance_km"]
        -
        sample["osm_distance_km"]
    )
    /
    sample["osm_distance_km"]
) * 100

sample["factor_error_pct"] = (
    abs(
        sample["route_factor"]
        -
        sample["osm_factor"]
    )
    /
    sample["osm_factor"]
) * 100

print("\nMean Error By Distance Band")
print(
    sample.groupby(
        "distance_band"
    )[
        "distance_error_pct"
    ]
    .mean()
    .round(2)
)
print("\nMedian Error By Distance Band")
print(
    sample.groupby(
        "distance_band"
    )[
        "distance_error_pct"
    ]
    .median()
    .round(2)
)

sample.groupby(
    "distance_band"
)[
    ["route_factor",
     "osm_factor"]
].mean()

sample.groupby(
    "distance_band"
)[
    ["route_factor", "osm_factor"]
].mean()

# =====================================================
# SUMMARY
# =====================================================

print("\n")
print("=" * 50)
print("VALIDATION SUMMARY")
print("=" * 50)

print(
    f"Routes Tested: "
    f"{len(sample)}"
)

print(
    f"Mean Distance Error: "
    f"{sample['distance_error_pct'].mean():.2f}%"
)

print(
    f"Median Distance Error: "
    f"{sample['distance_error_pct'].median():.2f}%"
)

print(
    f"Mean Factor Error: "
    f"{sample['factor_error_pct'].mean():.2f}%"
)

corr = sample[
    [
        "distance_km",
        "osm_distance_km"
    ]
].corr().iloc[0, 1]

print(
    f"Correlation: "
    f"{corr:.3f}"
)

print(
    f"Average Predicted Factor: "
    f"{sample['route_factor'].mean():.3f}"
)

print(
    f"Average OSM Factor: "
    f"{sample['osm_factor'].mean():.3f}"
)

# =====================================================
# SAVE
# =====================================================

sample.to_csv(
    "osm_validation_results.csv",
    index=False
)

print(
    "\nSaved:"
)

print(
    "osm_validation_results.csv"
)