from todo_service.todos.repository.todo_repo import TodosRepository
from todo_service.todos.schemas import TodoResponse, TodoCreate, TodoUpdate


class TodosService:
    def __init__(self, repository: TodosRepository):
        """Service layer for todos operations."""

        self.repository = repository

    async def create_todo(self, data: TodoCreate, current_user) -> TodoResponse:
        """Create a new TodoItem item for the current user.

        Args:
            data (TodoCreate): title and description of the new TodoItem.
            current_user (User): current user.

        Returns:
            TodoResponse: newly created TodoItem item.
        """
        todo = await self.repository.create(data, current_user)
        return TodoResponse.model_validate(todo)

    async def get_todo(self, todo_id: int, current_user) -> TodoResponse:
        """Get a TodoItem by ID for the current user.

        Args:
            todo_id: The ID of the TodoItem.
            current_user (User): The current user requesting the TodoItem.

        Returns:
            TodoResponse: The TodoItem if found.
        """
        list = await self.repository.get_by_id(todo_id, current_user)
        return TodoResponse.model_validate(list)

    async def get_todos(self, current_user) -> list[TodoResponse]:
        """Get all TodoItems for the current user.

        Args:
            current_user (User): current user.

        Returns:
            list[TodoResponse]: List of all TodoItems.
        """
        todos = await self.repository.get_all(current_user)
        return [TodoResponse.model_validate(todo) for todo in todos]

    async def get_todos_in_list(self, list_id: int, current_user) -> list[TodoResponse]:
        """Get all TodoItems in a given list for the current user.

        Args:
            list_id: The ID of the list to retrieve TodoItems from.
            current_user (User): The current user requesting the TodoItems.

        Returns:
            list[TodoResponse]: List of all TodoItems in the list.
        """
        todos = await self.repository.get_by_list_id(list_id, current_user)
        return [TodoResponse.model_validate(todo) for todo in todos]

    async def update_todo(
        self, todo_id: int, data: TodoUpdate, current_user
    ) -> TodoResponse:
        """Update an existing TodoItem for the current user.

        Args:
            todo_id (int): The ID of the TodoItem to update.
            data (TodoUpdate): The update data containing fields to modify.
            current_user (User): The current user performing the update.

        Returns:
            TodoResponse: The updated TodoItem.
        """
        list = await self.repository.update(todo_id, data, current_user)
        return TodoResponse.model_validate(list)

    async def delete_todo(self, todo_id: int, current_user) -> None:
        """Delete an existing TodoItem for the current user.

        Args:
            todo_id (int): The ID of the TodoItem to delete.
            current_user (User): The current user performing the deletion.
        """
        await self.repository.delete(todo_id, current_user)
