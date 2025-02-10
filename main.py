import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from os import getcwd
from password_window import PasswordDialog


# Функция, создающая главное окно и запускающая его
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(getcwd() + "/main_icon.png"))
    window = PasswordDialog()
    sys.exit(app.exec())
    
# Вызываем функцию, которая создает главное окно
if __name__ == "__main__":
    main()