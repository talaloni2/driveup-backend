import math
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from component_factory import get_passenger_service, get_knapsack_service, get_driver_service, get_time_service, \
    get_directions_service, get_cost_estimation_service, get_user_handler_service
from controllers.utils import AuthenticatedUser, authenticated_user, adjust_timezone
from mappings.factory_mapping import LIMITS_MAPPING
from model.driver_drive_order import DriverDriveOrder, DriveOrderStatus
from model.passenger_drive_order import PassengerDriveOrderStatus, PassengerDriveOrder
from model.requests.driver import DriverRequestDrive, DriverAcceptDrive, Limit, LimitValues
from model.requests.knapsack import KnapsackItem
from model.responses.driver import DriveDetails, OrderLocation
from model.responses.geocode import Geocode
from model.responses.knapsack import SuggestedSolution, KnapsackSolution
from model.responses.success import SuccessResponse
from model.responses.user import UserHandlerGetByEmailResponse
from model.top_candidate import TopCandidate
from service.cost_estimation_service import CostEstimationService
from service.directions_service import DirectionsService
from service.driver_service import DriverService
from service.knapsack_service import KnapsackService
from service.passenger_service import PassengerService
from service.time_service import TimeService
from service.user_handler_service import UserHandlerService

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


async def _estimate_incomes(passenger_service: PassengerService, suggestion: SuggestedSolution) -> SuggestedSolution:
    for suggestion_id, knapsack_suggestion in suggestion.solutions.items():
        total_income = 0
        for item in knapsack_suggestion.items:
            order = await passenger_service.get_by_order_id(int(item.id))
            total_income += order.estimated_cost
        knapsack_suggestion.total_value = total_income
    return suggestion


@router.post("/request-drives")
async def order_new_drive(
    order_request: DriverRequestDrive,
    force_reject: bool = False,
    knapsack_service: KnapsackService = Depends(get_knapsack_service),
    user: AuthenticatedUser = Depends(authenticated_user),
    passenger_service: PassengerService = Depends(get_passenger_service),
    driver_service: DriverService = Depends(get_driver_service),
    time_service: TimeService = Depends(get_time_service),
    directions_service: DirectionsService = Depends(get_directions_service),
    cost_estimation_service: CostEstimationService = Depends(get_cost_estimation_service),
) -> SuggestedSolution:

    if not force_reject:
        current_drive_orders: list[DriverDriveOrder] = await driver_service.get_suggestions(user.email)
        all_drive_orders_valid = all(d.expires_at > time_service.utcnow() for d in current_drive_orders)
        if current_drive_orders and all_drive_orders_valid:
            suggestions = _orders_to_suggestions(current_drive_orders, time_service)
            suggestions = get_suggestions_with_total_value_volume(suggestions)
            return await _estimate_incomes(passenger_service, suggestions)

    await reject_drives(knapsack_service, user, driver_service)
    rides = await get_top_candidates(
        current_location=[order_request.current_lat, order_request.current_lon],
        passenger_service=passenger_service,
        limits=order_request.limits,
        driver_id=user.email,
        directions_service=directions_service,
        cost_estimation_service=cost_estimation_service,
        time_service=time_service,
    )
    for ride in rides:
        await passenger_service.set_frozen_by(int(ride.id), user.email)
    suggestions = await knapsack_service.suggest_solution(user.email, 4, rides)
    suggestions = get_suggestions_with_total_value_volume(suggestions)
    await driver_service.save_suggestions(user.email, suggestions, [order_request.current_lat, order_request.current_lon])
    suggestions.time = adjust_timezone(suggestions.time, time_service)
    suggestions.expires_at = adjust_timezone(suggestions.expires_at, time_service)
    suggestions = await _estimate_incomes(passenger_service, suggestions)

    return suggestions


