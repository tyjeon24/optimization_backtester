from datetime import datetime

import pandera as pa
from pandera.typing import Series


class StockSchema(pa.DataFrameModel):
    """주식 데이터로 사용할 수 있는 pandas DataFrame 모델입니다.

    Args:
        Date: 날짜
        Open: 시가
        High: 고가
        Low: 저가
        Close: 종가
        Volume: 거래량

    Examples:
        ```python
        class MyClass:
            @pa.check_types
            def __init__(self, df: DataFrame[StockSchema]):
                self.df = df

        data = {"Date": [datetime.now()], "Open": [1.0], "High": [2.0], "Low": [0.9], "Close": [1.5], "Volume": [30.0]}
        df = pd.DataFrame(data)
        my_class = MyClass(df=df)
        ```

    Raises:
        pa.errors.SchemaError: 스키마와 일치하지 않을 때
    """

    Date: Series[datetime] = pa.Field()
    Open: Series[float] = pa.Field(ge=0)
    High: Series[float] = pa.Field(ge=0)
    Low: Series[float] = pa.Field(ge=0)
    Close: Series[float] = pa.Field(ge=0)
    Volume: Series[int] = pa.Field(ge=0)
    Ticker: Series[str] = pa.Field()

    class Config:
        strict = True
        coerce = True


class StockActionSchema(StockSchema):
    """주식 데이터로 사용할 수 있는 pandas DataFrame 모델입니다.

    Args:
        Action: 구매, 판매 신호입니다.

    Examples:
        ```python
        class MyClass2:
            @pa.check_types
            def __init__(self, df: DataFrame[StockActionSchema]):
                self.df = df

        data = {"Date": [datetime.now()], "Open": [1.0], "High": [2.0], "Low": [0.9], "Close": [1.5], "Volume": [30.0]}
        data["Action"] = ["Buy"]
        df = pd.DataFrame(data)
        my_class = MyClass2(df=df)
        ```

    Raises:
        pa.errors.SchemaError: 스키마와 일치하지 않을 때
    """

    Action: Series[str] = pa.Field(isin=["Buy", "Sell"])

    class Config:
        strict = False
        coerce = True
