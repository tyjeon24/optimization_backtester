from src.bt import *

band1 = BollingerBand(
    use_exponential_moving_average=False,
    moving_average_name="MiddleBand1",
    upper_band_name="UpperBand1",
    lower_band_name="LowerBand1",
    band_gap_name="BandGap1",
    target="Close",
)

band1.parameters = [
    {"name": "period", "type": "fixed", "value": 20, "value_type": "int"},
    {"name": "upper_multiplier", "type": "fixed", "value": 1.0, "value_type": "float"},
    {"name": "lower_multiplier", "type": "fixed", "value": 1.0, "value_type": "float"},
    {"name": "use_exponential_moving_average", "type": "fixed", "value": False, "value_type": "bool"},
]

band2 = BollingerBand(
    use_exponential_moving_average=False,
    moving_average_name="MiddleBand2",
    upper_band_name="UpperBand2",
    lower_band_name="LowerBand2",
    band_gap_name="BandGap2",
    target="Close",
)

band2.parameters = [
    {"name": "period", "type": "fixed", "value": 20, "value_type": "int"},
    {"name": "upper_multiplier", "type": "fixed", "value": 2.0, "value_type": "float"},
    {"name": "lower_multiplier", "type": "fixed", "value": 2.0, "value_type": "float"},
    {"name": "use_exponential_moving_average", "type": "fixed", "value": False, "value_type": "bool"},
]

band3 = BollingerBand(
    use_exponential_moving_average=False,
    moving_average_name="MiddleBand3",
    upper_band_name="UpperBand3",
    lower_band_name="LowerBand3",
    band_gap_name="BandGap3",
    target="Close",
)

band3.parameters = [
    {"name": "period", "type": "fixed", "value": 20, "value_type": "int"},
    {"name": "upper_multiplier", "type": "fixed", "value": 3.0, "value_type": "float"},
    {"name": "lower_multiplier", "type": "fixed", "value": 3.0, "value_type": "float"},
    {"name": "use_exponential_moving_average", "type": "fixed", "value": False, "value_type": "bool"},
]
ma20 = MovingAverage(name="MA20")
ma20.parameters = [
    {"name": "period", "type": "fixed", "value": 20, "value_type": "int"},
    {"name": "use_exponential_moving_average", "type": "fixed", "value": False, "value_type": "bool"},
]
ma60 = MovingAverage(name="MA60")
ma60.parameters = [
    {"name": "period", "type": "fixed", "value": 60, "value_type": "int"},
    {"name": "use_exponential_moving_average", "type": "fixed", "value": False, "value_type": "bool"},
]
ma120 = MovingAverage(name="MA120")
ma120.parameters = [
    {"name": "period", "type": "fixed", "value": 120, "value_type": "int"},
    {"name": "use_exponential_moving_average", "type": "fixed", "value": False, "value_type": "bool"},
]
ma200 = MovingAverage(name="MA200")
ma200.parameters = [
    {"name": "period", "type": "fixed", "value": 200, "value_type": "int"},
    {"name": "use_exponential_moving_average", "type": "fixed", "value": False, "value_type": "bool"},
]

