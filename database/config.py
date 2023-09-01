from passlib.context import CryptContext

privatekey_wallet = "cQL77b3ugaphBssqM71sCP9NZjvh43RJe7upimCyqdGanfSBXbvg"
bot_token = "6414062136:AAHqjtcnGiJfHzC697r4rbb9V5wLq_khNsk"
tg_admin_id = 822433170
username = "admin"

# create a test account for admin panel

word = "admin"
# for that we import (1 line)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# make hashed password
password = pwd_context.hash(word)
SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

api_url = "http://127.0.0.1:8000"