@router.post("/accept-drive")
async def accept_drive(
    accept_drive_request: DriverAcceptDrive,
    knapsack_service: KnapsackService = Depends(get_knapsack_service),
    passenger_service: PassengerService = Depends(get_passenger_service),
    driver_service: DriverService = Depends(get_driver_service),
    user: AuthenticatedUser = Depends(authenticated_user),
    time_service: TimeService = Depends(get_time_service),
    directions_service: DirectionsService = Depends(get_directions_service),
    users_service: UserHandlerService = Depends(get_user_handler_service),
) -> SuccessResponse:

    now = time_service.utcnow()
    driver_order = await _get_verified_order(accept_drive_request, driver_service, now, user)

    accept_success = await knapsack_service.accept_solution(
        user_id=user.email, solution_id=accept_drive_request.order_id
    )
    if not accept_success:
        return SuccessResponse(success=False)

    await _update_frozen_orders(accept_drive_request, driver_order, passenger_service, user)
    await driver_service.set_drive_status(driver_order.id, DriveOrderStatus.ACTIVE)

    await _update_estimated_arrivals(accept_drive_request, directions_service, now, passenger_service, driver_service, users_service, user)
    await reject_drives(knapsack_service, user, driver_service)
    return SuccessResponse(success=True)


async def _update_frozen_orders(accept_drive_request: DriverAcceptDrive, driver_order: DriverDriveOrder, passenger_service: PassengerService, user: AuthenticatedUser):
    order_ids = [int(order["id"]) for order in driver_order.passenger_orders]
    for order_id in order_ids:
        await passenger_service.activate_drive(order_id=order_id, drive_id=accept_drive_request.order_id)
    await passenger_service.release_unchosen_orders_from_freeze(user.email, order_ids)


async def _get_verified_order(accept_drive_request: DriverAcceptDrive, driver_service: DriverService, now: datetime, user: AuthenticatedUser) -> DriverDriveOrder:
    suggestion = await driver_service.get_suggestion(user.email, accept_drive_request.order_id)
    if not suggestion or suggestion.expires_at < now:
        raise HTTPException(
            status_code=HTTPStatus.NOT_ACCEPTABLE, detail={"message": "Suggestion not exists or expired"}
        )
    return suggestion


async def _update_estimated_arrivals(accept_drive_request: DriverAcceptDrive, directions_service: DirectionsService, now: datetime, passenger_service: PassengerService, driver_service: DriverService, users_service: UserHandlerService, user: AuthenticatedUser):
    route = await order_details(accept_drive_request.order_id, passenger_service, driver_service, users_service, user)
    passenger_locations = [r for r in route.order_locations if r.is_start_address]
    total_time = 0
    for i, loc in enumerate(passenger_locations):
        if i == 0:  # Driver is the first point, no need to estimate arrival time
            continue
        total_time += (await directions_service.get_directions(passenger_locations[i - 1].address,
                                                               passenger_locations[i].address)).duration_seconds
        await passenger_service.update_estimated_arrival(loc.user_email, accept_drive_request.order_id,
                                                         now + timedelta(seconds=total_time))


@router.post("/reject-drives")
async def reject_drives(
    knapsack_service: KnapsackService = Depends(get_knapsack_service),
    user: AuthenticatedUser = Depends(authenticated_user),
    driver_service: DriverService = Depends(get_driver_service),
) -> SuccessResponse:
    await driver_service.reject_solutions(user.email)
    resp = await knapsack_service.reject_solutions(user_id=user.email)
    return SuccessResponse(success=resp)


@router.get("/drive-details-preview/{drive_id}")
async def order_details_preview(
    drive_id: str,
    passenger_service: PassengerService = Depends(get_passenger_service),
    driver_service: DriverService = Depends(get_driver_service),
    users_service: UserHandlerService = Depends(get_user_handler_service),
    user: AuthenticatedUser = Depends(authenticated_user),
) -> DriveDetails:
    driver_drive = await driver_service.get_driver_drive_by_id(drive_id)
    passenger_order_ids = [int(passenger_order["id"]) for passenger_order in driver_drive.passenger_orders]
    passenger_orders: list[PassengerDriveOrder] = await passenger_service.get_by_ids(passenger_order_ids)

    return await _order_details(drive_id, passenger_orders, driver_drive, users_service, user)


