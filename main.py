from fastapi import FastAPI

from erp_backend import api

app = FastAPI(
    title="ERP Backend",
    version="0.1.0",
    description="REST API for university ERP project",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.include_router(api, prefix="/api")
