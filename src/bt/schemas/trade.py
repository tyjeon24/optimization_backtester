from datetime import datetime

import pandera as pa
from pandera.typing import Series


class TradeSchema(pa.DataFrameModel):
    Date: Series[datetime] = pa.Field()
    Action: Series[float] = pa.Field(isin=["Buy", "Sell"])
    Strength: Series[float] = pa.Field()
    Ticker: Series[str] = pa.Field()
    Price: Series[float] = pa.Field(ge=0)
    PortfolioPrice: Series[float] = pa.Field(ge=0)
    Quantity: Series[int] = pa.Field(ge=0)
    Tax: Series[float] = pa.Field(ge=0)
    Cash: Series[float] = pa.Field(ge=0)
    Margin: Series[float] = pa.Field()
    PortFolioValue: Series[float] = pa.Field()

    class Config:
        strict = True
        coerce = True
