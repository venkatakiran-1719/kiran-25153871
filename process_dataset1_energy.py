import pandas as pd
import json
from pymongo import MongoClient
from sqlalchemy import create_engine

MONGO_URI = "mongodb://localhost:27017/"
POSTGRES_URI = "postgresql://postgres:System%40123@localhost:5432/apdv_2026"

JSON_FILE_PATH = "Data/energy.json"
MONGO_DB_NAME = "apdv_2026"
RAW_COLLECTION = "raw_energy"
CLEAN_TABLE = "clean_energy"


# load json data
def load_json_data(file_path):
    print("Loading energy.json...")
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

# mongo db connection
def create_mongo_connection():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    return client, db

# raw data to mongodb
def push_raw_to_mongo(data, db, collection_name):
    print("Pushing raw JSON data to MongoDB...")
    collection = db[collection_name]
    collection.delete_many({})
    collection.insert_many(data)
    print("Inserted into MongoDB.")


# data retrivel from mongodb
def retrieve_raw_from_mongo(db, collection_name):
    print("Retrieving raw data from MongoDB...")
    collection = db[collection_name]
    raw_data = list(collection.find({}, {"_id": 0}))
    return raw_data

# preprocessing function
def preprocess_energy_data(raw_data):
    print("Preprocessing data...")

    # Flatten nested JSON
    df = pd.json_normalize(raw_data)

    print("\nMissing values before preprocessing:")
    print(df.isnull().sum())

    print("\nDuplicate rows before preprocessing:", df.duplicated().sum())

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(".", "_", regex=False)
        .str.replace(" ", "_", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    for col in ["state"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Convert year to numeric
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    # Convert all other non-text columns to numeric where possible
    for col in df.columns:
        if col not in ["state"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print("\nFinal shape:", df.shape)

    return df


def create_postgres_engine():
    return create_engine(POSTGRES_URI)


def push_clean_to_postgres(df, engine, table_name):
    print("Pushing preprocessed data to PostgreSQL...")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print("Preprocessed data stored in PostgreSQL.")


def main():
    #  Load JSON
    data = load_json_data(JSON_FILE_PATH)

    #  Push raw data to MongoDB
    mongo_client, db = create_mongo_connection()
    push_raw_to_mongo(data, db, RAW_COLLECTION)

    #  Retrieve raw data from MongoDB
    raw_data = retrieve_raw_from_mongo(db, RAW_COLLECTION)

    #  Preprocess data
    df_clean = preprocess_energy_data(raw_data)

    #  Push clean data to PostgreSQL
    engine = create_postgres_engine()
    push_clean_to_postgres(df_clean, engine, CLEAN_TABLE)

    # Close Mongo connection
    mongo_client.close()


if __name__ == "__main__":
    main()