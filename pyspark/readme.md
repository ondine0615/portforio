- 과거 15년도 L-members 대회에서 사용한 데이터입니다. K-training 과정 실습 중 얻게되었고, 이번 기회에 pyspark를 이용한 분석에 다시 사용하게 되었습니다. 다만 데이터의 제공한 곳과 학원의 계약에 따라 올리지 못한 파일들이 일부 존재합니다. 
  - 고객 정보 데이터, L-membership 데이터, 경쟁사 데이터, 구매데이터

# 문제의식
<img src="https://user-images.githubusercontent.com/76681523/210190286-e0b14c52-8293-45a3-96ac-72219a00c143.png" "width="40%">
![image](https://user-images.githubusercontent.com/76681523/210190286-e0b14c52-8293-45a3-96ac-72219a00c143.png width="40%"){:width="50" height="50"}
- 14년-15년에 있었던 전체적인 소비자 수 감소

# 탐색과정
1. Oracle Developer을 이용해 본래 고객정보, 구매내역 등 수개의 txt 파일로 분산되어 있었던 데이터들을 import (약 50GB)
2. python과 oracle을 연결한 뒤 성별, 나이대 등 다양한 소비자군을 나누어 소비자 수 감소에 유의미한 영향을 미치는 소비자층을 탐색
3. 이후 여성들 그 중에서도 20-30대의 여성들의 재방문율이 유의미하게 떨어졌다는 것을 확인하고 이를 기반으로 정보를 재범주화, 유의미한 데이터로 가공 cluster.csv로 저장.
![image](https://user-images.githubusercontent.com/76681523/210190595-d7d7fd30-6795-43f7-980e-28d1331f3a31.png){:width="50" height="50"}

# 분석과정
1. 추출한 데이터를 토대로 연관성을 분석하고, 군집화, 차원 축소 등을 고려해 매출감소 예측모델을 개발.
2. 예측모델로 도출된 인사이트와 통계를 이용해 매출감소고객들의 패턴을 분석하고자 함.

- 활용 방안은, 공통 특성을 가지고 있는 고객들의 행동 패턴을 파악하고, 이에 대응하는 가이드라인을 만드는 것입니다. 



- pyspark는 jupyter/pyspark-notebook docker image를 활용해 실행시켰습니다.(https://hub.docker.com/r/jupyter/pyspark-notebook)
