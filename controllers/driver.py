from datetime import datetime
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from component_factory import get_passenger_service, get_knapsack_service, get_driver_service, get_time_service
from controllers.utils import AuthenticatedUser, authenticated_user, adjust_timezone
from mappings.factory_mapping import LIMITS_MAPPING
from model.driver_drive_order import DriverDriveOrder
from model.passenger_drive_order import PassengerDriveOrderStatus
from model.requests.driver import DriverRequestDrive, DriverAcceptDrive, DriverRejectDrive, Limit, LimitValues
from model.requests.knapsack import KnapsackItem
from model.responses.driver import DriveDetails, OrderLocation
from model.responses.geocode import Geocode
from model.responses.knapsack import SuggestedSolution, KnapsackSolution
from model.responses.success import SuccessResponse
from service.driver_service import DriverService
from service.knapsack_service import KnapsackService
from service.passenger_service import PassengerService
from service.time_service import TimeService

router = APIRouter()

CANDIDATES_AMOUNT = 2


def _orders_to_suggestions(current_drive_orders: list[DriverDriveOrder], time_service: TimeService):
    return SuggestedSolution(
        time=adjust_timezone(current_drive_orders[0].time, time_service),
        expires_at=adjust_timezone(current_drive_orders[0].expires_at, time_service),
        solutions={
            k.id: KnapsackSolution(items=k.passenger_orders, algorithm=k.algorithm) for k in current_drive_orders
        },
    )


@router.post("/request-drives")
async def order_new_drive(
    order_request: DriverRequestDrive,
    force_reject: bool = True,
    knapsack_service: KnapsackService = Depends(get_knapsack_service),
    user: AuthenticatedUser = Depends(authenticated_user),
    passenger_service: PassengerService = Depends(get_passenger_service),
    driver_service: DriverService = Depends(get_driver_service),
    time_service: TimeService = Depends(get_time_service),
) -> SuggestedSolution:
    """
    1) Gets 10 drives from DB
    2) Converts them to list[KnapsackItem]
    3) Sends suggest_solution request
    4) Returns suggestion to FE
    """
    if not force_reject:
        current_drive_orders: list[DriverDriveOrder] = await driver_service.get_suggestions(user.email)
        if current_drive_orders:
            suggestions = _orders_to_suggestions(current_drive_orders, time_service)
            return get_suggestions_with_total_value_volume(suggestions)

    rides = await get_top_candidates(
        current_location=[order_request.current_lat, order_request.current_lon],
        passenger_service=passenger_service,
        limits=order_request.limits,
        driver_id=user.email,
    )
    await driver_service.reject_solutions(user.email)
    await knapsack_service.reject_solutions(user.email)
    suggestions = await knapsack_service.suggest_solution(user.email, 4, rides)
    suggestions = get_suggestions_with_total_value_volume(suggestions)
    await driver_service.save_suggestions(user.email, suggestions)
    suggestions.time = adjust_timezone(suggestions.time, time_service)
    suggestions.expires_at = adjust_timezone(suggestions.expires_at, time_service)

    return suggestions


@router.post("/accept-drive")
async def accept_drive(
    accept_drive_request: DriverAcceptDrive,
    knapsack_service: KnapsackService = Depends(get_knapsack_service),
    passenger_service: PassengerService = Depends(get_passenger_service),
    driver_service: DriverService = Depends(get_driver_service),
    user: AuthenticatedUser = Depends(authenticated_user),
    time_service: TimeService = Depends(get_time_service),
) -> SuccessResponse:
    """
    1) Sets selected order to "IN PROGRESS"
    2) Release frozen orders form DB
    3) Sends accept-solution to knapsack
    """
    # TODO: along with setting status to active, we need to assign drive id
    now = time_service.utcnow()
    suggestion = await driver_service.get_suggestion(user.email, accept_drive_request.order_id)
    if not suggestion or suggestion.expires_at < now:
        raise HTTPException(
            status_code=HTTPStatus.NOT_ACCEPTABLE, detail={"message": "Suggestion not exists or expired"}
        )
    accept_success = await knapsack_service.accept_solution(
        user_id=user.email, solution_id=accept_drive_request.order_id
    )

    order_ids = [int(order["id"]) for order in suggestion.passenger_orders]
    for order_id in order_ids:
        await passenger_service.activate_drive(order_id=order_id, drive_id=accept_drive_request.order_id)
        await passenger_service.set_status_to_drive_order(
            order_id=order_id, new_status=PassengerDriveOrderStatus.ACTIVE
        )

    await passenger_service.release_unchosen_orders_from_freeze(user.email, order_ids)
    return SuccessResponse(success=accept_success)


@router.post("/reject-drives")
async def reject_drive(
    reject_drives_request: DriverRejectDrive,
    knapsack_service: KnapsackService = Depends(get_knapsack_service),
    passenger_service: PassengerService = Depends(get_passenger_service),
) -> SuccessResponse:
    """
    1) Releases frozen drives
    2) Sends request to knapsack service
    """
    await passenger_service.release_unchosen_orders_from_freeze(reject_drives_request.email)
    resp = await knapsack_service.reject_solutions(user_id=reject_drives_request.email)
    return SuccessResponse(success=resp)


@router.get("/drive-details/{drive_id}")
async def order_details(
    drive_id: str,
    passenger_service: PassengerService = Depends(get_passenger_service),
    time_service: TimeService = Depends(get_time_service),
) -> DriveDetails:
    return DriveDetails(
        time=time_service.now(),
        id=drive_id,
        order_locations=[
            OrderLocation(
                user_email="d@d.com",
                is_driver=True,
                is_start_address=True,
                address=Geocode(latitude=32.080209, longitude=34.898453),
                price=10,
            ),
            OrderLocation(
                user_email="a@a.com",
                is_driver=False,
                is_start_address=True,
                address=Geocode(latitude=32.081118, longitude=34.889338),
                price=10,
            ),
            OrderLocation(
                user_email="b@b.com",
                is_driver=False,
                is_start_address=True,
                address=Geocode(latitude=32.087327, longitude=34.879775),
                price=10,
            ),
            OrderLocation(
                user_email="a@a.com",
                is_driver=False,
                is_start_address=False,
                address=Geocode(latitude=32.096715, longitude=34.873519),
                price=10,
            ),
            OrderLocation(
                user_email="b@b.com",
                is_driver=False,
                is_start_address=False,
                address=Geocode(latitude=32.088084, longitude=34.861633),
                price=10,
            ),
        ],
        total_price=20,
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


async def get_top_candidates(
    current_location,
    passenger_service: PassengerService,
    limits: dict[Limit, LimitValues],
    driver_id: str,
) -> list[KnapsackItem]:
    candidates = []
    orders = await passenger_service.get_top_order_candidates(
        candidates_amount=CANDIDATES_AMOUNT, current_location=current_location, driver_id=driver_id
    )
    for order in orders:
        if not is_order_acceptable(order=order, limits=limits):
            await passenger_service.release_order_from_freeze(driver_id, order.id)
            continue
        item = KnapsackItem(id=order.id, volume=order.passengers_amount, value=(-1 * order.distance_from_driver))
        if item.value == 0:
            item.value = -1

        candidates.append(item)

    return candidates