# setup model
models = [
    band1,
    band2,
    band3,
    ma20,
    ma60,
    ma120,
    ma200,
    RSI(),
    SingleMomentum(),
    MACDDivision(),
    CompareColumn(left="Close", right="MA20", symbol=">", name="BuyCloseOver200MA", action="buy"),
    CompareColumn(left="MA20", right="MA60", symbol=">", name="Buy20Over600MA", action="buy"),
    CompareColumn(left="MA60", right="MA120", symbol=">", name="Buy60Over120MA", action="buy"),
    CompareColumn(left="MA120", right="MA200", symbol=">", name="Buy120Over200MA", action="buy"),
    CompareColumn(left="Close", right="LowerBand1", symbol="<", name="BuyBelowLowerBand", action="buy"),
    CompareValue(left="RSI", symbol="<", name="BuyAtLowRSI", bound_min=1, bound_max=50, action="buy"),
    CompareValue(left="BandGap1", symbol="<", name="BuyNarrowBandGap1", bound_min=0.1, bound_max=3, action="buy"),
    CompareValue(left="BandGap2", symbol="<", name="BuyNarrowBandGap2", bound_min=0.1, bound_max=3, action="buy"),
    CompareValue(left="BandGap3", symbol="<", name="BuyNarrowBandGap3", bound_min=0.1, bound_max=3, action="buy"),
    CompareColumn(left="MACD", right="MACDSignal", symbol=">", name="MACDGoldenCross", action="buy"),
    CompareValue(left="MACD", symbol=">", name="MACDGoesUp", bound_min=-10, bound_max=10, action="buy"),
    CompareValue(left="RSI", symbol=">", name="SellAtHighRSI", bound_min=50, bound_max=100, action="sell"),
    CompareColumn(left="Close", right="UpperBand1", symbol="<", name="SellAboveUpperBand", action="sell"),
    CompareValue(left="BandGap1", symbol="<", name="BuyNarrowBandGap1", bound_min=0.1, bound_max=3, action="sell"),
    CompareValue(left="BandGap2", symbol="<", name="BuyNarrowBandGap2", bound_min=0.1, bound_max=3, action="sell"),
    CompareValue(left="BandGap3", symbol="<", name="BuyNarrowBandGap3", bound_min=0.1, bound_max=3, action="sell"),
    CompareColumn(left="Close", right="MA20", symbol="<", name="SellCloseUnder200MA", action="sell"),
    CompareColumn(left="MA20", right="MA60", symbol="<", name="Sell20Under600MA", action="sell"),
    CompareColumn(left="MA60", right="MA120", symbol="<", name="Sell60Under120MA", action="sell"),
    CompareColumn(left="MA120", right="MA200", symbol="<", name="Sell120Under200MA", action="sell"),
]

# setup model 연속값 활용
models_new = [
    band1,
    band2,
    band3,
    ma20,
    ma60,
    ma120,
    ma200,
    RSI(),
    SingleMomentum(),
    MACDDivision(),
    CompareColumn(left="Close", right="MA20", symbol="/", name="BuyCloseOver200MA", action="buy"),
    CompareColumn(left="MA20", right="MA60", symbol="/", name="Buy20Over600MA", action="buy"),
    CompareColumn(left="MA60", right="MA120", symbol="/", name="Buy60Over120MA", action="buy"),
    CompareColumn(left="MA120", right="MA200", symbol="/", name="Buy120Over200MA", action="buy"),
    CompareColumn(left="LowerBand1", right="Close", symbol="/", name="BuyBelowLowerBand", action="buy"),
    CompareColumn(left="MACD", right="MACDSignal", symbol="/", name="MACDGoldenCross", action="buy"),
    CompareColumn(left="MACDSignal", right="MACD", symbol="/", name="MACDDeadCross", action="sell"),
    CompareColumn(left="Close", right="UpperBand1", symbol="/", name="SellAboveUpperBand", action="sell"),
    CompareColumn(left="MA20", right="Close", symbol="/", name="SellCloseUnder200MA", action="sell"),
    CompareColumn(left="MA60", right="MA20", symbol="/", name="Sell20Under600MA", action="sell"),
    CompareColumn(left="MA120", right="MA60", symbol="/", name="Sell60Under120MA", action="sell"),
    CompareColumn(left="MA200", right="MA120", symbol="/", name="Sell120Under200MA", action="sell"),
    CompareValue(left="RSI", symbol="<", name="BuyAtLowRSI", bound_min=1, bound_max=50, action="buy"),
    CompareValue(left="MACD", symbol=">", name="MACDGoesUp", bound_min=-10, bound_max=10, action="buy"),
    CompareValue(left="RSI", symbol=">", name="SellAtHighRSI", bound_min=50, bound_max=100, action="sell"),
    CompareValue(left="BandGap1", symbol="<", name="BuyNarrowBandGap1", bound_min=0.1, bound_max=3, action="buy"),
    CompareValue(left="BandGap2", symbol="<", name="BuyNarrowBandGap2", bound_min=0.1, bound_max=3, action="buy"),
    CompareValue(left="BandGap3", symbol="<", name="BuyNarrowBandGap3", bound_min=0.1, bound_max=3, action="buy"),
    CompareValue(left="BandGap1", symbol="<", name="SellNarrowBandGap1", bound_min=0.1, bound_max=3, action="sell"),
    CompareValue(left="BandGap2", symbol="<", name="SellNarrowBandGap2", bound_min=0.1, bound_max=3, action="sell"),
    CompareValue(left="BandGap3", symbol="<", name="SellNarrowBandGap3", bound_min=0.1, bound_max=3, action="sell"),
]
