import pandas as pd
from sqlalchemy import create_engine

POSTGRES_URI = "postgresql://postgres:System%40123@localhost:5432/apdv_2026"
FILE_PATH = "Data/SEI06.20260415075552.csv"
RAW_TABLE = "raw_sei06"
CLEAN_TABLE = "clean_sei06"

# postgresql engine
def create_db_engine():
    return create_engine(POSTGRES_URI)

 # Load CSV data
def load_csv_data(file_path):
    print("Loading SEI06 data")
    return pd.read_csv(file_path)

 #  Push raw data
def push_raw_data(df, engine, table_name):
    print("Pushing raw data to PostgreSQL...")
    df.to_sql(table_name, engine, if_exists="replace", index=False)

#  retrieve raw data
def retrieve_raw_data(engine, table_name):
    print("Retrieving raw data from PostgreSQL...")
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)

# preprocessing
def preprocess_sei06_data(df):
    print("\nMissing values before preprocessing:")
    print(df.isnull().sum())

    print("\nDuplicate rows before preprocessing:", df.duplicated().sum())

    # Remove duplicates
    df = df.drop_duplicates()

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    # Standardize text columns
    text_cols = ["statistic", "statistic_label", "sector", "c02404v02898", "fuel_type", "unit"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Convert numeric columns
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    if "tlista1" in df.columns:
        df["tlista1"] = pd.to_numeric(df["tlista1"], errors="coerce").astype("Int64")

    if "c02405v02899" in df.columns:
        df["c02405v02899"] = pd.to_numeric(df["c02405v02899"], errors="coerce").astype("Int64")

    # Drop rows with critical missing values
    if "year" in df.columns and "value" in df.columns:
        df = df.dropna(subset=["year", "value"])

    # Drop constant columns
    drop_cols = []
    for col in ["unit", "statistic"]:
        if col in df.columns and df[col].nunique() == 1:
            drop_cols.append(col)

    df = df.drop(columns=drop_cols)

    print(f"\nDropped constant columns: {drop_cols}")

    print("\nMissing values after preprocessing:")
    print(df.isnull().sum())

    print("\nFinal shape:", df.shape)

    return df


def push_clean_data(df, engine, table_name):
    print("Pushing clean data to PostgreSQL...")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print("Preprocessed data stored in PostgreSQL.")


def main():
    # Load CSV data
    df = load_csv_data(FILE_PATH)

    #  Create PostgreSQL engine
    engine = create_db_engine()

    #  Push raw data
    push_raw_data(df, engine, RAW_TABLE)

    #  Retrieve raw data
    df_raw = retrieve_raw_data(engine, RAW_TABLE)

    # Preprocess data
    print("Preprocessing data...")
    df_clean = preprocess_sei06_data(df_raw.copy())

    #  Push clean data
    push_clean_data(df_clean, engine, CLEAN_TABLE)


if __name__ == "__main__":
    main()