@router.get("/drive-details/{drive_id}")
async def order_details(
    drive_id: str,
    passenger_service: PassengerService = Depends(get_passenger_service),
    driver_service: DriverService = Depends(get_driver_service),
    users_service: UserHandlerService = Depends(get_user_handler_service),
    user: AuthenticatedUser = Depends(authenticated_user),
) -> DriveDetails:

    passenger_orders: list[PassengerDriveOrder] = await passenger_service.get_by_drive_id(drive_id=drive_id)
    driver_drive = await driver_service.get_driver_drive_by_id(drive_id=drive_id)
    return await _order_details(drive_id, passenger_orders, driver_drive, users_service, user)


async def _add_phone_and_name_to_order_locations(passengers_order_locations: list[OrderLocation], token: str, users_service: UserHandlerService):
    found_users: dict[str, UserHandlerGetByEmailResponse] = {}
    for passengers_order_location in passengers_order_locations:
        email = passengers_order_location.user_email
        if email not in found_users:
            found_users[email] = await users_service.get_user_by_email(email, token)
        user = found_users[email].result
        passengers_order_location.name = user.full_name
        passengers_order_location.phone = user.phone_number
    return passengers_order_locations


async def _order_details(drive_id: str, passenger_orders: list[PassengerDriveOrder], driver_drive: DriverDriveOrder, users_service: UserHandlerService, driver: AuthenticatedUser) -> DriveDetails:
    if not passenger_orders or not driver_drive:
        raise HTTPException(
            status_code=HTTPStatus.NOT_ACCEPTABLE, detail={"message": "Drive id not exists"}
        )

    order_locations = []
    driver_user = await users_service.get_user_by_email(driver.email, driver.token)
    driver_order_location = OrderLocation(
        user_email=driver_drive.driver_id,
        is_driver=True,
        is_start_address=True,
        address=Geocode(latitude=driver_drive.current_location[0], longitude=driver_drive.current_location[1]),
        price=0,
        name=driver_user.result.full_name,
        phone=driver_user.result.phone_number,
    )
    order_locations.append(driver_order_location)

    current_location = Geocode(latitude=driver_drive.current_location[0], longitude=driver_drive.current_location[1])
    passengers_order_locations, total_price = await build_order_locations_list(current_location=current_location, other_drives=passenger_orders)

    passengers_order_locations = await _add_phone_and_name_to_order_locations(passengers_order_locations, driver.token, users_service)
    order_locations.extend(passengers_order_locations)

    return DriveDetails(
        time=driver_drive.time,
        id=drive_id,
        order_locations=order_locations,
        total_price=total_price
    )


@router.post("/finish-drive/{drive_id}")
async def finish_drive(
        drive_id: str,
        passenger_service: PassengerService = Depends(get_passenger_service),
        driver_service: DriverService = Depends(get_driver_service),
        user: AuthenticatedUser = Depends(authenticated_user),
):
    drive: DriverDriveOrder = await driver_service.get_driver_drive_by_id(drive_id)
    _validate_drive_for_finish(drive, user)

    await _finish_passenger_orders(drive_id, passenger_service)
    await driver_service.set_drive_status(drive_id, DriveOrderStatus.FINISHED)

    return SuccessResponse(success=True)


async def _finish_passenger_orders(drive_id, passenger_service):
    passenger_orders = await passenger_service.get_by_drive_id_iter(drive_id=drive_id)
    for passenger_order in passenger_orders:
        await passenger_service.set_status_to_drive_order(passenger_order.id, PassengerDriveOrderStatus.FINISHED)


