import socket
import os
import struct
import threading

# Время работы сервера в секундах (например, 10 секунд)
SERVER_RUNTIME = 10  # Время работы сервера в секундах

def start_server(host='localhost', port=5200):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Настройка для повторного использования адреса
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Сервер запущен и слушает на порту {port}...")

    # Запускаем таймер для автоматической остановки сервера
    timer = threading.Timer(SERVER_RUNTIME, stop_server, args=(server_socket,))
    timer.start()

    while True:
        try:
            print("Ожидание подключения клиента...")
            client_socket, client_address = server_socket.accept()
            print(f"Клиент подключился: {client_address}")
            handle_client(client_socket)
        except OSError as e:
            print(f"Ошибка при ожидании подключения: {e}")
            break  # Закрытие сервера в случае ошибки

def stop_server(server_socket):
    print("Ожидаем завершения работы сервера через таймер...")
    server_socket.close()
    print("Сервер остановлен.")

def handle_client(client_socket):
    try:
        data = client_socket.recv(1024)  # Получаем данные от клиента
        command_code, args = unpack_command(data)

        # Возвращаем номер полученной команды в текстовом виде
        response = f"Получена команда с номером: {command_code}"

        if command_code == 1:  # LIST_CMD
            response += "\n" + list_files()
            client_socket.send(response.encode('utf-8'))

        elif command_code == 2:  # GET_CMD
            filename = args[0]
            print(f"Запрос на файл: {filename}")  # Печатаем, какой файл был запрашиваем
            response += f"\nЗапрашиваем файл: {filename}"
            file_data = get_file(filename)
            client_socket.send(response.encode('utf-8') + file_data)  # Отправляем файл вместе с текстом

        elif command_code == 3:  # PUT_CMD
            filename = args[0]
            file_data = args[1]
            response += f"\nЗагружаем файл: {filename}"
            response += put_file(filename, file_data)
            client_socket.send(response.encode('utf-8'))

        elif command_code == 4:  # DELETE_CMD
            filename = args[0]
            response += f"\nУдаляем файл: {filename}"
            response += delete_file(filename)
            client_socket.send(response.encode('utf-8'))

    except Exception as e:
        print(f"Произошла ошибка при обработке запроса: {e}")

    finally:
        client_socket.close()
        print("Соединение с клиентом закрыто.")

def list_files():
    return '\n'.join(os.listdir('.'))  # Возвращаем список файлов в текущей директории

def get_file(filename):
    print(f"Сервер ищет файл: {filename}")  # Добавляем отладочную информацию
    try:
        with open(filename, 'rb') as f:
            return f.read()  # Отправляем содержимое файла клиенту
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")  # Добавляем сообщение, если файл не найден
        return "Файл не найден.".encode('utf-8')  # Перекодируем строку в байты с кодировкой utf-8

def put_file(filename, file_data):
    with open(filename, 'wb') as f:
        f.write(file_data)  # Записываем полученные данные в файл
    return f"Файл {filename} успешно загружен."

def delete_file(filename):
    try:
        os.remove(filename)
        return f"Файл {filename} удален."
    except FileNotFoundError:
        return f"Файл {filename} не найден."

def unpack_command(data):
    command_code = struct.unpack('B', data[:1])[0]
    args = []
    data = data[1:]
    while data:
        arg_length = struct.unpack('I', data[:4])[0]
        data = data[4:]
        args.append(data[:arg_length].decode('utf-8'))
        data = data[arg_length:]
    return command_code, args

if __name__ == '__main__':
    start_server()
