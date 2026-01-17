from pydantic import BaseModel


class LossSchema(BaseModel):
    loss: float