def _validate_drive_for_finish(drive, user):
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")
    if drive.driver_id != user.email:
        raise HTTPException(status_code=400, detail="Driver is not assigned to this drive")
    if drive.status != DriveOrderStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Non Active drive cannot be finished")


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
    directions_service: DirectionsService,
    cost_estimation_service: CostEstimationService,
    time_service: TimeService,
) -> list[KnapsackItem]:
    candidates = []
    orders = await passenger_service.get_top_order_candidates(
        candidates_amount=CANDIDATES_AMOUNT, current_location=current_location, driver_id=driver_id
    )
    current_location_as_geo: Geocode = Geocode(latitude=current_location[0], longitude=current_location[1])
    for order in orders:
        if not is_order_acceptable(order=order, limits=limits):
            await passenger_service.release_order_from_freeze(driver_id, order.id)
            continue
        profit = await _estimate_driver_profit(cost_estimation_service, current_location_as_geo, directions_service,
                                               order, time_service)
        profit = max(profit, 1)
        item = KnapsackItem(id=str(order.id), volume=order.passengers_amount, value=profit)
        candidates.append(item)

    return candidates


async def _estimate_driver_profit(cost_estimation_service: CostEstimationService, driver_location: Geocode, directions_service: DirectionsService, order: TopCandidate,
                                  time_service):
    passenger_start_point: Geocode = Geocode(latitude=order.source_location[0], longitude=order.source_location[1])
    directions = await directions_service.get_directions(driver_location, passenger_start_point)
    arrival_cost = cost_estimation_service.estimate_cost(time_service.now(), directions)
    return order.estimated_cost - arrival_cost


async def get_next_drive(current_location: Geocode, other_drives: list[PassengerDriveOrder]) -> PassengerDriveOrder:
    closest_drive = None
    min_distance = float('inf')

    for drive in other_drives:
        distance = calculate_distance(current_location.latitude, current_location.longitude, drive.source_location[0], drive.source_location[1])

        if distance < min_distance:
            min_distance = distance
            closest_drive = drive

    return closest_drive


def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    radius_of_earth = 6371  # Earth's radius in kilometers
    distance = radius_of_earth * c

    return distance


async def build_order_locations_list(current_location: Geocode, other_drives: list[PassengerDriveOrder]):
    total_price = 0
    drive_list = []
    remaining_pickup_drives: list[PassengerDriveOrder] = other_drives.copy()
    remaining_drop_drives: list[PassengerDriveOrder] = other_drives.copy()

    while remaining_pickup_drives:
        next_drive: PassengerDriveOrder = await get_next_drive(current_location, remaining_pickup_drives)
        if next_drive:
            total_price += next_drive.estimated_cost
            next_order_location = OrderLocation(
                user_email=next_drive.email,
                is_driver=False,
                is_start_address=True,
                address=Geocode(latitude=next_drive.source_location[0], longitude=next_drive.source_location[1]),
                price=next_drive.estimated_cost
            )

            drive_list.append(next_order_location)
            current_location = Geocode(latitude=next_drive.source_location[0], longitude=next_drive.source_location[1])
            remaining_pickup_drives.remove(next_drive)
        else:
            break

    while remaining_drop_drives:
        next_drive: PassengerDriveOrder = await get_next_drive(current_location, remaining_drop_drives)
        if next_drive:
            next_order_location = OrderLocation(
                user_email=next_drive.email,  # driver_drive.email,
                is_driver=False,
                is_start_address=False,
                address=Geocode(latitude=next_drive.dest_location[0], longitude=next_drive.dest_location[1]),
                price=next_drive.estimated_cost
            )

            drive_list.append(next_order_location)
            current_location = Geocode(latitude=next_drive.dest_location[0], longitude=next_drive.dest_location[1])
            remaining_drop_drives.remove(next_drive)
        else:
            break

    return drive_list, total_price




