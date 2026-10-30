import requests

def exploit():
    print("Проверка легитимного запроса на авторизацию:\n")
    r = requests.post("http://127.0.0.1:5000/login", data = {'username' : "admin", 'password': "SuperSecretAdminP@ss123!"})
    print(r.text)
    print("Проверка запроса чтения файла:\n")
    r = requests.get("http://127.0.0.1:5000/view", params = {'file':  "financial_2024.txt"})
    print(r.text)

if __name__ == "__main__":
    exploit()