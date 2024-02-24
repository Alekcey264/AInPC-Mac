#Импортируем из остальных файлов проекта необходимые зависимости - классы, функции и модули
from global_import import *
from main_window import MainWindow

#Создаем окно ввода пароля
class PasswordDialog(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
#Проверяем язык ввода пароля у пользователя
        regex = QRegularExpression("[A-Za-z0-9!@#$%^&*()-_=+\\|`~'\";:,.<>/?\\[\\]{}\\\\]+")
        validator = QRegularExpressionValidator(regex)

#Создаем строку для ввода пароля пользователя
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setValidator(validator)

#Создаем кнопку и привязываем в ней нажатие клавиши "Enter"
        self.submit_button = QPushButton("Войти", self)
        self.submit_button.setShortcut("Return")
        self.submit_button.clicked.connect(self.check_password)

        layout.addWidget(self.password_input)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)
        self.setWindowTitle("Проверка пароля")
        self.setFixedSize(200, 100)
        self.show()

#Проверяем правильность ввода пароля пользователя
    def check_password(self):
        entered_password = self.password_input.text()
        self.submit_button.setEnabled(False)
        command = "sudo -S pwd"
        process = Popen(command, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE, universal_newlines = True)
        stdout, stderr = process.communicate(entered_password + '\n')
        if not stdout:
            QMessageBox.warning(self, "Ошибка", "Пароль неверный. Повторите попытку.")
            self.submit_button.setEnabled(True)
        else:
            self.close() 
            self.main_window_code = MainWindow(entered_password)

            