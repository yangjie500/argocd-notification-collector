from fastapi import APIRouter

from event_collector.api.routes.argocd import router as argocd_router

api_router = APIRouter()

api_router.include_router(argocd_router)
