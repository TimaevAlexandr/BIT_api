import fastapi
import database.pydantic_models as pydantic_models
from database import crud
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import database.config as config
from database.pydantic_models import Token, TokenData, Admin, UserInDB

# импортируем перемещенные модели


api = fastapi.FastAPI()

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# переписываем функцию под наши нужды
def get_user(username: str):
    if username == config.username:
        return UserInDB(username=username, hashed_password=config.password)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict):
    # нам токен не нужно сжигать, поэтому мы убираем таймдельту
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@api.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@api.get("/users/me/", response_model=Admin)
async def read_users_me(current_user: Admin = Depends(get_current_user)):
    return current_user


"""
ТЕПЕРЬ ДОБАВЛЯЕМ АРГУМЕНТ
current_user: Admin = Depends(get_current_user)
В КАЖДУЮ ФУНКЦИЮ С ОБРАБОТКОЙ ПУТИ,
ЧТОБЫ ДОСТУП К ФУНКЦИЯМ БЫЛ ТОЛЬКО 
У АВТОРИЗОВАННОГО КЛИЕНТА
"""


@api.put('/user/{user_id}')
def update_user(user_id: int, user: pydantic_models.User_to_update = fastapi.Body(), current_user: Admin = Depends(
    get_current_user)):  # используя fastapi.Body() мы явно указываем, что отправляем информацию в теле запроса
    """Обновляем юзера"""
    if user_id == user.id:
        return crud.update_user(user).to_dict()


@api.delete('/user/{user_id}')
@crud.db_session
def delete_user(user_id: int = fastapi.Path(), current_user: Admin = Depends(
    get_current_user)):  # используя fastapi.Path() мы явно указываем, что переменную нужно брать из пути
    """
    Удаляем юзера
    :param user_id:
    :return:
    """
    crud.get_user_by_id(user_id).delete()
    return True


@api.post('/user/create')
def create_user(user: pydantic_models.User_to_create, current_user: Admin = Depends(get_current_user)):
    """
    Создаем Юзера
    :param user:
    :return:
    """
    return crud.create_user(tg_id=user.tg_ID,
                            nick=user.nick if user.nick else None).to_dict()


@api.get('/get_info_by_user_id/{user_id:int}')
@crud.db_session
def get_info_about_user(user_id, current_user: Admin = Depends(get_current_user)):
    """
    Получаем инфу по юзеру
    :param user_id:
    :return:
    """
    return crud.get_user_info(crud.User[user_id])


@api.get('/get_user_balance_by_id/{user_id:int}')
@crud.db_session
def get_user_balance_by_id(user_id, current_user: Admin = Depends(get_current_user)):
    """
    Получаем баланс юзера
    :param user_id:
    :return:
    """
    crud.update_wallet_balance(crud.User[user_id].wallet)
    return crud.User[user_id].wallet.balance


@api.get('/get_total_balance')
@crud.db_session
def get_total_balance(current_user: Admin = Depends(get_current_user)):
    """
    Получаем общий баланс

    :return:
    """
    balance = 0.0
    crud.update_all_wallets()
    for user in crud.User.select()[:]:
        balance += user.wallet.balance
    return balance


@api.get("/users")
@crud.db_session
def get_users(current_user: Admin = Depends(get_current_user)):
    """
    Получаем всех юзеров
    :return list:
    """
    users = []
    for user in crud.User.select()[:]:
        users.append(user.to_dict())
    return users


@api.get("/user_by_tg_id/{tg_id:int}")
@crud.db_session
def get_user_by_tg_id(tg_id, current_user: Admin = Depends(get_current_user)):
    """
    Получаем юзера по айди его ТГ
    :param tg_id:
    :return:
    """
    user = crud.get_user_info(crud.User.get(tg_ID=tg_id))
    return user


@api.get("/get_user_transactions/{user_id:int}")
@crud.db_session
def get_user_transactions(user_id, current_user: Admin = Depends(get_current_user)):
    return crud.get_user_transactions(user_id)


@api.post("/create_transaction/{user_id:int}")
@crud.db_session
def create_transaction(user_id, transaction: pydantic_models.Create_Transaction,
                       current_user: Admin = Depends(get_current_user)):
    return crud.create_transaction(crud.get_user_by_id(user_id), transaction.amount_btc_without_fee,
                                   transaction.receiver_address)


@api.get("/get_user_wallet/{user_id:int}")
@crud.db_session
def get_user_wallet(user_id, current_user: Admin = Depends(get_current_user)):
    return crud.get_wallet_info(crud.User[user_id].wallet)