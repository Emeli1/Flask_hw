import requests

# # Регистрация
response = requests.post("http://127.0.0.1:5000//register",
                         json={"email": "hdg@mail.ru",
                               "password": "123fd54sa",
                               })


# Авторизация
login_data = {"email": "hdg@mail.ru", "password": "123fd54sa"}
login_response = requests.post("http://127.0.0.1:5000/login", json=login_data)

if login_response.status_code == 200:
    token = login_response.json().get("token")  # Извлекаем токен из ответа
    user_id = 1

    # Создание объявления
    advs_data = {"name": "adv_1", "description": "sale", "owner": user_id}
    headers = {"Authorization": f"Bearer {token}"}  # Добавляем Bearer схему
    advs_response = requests.post("http://127.0.0.1:5000/advs", json=advs_data, headers=headers)
    adv_id = advs_response.json().get("id")

# response = requests.get("http://127.0.0.1:5000//advs/1")

# Изменение объявления
patch_headers = {"Authorization": f"Bearer {token}"}
patch_data = {"description": "rent"}

patch_response = requests.patch(f"http://127.0.0.1:5000/advs/{adv_id}", headers=patch_headers,
                                json=patch_data)

# Удаление объявления
delete_headers = {"Authorization": f"Bearer {token}"}
delete_response = requests.delete(f"http://127.0.0.1:5000/advs/{adv_id}", headers=delete_headers)


# print(response.text)
# print(response.status_code)

print(login_response.text)
print(login_response.status_code)

print(patch_response.text)
print(patch_response.status_code)

print(delete_response.text)
print(delete_response.status_code)