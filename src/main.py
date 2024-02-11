from fastapi import FastAPI
from pydantic import BaseModel

from src.db.orm import AsyncORM as db


app = FastAPI()

# ==========================================
@app.get('/cleartables/')
async def check_activation():
    return await db.create_tables()

@app.get('/addkeys/')
async def check_activation(quantity: int, max_usages: int):
    return await db.generate_keys(quantity, max_usages)

@app.get('/keys/')
async def check_activation():
    return await db.select_keys()
# ======================================

@app.get('/')
async def check_activation():
    ...

@app.get('/isactivated/')
async def check_activation(key: str, machine: str):
    return await db.is_activated(key, machine)

@app.post('/addactivation/')
async def add_activation(key, machine):
    print(key, machine)
    return await db.add_activation(key, machine)


