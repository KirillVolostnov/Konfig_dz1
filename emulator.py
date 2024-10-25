import os
import datetime
import zipfile
import yaml
import xml.etree.ElementTree as ET
from tkinter import Tk, Text, END

current_directory = ""

with open("config.yaml") as f:
    config = yaml.safe_load(f)
    vfs_path = config['vfs_path']
    log_path = config['log_path']


def ls(arg=None):
    with zipfile.ZipFile(vfs_path) as z:
        # Получаем список файлов и папок, находящихся в текущем каталоге
        if arg:
            if arg in z.namelist() and arg.endswith('/'):
                # Если передан аргумент, являющийся директорией, получаем список файлов и поддиректорий внутри этой директории
                files = [name for name in z.namelist()
                         if name.startswith(arg) and
                         ((name[len(arg):].count('/') == 0 and name != arg) or
                          (name[len(arg):].count('/') == 1 and name.endswith('/')))]

                # Убираем префикс текущего каталога, оставляя только имена
                files = [name[len(arg):].strip('/') for name in files]

            else:
                return f"No such directory: {arg}"
        else:
            # Если аргумент не передан или он не является директорией, получаем список файлов и поддиректорий в текущем каталоге
            files = [name for name in z.namelist()
                     if name.startswith(current_directory) and
                     ((name[len(current_directory):].count('/') == 0 and name != current_directory) or
                      (name[len(current_directory):].count('/') == 1 and name.endswith('/')))]

            # Убираем префикс текущего каталога, оставляя только имена
            files = [name[len(current_directory):].strip('/') for name in files]

    return files



def cd(directory=None):
    global current_directory
    if not directory:
        # Если аргумент не передан, меняем текущий каталог на домашний каталог
        current_directory = ""
        return f"Changed directory to virtual_filesystem.zip"
    with zipfile.ZipFile(vfs_path) as z:
        files = z.namelist()
        if directory in z.namelist():
            current_directory = directory
            return f"Changed directory to {current_directory}"
        else:
            return f"No such directory: {directory}"

def exit_shell():
    return "Exiting shell."


def wc(file):
    with zipfile.ZipFile(vfs_path) as z:
        if file in z.namelist():
            with z.open(file) as f:
                content = f.read().decode()
                lines = content.splitlines()
                words = content.split()
                return len(lines), len(words), len(content)
        else:
            None

def echo(text):
    return text


def log_action(command, result):
    try:
        # Проверяем, существует ли лог файл и пуст ли он
        if not os.path.exists(log_path) or os.path.getsize(log_path) == 0:
            root = ET.Element("log")
            tree = ET.ElementTree(root)
            tree.write(log_path, encoding='utf-8', xml_declaration=True)

        tree = ET.ElementTree(file=log_path)
        root = tree.getroot()

        # Создаем новый элемент для команды
        command_element = ET.Element("command")

        # Записываем команду
        cmd_element = ET.Element("text")
        cmd_element.text = command
        command_element.append(cmd_element)

        # Записываем результат
        result_element = ET.Element("result")
        result_element.text = str(result)
        command_element.append(result_element)

        # Записываем временную метку
        timestamp = ET.Element("timestamp")
        timestamp.text = str(datetime.datetime.now())
        command_element.append(timestamp)

        root.append(command_element)

        # Сохраняем с отступами
        with open(log_path, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True, method="xml")
    except Exception as e:
        print(f"Logging error: {str(e)}")

def clear_log_file():
    if os.path.exists(log_path):  # Проверяем, существует ли файл логов
        with open(log_path, 'w'):  # Открываем файл на запись, очищая его содержимое
            pass

def create_gui():
    clear_log_file()
    root = Tk()
    root.title("Shell Emulator")
    root.geometry("600x420")

    text_area = Text(root)
    text_area.pack()

    input_area = Text(root, height=2)
    input_area.pack(fill='x')

    commands = {
        "ls": ls,
        "cd": cd,
        "exit": exit_shell,
        "wc": wc,
        "echo": echo,
    }

    def execute_command(event=None):
        try:
            command = input_area.get("1.0", END).strip()
            input_area.delete("1.0", END)
            if command.lower() == "exit":
                log_action(command, "Exiting the shell")
                root.quit()
            command_parts = command.split(maxsplit=1)
            cmd_name = command_parts[0]
            cmd_arg = command_parts[1] if len(command_parts) > 1 else ""

            if cmd_name in commands:
                if cmd_name == "wc" and cmd_arg:
                    full_path = os.path.join(current_directory, cmd_arg)
                    result = commands[cmd_name](full_path)
                else:
                    result = commands[cmd_name](cmd_arg) if cmd_arg else commands[cmd_name]()

                log_action(command, result)
                text_area.insert(END, f"$ {command}\n{result}\n")
            else:
                text_area.insert(END, f"Unknown command: {cmd_name}\n")
        except Exception as e:
            text_area.insert(END, f"Error: {str(e)}\n")

    input_area.bind("<Return>", execute_command)
    root.mainloop()
if __name__ == '__main__':
    create_gui()