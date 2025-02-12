from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from todo_service.models import TodoList
from todo_service.schemas import ListBase, ListOut, ListUpdate, ListUpdateOut,ListCreateOut


async def create_list_in_db(db: AsyncSession, current_user, data: ListBase):
    new_list = TodoList(
            title=data.title, description=data.description, user_id=current_user.id
        )
    db.add(new_list)
    try:        
        await db.commit()
        await db.refresh(new_list)
        return ListCreateOut.model_validate(new_list)
    except SQLAlchemyError as e: 
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error, create failed {e}")


async def get_lists(db: AsyncSession, current_user):
    try:
        result = await db.scalars(
            select(TodoList)
            .where(TodoList.user_id == current_user.id)
            .options(selectinload(TodoList.todos))
        )
        lists = result.all()
        return [ListOut.model_validate(list) for list in lists]
    except SQLAlchemyError: 
        raise HTTPException(status_code=500, detail="Database error, get lists failed")


async def get_list_by_id(list_id: int, db: AsyncSession, current_user):
    try:
        query = (
            select(TodoList)
            .where(TodoList.id == list_id, TodoList.user_id == current_user.id)
            .options(selectinload(TodoList.todos))
        )
        result = await db.scalars(query)
        list_ = result.first()        
        if not list_:
            return None
        return ListOut.model_validate(list_)
    except SQLAlchemyError:         
        raise HTTPException(status_code=500, detail="Database error, get list failed")


async def update_list(list_id: int, data: ListUpdate, db: AsyncSession, current_user):
    try:
        query = select(TodoList).where(TodoList.id == list_id, TodoList.user_id == current_user.id)
        result = await db.scalars(query)
        list_item = result.one_or_none()
        if not list_item:
            return None
        # 动态更新字段，排除不可修改的字段
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            # 确保不修改 id 和 user_id
            if key not in {"id", "user_id"}:
                setattr(list_item, key, value)
        db.add(list_item)
        await db.commit()
        await db.refresh(list_item)
        return ListUpdateOut.model_validate(list_item)
    except SQLAlchemyError:  
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error, update failed")


async def delete_list(list_id: int, db: AsyncSession, current_user):
    try:
        query = select(TodoList).where(TodoList.id == list_id, TodoList.user_id == current_user.id)
        result = await db.scalars(query)
        list_item = result.one_or_none()

        if not list_item:
            return None  # 返回 None 由路由函数处理 404

        await db.delete(list_item)
        await db.commit()
        return list_item
    except SQLAlchemyError:  # 仅捕获 SQL 相关异常，避免不必要的 broad exception
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error, delete failed")
