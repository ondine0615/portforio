현재 진행 중에 있는 프로젝트입니다.  
"트위치에서 진행하고 있는 특정 인터넷 방송의 채팅을 분석하여 감정분석을 할 수 있을까?"
라는 스스로의 물음에 답하기 위한 과정이라고 프로젝트라고 할 수 있습니다. 

보다 자세한 방법론으로는 

1. chatty를 통해 생성한 twitch 방송의 채팅log를 
2. filebeat에서 json 형식으로 변환, 
3. kakfa producer에 넘긴 뒤, 
4. 이를 spark streaming의 sql 기능을 통해 통해 분석하려고 하고 있습니다.

전에 twitter의 api를 땡겨올 때는 logstash를 사용했습니다. 그래서 이번에는 동일사에서 나온 프로그램인 filebeat를 사용했습니다.   

노트북으로 서버를 올려 사용하고 있는 바, filebeat는 logstash에 비해 가볍고 cpu와 ram 리소스를 상당히 적게 소모한다는 장점이 좋은 편입니다.   

spark_streaming를 사용한 이유 또한  인터넷 방송 시간 동안 폭발적으로 채팅이 올라오기 때문에 서버 과부하를 방지할 수 있는 장점이 있습니다.

이에 스파크의 기능 중 지연처리(lazy evaluation) 방식으로 텀을 두고 한꺼번에 처리하는 것이 오히려 장점으로 작용할 수 있는 것이, 단일작업을 하는 만큼 다른 작업을 기다릴 때 오는 병목현상이 일어나지 않기 때문입니다.

하지만 아직까지는 에러를 해결하지 못해 일시적으로 멈춰져있는 상태입니다. 향후 업데이트를 통해 보완할 계획입니다.


# Twitter api - Kafka 연동방법에 대해
- Kafka의 기본적인 원리와 사용방법에 대해 익히며 진행했던 간단한 과정입니다. 

- AWS ec2 서비스를 기반으로 실행한다면 Amazon Linux 서비스를 기반으로 구축하거나, 따로 하드웨어에 서버를 설치하고자 한다면 rocky-linux를 통해 보다 편하게 진행할 수 있습니다.
- 레드헷 공식 홈페이지에서 개발전용 무료 프로그램을 등록한 뒤 설치해도 좋습니다. 
  - 데비안 계열 소프트웨어를 사용하실 때에는 그에 따라 조금 달리 실행하셔야 합니다.
  - Kali-Linux 다운로드 링크(https://rockylinux.org/download/)
  - RED HAT ENTERPRISE LINUX 다운로드 가이드(https://access.redhat.com/documentation/ko-kr/red_hat_enterprise_linux/7/html/installation_guide/chap-download-red-hat-enterprise-linux)
  
### 1. web service 실행
yum update -y   
yum install httpd -y   
sudo service httpd start  

### 2. java 설치  
안정성을 위해 자바8 서비스를 이용합니다.  
sudo yum install -y java-1.8.0-openjdk-devel.x86_64  

java –version  

### 3. Kafka 설치
wget https://dlcdn.apache.org/kafka/3.0.0/kafka_2.13-3.0.0.tgz  
tar xvf kafka_2.13-3.0.0.tgz   

### 4. Kafka 실행

- 브로커 실행
  - cd [카프카 설치 디렉토리]   
  - ./bin/zookeeper-server-start.sh config/zookeeper.properties & 
  - Daemon 확인법
    - sudo netstat -anp | egrep "9092|2181"
    - 브로커의 점유포트는 9092 입니다.

- Topic 생성
  - bin/kafka-topics.sh --create --topic twitter --partitions 1 --replication-factor 1 --bootstrap-server localhost:9092  &
  - 확인
    - bin/kafka-topics.sh --list --bootstrap-server localhost:9092

- Consumer 실행
  - EC2 프리티어 서비스를 이용하고 있다면, 새로운 인스턴스를 생성하여 위의 설치과정을 반복해야 합니다. 그 이후
    - ./bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic twitter --from-beginning 
    - 으로 kafka의 consumer을 실행시킬 수 있습니다. 

- Producer 실행
  - Producer은 데이터가 들어오는 입구와 같은 역할을 합니다. 이 곳을 통해 Twitter API에서 넘어오는 데이터들이 Kafka 내로 들어오게 됩니다.
  - api와 producer을 연결하는 통로는 logstash를 사용할 것입니다. 때문에 이 Producer로 사용하는 EC2 Instance에는 logstash도 설치해야 합니다.
  
  - 먼저 Kafka Producer을 실행합니다.
    - bin/kafka-console-producer.sh --topic twitter --bootstrap-server [ip 주소]:9092
    -  ip 주소는 ifconfig -a 명령어를 통해 알 수 있습니다. inet 이하 부분을 참고하면 됩니다. 
  
  - 그 이후 logstash 를 설치하자면,
    - wget https://artifacts.elastic.co/downloads/logstash/logstash-7.4.0.tar.gz
    - tar xvzf logstash-7.4.0.tar.gz
    
    - logstash는 리눅스 시스템 내 환경변수에 지정해 줘야 합니다.
      - $HOME 경로 내에 .bash_profile가 있다면 그 곳에, 그게 없다면 .bashrc 파일을 찾아 vi로 연 뒤에,
        - export LS_HOME=/home/ec2-user/logstash
        - PATH=$PATH:$LS_HOME/bin 
        - 이후 source .bash_profile/.bashrc 를 통해 변경사항을 저장해줘야 합니다. 

- 그 이후 producer.conf를 편집합니다. 

- 이후 logstash -f producer.conf 로 실행시키고, consumer 을 통해 출력되는 것을 확인합니다.

- producer과 consumer 사이에 원하는 방향에 따라 프로그램을 배치할 수 있습니다. 



