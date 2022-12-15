from sqlalchemy import Column, Integer, String, CHAR,Date
from db import Base


# 테이블 구조 정의 

class Users(Base):
    __tablename__="station_status"
    
    Station_id = Column(CHAR(20))
    is_installed=Column(Integer)
    is_renting=Column(Integer)
    last_Reported=Column(Integer)
    num_bikes_available=Column(Integer)
    num_docks_available=Column(Integer)
    date=Column(Date)