from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class DataInput(BaseModel):
    data: str

