import asyncio
import sys
import os

from db.orm import AsyncORM as db


sys.path.insert(1, os.path.join(sys.path[0], '..'))


class KeyMock:

    def generate(self):
        return 'Y04UB-5RGF3-BQYG7-ZB825-GEV8Y'


async def main():
    #создание новых ключей
    import time
    start = time.perf_counter()
    await db.create_tables()    
    await db.generate_keys(quantity=5, max_usages=3)
    res = await db.select_keys()
    assert len(res) == 5, f'{res}'

    #доступные активации
    await db.create_tables()    
    await db.generate_keys(quantity=1)
    res = await db.available_activations(1)    
    assert res == 1, f'{res}'   

    # добавление активации
    await db.create_tables() 
    await db.generate_keys(quantity=1, key_generator=KeyMock())
    res = await db.add_activation(KeyMock().generate(), 'personal_machine')
    assert res == True, f'{res}'
    res = await db.add_activation(KeyMock().generate(), 'personal_machine1')
    assert res == False, f'{res}'

    await db.create_tables()    
    await db.generate_keys(quantity=1, max_usages=2, key_generator=KeyMock())
    res = await db.available_activations(1)    
    assert res == 2, f'{res}'
    await db.add_activation(KeyMock().generate(), 'personal_machine')
    res = await db.available_activations(1)    
    assert res == 1, f'{res}'
    await db.add_activation(KeyMock().generate(), 'personal_machine1')
    res = await db.available_activations(1)    
    assert res == 0, f'{res}'

    #активация существует
    await db.create_tables() 
    await db.generate_keys(1, 2, key_generator=KeyMock())
    res = await db.activation_exists(1, 'personal_machine')
    assert res == False, f'{res}'
    await db.add_activation(KeyMock().generate(), 'personal_machine')
    res = await db.activation_exists(1, 'personal_machine')
    assert res == True, f'{res}'  


    print('tests passed')   

if __name__ == '__main__':
    asyncio.run(main())

    import subprocess

    UUID = str(subprocess.check_output('wmic csproduct get UUID'),'utf-8').split('\n')[1].strip()

    print(UUID) 