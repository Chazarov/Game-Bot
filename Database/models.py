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
        print(str(type(self)) + "  was deleted")
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
    
    # Параметры самой игры представлены отдельным объектом, который хранится в таблице
    # соответствующей игры, где имеет собственный id 
    game_id: Mapped[int] = mapped_column(Integer, nullable = False)
   
    
    

class TTT_game(Base):
    __tablename__ = "Tic tac toe game"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Параметры для визуализации игры 
    # (id сообщений, которые будут представлять собой игровое поля для обоих 
    # игроков)
    creator_field_message_id: Mapped[int] = mapped_column(Integer, nullable = True)
    guest_field_message_id: Mapped[int] = mapped_column(Integer, nullable = True)

    # Параметры игры
    # размерность игрового поля
    n: Mapped[int] = mapped_column(Integer, nullable = True)
    m: Mapped[int] = mapped_column(Integer, nullable = True)

    field: Mapped[str] = mapped_column(Text, nullable = True)

    async def add_creator_field_message_id(self, session:AsyncSession, field_message_id:int):
        print("add creator field")
        self.creator_field_message_id = field_message_id
        await session.commit()
    
    async def add_guest_field_message_id(self, session:AsyncSession, field_message_id:int):
        print("add guest field")
        self.guest_field_message_id = field_message_id
        await session.commit()

    async def set_field(self, session:AsyncSession, field:str):
        self.field = field
        await session.commit()
        

    




class Durak_game(Base):
    __tablename__ = "Durak game"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    creator_display_message_1: Mapped[int] = mapped_column(Integer, nullable = True)
    creator_display_message_2: Mapped[int] = mapped_column(Integer, nullable = True)
    creator_display_message_3: Mapped[int] = mapped_column(Integer, nullable = True)

    guest_display_message_1: Mapped[int] = mapped_column(Integer, nullable = True)
    guest_display_message_2: Mapped[int] = mapped_column(Integer, nullable = True)
    guest_display_message_3: Mapped[int] = mapped_column(Integer, nullable = True)

    creator_fields_are_filled_in: Mapped[bool] = mapped_column(Boolean, default = False)
    guest_fields_are_filled_in: Mapped[bool] = mapped_column(Boolean, default = False) 

    current_game_data: Mapped[str] = mapped_column(Text, nullable = True)





    async def set_display_messages_creator(self, session:AsyncSession, message1, message2, message3):
        self.creator_display_message_1 = message1
        self.creator_display_message_2 = message2
        self.creator_display_message_3 = message3

        self.creator_fields_are_filled_in = True

        await session.commit()

    async def set_display_messages_guest(self, session:AsyncSession, message1, message2, message3):
        self.guest_display_message_1 = message1
        self.guest_display_message_2 = message2
        self.guest_display_message_3 = message3

        self.guest_fields_are_filled_in = True

        await session.commit()

    async def set_current_game_data(self, session:AsyncSession, game_data:str):
        self.current_game_data = game_data

        await session.commit()
    

    



