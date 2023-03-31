
### 기능을 추가하며 일부 수정 중에 있습니다. (등록번호 -> 등록&출원번호에 의한 정보 저장)
 

# 들어가며

- 특허청의 자회사인 Kipris plus에서 제공하는 api를 airflow를 활용해 필요한 정보들을 mysql에 적재하는 과정을 일부 구현했습니다.

# 프로젝트 구조
![image](https://user-images.githubusercontent.com/76681523/229028890-e928dee8-e583-4c45-84de-3232282b76b5.png)


## 설명
![image](https://user-images.githubusercontent.com/76681523/229028944-23035cf6-fe14-4569-a82b-97584d63a737.png)

1. 변동사항 api를 통해 변동된 정보가 있는 특허번호를 받아 redis에 일시적으로 저장합니다.
2. 저장된 번호를 하나씩 꺼내 전체 데이터를 요청합니다. 
3. 받아온 데이터를 양식에 맞게 db에 저장
4. 저장된 데이터들은 Django를 이용, 자동으로 api로 제공하게끔 합니다. 
