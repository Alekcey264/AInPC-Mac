from PyQt6.QtCore import QSize, Qt, QTimer, QThread, pyqtSignal, QRegularExpression
from PyQt6.QtWidgets import QCheckBox, QGridLayout, QLineEdit, QMessageBox, QSplashScreen, QMainWindow, QApplication, QTreeWidget, QTableWidget, QAbstractItemView, QHeaderView, QTreeWidgetItem, QTableWidgetItem, QLabel, QPushButton, QDialog, QTextEdit, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout
from PyQt6.QtGui import QPalette, QColor, QAction, QPixmap, QIcon, QRegularExpressionValidator
import sys, sqlite3, pyqtgraph
from os import getcwd
from subprocess import *
from psutil import virtual_memory, disk_partitions, disk_usage
from fetch import initialize_disks, initialize_ram, initialize_gpu, initialize_mb, initialize_cpu
from datetime import datetime
from pathlib import Path

massive_cpu_temp = []
massive_gpu_temp = []
massive_nand_temp = []
massive_mb_temp = []
root_for_timer = None
text_for_timer = None
cpu_cores = None
massive_cpu_load = []
massive_gpu_load = []
massive_cpu_clock = []
massive_gpu_clock = []
massive_cpu_power = []
massive_gpu_power = []
physical_disks = initialize_disks()
ram_text_info = initialize_ram()
gpu_text_info = initialize_gpu()
mb_text_info = initialize_mb()
cpu_info_text = initialize_cpu()

def get_average(massive):
    return round(sum(massive) / len (massive), 2)