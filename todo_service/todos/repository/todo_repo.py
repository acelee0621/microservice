from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from todo_service.core.exceptions import NotFoundException
from todo_service.todos.models import Todos
from todo_service.todos.schemas import TodoCreate, TodoUpdate


class TodosRepository:
    """Repository for handling Todos database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: TodoCreate, current_user) -> Todos:
        """Create a new TodoItem item for the current user.

        Args:
            data (TodoCreate): title and description of the new TodoItem.
            current_user (User): current user.

        Returns:
            Todos: newly created TodoItem item.

        Raises:
            AlreadyExistsException: if a TodoItem with the same title already exists.
        """

        new_todo = Todos(
            title=data.title,
            description=data.description,
            list_id=data.list_id,
            user_id=current_user.id,
        )
        self.session.add(new_todo)
        try:
            await self.session.commit()
            await self.session.refresh(new_todo)
            return new_todo
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Database operation failed, create failed {e}")

    async def get_by_id(self, todo_id: int, current_user) -> Todos:
        """Get a TodoItem by ID for the current user.

        Args:
            list_id (int): The ID of the TodoItem to retrieve.
            current_user (User): The current user requesting the TodoItem.

        Returns:
            Todos: The TodoItem if found.

        Raises:
            NotFoundException: If the TodoItem is not found or does not belong to the current user.
        """

        query = select(Todos).where(
            Todos.id == todo_id, Todos.user_id == current_user.id
        )
        result = await self.session.scalars(query)
        todo = result.one_or_none()
        if not todo:
            raise NotFoundException(f"TodoItem with id {todo_id} not found")
        return todo

    async def get_all(self, current_user) -> list[Todos]:
        """Get all TodoItems for the current user.

        Args:
            current_user (User): current user.

        Returns:
            list[Todos]: List of all TodoItems.
        """
        result = await self.session.scalars(
            select(Todos).where(Todos.user_id == current_user.id)
        )
        return result.all()

    async def get_by_list_id(self, list_id: int, current_user) -> list[Todos]:
        """Get all TodoItems for the current user in a given list.

        Args:
            list_id (int): The ID of the list to retrieve TodoItems from.
            current_user (User): The current user requesting the TodoItems.

        Returns:
            list[Todos]: List of all TodoItems in the list.
        """
        query = select(Todos).where(
            Todos.list_id == list_id, Todos.user_id == current_user.id
        )
        result = await self.session.scalars(query)
        todos = result.all()
        return todos

    async def update(self, todo_id: int, data: TodoUpdate, current_user) -> Todos:
        """Update an existing TodoItem item for the current user.

        Args:
            list_id (int): The ID of the TodoItem to update.
            data (TodoUpdate): The update data containing fields to modify.
            current_user (User): The current user performing the update.

        Returns:
            Todos: The updated TodoItem item.

        Raises:
            ValueError: If no fields are provided for update.
            NotFoundException: If the TodoItem is not found or does not belong to the current user.
        """
        query = select(Todos).where(Todos.id == todo_id, Todos.user_id == current_user.id)
        result = await self.session.scalars(query)
        todo_item = result.one_or_none()
        if not todo_item:
            raise NotFoundException(
                f"TodoItem with id {todo_id} not found or does not belong to the current user or list"
            )
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            raise ValueError("No fields to update")
        for key, value in update_data.items():
            # 确保不修改 list_id 和 user_id
            if key not in {"list_id", "user_id"}:
                setattr(todo_item, key, value)            
        await self.session.commit()
        return todo_item

    async def delete(self, todo_id: int, current_user) -> None:
        """Delete an existing TodoItem for the current user.

        Args:
            list_id (int): The ID of the TodoItem to delete.
            current_user (User): The current user performing the deletion.

        Raises:
            NotFoundException: If the TodoItem is not found or does not belong to the current user.
        """
        query = select(Todos).where(Todos.id == todo_id, Todos.user_id == current_user.id)
        result = await self.session.scalars(query)
        todo_item = result.one_or_none()
        if not todo_item:        
            raise NotFoundException(f"TodoItem with id {todo_id} not found")
        await self.session.delete(todo_item)
        await self.session.commit()