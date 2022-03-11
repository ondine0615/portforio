Company Guide(https://comp.fnguide.com/)   
등급별 금리스프레드 테이블(https://www.kisrating.co.kr/ratingsStatistics/statics_spread.do)

Company Guide 에서 제공하는 기업 정보와 한국신용평가에서 제공하는 등급별 금리스프레드 정보를 가지고 와서

" 이 기업이 투자할만한 가치가 있는 회사인가? " 에 대해 편하게, 그리고 좀 길게 알아보고자 만든 코드입니다. 

**  Chrome browser과, chromedriver를 먼저 설치하셔야 합니다. - 2022년 3월 시점 최신 버전은 99버전입니다. 베타 버전이 아마 100버전였던걸로 기억합니다. 
**  selenium, BeautifulSoup4, pandas가 설치되어있어야 합니다.
**  airflow를 통한 scheduling이 필요합니다. 
**  본 코드는 Ubuntu20.04 server 상에서 제작되었습니다. (근데 어차피 airflow랑 같이 돌릴려면 리눅스 상에서 돌려야 했었나)
**  계산은 컴퓨터가 해주지만, 판단은 본인이 직접 하셔야 합니다. 
**  학습 과정에서 제작한 코드입니다. 
