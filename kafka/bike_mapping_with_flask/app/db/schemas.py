import datetime
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    station_id : int
    is_installed : int
    is_renting : int
    last_reported : int
    num_bikes_available : int
    num_docks_available : int
    date : Optional[datetime]=None
    
class User(UserBase):
    id : int
    
    class Config:
        orm_mode = True
        
    