import datetime

from pydantic import BaseModel


class PowerAtTime(BaseModel):
    time: datetime.datetime
    power: float

    class Config:
        orm_mode = True


PowerTimeSeries = list[PowerAtTime]
