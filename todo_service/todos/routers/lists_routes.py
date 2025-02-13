from typing import Annotated

from fastapi import APIRouter, Depends, status

from todo_service.core.dependencies import DBSessionDep
from todo_service.core.auth import CurrentUserDep, get_current_user
from todo_service.todos.repository.list_repo import TodoListRepository
from todo_service.todos.service.list_service import TodoListService
from todo_service.todos.schemas import ListCreate, ListUpdate, ListResponse


router = APIRouter(tags=["Lists"], dependencies=[Depends(get_current_user)])


def get_list_service(session: DBSessionDep) -> TodoListService:
    """Dependency for getting hero service instance."""
    repository = TodoListRepository(session)
    return TodoListService(repository)


ServiceDep = Annotated[TodoListService, Depends(get_list_service)]


@router.post("/lists", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    service: ServiceDep, current_user: CurrentUserDep, data: ListCreate
) -> ListResponse:
    created_list = await service.create_list(data=data, current_user=current_user)
    return created_list


@router.get("/lists", response_model=list[ListResponse])
async def get_all_lists(service: ServiceDep, current_user: CurrentUserDep):
    all_list = await service.get_lists(current_user=current_user)
    return all_list


@router.get("/lists/{list_id}", response_model=ListResponse)
async def get_list(
    list_id: int,
    service: ServiceDep,
    current_user: CurrentUserDep,
) -> ListResponse:
    list_ = await service.get_list(list_id=list_id, current_user=current_user)
    return list_


@router.put(
    "/lists/{list_id}", response_model=ListResponse, status_code=status.HTTP_200_OK
)
async def update_list_endpoint(
    list_id: int, data: ListUpdate, service: ServiceDep, current_user: CurrentUserDep
) -> ListResponse:
    updated_list = await service.update_list(
        list_id=list_id, data=data, current_user=current_user
    )
    return updated_list


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list_endpoint(
    list_id: int, service: ServiceDep, current_user: CurrentUserDep
) -> None:
    await service.delete_list(list_id=list_id, current_user=current_user)
