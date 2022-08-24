# Airflow를 이용한 twitch emoji 자동 사용량 추적 파이프라인 구축 

## 설명

- Amazon의 자회사 중 하나인 인터넷 방송 플랫폼 Twitch에서는 시청자가 특정 인터넷 방송인의 구독권을 구매한 뒤 채팅창 내에서 이모티콘을 사용할 수 있는 권리를 얻을 수 있습니다. 
  - 실제 사용 emoji 예시 ) https://twitchemotes.com/channels/49045679
- 이 이모티콘의 사용은 단순히 방송의 가용자원을 보다 다채롭게 만들어 보다 재미있는 방송을 만들어 나갈 수 있는 바탕을 제공한다고 할 수 있습니다. 하지만, 사업적인 측면에서 볼 때, 구독권을 통한 인터넷 방송인의 수익창출에 많은 영향을 미치는 요소 중 하나라고 파악할 수 있습니다. 즉, 1달마다 한번씩 자동결제하는 시스템을 통해 어느 정도 계산이 가능한 고정수입을 얻을 수 있는 것입니다.
  - 예를 들어 1000명의 구독자 수를 확보한 방송인의 경우라면, 플랫폼 수수료와 세금을 모두 지불한 뒤 약 300만원의 고정수입을 얻을 수 있다고 파악할 수 있습니다.


  
## 구성
  
  ![다운로드 (1)](https://user-images.githubusercontent.com/76681523/163663999-a1ee034e-b85b-4af4-af0a-5ecc0bb1c0eb.jpg)

- 


### twitch_chat_airflow.py
- airflow의 설정파일입니다.
  - 전체적인 과정은 1. 수집 - 2. 처리 - 3. 저장 - 4. 시각화 하는 과정을 거칩니다. 

1. extract_from_website.py
- Twitch의 미러사이트에서 VOD의 ID, 방송 날짜를 가지고 와 TwitchDownloadCLI를 통해 채팅 로그를 text 파일 형태로 수집합니다.
  - 수집된 텍스트의 예시
    - ![image](https://user-images.githubusercontent.com/76681523/165242664-fafa1b0e-d041-454e-bf9c-ba7981b16d40.png)
  
2. emotion_count_all.py, OR emotion_count_3.py
- all.py 파일은 수집한 모든 .txt 파일을 모두 전처리 과정을 거칠 수 있게 만들어 놓은 것이고,
- 3.py 파일은 가장 최근에 수집한 .txt 파일들만 전처리 과정을 거쳐 csv파일로 변환할 수 있게끔 만들어 놓은 파일입니다.
  - 전자는 전체 text 형태의 파일들을 분석하고, 후자는 가장 최근의 파일만 분석합니다. 이 때의 airflow 실행 주기는 daily로 설정되어있는 바, 가장 최근의 파일만 분석해 csv 파일로 변환할 수 있도록 함이 옳지만, 수집 초기에 부득이하게 한번에 많은 파일을 분석해야 하는 경우 count_all.py 파일을 사용할 수 있습니다. 
    - 분석 후 csv 파일의 형태
    - ![image](https://user-images.githubusercontent.com/76681523/165243274-c45f0314-8675-411c-bced-41e72ca293d5.png)
      - 앞서 볼 수 있었던 각종 채팅 로그들은 모두 삭제되고, 그 날 방송에서 사용된 이모티콘의 사용량만 추적한 것을 확인할 수 있습니다. 
3. concat_csv.py
- 처리를 끝낸 후 폴더 내에 날짜별로 저장되어 있던 csv 파일들을 하나의 표로 합친 후 구해 놓았던 계산값들의 총합으로 구성합니다. 이는 db로 넘어가는 데이터의 바로 전 단계입니다.
- ![image](https://user-images.githubusercontent.com/76681523/165245860-7e393858-fb95-4afc-be59-f36b72adeac9.png)
  - 처리를 통해 모든 csv 파일에서 계산한 count 값들이 하나로 합쳐졌고, airflow에서  sqlite operator를 통해 result.db로 저장한 뒤 superset에서 저장한 설정값에 따라 자동으로 시각화하 수 있습니다. 
  - 

- ![image](https://user-images.githubusercontent.com/76681523/165246210-593f6b7c-8b36-41fd-a967-e40509fcb030.png) 
  - SUPERSET 쿼리 결과 파일
- ![image](https://user-images.githubusercontent.com/76681523/165255978-78fa6db7-ac05-47ab-8481-0f6f1a084fc4.png)
  - PIE 형태로 시각화   




## 더 나아가

비지니스적인 측면에서 접근하였으나, 현 사회를 관통하는 주제 중 하나인 밈(meme)에 대해 더 큰 함의를 가지고 있다는 것을 어느 순간부터 깨닫게 되었습니다. 시간이 될 때 이에 대한 다양한 측면에서의 분석을 더 해보고자 합니다. 
