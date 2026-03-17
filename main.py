import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel
import database
from models import *
from fastapi.middleware.cors import CORSMiddleware
from routers.request_router import router as request_router
from routers.pharmacy_router import router as pharmacy_router
from routers.auth import router as auth_router




app = FastAPI(
    title="pharma-portal Backend API",
    description="Backend API for Pharma-Portal",
    version="0.0.1"
)


# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(database.engine)


create_db_and_tables()


# Root endpoint (no authentication required)
@app.get("/")
def root():
    return JSONResponse(content={"message": "Welcome to the Pharma-Portal Backend API. For documentation, please refer to /docs."})




app.include_router(request_router)
app.include_router(pharmacy_router)
app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Railway sets PORT env var
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)