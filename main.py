#Импортируем из остальных файлов проекта необходимые зависимости - классы, функции и модули
from global_import import QApplication, sys, QIcon, getcwd
from password_window import PasswordDialog

#Функция, создающая главное окно и запускающая его
def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(getcwd() + "/main_icon.png"))
    window = PasswordDialog()
    sys.exit(app.exec())
    
#Вызываем функцию, которая создает главное окно
if __name__ == "__main__":
    main()