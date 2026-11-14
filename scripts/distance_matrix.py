import pandas as pd
import numpy as np

from scipy.spatial import KDTree

# ========================================
# FUNCTIONS
# ========================================

def haversine(lat1, lon1, lat2, lon2):

    R = 6371

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (

        np.sin(dlat / 2) ** 2

        +

        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2

    )

    c = 2 * np.arctan2(
        np.sqrt(a),
        np.sqrt(1 - a)
    )

    return R * c


# ========================================
# CLASSIFICATION FACTORS
# ========================================

FACTORS = {

    "Urban: Nearer to a major town or city":
        1.10,

    "Urban: Further from a major town or city":
        1.20,

    "Smaller rural: Nearer to a major town or city":
        1.30,

    "Larger rural: Nearer to a major town or city":
        1.35,

    "Smaller rural: Further from a major town or city":
        1.50,

    "Larger rural: Further from a major town or city":
        1.65

}


# ========================================
# LOAD DATA
# ========================================

print("Loading datasets...")

demand_nodes = pd.read_csv(
    "demand_nodes.csv"
)

warehouses = pd.read_csv(
    "candidate_warehouses_clean.csv"
)

print(
    f"Demand Nodes: {len(demand_nodes):,}"
)

print(
    f"Warehouses: {len(warehouses):,}"
)

# ========================================
# BUILD KDTREE
# ========================================

print("\nBuilding KDTree...")

coordinates = np.column_stack(

    (
        demand_nodes["lat"],
        demand_nodes["lon"]
    )

)

kdtree = KDTree(
    coordinates
)

print("KDTree built.")

# ========================================
# HELPERS
# ========================================

def nearest_factor(lat, lon):

    _, idx = kdtree.query(
        (lat, lon)
    )

    classification = (
        demand_nodes.iloc[idx]
        ["classification"]
    )

    return FACTORS.get(
        classification,
        1.25
    )


# ========================================
# ROUTE FACTOR
# ========================================

def route_factor(

    warehouse_lat,
    warehouse_lon,

    msoa_lat,
    msoa_lon,

    crow_fly_distance

):

    factors = []

    if crow_fly_distance < 30:

        sample_points = [

            (
                warehouse_lat,
                warehouse_lon
            ),

            (
                msoa_lat,
                msoa_lon
            )

        ]

    elif crow_fly_distance < 100:

        sample_points = [

            (
                warehouse_lat,
                warehouse_lon
            ),

            (

                (
                    warehouse_lat + msoa_lat
                ) / 2,

                (
                    warehouse_lon + msoa_lon
                ) / 2

            ),

            (
                msoa_lat,
                msoa_lon
            )

        ]

    else:

        sample_points = [

            (
                warehouse_lat,
                warehouse_lon
            ),

            (

                warehouse_lat
                + (
                    msoa_lat
                    - warehouse_lat
                ) * 0.25,

                warehouse_lon
                + (
                    msoa_lon
                    - warehouse_lon
                ) * 0.25

            ),

            (

                warehouse_lat
                + (
                    msoa_lat
                    - warehouse_lat
                ) * 0.50,

                warehouse_lon
                + (
                    msoa_lon
                    - warehouse_lon
                ) * 0.50

            ),

            (

                warehouse_lat
                + (
                    msoa_lat
                    - warehouse_lat
                ) * 0.75,

                warehouse_lon
                + (
                    msoa_lon
                    - warehouse_lon
                ) * 0.75

            ),

            (
                msoa_lat,
                msoa_lon
            )

        ]

    for lat, lon in sample_points:

        factors.append(
            nearest_factor(
                lat,
                lon
            )
        )

    return np.mean(
        factors
    )


# ========================================
# BUILD DISTANCE MATRIX
# ========================================

print(
    "\nCalculating route-aware distances..."
)

distance_records = []

for _, msoa in demand_nodes.iterrows():

    for _, warehouse in warehouses.iterrows():

        crow_fly = haversine(
            msoa["lat"],
            msoa["lon"],
            warehouse["latitude"],
            warehouse["longitude"]
        )

        factor = route_factor(
            warehouse["latitude"],
            warehouse["longitude"],
            msoa["lat"],
            msoa["lon"],
            crow_fly
        )

        if crow_fly < 50:

            factor *= 1.15

        elif crow_fly < 150:

            factor *= 1.05

        road_distance = (
            crow_fly
            * factor
        )

        distance_records.append(
            {
                "msoa": msoa["msoa"],
                "warehouse": warehouse["warehouse"],
                "crow_fly_km": round(crow_fly, 2),
                "route_factor": round(factor, 3),
                "distance_km": round(road_distance, 2)
            }
        )

# ========================================
# BUILD DATAFRAME
# ========================================

distance_matrix = pd.DataFrame(
    distance_records
)

distance_matrix = distance_matrix.merge(

    demand_nodes[
        [
            "msoa",
            "population"
        ]
    ],

    on="msoa",

    how="left"

)

distance_matrix[
    "weighted_distance"
] = (

    distance_matrix[
        "population"
    ]

    *

    distance_matrix[
        "distance_km"
    ]

)

# ========================================
# DIAGNOSTICS
# ========================================

print(
    "\nAverage Crow Fly Distance:"
)

print(
    round(
        distance_matrix[
            "crow_fly_km"
        ].mean(),
        2
    )
)

print(
    "\nAverage Route Factor:"
)

print(
    round(
        distance_matrix[
            "route_factor"
        ].mean(),
        3
    )
)

print(
    "\nAverage Estimated Road Distance:"
)

print(
    round(
        distance_matrix[
            "distance_km"
        ].mean(),
        2
    )
)

# ========================================
# SAVE
# ========================================

distance_matrix.to_csv(

    "distance_matrix_kdtree.csv",

    index=False

)

print(
    "\nSaved:"
)

print(
    "distance_matrix_kdtree.csv"
)

