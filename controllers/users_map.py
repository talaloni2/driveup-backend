from fastapi import APIRouter, Depends

from component_factory import get_subscription_handler_service
from service.subscription_handler_service import SubscriptionHandlerService

router = APIRouter()


@router.get("/{user_email}")
async def get_by_user_email(
        email: str,
        subscription_handler_service: SubscriptionHandlerService = Depends(get_subscription_handler_service),
):
    return await subscription_handler_service.get_by_user_email(email=email)
