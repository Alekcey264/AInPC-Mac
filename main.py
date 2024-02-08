from global_import import QApplication, sys, QIcon, getcwd
from password_window import PasswordDialog

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(getcwd() + "/main_icon.png"))
    window = PasswordDialog()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()