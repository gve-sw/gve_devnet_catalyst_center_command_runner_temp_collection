from pymongo import MongoClient, errors
from decouple import config
from functools import lru_cache


@lru_cache
def get_db_client(host='localhost'):
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = config("DBSTRING")

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)
    return client


def create_ts(name='switch_temp'):
    """
    Create a new time series collection
    """
    client = get_db_client()
    db = client.device_temp
    try:
        db.create_collection(
            name,
            timeseries={
                "timeField": "timestamp",
                "metaField": "metadata",
                "granularity": "seconds"
            }
        )
    except errors.CollectionInvalid as e:
        print(f"{e}. Continuing")


def get_or_generate_collection(name="switch_temp"):
    client = get_db_client()
    db = client.device_temp
    create_ts(name=name)
    collection = db[name]
    return collection


def drop(name='switch_temp'):
    """
    Drop any given collection by name
    """
    client = get_db_client()
    db = client.device_temp
    try:
        db.drop_collection(name)
    except errors.CollectionInvalid as e:
        print(f"Collection error:\n {e}")
        raise Exception("Cannot continue")


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":

    # Get the database
    dbname = get_db_client()
