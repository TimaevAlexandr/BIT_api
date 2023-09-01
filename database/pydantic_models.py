import pydantic
from datetime import datetime


class User(pydantic.BaseModel):
    id: int
    tg_ID:  int
    nick:   str = None
    create_date: datetime
    wallet: 'Wallet'
    sended_transactions: list['Transaction'] = None
    received_transactions:  list['Transaction'] = None


class Transaction(pydantic.BaseModel):
    id: int
    sender: User = None
    receiver: User = None
    sender_wallet: 'Wallet' = None
    receiver_wallet: 'Wallet' = None
    sender_address: str
    receiver_address: str
    amount_btc_with_fee: float
    amount_btc_without_fee: float
    fee: float
    date_of_transaction: datetime
    tx_hash: str


class Wallet(pydantic.BaseModel):
    id: int
    user: User
    balance: float = 0.0
    private_key: str
    address: str
    sended_transactions: list[Transaction] = []
    received_transactions: list[Transaction] = []

class User_to_update(pydantic.BaseModel):
    id: int
    tg_ID:  int = None
    nick:   str = None
    create_date: datetime = None
    wallet: 'Wallet' = None

class User_to_create(pydantic.BaseModel):
    tg_ID:  int = None
    nick:   str = None

class Create_Transaction(pydantic.BaseModel):
    tg_ID : int
    receiver_address : str
    amount_btc_without_fee : float


# auth
class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    username: str | None = None


class Admin(pydantic.BaseModel): # вместо User, так как он уже есть
# а так же удаляем лишние свойства
    username: str


class UserInDB(Admin):
    hashed_password: str

User.model_rebuild()
User_to_create.model_rebuild()
Transaction.model_rebuild()
Create_Transaction.model_rebuild()
Wallet.model_rebuild()