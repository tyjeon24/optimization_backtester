from datetime import datetime

import pandera as pa
from pandera.typing import Series


class PortfolioSchema(pa.DataFrameModel):
    """주식 데이터로 사용할 수 있는 pandas DataFrame 모델입니다.

    Args:
        Date: 날짜
        Portfolio: 주식 투자에 따른 계좌 가치 변화
        Baseline: 벤치마크(보통 ETF) 단순 바이앤홀드 시 가치 변화

    Examples:
        ```python
        class MyClass:
            @pa.check_types
            def __init__(self, df: DataFrame[PortfolioSchema]):
                self.df = df

        data = {"Date": [datetime.now()], "Portfolio": [1.0], "Baseline": [2.0]}
        df = pd.DataFrame(data)
        my_class = MyClass(df=df)
        ```

    Raises:
        pa.errors.SchemaError: 스키마와 일치하지 않을 때
    """

    Date: Series[datetime] = pa.Field()
    Portfolio: Series[float] = pa.Field()
    Baseline: Series[float] = pa.Field()

    class Config:
        strict = True
        coerce = True
