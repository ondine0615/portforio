import requests
import xmltodict

basic_url="http://plus.kipris.or.kr/openapi/rest/RegistrationService/"
taskId="registrationInfo"
reg_number='registrationNumber'
number='1010249500000'
api_key = "Y74vSqogy7fkw71F26g146N4s9Harc7sLqm4ONkWHWE="
api_key_2= "S5sUeUcewvE0=dLF=a9IKgK72zEAvD5bkiPciv4BIEU="
url =f'{basic_url}{taskId}?{reg_number}={number}&accessKey={api_key}'
url
url_2=f'{basic_url}{taskId}?{reg_number}={number}&accessKey={api_key_2}'
url_2

st=requests.get(url_2)
content_xml=st.content

body=list(xmltodict.parse(content_xml)['response']['body'])[0]
content=xmltodict.parse(content_xml)['response']['body'][f'{body}']
detail_name=list(content)[0]
content=content[detail_name]

if len(content) !=0:
    for key,item in content.items():
        if key=='registrationRightInfo':
            print(list(content['registrationRightInfo']))