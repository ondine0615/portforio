import os
import requests
from bs4 import BeautifulSoup
import webbrowser
import time

URL = "https://cafe.naver.com/ArticleList.nhn?search.clubid=10050146&search.menuid=334&search.boardtype=L"
my_arr = []  # 여태까지 확인한 모든 게시물 목록
#is_first = True
target = ["삼성", "갤럭시북", "LG", "gram", "엘지", "그램"]  # 1개라도 포함되야함
excepts = ["삽니다", "매입", "구매", "구입"]  # 1개라도 포함되면 안됨

def main():
    while True:
        html = request(URL)  # 중고나라 특정 게시판의 접속 URL
        soup = BeautifulSoup(html, 'html.parser')  # 요청 결과 분석
        tr_arr = soup.select('#main-area > div:nth-child(6) > table > tbody > tr')  # 원하는 element 추출 (CSS 선택자 사용)
        for tr in tr_arr:  # array 를 반복하여 모든 목록의 내용 확인을 위한 for loop
            is_new_item = True  # 기본적으로 '새 상품이 있을거야' 라고 기대함
            a_tag = tr.select_one('td.td_article > div.board-list > div > a')  # 게시물 제목을 확인
            map = {  # 게시물 데이터를 map 자료구조의 형태로 저장
                "title": a_tag.text.strip(),  # 제목
                "url": a_tag["href"],  # 방문할 URL
                "is_checked": False,  # 확인을 했는지 여부
            }

            for element in my_arr:  # 여태까지 확인한 모든 게시물을 다시 확인
                if element["url"] == map["url"]:  # 동일한 URL 이 있는지 확인
                    is_new_item = False  # 동일한게 있으면 새로운 상품이 아님
                    break  # 추가적인 확인은 무의미하므로 반복 중단

            if is_new_item:  # 만약 새로운 상품이라면?
                my_arr.insert(0, map)  # 저장

        if is_first:  # 알고리즘이 첫 실행이라면?
            global is_first  # 전역변수에 값을 새로 할당하기 위해, 전역변수를 사용할것이라고 표현
            is_first = False  # 이제는 처음이 아니라고 설정(Semaphore, 세마포어)
            for element in my_arr:  # 처음 목록은 전부 다
                element["is_checked"] = True  # 확인한걸로 처리 (귀찮으니까)
            continue  # 첫 설정하고 넘어감

        for element in my_arr:
            if not element["is_checked"]:
                element["is_checked"] = True
                print(f'TEST - element["title"] ==> ', element["title"])
                if any(x in element["title"] for x in target) and not any(x in element["title"] for x in excepts):
                    print(f'TEST - 새로운 아이템 등장 ==> ', element["title"])
                    webbrowser.open(f"https://cafe.naver.com{element['url']}")
                    notify(element["title"], '새로운 아이템 등장')

        print(f'reload')
        time.sleep(10)

def request(url):
    try:
        response = requests.request('GET', url)
    except Exception as e:
        print(e)
        notify('오류 발생', e)
        if e is ConnectionResetError or e is TimeoutError or e is ConnectTimeoutError or e is MaxRetryError or e is ConnectTimeout:
            print('재시도')
            request(url)
            return

    if response.status_code != 200:
        print(response.status_code)
        raise f'${response.status_code}'

    return response.text

def notify(title, text):
    # loop = asyncio.get_event_loop()
    # loop.run_in_executor(None, os.system, f"""
    #     osascript -e 'tell app "System Events" to display dialog "{title}"'
    # """)
    os.system(f"""
        osascript -e 'display notification "{title}" with title "{text}"'
    """)
    os.system(f'say "{title}"')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        notify('오류 발생', e)