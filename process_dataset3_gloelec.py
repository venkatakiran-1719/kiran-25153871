import pandas as pd
from sqlalchemy import create_engine

POSTGRES_URI = "postgresql://postgres:System%40123@localhost:5432/apdv_2026"
FILE_PATH = "Data/merged_gloelecload_2006_2024.csv"
RAW_TABLE = "raw_gloelec"
CLEAN_TABLE = "clean_gloelec"

# preprocessing
def preprocess_data(df):
    print("\nMissing values before preprocessing:")
    print(df.isnull().sum())

    print("\nDuplicate rows before preprocessing:", df.duplicated().sum())

    # Drop missing values
    df = df.dropna()

    # Remove duplicates
    df = df.drop_duplicates()

    print("\nMissing values after preprocessing:")
    print(df.isnull().sum())

    print("\nDuplicate rows after preprocessing:", df.duplicated().sum())

    #  TimestampConvert
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Feature engineering
    df["Month"] = df["Timestamp"].dt.month
    df["Day"] = df["Timestamp"].dt.day
    df["Hour"] = df["Timestamp"].dt.hour
    df["Minute"] = df["Timestamp"].dt.minute
    df["DayOfWeek"] = df["Timestamp"].dt.dayofweek
    df["IsWeekend"] = df["DayOfWeek"].isin([5, 6]).astype(int)

    # Drop Timestamp
    df = df.drop(columns=["Timestamp"])

    return df

#  Create DB engine
def create_db_engine():
    return create_engine(POSTGRES_URI)

#  Load CSV
def load_csv_data(file_path):
    print("Loading global electricity load data...")
    return pd.read_csv(file_path)

#  Push raw data
def push_raw_data(df, engine, table_name):
    print("Pushing raw data to PostgreSQL...")
    df.to_sql(table_name, engine, if_exists="replace", index=False)

#  Retrieve raw data
def retrieve_raw_data(engine, table_name):
    print("Retrieving raw data from PostgreSQL...")
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)

#  Clean column names
def clean_column_names(df):
    df.columns = [col.replace(" ", "_").lower() for col in df.columns]
    return df

# Push clean data
def push_clean_data(df, engine, table_name):
    print("Pushing clean data to PostgreSQL...")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print("Preprocessed data stored in PostgreSQL.")


def main():
    #  Load CSV
    df = load_csv_data(FILE_PATH)

    #  Create DB engine
    engine = create_db_engine()

    #  Push raw data
    push_raw_data(df, engine, RAW_TABLE)

    #  Retrieve raw data
    df_raw = retrieve_raw_data(engine, RAW_TABLE)

    #  Preprocess data
    print("Preprocessing data...")
    df_clean = preprocess_data(df_raw.copy())

    #  Clean column names
    df_clean = clean_column_names(df_clean)

    # Push clean data
    push_clean_data(df_clean, engine, CLEAN_TABLE)


if __name__ == "__main__":
    main()