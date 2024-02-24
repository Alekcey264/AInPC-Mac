#Импортируем все необходимые модули из библиотеки для работы с графическим интерфейсом
from PyQt6.QtCore import QSize, Qt, QTimer, QThread, pyqtSignal, QRegularExpression
from PyQt6.QtWidgets import QCheckBox, QGridLayout, QLineEdit, QMessageBox, QSplashScreen, QMainWindow, QApplication, QTreeWidget, QTableWidget, QAbstractItemView, QHeaderView, QTreeWidgetItem, QTableWidgetItem, QLabel, QPushButton, QDialog, QTextEdit, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout
from PyQt6.QtGui import QPalette, QColor, QAction, QPixmap, QIcon, QRegularExpressionValidator
#Импортируем библиотеки для работы системой, базами данных, построения графиков
import sys, sqlite3, pyqtgraph
#Импортируем модули для работы с операционной системой
from os import getcwd
#Импортируем модули для работы с системным терминалом
from subprocess import *
#Импортируем модули для получения данных с оперативной памяти
from psutil import virtual_memory, disk_partitions, disk_usage
#Импортируем модуль для получения текущего времени системы
from datetime import datetime
#Импортируем модуль для работы с системными путями файлов
from pathlib import Path

#Функция, вычисляющая среднее значение массива и округляющая его значения
def get_average(massive):
    return round(sum(massive) / len (massive), 2)

#Записываем местоположение базы данных в отдельную переменную, чтобы доступ к ней
#можно было получить из всех частей кода
db = getcwd() + "/aipcdb_mac.db"