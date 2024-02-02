import os
import aioredis
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI

from .main_v1 import router as router_v1


app = FastAPI(
    docs_url="/",
    title="Semantic Kraus API backend",
    description="Development version of the Semantic Kraus backend.",
    version="0.1.0",
)

app.include_router(router_v1)
origins = ["*"]

app = VersionedFastAPI(app, version_format="{major}", prefix_format="/v{major}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
