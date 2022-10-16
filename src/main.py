import datetime

from typing import Union
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import models
from . import schemas

from .db import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/grid/flow", response_model=schemas.PowerTimeSeries)
def read_grid_flow(days: int = 1, db: Session = Depends(get_db)):
    # Calculate the cut-off time.
    today = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
    start = today + datetime.timedelta(days=1 - days)

    # Get the flow data from the database for the number of days less 1.
    data = (
        db.query(models.TransformerBasic)
        .filter(models.TransformerBasic.time >= start)
        .order_by(models.TransformerBasic.time.asc())
        .all()
    )

    results_so_far = [i for i in data]

    # Estimate today's flow data (make it same as yesterday's)
    # TODO: Add a more sophisticated estimation model in future.
    yesterday = today + datetime.timedelta(days=-1)

    # Get yesterday's data.
    data = (
        db.query(models.TransformerBasic)
        .filter(models.TransformerBasic.time >= yesterday)
        .filter(models.TransformerBasic.time < today)
        .order_by(models.TransformerBasic.time.asc())
        .all()
    )

    now = datetime.datetime.utcnow()
    for d in data:
        i = {"power": d.power, "time": d.time + datetime.timedelta(days=1)}
        if i["time"] < now:
            results_so_far.append(i)

    # Return results
    return results_so_far
