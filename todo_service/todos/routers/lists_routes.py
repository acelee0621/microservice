from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from todo_service.core.database import get_db
from todo_service.core.auth import get_current_user
from todo_service.todos.repository.list_repo import TodoListRepository
from todo_service.todos.service.list_service import TodoListService
from todo_service.todos.schemas import ListCreate, ListUpdate, ListResponse, UserRead


router = APIRouter(tags=["Lists"], dependencies=[Depends(get_current_user)])


def get_list_service(session: AsyncSession = Depends(get_db)) -> TodoListService:
    """Dependency for getting hero service instance."""
    repository = TodoListRepository(session)
    return TodoListService(repository)


@router.post("/lists", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    data: ListCreate,
    service: TodoListService = Depends(get_list_service),
    current_user: UserRead = Depends(get_current_user),
) -> ListResponse:
    created_list = await service.create_list(data=data, current_user=current_user)
    return created_list


@router.get("/lists", response_model=list[ListResponse])
async def get_all_lists(
    service: TodoListService = Depends(get_list_service),
    current_user: UserRead = Depends(get_current_user),
):
    all_list = await service.get_lists(current_user=current_user)
    return all_list


@router.get("/lists/{list_id}", response_model=ListResponse)
async def get_list(
    list_id: int,
    service: TodoListService = Depends(get_list_service),
    current_user: UserRead = Depends(get_current_user),
) -> ListResponse:
    list_ = await service.get_list(list_id=list_id, current_user=current_user)
    return list_


@router.put(
    "/lists/{list_id}", response_model=ListResponse, status_code=status.HTTP_200_OK
)
async def update_list_endpoint(
    list_id: int,
    data: ListUpdate,
    service: TodoListService = Depends(get_list_service),
    current_user: UserRead = Depends(get_current_user),
) -> ListResponse:
    updated_list = await service.update_list(
        list_id=list_id, data=data, current_user=current_user
    )
    return updated_list


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list_endpoint(
    list_id: int,
    service: TodoListService = Depends(get_list_service),
    current_user: UserRead = Depends(get_current_user),
) -> None:
    await service.delete_list(list_id=list_id, current_user=current_user)
