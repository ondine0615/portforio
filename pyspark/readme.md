과거 15년도 L-members 대회에서 사용한 데이터입니다. K-training 과정 실습 중 얻게되었고, 이번 기회에 pyspark를 이용한 분석에 다시 사용하게 되었습니다. 다만 데이터의 제공한 곳과 학원의 계약에 따라 올리지 못한 파일들이 일부 존재합니다. 
- 고객 정보 데이터, L-membership 데이터, 경쟁사 데이터, 구매데이터

cluster.csv 파일 정보
1. Oracle Developer을 이용해 본래 txt 파일로 존재하던 데이터를 sql로 import, 이후 고객정보,구매내역 등을 기반으로 정보를 재범주화, 유의미한 데이터로 가공했습니다.
2. 추출한 데이터를 토대로 연관성을 분석하고, 군집화, 차원 축소 등을 고려해 매출감소 예측모델을 개발했습니다.
3. 예측모델로 도출된 인사이트와 통계를 이용해 매출감소고객들의 패턴을 분석하고자 했습니다. 

- 활용 방안은, 공통 특성을 가지고 있는 고객들의 행동 패턴을 파악하고, 이에 대응하는 가이드라인을 만드는 것입니다. 

- pyspark는 jupyter/pyspark-notebook docker image를 활용해 실행시켰습니다.(https://hub.docker.com/r/jupyter/pyspark-notebook)
