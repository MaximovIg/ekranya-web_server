from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from typing import Annotated


created_at = Annotated[datetime,  mapped_column(server_default=func.now())] 


class Base(DeclarativeBase):
    ...


class KeysOrm(Base):
    __tablename__ = 'keys'

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str]         #Код формата XXXXX-XXXXX-XXXXX-XXXXX-XXXXX
    max_usages: Mapped[int]  #Изначальное количество доступных активаций на различных уникальных машинах
    used: Mapped[int]        #На скольких уникальных машинах уже активирован код
    created_at: Mapped[created_at]


class ActivationsOrm(Base):
    __tablename__ = 'activations'

    id: Mapped[int] = mapped_column(primary_key=True)
    key_id: Mapped[str] = mapped_column(ForeignKey('keys.id', ondelete='CASCADE'))
    machine: Mapped[str]     #Уникальная машина, на которой код был активирован        
    activated_at: Mapped[created_at]

