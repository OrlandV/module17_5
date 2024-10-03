from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from backend.db_depends import get_db
from sqlalchemy import select, insert, update, delete
from models import Task, User
from shemas import CreateTask, UpdateTask
from slugify import slugify

router = APIRouter(prefix='/task', tags=['task'])


@router.get('/')
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    tasks = db.scalars(select(Task)).all()
    if len(tasks) == 0:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tasks not found.'
        )
    return tasks


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found.'
        )
    return task


@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], new_task: CreateTask, user_id: int):
    task = db.scalar(select(Task).where(Task.slug == new_task.title.lower()))
    if task is not None:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'The task with title {new_task.title} already exists.'
        )
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found.'
        )
    db.execute(insert(Task).values(
        title=new_task.title,
        content=new_task.content,
        priority=new_task.priority,
        user_id=user_id,
        slug=slugify(new_task.title.lower())
    ))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful.'
    }


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, updated_task: UpdateTask):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found.'
        )
    task = db.scalar(select(Task).where(Task.slug == updated_task.title.lower()))
    if task is not None:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'The task with title {updated_task.title} already exists.'
        )
    db.execute(update(Task).where(Task.id == task_id).values(
        title=updated_task.title,
        content=updated_task.content,
        priority=updated_task.priority,
        slug=slugify(updated_task.title.lower())
    ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task update is successful.'
    }


@router.delete('/delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task was not found.'
        )
    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Task delete is successful.'
    }
