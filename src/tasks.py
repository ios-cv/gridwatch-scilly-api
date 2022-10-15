import csv
import requests
import time

from datetime import datetime
from dateutil.parser import parse
from io import StringIO

from .db import engine, SessionLocal
from .models import Base, DataLoad, TransformerBasic


def start_of_today():
    return datetime.combine(datetime.now(), datetime.time.min)


def update_live_transformer_primary():
    db = SessionLocal()
    try:
        # Check in the database when we last updated this.
        last_load = db.query(DataLoad).filter(DataLoad.dataset == "live_primary").order_by("time").first()

        # If it's worth looking for new data, then retrieve it from the WPD API.
        if last_load is not None and last_load.time > start_of_today():
            print("Not worth looking for new data. Return.")
            return

        # FIXME: For some reason the WPD API returns stale data for this resource, but the CSV donwload link stays up
        #        to date... Until they fix this (or I figure out what I'm doing wrong), we'll stick to downloading the
        #        JSON data instead.

        print("Make network request.")
        r = requests.get(
            "https://connecteddata.nationalgrid.co.uk/dataset/3c00a5e2-5ce2-4324-815c-cf4a0753fe42/resource/6a3026eb-95c2-4796-9b08-0b78d80c5e2a/download/isles-of-scilly.csv"
        )
        print("Network request completed.")

        f = StringIO(r.text)
        reader = csv.DictReader(f)

        parsed_data = []
        for line in reader:
            parsed_data.append((
                parse(line["time"]),
                line["value"]
            ))

        # Check if retrieved data is new.
        if last_load is not None and last_load.props["end_time"] >= parsed_data[-1][0]:
            print("Data is not new. Return.")
            return

        # If it is, write it to the database.
        objs = []
        for d in parsed_data:
            objs.append(
                TransformerBasic(time=d[0], power=d[1])
            )
        db.bulk_save_objects(objs)

        # Update the last checked data if we got anything new.
        db.add(DataLoad(
            dataset="live_primary",
            time=datetime.utcnow(),
            props={"end_time": parsed_data[-1][0].strftime("%Y%m%dT%H%M%S")}
        ))

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    print("Starting schedule tasks runner.")

    # Create the database schema if it doesn't exist.
    print("Creating database tables if required.")
    Base.metadata.create_all(bind=engine)

    print("Starting task scheduler main loop.")
    while True:
        print("Task scheduler triggered.")

        update_live_transformer_primary()

        # Wait for next iteration time.
        print("Task scheduler run completed. Waiting for next time.")
        time.sleep(300)
