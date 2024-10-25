import unittest
import zipfile
import yaml
from emulator import ls, cd, exit_shell, wc, echo, log_action, clear_log_file

# Загрузка конфигурации из файла config.yaml
with open("config.yaml") as f:
    config = yaml.safe_load(f)

vfs_path = config['vfs_path']
log_path = config['log_path']

class TestShellCommands(unittest.TestCase):

    def setUp(self):
        # Открываем архив виртуальной файловой системы перед началом тестов
        self.z = zipfile.ZipFile(vfs_path)
        # Очищаем файл журнала перед началом тестов
        clear_log_file()

    def tearDown(self):
        # Закрываем архив виртуальной файловой системы после окончания тестов
        self.z.close()

    def test_ls(self):
        # Проверка вывода команды ls без аргументов
        files = ls()
        self.assertEqual(files, ['file1.txt', 'file2.txt'])

        # Проверка вывода команды ls с аргументом, указывающим на существующую директорию
        files = ls('virtual_filesystem/new2/')
        self.assertEqual(files, ['new23'])

        # Проверка вывода команды ls с аргументом, указывающим на несуществующую директорию
        result = ls('nonexistent_dir')
        self.assertEqual(result, "No such directory: nonexistent_dir")

    def test_cd(self):
        # Проверка смены директории на домашнюю (пустую)
        result = cd()
        self.assertEqual(result, "Changed directory to virtual_filesystem.zip")

        # Проверка смены директории на существующую
        result = cd('virtual_filesystem/new1/')
        self.assertEqual(result, "Changed directory to virtual_filesystem/new1/")

        # Проверка смены директории на несуществующую
        result = cd('nonexistent_dir')
        self.assertEqual(result, "No such directory: nonexistent_dir")

    def test_exit(self):
        # Проверка выхода из эмулятора
        result = exit_shell()
        self.assertEqual(result, "Exiting shell.")

    def test_wc(self):
        # Проверка команды wc с аргументом, указывающим на существующий файл
        result = wc('virtual_filesystem/new1/file1.txt')
        self.assertEqual(result, (1, 2, 12))

        # Проверка команды wc с аргументом, указывающим на несуществующий файл
        result = wc('virtual_filesystem/nonexistent_file.txt')
        self.assertIsNone(result, "No such file: virtual_filesystem/nonexistent_file.txt")

    def test_echo(self):
        # Проверка команды echo с аргументом
        result = echo("Hello, World!")
        self.assertEqual(result, "Hello, World!")
        result = echo("World!")
        self.assertEqual(result, "World!")
        result = echo("")
        self.assertEqual(result, "")

    def test_log_action(self):
        # Проверка записи команды и результата в журнал
        command = "ls"
        result = ls()
        log_action(command, result)

        # Проверка чтения журнала и получения последней команды и результата
        with open(log_path, 'r') as f:
            content = f.read()
            self.assertIn(command, content)
            self.assertIn(str(result), content)

if __name__ == '__main__':
    unittest.main()