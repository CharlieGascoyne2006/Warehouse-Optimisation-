import pandas as pd

# ========================================
# FUNCTIONS
# ========================================

def standardise_columns(df):

    df = df.copy()

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    return df


def inspect_dataframe(name, df):

    print("\n" + "=" * 60)
    print(name.upper())
    print("=" * 60)

    print("\nColumns:")
    print(df.columns.tolist())

    print(f"\nShape: {df.shape}")

    print("\nFirst 5 Rows:")
    print(df.head())


def load_broken_csv(file_path, column_names):

    df = pd.read_csv(file_path, header=None)

    df = df[0].str.split(",", expand=True)

    df.columns = column_names

    df = df.iloc[1:].reset_index(drop=True)

    return df


# ========================================
# LOAD DATASETS
# ========================================

population = pd.read_excel(
    "sapemsoasyoa20222024.xlsx",
    sheet_name="Mid-2024 MSOA 2021",
    header=3
)

centroids = pd.read_csv(
    "MSOA_PopCentroids_EW_2021_V2.csv"
)

classification = pd.read_csv(
    "MSOA_(2021)_EW_BSC_V3_to_Rural_Urban_Classification.csv"
)

warehouses = load_broken_csv(
    "candidate_warehouses.csv",
    ["warehouse", "latitude", "longitude"]
)

ports = load_broken_csv(
    "Ports.csv",
    ["port", "latitude", "longitude"]
)


population = standardise_columns(population)
classification = standardise_columns(classification)



# ========================================
# CONVERT DATA TYPES
# ========================================

warehouses["latitude"] = warehouses["latitude"].astype(float)
warehouses["longitude"] = warehouses["longitude"].astype(float)

ports["latitude"] = ports["latitude"].astype(float)
ports["longitude"] = ports["longitude"].astype(float)


# ========================================
# CLEAN POPULATION
# ========================================

population_clean = population[
    [
        "msoa_2021_code",
        "msoa_2021_name",
        "total"
    ]
].copy()

population_clean.columns = [
    "msoa",
    "msoa_name",
    "population"
]


# ========================================
# CLEAN CLASSIFICATION
# ========================================

classification_clean = classification[
    [
        "msoa21cd",
        "lat",
        "long",
        "urban_rura",
        "ruc21nm"
    ]
].copy()

classification_clean.columns = [
    "msoa",
    "lat",
    "lon",
    "urban_rural",
    "classification"
]


# ========================================
# BUILD DEMAND NODES
# ========================================

demand_nodes = population_clean.merge(
    classification_clean,
    on="msoa",
    how="left"
)


# ========================================
# EXPORT CLEAN DATA
# ========================================

demand_nodes.to_csv(
    "demand_nodes.csv",
    index=False
)

warehouses.to_csv(
    "candidate_warehouses_clean.csv",
    index=False
)

ports.to_csv(
    "ports_clean.csv",
    index=False
)



