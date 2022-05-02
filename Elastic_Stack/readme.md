## filebeat 설정
** 우분투20.04 서버 기준 /etc/filebeat/filebeat.yml을 열어 편집하시면 됩니다. 
  
Filebeat는 lumberjack 프로토콜(over TCP)을 통해 Logstash(이하 로그스태시)로 다이렉트로 이벤트 전송이 가능합니다.   
로그스태시를 아웃풋으로 두려면 엘라스틱서치 아웃풋은 사용하지 않아야 합니다. 이를 위해선 아래쪽에 있는 elasticsearch 관련한 설정은 주석처리한 뒤, 아래와 같이 로그스태시 url을 설정하시면 됩니다.    

output.logstash:    
  hosts: ["127.0.0.1:5044"]            
![image](https://user-images.githubusercontent.com/76681523/166200351-a8941eb1-4fcc-423c-9b23-3867b5b4cae2.png)

인덱스 템플릿을 자동으로 불러오는 옵션은 엘라스틱서치 아웃풋일 때만 작동합니다. 때문에 이 설정을 사용하기 위해서는 반드시 수동으로 엘라스틱서치 인덱스 템플릿을 로드해야 합니다.              
 
## docker 설정   

https://github.com/deviantony/docker-elk   

내려받은 docker-compose.yml 파일을 열어보면 services.elasticsearch.build 내에 container_name 란이 있습니다. 이를 주석처리해야 docker-compose 파일 실행시에 에러가 나지 않습니다.   

## Kibanna 설정  

kibanna는 index pattern을 설정한 뒤에 사용할 수 있습니다. 관련한 구체적인 설명들은 https://www.youtube.com/watch?v=yF5z6zf4EH4 를 통해 전문가의 설명을 들을 수 있습니다.  

![image](https://user-images.githubusercontent.com/76681523/166200961-fa08ffcd-909d-48c8-af0d-d5f45b1d463a.png)
최종적인 결과물은 Visualize 탭에서 확인할 수 있습니다. 

