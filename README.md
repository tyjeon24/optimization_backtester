# 구매 전략 정리

1. 단순 골든크로스 : "MovingAverage5 > MovingAverage120"
2. MACD > 0 : 실제로는 "MovingAverage12 > MovingAverage26" 식과 동일
3. MACD > Signal : 
4. RSI > 70
5. 볼린저 밴드 갭
   1. 표준편차 +1, +2, +3, -1, -2, -3선을 각각 B1, B2, B3, B-1, B-2, B-3이라고 하자.
   2. 각 표준편차별 편차를 Gap1, Gap2, Gap3이라고 하자
      1. 이것도 뺄셈보다 나눗셈이 좋을수도 있음
   3. 이 Gap은 실제론 MACD와 역할이 같음.
      1. 그러나 '절대로' 크로스는 발생하지 않음. 즉 >0, <0 조건은 무의미함.
      2. 대신 갭이 좁아지고 넓어지는 값은 쓸 수 있음.
      3. 예시1: SingleMomentum을 넣어서 '지속감소 몇턴간'인 경우 구매/판매
      4. 예시2: Gap의 이동평균이 얼마 이하 이렇게 적어도 될 듯.

# 포트폴리오 클래스
* 사용자는 '그래서 이 전략 결과가 어때?'라는 질문을 할 것이며 이에 답해줄 데이터 보고서가 필요.
* 포트폴리오 클래스가 이 역할을 해 줌.
* portfolio init
  * Portfolio(metric="cagr", constraints=["mdd <= 15"])
* portfolio.report : pd.DataFrame
  * pandas dataframe 변수
  * cash : float
  * final_value : float
  * portfolio_return:float = cash 
  * start:datetime
  * end:datetime
  * baseline : SPY 단순 바이앤홀드 시 수익률(최종값/최초값)
  * alpha:float, SPY 구매하는 것보다 더 얻게 될 초과수익률. 예: spy 단순 바이앤홀드가 5%, 이 전략이 7%라면 alpha=7-5=2
    * 이 값은 portfolio_return - baseline으로 계산하면 됨
  * cagr:float : 크면 좋음
  * mdd:float : 작으면 좋음
  * calmar_ratio:float = cagr/mdd : 크면 좋음
  * win_rate : 판매 시 익절비율 / (전체판매횟수)