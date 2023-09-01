import requests
import database.pydantic_models as pydantic_models
from database.config import api_url



# создаем заголовок в котором указываем, что тип контента - форма
form_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# когда мы отправляем данные в виде формы,
# то присваиваем значения параметрам через равно,
# а перечисляем их через амперсанд
payload = 'username=admin&password=admin'
raw_token = requests.post(api_url+"/token",
                         headers=form_headers,
                         data=payload)
token = raw_token.json()     # получаем словарь из ответа сервера
sesh = requests.Session()   # создаем экземпляр сессии
# добавляем хедеры с токеном авторизации, благодаря чему API будет понимать кто мы и возвращать нужные нам ответы
sesh.headers = {
      'accept': 'application/json',
  'Authorization': "Bearer " + token['access_token']
}


# Далее мы заменяем requests на sesh. Все методы у него такие же.
def update_user(user: dict):
    """Обновляем юзера"""
    # валидируем данные о юзере, так как мы не под декоратором fastapi и это нужно делать вручную
    user = pydantic_models.User_to_update.model_validate(user)
    # чтобы отправить пост запрос - используем метод .post, в аргументе data - отправляем строку в формате json
    responce = sesh.put(f'{api_url}/user/{user.id}', data=user.model_dump_json())
    try:
        return responce.json()
    except:
        return responce.text


def delete_user(user_id: int):
    """
    Удаляем юзера
    :param user_id:
    :return:
    """
    return sesh.delete(f'{api_url}/user/{user_id}').json()


def create_user(user: pydantic_models.User_to_create):
    """
    Создаем Юзера
    :param user:
    :return:
    """
    user = pydantic_models.User_to_create.model_validate(user)
    return sesh.post(f'{api_url}/user/create', data=user.model_dump_json()).json()


def get_info_about_user(user_id):
    """
    Получаем инфу по юзеру
    :param user_id:
    :return:
    """
    return sesh.get(f'{api_url}/get_info_by_user_id/{user_id}').json()


def get_user_balance_by_id(user_id):
    """
    Получаем баланс юзера
    :param user_id:
    :return:
    """
    responce = sesh.get(f'{api_url}/get_user_balance_by_id/{user_id}')
    try:
        return float(responce.text)
    except:
        return f'Error: Not a Number\nResponce: {responce.text}'


def get_total_balance():
    """
    Получаем общий баланс

    :return:
    """
    responce = sesh.get(f'{api_url}/get_total_balance')
    try:
        return float(responce.text)
    except:
        return f'Error: Not a Number\nResponce: {responce.text}'


def get_users():
    """
    Получаем всех юзеров
    :return list:
    """
    return sesh.get(f"{api_url}/users").json()


def get_user_by_tg_id(tg_id):
    """
    Получаем юзера по айди его ТГ
    :param tg_id:
    :return:
    """
    return sesh.get(f"{api_url}/user_by_tg_id/{tg_id}").json()


def get_user_transactions(user_id):
    responce = sesh.get(f"{api_url}/get_user_transactions/{user_id}")
    try:
        return responce.json()
    except Exception as E:
        return f"{responce.text} \n" \
               f"Exception: {E.args, E.__traceback__}"


def create_transaction(tg_id, receiver_address: str, amount_btc_without_fee: float):
    user_dict = get_user_by_tg_id(tg_id)
    payload = {'receiver_address': receiver_address,
               'amount_btc_without_fee': amount_btc_without_fee}
    responce = sesh.post(f"{api_url}/create_transaction/{user_dict['id']}", json=payload)
    return responce.text


def get_user_wallet_by_tg_id(tg_id):
    user_dict = get_user_by_tg_id(tg_id)
    return sesh.get(f"{api_url}/get_user_wallet/{user_dict['id']}").json()