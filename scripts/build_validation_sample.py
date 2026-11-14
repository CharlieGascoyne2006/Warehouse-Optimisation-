# ================================================================================================================


# Build sample 


# ================================================================================================================


import pandas as pd


# =====================================
# LOAD DISTANCE MATRIX
# =====================================

df = pd.read_csv("distance_matrix_kdtree.csv")

# =====================================
# DISTANCE BANDS
# =====================================

def distance_band(distance):

    if distance < 50:
        return "Short"

    elif distance < 150:
        return "Medium"

    elif distance < 300:
        return "Long"

    else:
        return "Very Long"


df["distance_band"] = df["distance_km"].apply(distance_band)

print(
    df["distance_band"]
    .value_counts()
)

# =====================================
# SAMPLE 25 FROM EACH BAND
# =====================================


sample = (
    df.groupby("distance_band", group_keys=False)
      .sample(n=25, random_state=42)
)


# =====================================
# SAVE
# =====================================

demand_nodes = pd.read_csv("demand_nodes.csv")
warehouses = pd.read_csv("candidate_warehouses_clean.csv")

sample = sample.merge(
    demand_nodes[
        ["msoa", "lat", "lon"]
    ],
    on="msoa",
    how="left"
)

sample = sample.merge(
    warehouses[
        ["warehouse", "latitude", "longitude"]
    ],
    on="warehouse",
    how="left"
)

sample.to_csv(
    "osm_validation_sample.csv",
    index=False
)

print(sample["distance_band"].value_counts())