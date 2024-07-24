from sqlalchemy import String, Integer, Text, DateTime, func, MetaData, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from sqlalchemy.ext.asyncio import AsyncSession

class USER_STATES:
    IN_GAME = "IN_GAME"
    WAITING_FOR_A_GAME = "WAITING_FOR_A_GAME"
    NOT_ACTIVE = "NOT_ACTIVE"
    
metadata_obj = MetaData()

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default = func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default = func.now())

    async def delete(self, session:AsyncSession):
        await session.delete(self)
        await session.commit()
        

class User(Base):
    __tablename__ = "Users"
    id: Mapped[int] = mapped_column(Integer, primary_key = True)
    name: Mapped[str] = mapped_column(String(40), nullable = False)
    tag: Mapped[str] = mapped_column(String(40), default = None, nullable = True)
    state: Mapped[str] = mapped_column(String(40), nullable = False)
    game_params: Mapped[str] = mapped_column(String(40), nullable = True, default = None)
    balance: Mapped[int] = mapped_column(Integer, default = 0)

    loses: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)

    # WHAT???????????????????????????????????????????????????????????????????????????????????
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class promo_codes(Base):
    __tablename__ = "Promocodes"

    promoname: Mapped[str] = mapped_column(String(40), primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, default=0)

class Lobby(Base):
    __tablename__ = "lobby"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connection_fall: Mapped[int] = mapped_column(Integer, default = 0)#Пока не используется
    bet: Mapped[int] = mapped_column(Integer, default = 0)

    creator_id: Mapped[int] = mapped_column(Integer, nullable = False)
    guest_id: Mapped[int] = mapped_column(Integer, nullable = False)

    game_name: Mapped[str] = mapped_column(String(40), nullable = False)
    #Параметры , по которым будет происходить поиск противника
    general_game_parametrs: Mapped[str] = mapped_column(Text, nullable = False)
    
    # Параметры самой игры представлены отдельным объектом, который хранится в таблице
    # соответствующей игры, где имеет собственный id 
    game_id: Mapped[int] = mapped_column(Integer, nullable = False)
   
    
    

class TTT_game(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Параметры для визуализации игры 
    # (id сообщений, которые будут представлять собой игровое поля для обоих 
    # игроков)
    creator_field_message_id: Mapped[int] = mapped_column(Integer, nullable = False)
    guest_field_message_id: Mapped[int] = mapped_column(Integer, nullable = False)

    # Параметры игры
    # размерность игрового поля
    n: Mapped[int] = mapped_column(Integer, nullable = False)
    m: Mapped[int] = mapped_column(Integer, nullable = False)

    field: Mapped[str] = mapped_column(Text, nullable = False)

    async def add_creator_field_message_id(self, session:AsyncSession, field_message_id:int):
        self.creator_field_message_id = field_message_id
        session.commit()
    
    async def add_guest_field_message_id(self, session:AsyncSession, field_message_id:int):
        self.creator_field_message_id = field_message_id
        session.commit()

    async def set_field(self, session:AsyncSession, field:str):
        self.field = field
        session.commit()
        

    




class Durak_game(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    

    



