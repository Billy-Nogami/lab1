import socket
import struct

def send_command(command_code, *args):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Подключаемся к серверу на localhost и порту 5100
    print("Попытка подключиться к серверу...")
    client_socket.connect(('localhost', 5200))  # Подключаемся к серверу
    print("Успешное подключение к серверу!")

    # Упаковываем команду и аргументы в бинарный формат
    command = pack_command(command_code, *args)
    print(f"Отправка команды на сервер: {command}")

    # Отправляем команду на сервер
    client_socket.send(command)

    # Получаем ответ от сервера
    data = client_socket.recv(1024)
    print(f"Ответ от сервера: {data.decode('utf-8')}")

    # Получаем сам файл, если он есть
    file_data = client_socket.recv(1024)
    if file_data:
        with open(f"received_{args[0]}", 'wb') as f:
            f.write(file_data)  # Сохраняем файл на клиенте
        print(f"Файл {args[0]} получен и сохранен как received_{args[0]}")
    else:
        print("Файл не был найден или не был передан.")

    # Закрываем соединение с сервером
    client_socket.close()
    print("Соединение с сервером закрыто.")

def list_files():
    print("Запрашиваем список файлов на сервере...")
    send_command(1)  # Отправляем команду GET_CMD для получения списка файлов

def get_file(filename):
    print(f"Запрашиваем файл: {filename}")
    send_command(2, filename)  # Отправляем команду GET_CMD для получения файла

def put_file(filename):
    print(f"Загружаем файл: {filename}")
    with open(filename, 'rb') as f:
        file_data = f.read()
        send_command(3, filename, file_data)
    print(f"Файл {filename} успешно загружен на сервер.")

def delete_file(filename):
    print(f"Удаляем файл: {filename}")
    send_command(4, filename)  # Отправляем команду DELETE_CMD для удаления файла

def pack_command(command_code, *args):
    packed_data = struct.pack('B', command_code)  # Упаковываем код команды
    for arg in args:
        if isinstance(arg, str):
            packed_data += struct.pack(f'{len(arg)}s', arg.encode('utf-8'))  # Строки
        elif isinstance(arg, bytes):
            packed_data += struct.pack(f'I{len(arg)}s', len(arg), arg)  # Для файлов (длина и данные)
    return packed_data

if __name__ == '__main__':
    # Пример вызова функций для всех команд
    list_files()  # Получаем список файлов
    get_file("example.txt")  # Запрашиваем файл
    put_file("example.txt")  # Загружаем файл
    delete_file("example.txt")  # Удаляем файл
