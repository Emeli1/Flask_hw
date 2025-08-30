from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
import jwt
import datetime

from models import Session, Advertisement, User
from errors import HttpError
from schema import CreateAdvRequest, UpdateAdvRequest, validate, RegisterRequest, AuthRequest
from flask_bcrypt import Bcrypt

app = Flask("app")
bcrypt = Bcrypt(app)


SECRET_KEY = '1234'

def create_token(user_id):
    token = jwt.encode({
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1) # Токен будет действителен 1 день
    }, SECRET_KEY, algorithm="HS256")
    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None # Токен истёк
    except jwt.InvalidTokenError:
        return None # Неверный токен


def hash_password(password: str) -> str:
    password = password.encode()
    password = bcrypt.generate_password_hash(password)
    password = password.decode()
    return password


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(response):
    request.session.close()
    return response


@app.errorhandler(HttpError)
def error_handler(err: HttpError):
    http_response = jsonify({"error": err.message})
    http_response.status_code = err.status_code
    return http_response


def get_current_user():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    parts = auth_header.split(" ")

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    try:
        token = parts[1]
    except IndexError:
        return None

    user_id = decode_token(token)
    if user_id:
        user = request.session.query(User).filter_by(id=user_id).first()  # Ищем пользователя по ID
        return user
    return None


def get_adv_by_id(advertisement_id: int) -> Advertisement:
    adv = request.session.get(Advertisement, advertisement_id)
    if adv is None:
        raise HttpError(404, "Advertisement not found")
    return adv


def add_adv(advertisement: Advertisement) -> None:
    try:
        request.session.add(advertisement)
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, message="Advertisement already exists")


def register():
    json_data = validate(RegisterRequest, request.json)
    # Хэшируем пароль
    hashed_password = hash_password(json_data["password"])
    user = User(
        email=json_data['email'],
        hashed_password=hashed_password
    )
    try:
        request.session.add(user)
        request.session.commit()
        return jsonify({"message": "User registered successfully."}), 201
    except IntegrityError:
        request.session.rollback()  # Откатываем сессию при ошибке
        raise HttpError(409, message="User with this email already exists.")


def login():
    json_data = validate(AuthRequest, request.json)
    user = request.session.query(User).filter_by(email=json_data["email"]).first()
    if user and bcrypt.check_password_hash(user.hashed_password, json_data["password"]):
        token = create_token(user.id) # Создаём токен для пользователя
        return jsonify({"message": "Login successful", "token": token}), 200
    else:
        raise HttpError(401, message="Invalid email or password.")


class AdvertisementView(MethodView):

    def get(self, advertisement_id):
        adv = get_adv_by_id(advertisement_id)
        return jsonify(adv.json)

    def post(self):
        current_user = get_current_user()
        if not current_user:
            raise HttpError(403, message="You must be logged in to create an advertisement.")

        json_data = validate(CreateAdvRequest, request.json)

        adv = Advertisement(
            name=json_data["name"],
            description=json_data["description"],
            owner = current_user.id
        )
        add_adv(adv)
        return jsonify(adv.id_json)

    def patch(self, advertisement_id):
        current_user = get_current_user()
        if not current_user:
            raise HttpError(403, message="You must be logged in to edit an advertisement.")

        adv = get_adv_by_id(advertisement_id)
        if adv.owner != current_user.email:
            raise HttpError(403, message="You do not have permission to edit this advertisement.")

        json_data = validate(UpdateAdvRequest, request.json)

        if "name" in json_data:
            adv.name = json_data["name"]
        if "description" in json_data:
            adv.description = json_data["description"]
        if "owner" in json_data:
            adv.owner = json_data["owner"]

        add_adv(adv)
        return jsonify(adv.id_json)

    def delete(self, advertisement_id):
        current_user = get_current_user()
        if not current_user:
            raise HttpError(403, message="You must be logged in to delete an advertisement.")

        adv = get_adv_by_id(advertisement_id)
        if adv.owner != current_user.email:
            raise HttpError(403, message="You do not have permission to delete this advertisement.")

        request.session.delete(adv)
        request.session.commit()
        return jsonify({"message": "Advertisement deleted"})


adv_view = AdvertisementView.as_view("adv_view")

app.add_url_rule("/register", view_func=register, methods=["POST"])
app.add_url_rule("/login", view_func=login, methods=["POST"])
app.add_url_rule("/advs", view_func=adv_view, methods=["POST"])
app.add_url_rule(
    "/advs/<int:advertisement_id>", view_func=adv_view, methods=["GET", "PATCH", "DELETE"]
)



app.run()