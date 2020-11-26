from fastapi.testclient import TestClient

from erp_backend import api

client = TestClient(api)
