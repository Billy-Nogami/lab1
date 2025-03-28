import socket

# Функция для отправки запроса и получения ответа от сервера
def send_request(request):
    server_address = ('localhost', 9999)

    # Создаем сокет
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(server_address)

        # Отправляем запрос серверу
        client_socket.sendall(request.encode())

        # Получаем ответ от сервера
        full_response = ""
        while True:
            data = client_socket.recv(4096).decode('utf-8')  # Чтение данных по частям
            if not data:
                break
            full_response += data

            # Отправляем подтверждение получения данных
            client_socket.send("ACK".encode())

        print("Ответ от сервера:")
        print(full_response)

# Запрос от пользователя
def get_user_query():
    print("Введите команду:\n1. Для просмотра списка таблиц введите 'show files'\n2. Для просмотра структуры таблицы введите 'show structure <table_name>'\n3. Для выполнения запроса введите SQL-подобный запрос")
    return input("Запрос: ")

# Основной цикл клиента
if __name__ == "__main__":
    while True:
        request = get_user_query()  # Получаем запрос от пользователя
        if request.lower() == "exit":
            print("Завершаем работу.")
            break
        send_request(request)
