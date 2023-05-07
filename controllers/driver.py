from fastapi import APIRouter, Depends

from component_factory import get_passenger_service, get_knapsack_service

from model.requests.driver import DriverOrderDrive, DriverAcceptDrive, DriverRejectDrive
from model.drive_order import DriveOrder
from model.responses.driver import DriverSuggestedDrives, DriverAcceptDriveResponse, DriverRejectDriveResponse
from service.passenger_service import PassengerService
from service.knapsack_service import KnapsackService

router = APIRouter()

CANDIDATES_AMOUNT = 10

#TODO add routing /requestDrive
async def order_new_drive(
    knapsack_service: KnapsackService = Depends(get_knapsack_service)
) -> DriverSuggestedDrives:
    """
    1) Get 10 drives from DB
    2) Convert them to list[KnapsackItem]
    3) send suggest_solution request
    4) Return suggestion to FE
    """
    rides = get_top_candidates(current_location=DriverOrderDrive.current_location)
    suggestions = knapsack_service.suggest_solution(DriverOrderDrive.user_id, 4, rides)
    # TODO adjust to required response structure - not decided yet
    return suggestions

#TODO add routing /acceptdrive
async def accept_drive(
    user_id,
    order_id,
    knapsack_service: KnapsackService = Depends(get_knapsack_service)

):
    """
    1) Release frozen orders form DB - #TODO how do I know i'm releasing orders that this driver set to be  freezed? what if its another driver?
    2) sets selected order to "IN PROGRESS"
    3) sends accept-solution to knapsack
    """
    await release_unchosen_orders(order_id)
    await set_order_as_in_progress(order_id)
    resp = knapsack_service.accept_solution(user_id=user_id, order_id=order_id)
    if resp != 200: # TODO real statuses
        return 500

#TODO add routing /acceptdrive
async def reject_drive(
    user_id,
    order_id,
    knapsack_service: KnapsackService = Depends(get_knapsack_service)
):
    """
    1) release frozen drives
    """


async def get_top_candidates(current_location,
    passenger_service: PassengerService = Depends(get_passenger_service)

) -> list[KnapsackItem]:
    candidates = list[KnapsackItem]
    orders = await passenger_service.get_top_order_candidats(candidates_amount=CANDIDATES_AMOUNT,
                                                             current_location=current_location) #TODO this should change the state of this order to "FREEZE" in DB
    for order in orders:
        item = KnapsackItem(id = 1, volume = 1, value = 123) # TODO calculate volume, value, id might be the Order id from DB

        candidates.append(item)

    return candidates

async def release_unchosen_orders(suggestions:list[KnapsackItem],
    passenger_service: PassengerService = Depends(get_passenger_service)

) -> None:
    """
    1) extract order_ids from suggestions
    2) for every frozen entry - if it frozen because of current service - release it
    """
    orders = await passenger_service.release_frozen_orders()
