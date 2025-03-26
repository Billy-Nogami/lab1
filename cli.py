import socket
import json

# Функция для отправки запроса и получения ответа от сервера
def send_query(query):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5100))

    client_socket.sendall(query.encode())  # Отправка запроса

    if query == "SHOW TABLES":
        data = client_socket.recv(4096)  # Увеличиваем буфер для получения данных
        if not data:
            print("Нет данных от сервера.")
            return
        try:
            response = json.loads(data.decode())  # Декодируем JSON ответ
            print("Структура таблиц:")
            for table, columns in response.items():
                print(f"{table}: {columns}")
        except json.JSONDecodeError as e:
            print("Ошибка декодирования JSON:", e)
            print("Ответ от сервера:", data.decode())
    elif query.startswith("SELECT"):
        data = client_socket.recv(4096)  # Увеличиваем буфер
        if not data:
            print("Нет данных от сервера.")
            return
        print("Результат запроса:")
        print(data.decode())
    else:
        print("Неизвестная команда.")

    client_socket.close()

if __name__ == '__main__':
    while True:
        query = input("Введите запрос (SHOW TABLES или SELECT): ")
        if query.lower() == "exit":
            break
        send_query(query)
