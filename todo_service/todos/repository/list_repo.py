from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from todo_service.core.exceptions import AlreadyExistsException, NotFoundException
from todo_service.todos.models import TodoList
from todo_service.todos.schemas import ListCreate, ListUpdate


class TodoListRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ListCreate, current_user) -> TodoList:
        """Create a new TodoList item.

        Args:
            current_user (User): current user.
            data (ListCreate): title and description of the new list.

        Returns:
            TodoList: newly created TodoList item.

        Raises:
            AlreadyExistsException: if a TodoList with the same title already exists.
        """

        new_list = TodoList(
            title=data.title, description=data.description, user_id=current_user.id
        )
        self.session.add(new_list)
        try:
            await self.session.commit()
            await self.session.refresh(new_list)
            return new_list
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistsException(
                f"Todo list with title {data.title} already exists"
            )

    async def get_by_id(self, list_id: int, current_user) -> TodoList:
        """Get a TodoList by ID for the current user.

        Args:
            list_id: The ID of the TodoList.
            current_user_id: The ID of the current user.

        Returns:
            Optional[TodoList]: The TodoList if found, otherwise None.
        """
        query = (
            select(TodoList)
            .where(TodoList.id == list_id, TodoList.user_id == current_user.id)
            .options(selectinload(TodoList.todos))
        )
        result = await self.session.scalars(query)
        list_ = result.one_or_none()
        if not list_:
            raise NotFoundException(f"TodoList with id {list_id} not found")
        return list_

    async def get_all(self, current_user) -> list[TodoList]:
        """Get all lists.

        Returns:
            List[TodoList]: List of all todo lists.
        """
        result = await self.session.scalars(
            select(TodoList)
            .where(TodoList.user_id == current_user.id)
            .options(selectinload(TodoList.todos))
        )
        return result.all()

    async def update(self, list_id: int, data: ListUpdate, current_user) -> TodoList:
        """Update an existing TodoList item for the current user.

        Args:
            list_id (int): The ID of the TodoList to update.
            data (ListUpdate): The update data containing fields to modify.
            current_user (User): The current user performing the update.

        Returns:
            TodoList: The updated TodoList item.

        Raises:
            ValueError: If no fields are provided for update.
            NotFoundException: If the TodoList is not found or does not belong to the current user.
        """

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("No fields to update")
        # 确保不修改 `id` 和 `user_id`
        update_data.pop("id", None)
        update_data.pop("user_id", None)
        query = (
            update(TodoList)
            .where(TodoList.id == list_id, TodoList.user_id == current_user.id)
            .values(**update_data)
        )
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException(
                f"TodoList with id {list_id} not found or does not belong to the current user"
            )
        await self.session.commit()
        return await self.get_by_id(list_id, current_user)

    async def delete(self, list_id: int, current_user) -> None:
        """Delete an existing TodoList item for the current user.

        Args:
            list_id (int): The ID of the TodoList to delete.
            current_user (User): The current user performing the deletion.

        Raises:
            NotFoundException: If the TodoList is not found or does not belong to the current user.
        """
        query = delete(TodoList).where(
            TodoList.id == list_id, TodoList.user_id == current_user.id
        )
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundException(f"TodoList with id {list_id} not found")
        await self.session.commit()
