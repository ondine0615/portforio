from sqlalchemy.orm import declarative_base

from sqlalchemy import create_engine

# 연결 생성
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL="postgresql://postgre:password@localhost/OSLO_CITY_Bike"

engine=create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db =None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
        