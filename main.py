from fastapi import FastAPI
from pydantic import BaseModel, Field
app = FastAPI()
class EchoRequest(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0)
@app.post("/echo")
def echo(data: EchoRequest):
    return {
        "message": "Data received successfully",
        "data": data.model_dump()
    }