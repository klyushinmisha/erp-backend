from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from erp_backend import api

app = FastAPI(
    title="ERP Backend",
    version="0.1.0",
    description="REST API for university ERP project",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api, prefix="/api")
