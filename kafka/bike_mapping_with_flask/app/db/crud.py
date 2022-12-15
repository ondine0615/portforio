def create_user(session: session, user:schemas.UserBase) -> Users:
    db_user = Users(
        nickname =user.nickname,
        
    )