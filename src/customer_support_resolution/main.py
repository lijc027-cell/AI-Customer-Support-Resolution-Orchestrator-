"""FastAPI entrypoint for the customer support resolution skeleton."""

from __future__ import annotations

from fastapi import FastAPI

from customer_support_resolution.api.routes import router

app = FastAPI(
    title="Customer Support Resolution",
    version="0.1.0",
    description="Backend skeleton for an AI customer support resolution orchestrator.",
)
app.include_router(router)

