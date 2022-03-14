Company Guide(https://comp.fnguide.com/)   
등급별 금리스프레드 테이블(https://www.kisrating.co.kr/ratingsStatistics/statics_spread.do)

Company Guide 에서 제공하는 기업 정보와 한국신용평가에서 제공하는 등급별 금리스프레드 정보를 가지고 와서

" 이 기업이 투자할만한 가치가 있는 회사인가? " 에 대해 편하게, 그리고 좀 길게 차근차근 살펴보고 싶어 만든 코드입니다. 

**  Chrome browser과, chromedriver를 먼저 설치하셔야 합니다. - 2022년 3월 시점 최신 버전은 99버전입니다. 베타 버전이 아마 100버전였던걸로 기억합니다.   
**  selenium, BeautifulSoup4, pandas가 설치되어있어야 합니다.  
**  airflow를 통한 scheduling이 필요합니다.     
**  계산은 컴퓨터가 해주지만, 투자 판단은 본인이 직접 하셔야 합니다.     
**  학습 과정에서 제작한 코드입니다. 적절한 판단이 필요합니다.    
**  전날이 공휴일이였다거나 주말이었다면 날짜를 그 전으로 바꿔야 작동합니다. 빨간 날에는 데이터가 올라오지 않아 out of the range 버그가 납니다.  
**  본 코드는 Ubuntu20.04 server 상에서 제작되었습니다. 윈도우와 달리 따로 import 할 것들이 필요합니다.
- from selenium.webdriver.common.by import By  
- from pyvirtualdisplay import Display     
- 사용방법과 설치방법은 이를 구글링하면 바로 나올 것입니다.   
( ** Chromedriver 관련해서 번거로운 것이 싫다면, 그냥 자동으로 버전을 찾아 드라이버를 적용시켜주는 패키지를 사용하셔도 무방합니다. 실제로 이번 기회에 사용해 보았는데 일회성으로 사용하기에 좋았습니다. 다만 지속적으로 셀레니움을 사용할 일이 있다면 driver을 다운받아 경로를 지정해 주시는게 좋지 않을까 싶습니다.  
다운은 [ pip install chromedriver-autoinstaller] 을 통해 가능합니다. 


#-------------------------------------------------


