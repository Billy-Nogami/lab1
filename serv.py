import socket
import os
import csv
import json

# Функция для получения структуры таблиц (названия файлов CSV)
def get_table_structure():
    table_structure = {}
    # Проходим по всем папкам и подкаталогам, ищем файлы с расширением .csv
    for folder_name, subfolders, filenames in os.walk('.'):
        for file_name in filenames:
            if file_name.endswith('.csv'):
                table_name = file_name.split('.')[0]  # Имя файла — это имя таблицы
                file_path = os.path.join(folder_name, file_name)
                with open(file_path, mode='r', newline='') as file:
                    reader = csv.DictReader(file)
                    table_structure[table_name] = list(reader.fieldnames)  # Сохраняем структуру таблицы
    return table_structure

# Функция для обработки запроса SHOW TABLES
def handle_show_tables(client_socket):
    table_structure = get_table_structure()
    if table_structure:
        response = json.dumps(table_structure)  # Преобразуем структуру таблиц в JSON
        client_socket.sendall(response.encode())
    else:
        client_socket.sendall("Нет доступных таблиц".encode())

# Функция для обработки запроса SELECT
def handle_select(client_socket, table_name, condition):
    file_path = f'./{table_name}.csv'
    if not os.path.exists(file_path):
        client_socket.sendall(f"Таблица {table_name} не найдена.".encode())
        return
    
    with open(file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        result = []
        for row in reader:
            # Применяем условие WHERE, если оно задано
            if condition:
                try:
                    if eval(condition.format(**row)):  # Используем eval для выполнения условия
                        result.append(row)
                except Exception as e:
                    client_socket.sendall(f"Ошибка в условии WHERE: {e}".encode())
                    return
            else:
                result.append(row)
        
        # Если результаты найдены, отправляем их в CSV формате
        if result:
            output = ''
            for row in result:
                output += ','.join([str(value) for value in row.values()]) + '\n'
            client_socket.sendall(output.encode())
        else:
            client_socket.sendall("Нет данных по запросу.".encode())

# Функция для обработки запросов клиента
def handle_client(client_socket):
    data = client_socket.recv(1024).decode()
    print(f"Получен запрос: {data}")

    if data.startswith("SELECT"):
        parts = data.split("WHERE")
        table_name = parts[0].split()[1].strip()
        condition = parts[1].strip() if len(parts) > 1 else None
        handle_select(client_socket, table_name, condition)
    elif data == "SHOW TABLES":
        handle_show_tables(client_socket)
    else:
        client_socket.sendall("Неизвестная команда".encode())

# Основная функция для запуска сервера
def start_server(host='localhost', port=5100):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Сервер запущен и слушает на порту {port}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Клиент подключился: {client_address}")
        handle_client(client_socket)
        client_socket.close()

if __name__ == '__main__':
    start_server()
