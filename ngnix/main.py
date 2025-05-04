from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List
from pydantic import BaseModel

app = FastAPI()

class NameRequest(BaseModel):
    name: str

@app.get("/date")
async def get_date():
    current_date = datetime.now()
    return JSONResponse(content={"year": current_date.year, "month": current_date.month, "day": current_date.day})

@app.post("/name")
async def get_name(request: NameRequest):
    data = [{"name": request.name} for _ in range(10000)]
    return JSONResponse(content=data) 