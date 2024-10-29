from fastapi import APIRouter

from app.controllers.api import api_messages
from app.controllers.api.endpoints import (
    auth,
    templates,
    users,
    properties,
    houses,
    tenants,
    contracts,
    payment_installment,
    expenses,
    guarantor,
)

auth_router = APIRouter()
auth_router.include_router(auth.router, prefix="/auth", tags=["auth"])

api_router = APIRouter(
    responses={
        401: {
            "description": "No `Authorization` access token header, token is invalid or user removed",
            "content": {
                "application/json": {
                    "examples": {
                        "not authenticated": {
                            "summary": "No authorization token header",
                            "value": {"detail": "Not authenticated"},
                        },
                        "invalid token": {
                            "summary": "Token validation failed, decode failed, it may be expired or malformed",
                            "value": {"detail": "Token invalid: {detailed error msg}"},
                        },
                        "removed user": {
                            "summary": api_messages.JWT_ERROR_USER_REMOVED,
                            "value": {"detail": api_messages.JWT_ERROR_USER_REMOVED},
                        },
                    }
                }
            },
        },
    }
)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(properties.router, tags=["properties"])
api_router.include_router(houses.router, tags=["houses"])
api_router.include_router(tenants.router, tags=["tenants"])
api_router.include_router(templates.router, tags=["templates"])
api_router.include_router(contracts.router, tags=["contracts"])
api_router.include_router(payment_installment.router, tags=["payment_installment"])
api_router.include_router(expenses.router, tags=["expenses"])
api_router.include_router(guarantor.router, tags=["guarantor"])
