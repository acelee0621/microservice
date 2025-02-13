from todo_service.todos.repository.list_repo import TodoListRepository
from todo_service.todos.schemas import ListResponse, ListCreate, ListUpdate


class TodoListService:
        
    def __init__(self, repository: TodoListRepository):
        """Service layer for list operations."""
        
        self.repository = repository        
        
    async def create_list(self, data: ListCreate, current_user) -> ListResponse:
        """Create a new TodoList item.
        
        Args:
            data (ListCreate): title and description of the new list.
            current_user (User): current user.
        
        Returns:
            ListResponse: newly created TodoList item.
        """

        list = await self.repository.create(data, current_user)
        return ListResponse.model_validate(list)        
        
    async def get_list(self, list_id: int, current_user) -> ListResponse:
        """Get a TodoList by ID for the current user.
        
        Args:
            list_id: The ID of the TodoList.
            current_user (User): current user.
        
        Returns:
            ListResponse: The TodoList if found, otherwise None.
        """
        list = await self.repository.get_by_id(list_id, current_user)
        return ListResponse.model_validate(list)    

    async def get_lists(self, current_user) -> list[ListResponse]:
        """Get all lists for the current user.
        
        Args:
            current_user (User): current user.
        
        Returns:
            list[ListResponse]: List of all todo lists.
        """
        lists = await self.repository.get_all(current_user)
        return [ListResponse.model_validate(list) for list in lists]

    async def update_list(self, list_id: int, data: ListUpdate, current_user) -> ListResponse:
        """Update an existing TodoList item for the current user.
        
        Args:
            list_id: The ID of the TodoList to update.
            data (ListUpdate): The update data containing fields to modify.
            current_user (User): current user.
        
        Returns:
            ListResponse: The updated TodoList item.
        """
        list = await self.repository.update(list_id, data, current_user)
        return ListResponse.model_validate(list)

    async def delete_list(self, list_id: int, current_user) -> None:
        """Delete an existing TodoList item for the current user.

        Args:
            list_id (int): The ID of the TodoList to delete.
            current_user (User): The current user performing the deletion.
        
        """

        await self.repository.delete(list_id, current_user)