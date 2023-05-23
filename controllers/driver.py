from typing import Any

from datetime import datetime

from fastapi import APIRouter, Depends

from component_factory import get_passenger_service, get_knapsack_service
from controllers.utils import AuthenticatedUser, authenticated_user
from model.drive_order import DriveOrderStatus
from model.requests.driver import DriverRequestDrive, DriverAcceptDrive, DriverRejectDrive
from mappings.factory_mapping import LIMITS_MAPPING

from model.requests.driver import DriverRequestDrive, DriverAcceptDrive, DriverRejectDrive, Limit, LimitValues
from model.drive_order import DriveOrder
from model.responses.driver import DriverSuggestedDrives  # DriverAcceptDriveResponse, DriverRejectDriveResponse
from model.responses.knapsack import SuggestedSolution, AcceptSolutionResponse, RejectSolutionResponse

from service.passenger_service import PassengerService
from service.knapsack_service import KnapsackService
from model.requests.knapsack import KnapsackItem
from model.responses.driver import DriveDetails, OrderLocation, \
    Geocode  # DriverAcceptDriveResponse, DriverRejectDriveResponse
from model.responses.knapsack import SuggestedSolution
from service.knapsack_service import KnapsackService
from service.passenger_service import PassengerService

router = APIRouter()

CANDIDATES_AMOUNT = 2


@router.post("/request-drives")
async def order_new_drive(
        order_request: DriverRequestDrive, knapsack_service: KnapsackService = Depends(get_knapsack_service),
        user: AuthenticatedUser = Depends(authenticated_user),
        passenger_service: PassengerService = Depends(get_passenger_service)
) -> SuggestedSolution:
    """
    1) Gets 10 drives from DB
    2) Converts them to list[KnapsackItem]
    3) Sends suggest_solution request
    4) Returns suggestion to FE
    """
    rides = await get_top_candidates(current_location=[order_request.current_lat, order_request.current_lon],
                                     passenger_service=passenger_service, limits=order_request.limits)
    await knapsack_service.reject_solutions(user.email)
    suggestions = await knapsack_service.suggest_solution(user.email, 4, rides)
    # TODO adjust to required response structure - Yarden
    return get_suggestions_with_total_value_volume(suggestions)


@router.post("/accept-drive")
async def accept_drive(
        accept_drive_request: DriverAcceptDrive,
        knapsack_service: KnapsackService = Depends(get_knapsack_service),
        passenger_service: PassengerService = Depends(get_passenger_service)
):
    """
    1) Sets selected order to "IN PROGRESS"
    2) Release frozen orders form DB
    3) Sends accept-solution to knapsack
    """
    await passenger_service.set_status_to_drive_order(order_id=accept_drive_request.order_id, new_status=DriveOrderStatus.ACTIVE)
    await passenger_service.release_unchosen_orders_from_freeze(accept_drive_request.order_id,
                                                                accept_drive_request.email)
    resp = knapsack_service.accept_solution(user_id=accept_drive_request.email, solution_id='solution_id')
    if resp != 200:  # TODO real statuses
        return 500


@router.post("/reject-drives")
async def reject_drive(
        reject_drives_request: DriverRejectDrive,
        knapsack_service: KnapsackService = Depends(get_knapsack_service),
        passenger_service: PassengerService = Depends(get_passenger_service)

):
    """
    1) Releases frozen drives
    2) Sends request to knapsack service
    """
    await passenger_service.release_unchosen_orders_from_freeze(reject_drives_request.email)
    resp = knapsack_service.reject_solutions(user_id=reject_drives_request.email)


@router.get("/drive-details/{drive_id}")
async def order_details(
    drive_id: str,
    user: AuthenticatedUser = Depends(authenticated_user),
    passenger_service: PassengerService = Depends(get_passenger_service),
) -> DriveDetails:

    return DriveDetails(
        time=datetime.now(),
        id=drive_id,
        order_locations=[
            OrderLocation(
                user_email=user.email,
                is_driver=True,
                is_start_address=True,
                address=Geocode(latitude=32.0762148, longitude=34.7731433),
                price=10,
            ),
            OrderLocation(
                user_email="mockPassenger@gmail.com",
                is_driver=False,
                is_start_address=True,
                address=Geocode(latitude=32.0762148, longitude=34.7731433),
                price=10,
            ),
            OrderLocation(
                user_email="222mockPassenger2@gmail.com",
                is_driver=False,
                is_start_address=True,
                address=Geocode(latitude=32.0762148, longitude=34.7731433),
                price=10,
            ),
            OrderLocation(
                user_email="mockPassenger@gmail.com",
                is_driver=False,
                is_start_address=False,
                address=Geocode(latitude=32.0762148, longitude=34.7731433),
                price=10,
            ),
            OrderLocation(
                user_email="222mockPassenger2@gmail.com",
                is_driver=False,
                is_start_address=False,
                address=Geocode(latitude=32.0762148, longitude=34.7731433),
                price=10,
            ),
        ],
        total_price=20
    )


def get_suggestions_with_total_value_volume(suggestions: SuggestedSolution) -> SuggestedSolution:
    for i, suggestion in suggestions.solutions.items():
        suggestions.solutions[i].total_value = sum(map(lambda x: x.value, suggestion.items))
        suggestions.solutions[i].total_volume = sum(map(lambda x: x.volume, suggestion.items))
    return suggestions


def is_order_acceptable(order: Any, limits: dict[Limit, LimitValues]) -> bool:
    for limit, limit_values in limits.items():
        limit_function = LIMITS_MAPPING[limit.value]
        if not limit_function(order, limit_values):
            return False
    return True


async def get_top_candidates(current_location,
                             passenger_service: PassengerService,
                             limits: dict[Limit, LimitValues]
                             ) -> list[KnapsackItem]:
    candidates = []
    orders = await passenger_service.get_top_order_candidates(
        candidates_amount=CANDIDATES_AMOUNT,
        current_location=current_location
    )  # TODO this should change the state of this order to "FREEZE" in DB
    for order in orders:
        if not is_order_acceptable(order=order, limits=limits):
            continue
        item = KnapsackItem(id=order.id, volume=order.passengers_amount,
                            value=(-1 * order.distance_from_driver))  # TODO calculate volume, value, id might be the Order id from DB

        candidates.append(item)

    return candidates


async def release_unchosen_orders(suggestions: list[KnapsackItem],
                                  passenger_service: PassengerService = Depends(get_passenger_service)

                                  ) -> None:
    """
    1) extract order_ids from suggestions
    2) for every frozen entry - if it frozen because of current service - release it
    """
    orders = await passenger_service.release_frozen_orders()
