import requests

# Регистрация
response = requests.post("http://127.0.0.1:5000//register",
                         json={"email": "hdg@mail.ru",
                               "password": "123fd54sa",
                               })


# Авторизация
login_data = {"email": "hdg@mail.ru", "password": "123fd54sa"}
login_response = requests.post("http://127.0.0.1:5000/login", json=login_data)

if login_response.status_code == 200:
    token = login_response.json().get("token")  # Извлекаем токен из ответа

    # Создание объявления
    advs_data = {"name": "adv_1", "description": "sale", "owner": "user_1"}
    headers = {"Authorization": f"Bearer {token}"}  # Добавляем Bearer схему
    advs_response = requests.post("http://127.0.0.1:5000/advs", json=advs_data, headers=headers)

    print(f"Advs response: {advs_response.status_code}, {advs_response.text}")
else:
    print(f"Login failed: {login_response.status_code}, {login_response.text}") # Выводим причину ошибки логина


# response = requests.post("http://127.0.0.1:5000//advs",
#                          json={"name": "adv_1",
#                                "description": "sale",
#                                "owner": "user_1",
#                                })

# response = requests.post("http://127.0.0.1:5000//advs",
#                          json={"name": "adv_2",
#                                "owner": "user_1",
#                                })

response = requests.get("http://127.0.0.1:5000//advs/1")

# response = requests.patch("http://127.0.0.1:5000//advs/1",
#                          json={"name": "adv_1",
#                                "description": "rent",
#                                "owner": "user_1",
#                                })

# response = requests.delete("http://127.0.0.1:5000//advs/1")

print(response.text)
print(response.status_code)
#
# print(login_response.text)
# print(login_response.status_code)