from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from todo_service.core.database import get_db
from todo_service.core.auth import get_current_user
from todo_service.todos.repository.todo_repo import TodosRepository
from todo_service.todos.service.todo_service import TodosService
from todo_service.todos.schemas import TodoCreate, TodoUpdate, TodoResponse, UserRead


router = APIRouter(tags=["Todos"], dependencies=[Depends(get_current_user)])


def get_todos_service(session: AsyncSession = Depends(get_db)) -> TodosService:
    """Dependency for getting todos service instance."""
    repository = TodosRepository(session)
    return TodosService(repository)


@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    data: TodoCreate,
    service: TodosService = Depends(get_todos_service),
    current_user: UserRead = Depends(get_current_user),
)->TodoResponse:
    """Create new todo."""
    created_todo = await service.create_todo(data=data, current_user=current_user)
    return created_todo


@router.get("/todos", response_model=list[TodoResponse])
async def get_all_todos(
    service: TodosService = Depends(get_todos_service),
    current_user: UserRead = Depends(get_current_user),
)->list[TodoResponse]:
    """Get all todos."""
    all_todos = await service.get_todos(current_user=current_user)
    return all_todos


@router.get("/todos/list/{list_id}", response_model=list[TodoResponse])
async def get_todos_by_list_id(
    list_id: int,
    service: TodosService = Depends(get_todos_service),
    current_user: UserRead = Depends(get_current_user),
)->list[TodoResponse]:
    """Get all todos in given list."""
    todos = await service.get_todos_in_list(list_id=list_id, current_user=current_user)    
    return todos


@router.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo_by_id(
    todo_id: int,
    service: TodosService = Depends(get_todos_service),
    current_user: UserRead = Depends(get_current_user),
)->TodoResponse:
    """Get todo by id."""
    todo = await service.get_todo(todo_id=todo_id, current_user=current_user)    
    return todo


@router.patch(
    "/todos/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK
)
async def update_todo_endpoint(
    todo_id: int,
    data: TodoUpdate,
    service: TodosService = Depends(get_todos_service),
    current_user: UserRead = Depends(get_current_user),
)->TodoResponse:
    """Update todo."""
    updated_todo = await service.update_todo(
        todo_id=todo_id, data=data, current_user=current_user
    )    
    return updated_todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_endpoint(
    todo_id: int,
    service: TodosService = Depends(get_todos_service),
    current_user: UserRead = Depends(get_current_user),
)->None:
    """Delete todo."""
    await service.delete_todo(todo_id=todo_id, current_user=current_user)
    