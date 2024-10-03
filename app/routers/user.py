from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from backend.db_depends import get_db
from typing import Annotated
from models import User, Task
from shemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify

router = APIRouter(prefix='/user', tags=['user'])


@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    if len(users) == 0:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Users not found.'
        )
    return users


@router.get('/user_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found.'
        )
    return user


@router.get('/user_id/tasks')
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found.'
        )
    tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    if len(tasks) == 0:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tasks not found.'
        )
    return tasks


@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], new_user: CreateUser):
    user = db.scalar(select(User).where(User.slug == new_user.username))
    if user is not None:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'The user with username {new_user.username} already exists.'
        )
    db.execute(insert(User).values(
        username=new_user.username,
        firstname=new_user.firstname,
        lastname=new_user.lastname,
        age=new_user.age,
        slug=slugify(new_user.username)
    ))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful.'
    }


@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, updated_user: UpdateUser):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found.'
        )
    db.execute(update(User).where(User.id == user_id).values(
        firstname=updated_user.firstname,
        lastname=updated_user.lastname,
        age=updated_user.age
    ))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User update is successful.'
    }


@router.delete('/delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User was not found.'
        )
    db.execute(delete(Task).where(Task.user_id == user_id))
    db.execute(delete(User).where(User.id == user_id))
    db.commit()
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'User delete is successful.'
    }
