from model.base_dto import BaseModel


class SubscriptionHandlerCreateUserSubscriptionMapRequest(BaseModel):
    subscription_name: str
    user_email: str
    card_owner_id: str
    card_number: str
    cvv: str
