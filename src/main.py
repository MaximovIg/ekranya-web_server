from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.db.orm import AsyncORM as db


app = FastAPI()
# ==========================================
# @app.get('/cleartables/')
# async def create_table():
#     await db.create_tables()

@app.get('/addkeys/')
async def generate_keys(quantity: int, max_usages: int):
    await db.generate_keys(quantity, max_usages)

# @app.get('/keys/')
# async def select_keys():
#     return await db.select_keys()
# ======================================

class ActivationItem(BaseModel):
    key: str
    success: bool


@app.get('/')
async def index():
    ...

@app.get('/isactivated/')
async def check_activation(key: str, machine: str):   
        if await db.is_activated(key, machine):
            return ActivationItem(key=key, success=True)
        else:
            return ActivationItem(key=key, success=False) 

@app.post('/addactivation/')
async def add_activation(key, machine):
    if await db.add_activation(key, machine):
        return ActivationItem(key=key, success=True)
    else:
        return ActivationItem(key=key, success=False)



