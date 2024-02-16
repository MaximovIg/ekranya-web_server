import sys
import logging

from sqlalchemy import select, and_

from src.db.database import async_engine, async_session
from src.db.models import Base, KeysOrm, ActivationsOrm

from src.utils.key import Key


logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
logger.handlers = [stream_handler, ]
logger.setLevel(logging.DEBUG)


class AsyncORM:
   
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def select_keys():
        async with async_session() as session:
            result = await session.execute(select(KeysOrm))
            return [orm.key for orm in result.scalars().all()]
    
    @staticmethod
    async def generate_keys(quantity=1, max_usages=1, *, key_generator=Key()):
        async with async_session() as session:
            keys = []
            existed_keys = await AsyncORM.select_keys()    
            for _ in range(quantity):
                key = key_generator.generate()
                while key in existed_keys:
                    key = key_generator.generate()
                keys.append(key)

            keys_orm = []
            for key in keys:
                keys_orm.append(KeysOrm(key=key, max_usages=max_usages, used=0))                
            session.add_all(keys_orm)
            await session.commit()

    @staticmethod
    async def add_activation(key, machine) -> bool:
        async with async_session() as session:            
            #проверить, что такой ключ существует
            existed_keys = await AsyncORM.select_keys()
            
            if key not in existed_keys:
                return False
            
            res = await session.execute(select(KeysOrm).filter_by(key=key))
            key_id = res.scalars().one().id

            #проверить, что активация с таким ключом на такой машине уже есть
            if await AsyncORM.activation_exists(key_id, machine):
                return True
            
            #проверить, что есть доступные активации 
            if await AsyncORM.available_activations(key_id) <= 0:
                return False            
            
            #добавить новую активацию
            session.add(ActivationsOrm(key_id=key_id, machine=machine))
            
            #обновить доступные активации
            res = await session.execute(select(KeysOrm).filter_by(key=key))
            key_used = res.scalars().one().used
            await AsyncORM.update_used(key_id, key_used+1)
            await session.commit()
            
            return True
        
    @staticmethod
    async def update_used(key_id, new_used):
        async with async_session() as session:
            key = await session.get(KeysOrm, key_id)            
            key.used = new_used

            session.add(key)
            await session.commit()
        
    @staticmethod
    async def activation_exists(key_id, machine):        
        async with async_session() as session:
            res = await session.execute(select(ActivationsOrm).where(
                and_(
                    ActivationsOrm.key_id == key_id,
                    ActivationsOrm.machine == machine
                    )
                    ))         
            if res.scalar():
                return True
            else:
                return False                    
            
    @staticmethod
    async def is_activated(key, machine):
        async with async_session() as session:
            try:
                res = await session.execute(select(KeysOrm).filter_by(key=key))
                key_id = res.scalars().one().id
                res = await session.execute(select(ActivationsOrm).where(
                    and_(
                        ActivationsOrm.key_id == key_id,
                        ActivationsOrm.machine == machine
                        )
                        ))          
                if res.scalar():
                    logger.debug('activation key %s exists for machine %s' % (key, machine))                                         
                    return True
                else:
                    logger.debug('activation key %s does not exist for machine %s' % (key, machine))
                    return False
            except Exception as err:
                logger.error(err)
                return False

    @staticmethod
    async def available_activations(key):
        async with async_session() as session:
            if isinstance(key, int):
                res = await session.execute(select(KeysOrm).filter_by(id=key))                
                key = res.scalars().one().key

            res = await session.execute(select(KeysOrm).filter_by(key=key))
            max_usages = res.scalars().one().max_usages
            res = await session.execute(select(KeysOrm).filter_by(key=key))
            used = res.scalars().one().used

            return max_usages-used