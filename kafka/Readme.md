# Twitter api - Kafka 연동방법에 대해
- Kafka의 기본적인 원리와 사용방법에 대해 익히며 진행했던 간단한 과정입니다. 

- AWS ec2 서비스를 기반으로 실행한다면 Amazon Linux 서비스를 기반으로 구축하거나, 따로 하드웨어에 서버를 설치하고자 한다면 rocky-linux를 통해 보다 편하게 진행할 수 있습니다.
- 레드헷 공식 홈페이지에서 개발전용 무료 프로그램을 등록한 뒤 설치해도 좋습니다. 
  - Amazon Linux는 centos를 기반으로, rocky-Linux는 centos의 서비스 종료에 시작된 소프트웨어입니다.
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



