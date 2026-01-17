import pandas as pd

from src.bt.metrics.alpha import Alpha
from src.bt.metrics.cagr import CAGR
from src.bt.metrics.calmar_ratio import CalmarRatio
from src.bt.metrics.mdd import MDD


def test_backtester_evaluate(backtester):
    # 이 테스트는 백테스트 핵심 부분인 모델의 주식 백테스팅 기능이 작동함을 보장합니다.
    loss_metric_name = backtester.metric
    loss = backtester.evaluate()
    assert isinstance(loss, dict)
    assert loss_metric_name in loss.keys()


def test_backtester_fit(backtester):
    # 이 테스트는 베이지안 최적화 기반의 파라미터 최적화가 작동함을 보장합니다.
    n_trials = 3
    backtester.fit(n_trials=n_trials)
    optimizer_result = backtester.optimizer.show_results()
    assert isinstance(optimizer_result, pd.DataFrame)
    assert len(optimizer_result) == n_trials


def test_backtester_result_trade(backtester_fitted):
    # 이 테스트는 최적화된 주식 공식의 거래 시뮬레이션 기록을 받아볼 수 있음을 보장합니다.

    trade_df_columns = [
        "Date",
        "Action",
        "Ticker",
        "Price",
        "PortfolioPrice",
        "Quantity",
        "Cash",
        "Margin",
        "PortfolioValue",
    ]

    assert isinstance(backtester_fitted.prediction.get("trade"), pd.DataFrame)
    for column in trade_df_columns:
        assert (
            column in backtester_fitted.prediction["trade"].columns
        ), f"The column '{column}' does not exist in backtester trade columns."


def test_backtester_result_portfolio(backtester_fitted):
    # 이 테스트는 최적화된 주식 공식이 매일 얼마의 수익을 거두는지와 기준선(ETF)을 받아볼 수 있음을 보장합니다.

    portfolio_df_columns = ["Portfolio", "Baseline"]

    portfolio = backtester_fitted.prediction.get("portfolio")
    assert isinstance(portfolio, pd.DataFrame)
    assert pd.api.types.is_datetime64_any_dtype(portfolio["Date"])
    for column in portfolio_df_columns:
        assert (
            column in backtester_fitted.prediction["portfolio"].columns
        ), f"The column '{column}' does not exist in backtester trade columns."


def test_metrics_calmar_ratio(backtester_fitted):
    # Calmar Ratio 계산 기능
    assert isinstance(CalmarRatio().calculate(backtester_fitted.prediction["portfolio"]), float)


def test_metrics_cagr(backtester_fitted):
    # CAGR 계산 기능
    assert isinstance(CAGR().calculate(backtester_fitted.prediction["portfolio"]), float)


def test_metrics_mdd(backtester_fitted):
    # MDD 계산 기능
    assert isinstance(MDD().calculate(backtester_fitted.prediction["portfolio"]), float)


def test_metrics_alpha(backtester_fitted):
    # Alpha 계산 기능
    assert isinstance(Alpha().calculate(backtester_fitted.prediction["portfolio"]), float)


def test_backtester_sliding_test(backtester_fitted):
    # 이 테스트는 백테스트 구간을 쪼개어, 여러 종류의 market regime에 대해 강건한 모델을 만드는 sliding test기능을 보장합니다.
    # 주식 시장은 다양한 요인에 의해 변화하며 과거 데이터만으로 미래를 100% 예측할 수는 없습니다.
    # 예측할 수 없는 항목들 : (1) 주식 시장 외부 이벤트 (2) 기업 공시에 따른 급변 등
    # 마찬가지로 2023년까지 잘 작동하는 모델이라도, 2024년에는 잘 작동하지 않을 수 있습니다.
    # 그러나 과거 데이터의 여러 상황에서 강건한 모델은 미래에 상대적으로 더 잘 작동하리라고 생각할 수 있습니다.
    # 예) Market regime에 강건한 모델은 상승장, 하락장과 무관하게 적용할 수 있습니다.
    # sliding_test는 Market regime에 대한 강건성을 확보하려는 시도입니다.
    # 예) 2020~2021년 단일 테스트가 아니라, 2020.01 ~ 2020.06, 2020.02 ~ 2020.07, ..., 2020.07 ~ 2020.12에 대해 1개월마다 밀어가며 테스트하고, 최악의 성과를 지표로 선정합니다.

    # 이걸 어떻게 테스트하지?
    # start end를 명시적으로 넘겨주고,
    # 1달 step 1년 길이로 하면 몇개월치 나오는지 알 수 있을 거임
    # losses 리스트에 저장하도록 하고
    # assert len(losses) == 5 뭐 이렇게 하면 될 듯?
    assert len(backtester_fitted.alphas) == 3
    assert len(backtester_fitted.alphas) == len(backtester_fitted.mdds)


def test_backtester_predict(backtester_fitted):
    prediction = backtester_fitted.predict(start="20200101")
    assert len(prediction) == 2
