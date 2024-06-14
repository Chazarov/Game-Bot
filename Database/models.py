from sqlalchemy import String, Integer, Text, DateTime, func, MetaData, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class USER_STATES:
    IN_GAME = "IN_GAME"
    WAITING_FOR_A_GAME = "WZITING_FOR_A_GAME"
    NOT_ACTIVE = "NOT_ACTIVE"
    
metadata_obj = MetaData()

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default = func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default = func.now())

class User(Base):
    __tablename__ = "Users"
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(40), nullable = False)
    tag: Mapped[str] = mapped_column(String(40), default = "не указан")
    state: Mapped[str] = mapped_column(String(40), nullable = False)

class TTTlobbi(Base):# tic tac toe lobbi 
    __tablename__ = "tic tac toe lobbi"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    X_user_id: Mapped[int] = mapped_column(Integer, nullable = False)
    O_user_id: Mapped[int] = mapped_column(Integer, nullable = False)

    



