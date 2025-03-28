import socket
import csv
import json
import threading
import os

# Функция для обработки запроса клиента
def handle_client(client_socket):
    try:
        # Получаем запрос от клиента
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Получен запрос: {request}")

        if request.strip().lower() == "show files":
            # Запрос для показа структуры файлов проекта
            show_files(client_socket)
        elif request.lower().startswith("show structure"):
            # Запрос для показа структуры таблицы
            table_name = request.split(" ")[2]
            show_structure(table_name, client_socket)
        else:
            # Парсим запрос: предполагаем формат SELECT FROM table WHERE condition
            table_name, condition = parse_request(request)
            # Чтение и фильтрация данных из CSV файла
            csv_file = f"./{table_name}/{table_name}.csv"
            if condition:  # Если есть условие WHERE
                data = filter_data(csv_file, condition)
            else:
                data = get_all_data(csv_file)  # Если нет условия, возвращаем всю таблицу
            # Отправка результата клиенту
            send_csv_result(data, client_socket)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        client_socket.close()

# Показ всех доступных файлов (таблиц)
def show_files(client_socket):
    try:
        # Получаем список всех папок (таблиц)
        directories = [d for d in os.listdir('.') if os.path.isdir(d)]
        response = "Доступные таблицы (папки):\n" + "\n".join(directories)
        client_socket.send(response.encode())
    except Exception as e:
        client_socket.send(f"Ошибка при получении файлов: {e}".encode())

# Показ структуры конкретной таблицы (названия столбцов)
def show_structure(table_name, client_socket):
    try:
        csv_file = f"./{table_name}/{table_name}.csv"
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            structure = reader.fieldnames  # Структура таблицы (названия колонок)
            response = f"Структура таблицы {table_name}:\n" + ", ".join(structure)
            client_socket.send(response.encode())
    except Exception as e:
        client_socket.send(f"Ошибка при получении структуры: {e}".encode())

# Парсинг запроса
def parse_request(request):
    if " WHERE " in request:  # Если есть условие WHERE
        parts = request.split(' WHERE ')
        table_name = parts[0].split('FROM ')[1].strip()
        condition = parts[1].strip()
    else:  # Если нет условия WHERE, то возвращаем пустое условие
        parts = request.split('FROM ')
        table_name = parts[1].strip()
        condition = ""
    return table_name, condition

# Чтение CSV файла и фильтрация данных по условию
def filter_data(csv_file, condition):
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        filtered_rows = []
        column_names = reader.fieldnames  # Получаем все имена столбцов

        for row in reader:
            try:
                # Преобразуем все числа в строках в числа для корректных сравнений
                row = {key: try_convert(value) for key, value in row.items()}
                
                # Применяем условие фильтрации (проверяем, что столбец существует в данных)
                condition_with_columns = condition
                for column in column_names:
                    condition_with_columns = condition_with_columns.replace(column, f"row.get('{column}')")

                # Применяем условие
                if eval(condition_with_columns, {}, {"row": row}):  
                    filtered_rows.append(row)
            except Exception as e:
                print(f"Ошибка при применении условия: {e}")
    return filtered_rows

# Получение всех данных из таблицы
def get_all_data(csv_file):
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        all_rows = [row for row in reader]
    return all_rows

# Функция для попытки преобразования строки в число (int или float)
def try_convert(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

# Отправка результатов в CSV формате
# Отправка результатов в CSV формате по частям
# Отправка результатов в CSV формате по частям с подтверждением от клиента
def send_csv_result(data, client_socket):
    if not data:
        client_socket.send("Нет данных по запросу".encode())
        return

    # Формирование CSV результата
    result = ",".join(data[0].keys()) + "\n"  # Заголовки столбцов
    for row in data:
        result += ",".join(str(row[col]) for col in row) + "\n"

    # Отправка данных по частям (например, по 4096 байт)
    max_chunk_size = 4096  # Размер пакета для отправки

    # Разбиваем результат на части
    for i in range(0, len(result), max_chunk_size):
        chunk = result[i:i + max_chunk_size]
        client_socket.send(chunk.encode())
        print(f"Отправлено {len(chunk)} байт")  # Логируем размер отправленного пакета

        # Ожидаем подтверждение от клиента, что данные получены
        ack = client_socket.recv(1024).decode('utf-8')
        if ack != "ACK":
            print(f"Ошибка: клиент не подтвердил получение данных.")
            break

    print(f"Отправлено всего {len(result)} байт")  # Логируем общий размер отправленных данных


# Функция для запуска сервера
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 9999))
    server.listen(5)

    print("Сервер запущен и ожидает подключения...")

    while True:
        client_socket, addr = server.accept()
        print(f"Подключен клиент {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

start_server()

