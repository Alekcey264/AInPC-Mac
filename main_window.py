from global_import import *
from fetch import *
from additional_classes import *
from graphs_window import GraphsWindow
from report_window import ReportWindow

class MainWindow(QMainWindow):
    def __init__(self, password_for_work):
        super().__init__()

        self.password_for_work = password_for_work
        
        splash = self.show_splash_screen()
        splash.showMessage("Идет инициализация...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, Qt.GlobalColor.white)
        self.initializing_thread = InitializingThread(splash, password_for_work)
        self.initializing_thread.start()
        self.initializing_thread.init_signal.connect(self.on_change_init, Qt.ConnectionType.QueuedConnection)

        self.setWindowTitle("AInPC")
        self.setFixedSize(QSize(830, 500))
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(192, 192, 192))

        menubar = self.menuBar()
        file_menu = menubar.addMenu("Вид")
        menubar_height = self.menuBar().height()
        graphs_item = QAction("Графики", self)
        report_item = QAction("Сформировать отчет", self)
        terminal_item = QAction("Терминал", self)

        file_menu.addAction(graphs_item)
        file_menu.addAction(terminal_item)
        file_menu.addAction(report_item)

        graphs_item.triggered.connect(self.open_graphs_window)
        terminal_item.triggered.connect(self.open_terminal)
        report_item.triggered.connect(self.open_report_window)
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setGeometry(10, menubar_height, 150, self.height() - menubar_height - 10)
        self.tree_widget.setHeaderHidden(True)
        self.setup_tree()
        self.tree_widget.itemSelectionChanged.connect(self.on_item_selected)
        self.tree_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(self.tree_widget.width() + 20 + 10, menubar_height, self.width() - self.tree_widget.width() - 20 - 10 - 10, self.height() - menubar_height - 10)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(False)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.verticalHeader().setDefaultSectionSize(1)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.timer = QTimer(self)
        self.stats_thread = StatsThread(password_for_work)
        self.timer.timeout.connect(self.update_table_with_timer)
        self.stats_thread.stats_signal.connect(self.on_change, Qt.ConnectionType.QueuedConnection)


    def setup_table(self, row_count):
        column_names = ["Поле", "Описание"]
        self.table_widget.setRowCount(row_count)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(column_names)

    def on_change_init(self, data):
        global massive_cpu_load
        global massive_gpu_load
        global massive_cpu_clock
        global massive_gpu_clock
        global massive_cpu_power
        global massive_gpu_power
        massive_cpu_load = data[0]
        massive_cpu_clock = data[1]
        massive_cpu_power = data[2]
        massive_gpu_load = data[3]
        massive_gpu_clock = data[4]
        massive_gpu_power = data[5]
        self.create_main_window(data[6])

    def on_change(self, data):
        if data[1] == "CPU":
            if data[2] == "Load":
                global massive_cpu_load
                massive_cpu_load = data[0]
            elif data[2] == "Clock":
                global massive_cpu_clock
                massive_cpu_clock = data[0]
            elif data[2] == "Power":
                global massive_cpu_power
                massive_cpu_power = data[0]
        elif data[1] == "GPU":
            if data[2] == "Load":
                global massive_gpu_load
                massive_gpu_load = data[0]
            elif data[2] == "Clock":
                global massive_gpu_clock
                massive_gpu_clock = data[0]
            elif data[2] == "Power":
                global massive_gpu_power
                massive_gpu_power = data[0]

    def fix_table(self):
        for row in range(self.table_widget.rowCount()):
            for col in range(self.table_widget.columnCount()):
                if (self.table_widget.rowSpan(row, col) > 1) or (self.table_widget.columnSpan(row, col) > 1):
                    self.table_widget.setSpan(row, col, 1, 1)
        self.table_widget.clearContents()

    def setup_tree(self):
        root_item_cpu = QTreeWidgetItem(self.tree_widget, ["Процессор"])               
        child_item1_cpu = QTreeWidgetItem(root_item_cpu, ["Температура"])
        child_item2_cpu = QTreeWidgetItem(root_item_cpu, ["Загрузка"])
        сhild_item3_cpu = QTreeWidgetItem(root_item_cpu, ["Частота"])
        child_item4_cpu = QTreeWidgetItem(root_item_cpu, ["Напряжение"])

        root_item_gpu = QTreeWidgetItem(self.tree_widget, ["Видеокарта"])
        child_item1_gpu = QTreeWidgetItem(root_item_gpu, ["Температура"])
        child_item2_gpu = QTreeWidgetItem(root_item_gpu, ["Загрузка"])
        сhild_item3_gpu = QTreeWidgetItem(root_item_gpu, ["Частота"])
        child_item4_gpu = QTreeWidgetItem(root_item_gpu, ["Напряжение"])

        root_item_ram = QTreeWidgetItem(self.tree_widget, ["Оперативная память"])
        child_item1_ram = QTreeWidgetItem(root_item_ram, ["Числовая информация"])

        root_item_mb = QTreeWidgetItem(self.tree_widget, ["Материнская плата"])
        child_item1_mb = QTreeWidgetItem(root_item_mb, ["Температура"])
        #child_item2_mb = QTreeWidgetItem(root_item_mb, ["Вентиляторы"])

        root_item_logical_disks = QTreeWidgetItem(self.tree_widget, ["Логические диски"])
        root_item_physical_disks = QTreeWidgetItem(self.tree_widget, ["Физические диски"])

        self.tree_widget.expandAll()

    def close_window(self):
        self.close()

    def update_table_with_timer(self):
        if root_for_timer == "CPU":
            if text_for_timer == "Temperature":
                self.fill_table_cpu_temp()
            elif text_for_timer == "Load":
                if not massive_cpu_load:
                    self.close_window()
                if not self.stats_thread.isRunning():
                    self.stats_thread.set_type(root_for_timer, text_for_timer)
                    self.stats_thread.start()
                self.fill_table_cpu(massive_cpu_load)
            elif text_for_timer == "Clock":
                if not massive_cpu_clock:
                    self.close_window()
                if not self.stats_thread.isRunning():
                    self.stats_thread.set_type(root_for_timer, text_for_timer)
                    self.stats_thread.start()
                self.fill_table_cpu(massive_cpu_clock)
            elif text_for_timer == "Power":
                if not massive_cpu_power:
                    self.close_window()
                if not self.stats_thread.isRunning():
                    self.stats_thread.set_type(root_for_timer, text_for_timer)
                    self.stats_thread.start()
                self.fill_table_cpu_power(massive_cpu_power)
        elif root_for_timer == "GPU":
            if text_for_timer == "Temperature":
                self.fill_table_gpu_temp()
            elif text_for_timer == "Load":
                if not massive_gpu_load:
                    self.close_window()
                if not self.stats_thread.isRunning():
                    self.stats_thread.set_type(root_for_timer, text_for_timer)
                    self.stats_thread.start()
                self.fill_table_gpu(massive_gpu_load)
            elif text_for_timer == "Clock":
                if not massive_gpu_clock:
                    self.close_window()
                if not self.stats_thread.isRunning():
                    self.stats_thread.set_type(root_for_timer, text_for_timer)
                    self.stats_thread.start()
                self.fill_table_gpu(massive_gpu_clock)
            elif text_for_timer == "Power":
                if not massive_gpu_power:
                    self.close_window()
                if not self.stats_thread.isRunning():
                    self.stats_thread.set_type(root_for_timer, text_for_timer)
                    self.stats_thread.start()
                self.fill_table_gpu(massive_gpu_power)
        elif root_for_timer == "RAM":
            if text_for_timer == "Nums":
                self.fill_table_ram()
        elif root_for_timer == "Motherboard":
            if text_for_timer == "Temperature":
                self.fill_table_mb_temp()
        elif root_for_timer == "PhysicalDisk":
            self.update_nand_temp()

    def on_item_selected(self):
        global root_for_timer
        global text_for_timer
        root_for_timer = None
        text_for_timer = None
        selected_item = self.tree_widget.selectedItems()[0]
        selected_text = selected_item.text(0)
        root_item = selected_item.parent()
        if root_item is not None:
            root_text = root_item.text(0)
        else:
            root_text = None        
        if selected_item:
            self.initialize_table(root_text, selected_text)

    def fill_table_cpu_temp(self):
        fetch_sensors("tdie", massive_cpu_temp)
        for row in range(cpu_cores - 1):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(f"Ядро процессора #{row + 1}") + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(massive_cpu_temp[row][1]) + '\u00B0C'))

        self.table_widget.setSpan(cpu_cores - 1, 0, 1, 2)

        self.table_widget.setItem(cpu_cores, 0, QTableWidgetItem("Средняя температура процессора"))
        self.table_widget.setItem(cpu_cores, 1, QTableWidgetItem(str(massive_cpu_temp[cpu_cores - 1][1]) + '\u00B0C'))

    def fill_table_cpu(self, massive):
        for row in range(cpu_cores - 1):
            self.table_widget.setItem(row, 0, QTableWidgetItem(f"Ядро процессора #{row + 1}" + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(massive[row])))

    def fill_table_cpu_power(self, massive):
        self.table_widget.setItem(0, 0, QTableWidgetItem("Процессор" + '\t'))
        self.table_widget.setItem(0, 1, QTableWidgetItem(str(massive[0])))

    def fill_table_gpu_temp(self):
        fetch_sensors("tdev", massive_gpu_temp)
        avg_temp = []
        for row in range(len(massive_gpu_temp) * 2):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(f"Ядро видеокарты #{row + 1}") + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(massive_gpu_temp[row//2][1]) + '\u00B0C'))
            avg_temp.append(massive_gpu_temp[row//2][1])

        self.table_widget.setSpan(row + 1, 0, 1, 2)

        self.table_widget.setItem(row + 2, 0, QTableWidgetItem("Средняя температура видеокарты"))
        self.table_widget.setItem(row + 2, 1, QTableWidgetItem(str(round(sum(avg_temp) / len(avg_temp), 1)) + '\u00B0C'))

    def fill_table_gpu(self, massive):
        self.table_widget.setItem(0, 0, QTableWidgetItem("Видеокарта" + '\t'))
        self.table_widget.setItem(0, 1, QTableWidgetItem(str(massive[0])))

    def fill_table_ram(self):
        ram_massive =[["total=", "Общий объем физической памяти = "], ["available=", "Объем доступной для процессов памяти = "], ["percent=", "Загруженность памяти = "],
              ["used=", "Объем используемой памяти = "], ["free=", "Объем свободной памяти = "], ["active=", "Объем активной памяти = "],
              ["inactive=", "Объем неактивной памяти = "], ["wired=", "Объем зарезервированной системой памяти = "]]
        ram_info = str(virtual_memory())
        ram_info = ram_info[ram_info.find("(") + 1: ram_info.find(")")].split(", ")
        for i in range(len(ram_info)):
            for item1 in ram_massive:
                if item1[0] == ram_info[i][:ram_info[i].find("=") + 1]:
                    ram_info[i] = ram_info[i].replace(item1[0], item1[1])
                    break
        for row in range(len(ram_info)):
            if ram_info[row][:ram_info[row].find(" = ")] == "Загруженность памяти":
                self.table_widget.setItem(row, 0, QTableWidgetItem(str(ram_info[row][:ram_info[row].find(" = ")]) + '\t'))
                self.table_widget.setItem(row, 1, QTableWidgetItem(str(ram_info[row][ram_info[row].find(" = ") + 2 :].strip()) + '%'))
            else:
                self.table_widget.setItem(row, 0, QTableWidgetItem(str(ram_info[row][:ram_info[row].find(" = ")]) + '\t'))
                num = int(ram_info[row][ram_info[row].find(" = ") + 2 :].strip())
                num = round(num / (1024 ** 3), 2)
                self.table_widget.setItem(row, 1, QTableWidgetItem(str(num) + ' Гб'))

    def fill_table_mb_temp(self):
        fetch_sensors_mb_temp(massive_mb_temp)
        self.table_widget.setItem(0, 0, QTableWidgetItem("Левое вентиляционное отверстие" + '\t'))
        self.table_widget.setItem(0, 1, QTableWidgetItem(str(round(massive_mb_temp[1][1], 1)) + '\u00B0C'))
        self.table_widget.setItem(1, 0, QTableWidgetItem("Правое вентиляционное отверстие" + '\t'))
        self.table_widget.setItem(1, 1, QTableWidgetItem(str(round(massive_mb_temp[2][1], 1)) + '\u00B0C'))

        self.table_widget.setSpan(2, 0, 1, 2)

        self.table_widget.setItem(3, 0, QTableWidgetItem("Батарея" + '\t'))
        self.table_widget.setItem(3, 1, QTableWidgetItem(str(round(massive_mb_temp[0][1], 1)) + '\u00B0C'))
    
    def fill_table_cpu_info(self, cpu_count):
        cpu = cpu_info_text
        cpu_specs = ["Название процессора", "Общее количество ядер", "Количество ядер производительности", "Базовая частота ядер производительности",
                     "Количество ядер эффективности", "Базовая частота ядер эффективности", "Кэш 1-го уровня", "Кэш 2-го уровня ядер производительности",
                     "Кэш 2-го уровня ядер эффективности", "Кэш 3-го уровня", "Количество ядер нейронного движка", "Производитель", "Серийный номер",
                     "Официальный сайт производителя"]
        if cpu:
            for row in range(cpu_count):
                self.table_widget.setItem(row, 0, QTableWidgetItem(cpu_specs[row] + '\t'))
                self.table_widget.setItem(row, 1, QTableWidgetItem(cpu[row]))
        else:
            for row in range(cpu_count):
                self.table_widget.setItem(row, 0, QTableWidgetItem(cpu_specs[row] + '\t'))
                self.table_widget.setItem(row, 1, QTableWidgetItem("-"))
        self.table_widget.setItem(row + 1, 0, QTableWidgetItem(cpu_specs[row + 1] + '\t'))
        serial_number = run('system_profiler SPHardwareDataType | grep "Serial Number (system):"', shell=True, capture_output=True, text=True).stdout.strip()
        self.table_widget.setItem(row + 1, 1, QTableWidgetItem(serial_number[serial_number.index(":") + 2:]))
        self.table_widget.setItem(row + 2, 0, QTableWidgetItem(cpu_specs[row + 2] + '\t'))
        self.table_widget.setCellWidget(row + 2, 1, HyperlinkLabel("Проверить гарантию", "https://checkcoverage.apple.com/?locale=ru_RU "))

    def fill_table_gpu_info(self, gpu_count):
        gpu = gpu_text_info
        for row in range(gpu_count):
            text = gpu[row][:gpu[row].find(":")]
            if "Apple" in text:
                text = text.strip()
            value = gpu[row][gpu[row].find(":") + 1:].strip()
            if value:
                self.table_widget.setItem(row, 0, QTableWidgetItem(text + '\t'))
                self.table_widget.setItem(row, 1, QTableWidgetItem(value))
            else:
                self.table_widget.setItem(row, 0, QTableWidgetItem(text + ':'))
                self.table_widget.setSpan(row, 0, 1, 2)

    def fill_table_ram_info(self, ram_count):
        ram = ram_text_info
        for row in range(ram_count):
            self.table_widget.setItem(row, 0, QTableWidgetItem(ram[row][:ram[row].find(":")].strip() + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(ram[row][ram[row].find(":") + 1:].strip()))

    def fill_table_mb_info(self, mb_count):
        mb = mb_text_info
        for row in range(mb_count):
            self.table_widget.setItem(row, 0, QTableWidgetItem(mb[row][:mb[row].find(":")].strip() + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(mb[row][mb[row].find(":") + 1:].strip()))

    def fill_table_logical_disks(self, disks_count):
        list_of_disks = disk_partitions(all = False)
        i = 0
        list_of_disk_usage = disk_usage(list_of_disks[0][1])
        self.table_widget.setItem(0, 0, QTableWidgetItem("Общий размер хранилища" + '\t'))
        self.table_widget.setItem(0, 1, QTableWidgetItem(str(round(list_of_disk_usage[0] / (1024 ** 3), 2)) + " Гб"))
        self.table_widget.setItem(1, 0, QTableWidgetItem("Свободно памяти в хранилище" + '\t'))
        self.table_widget.setItem(1, 1, QTableWidgetItem(str(round(list_of_disk_usage[2] / (1024 ** 3), 2)) + " Гб"))
        self.table_widget.setSpan(2, 0, 1, 2)

        for row in range(3, disks_count, 6):
            self.table_widget.setItem(row, 0, QTableWidgetItem("Название раздела" + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(list_of_disks[i][0])))
            self.table_widget.setItem(row + 1, 0, QTableWidgetItem("Точка монтирования раздела" + '\t'))
            self.table_widget.setItem(row + 1, 1, QTableWidgetItem(str(list_of_disks[i][1])))
            self.table_widget.setItem(row + 2, 0, QTableWidgetItem("Файловая система раздела" + '\t'))
            self.table_widget.setItem(row + 2, 1, QTableWidgetItem(str(list_of_disks[i][2])))
            list_of_disk_usage = disk_usage(list_of_disks[i][1])
            self.table_widget.setItem(row + 3, 0, QTableWidgetItem("Объем памяти, используемый разделом" + '\t'))
            self.table_widget.setItem(row + 3, 1, QTableWidgetItem(str(round(list_of_disk_usage[1] / (1024 ** 3), 2)) + " Гб"))
            self.table_widget.setItem(row + 4, 0, QTableWidgetItem("Загруженность раздела" + '\t'))
            self.table_widget.setItem(row + 4, 1, QTableWidgetItem(str(list_of_disk_usage[3]) + "%"))
            self.table_widget.setSpan(row + 5, 0, 1, 2)
            i += 1

    def fill_table_physical_disks(self, disks_count, nand_temp_count):
        for row in range(nand_temp_count):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(f"Температура чипа NAND #{row + 1}") + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(massive_nand_temp[row][1]) + '\u00B0C'))
        disks = physical_disks
        self.table_widget.setSpan(nand_temp_count, 0, 1, 2)
        i = 0
        for row in range(nand_temp_count + 1, disks_count):
            text = disks[i][:disks[i].find(":")]
            value = disks[i][disks[i].find(":") + 1:].strip()
            if value:
                self.table_widget.setItem(row, 0, QTableWidgetItem(text + '\t'))
                self.table_widget.setItem(row, 1, QTableWidgetItem(value))     
            else:
                self.table_widget.setItem(row, 0, QTableWidgetItem(text + ':'))
                self.table_widget.setSpan(row, 0, 1, 2)
            i += 1
    
    def update_nand_temp(self):
        fetch_sensors("NAND", massive_nand_temp)
        for row in range(len(massive_nand_temp)):
            self.table_widget.setItem(row, 0, QTableWidgetItem(str(f"Температура чипа NAND #{row + 1}") + '\t'))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(massive_nand_temp[row][1]) + '\u00B0C'))
        
    def initialize_table(self, root, text):
        global root_for_timer
        global text_for_timer
        self.fix_table()
        if not root:
            self.timer.stop()
            if text == "Процессор":
                if cpu_info_text:
                    cpu_count = len(cpu_info_text)
                else:
                    message_box = QMessageBox()
                    message_box.setWindowTitle("Ошибка")
                    message_box.setText("Возникла ошибка в ходе получения информации о процессоре, пожалуйста, попробуйте открыть вкладку повторно или перезапустите программу.")
                    message_box.setIcon(QMessageBox.Icon.Warning)
                    message_box.exec()
                    cpu_count = 12
                self.setup_table(cpu_count + 2)
                self.fill_table_cpu_info(cpu_count)
            elif text == "Видеокарта":
                gpu_count = len(gpu_text_info)
                self.setup_table(gpu_count)
                self.fill_table_gpu_info(gpu_count)
            elif text == "Оперативная память":
                ram_count = len(ram_text_info)
                self.setup_table(ram_count)
                self.fill_table_ram_info(ram_count)
            elif text == "Материнская плата":
                mb_count = len(mb_text_info)
                self.setup_table(mb_count)
                self.fill_table_mb_info(mb_count)
            elif text == "Логические диски":
                column_names = ["Поле", "Описание"]
                logical_disks_count = 3 + (len(disk_partitions(all = False)) - 1) * 6 + 5
                self.setup_table(logical_disks_count)
                self.fill_table_logical_disks(logical_disks_count)
            elif text == "Физические диски":
                root_for_timer = "PhysicalDisk"
                fetch_sensors("NAND", massive_nand_temp)
                physical_disks_count = len(physical_disks) + len(massive_nand_temp)
                self.setup_table(physical_disks_count)
                self.fill_table_physical_disks(physical_disks_count, len(massive_nand_temp))
        elif root == "Процессор":
            global cpu_cores
            fetch_sensors("tdie", massive_cpu_temp)
            cpu_cores = len(massive_cpu_temp)
            if text == "Температура":
                root_for_timer = "CPU"
                text_for_timer = "Temperature"
                column_names = ["Устройство", "Температура"]
                self.table_widget.setRowCount(cpu_cores + 1)
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                self.fill_table_cpu_temp()
            elif text == "Загрузка":
                if not massive_cpu_load:
                    self.close_window()
                root_for_timer = "CPU"
                text_for_timer = "Load"
                column_names = ["Устройство", "Загрузка"]
                self.table_widget.setRowCount(cpu_cores - 1)
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                if massive_cpu_load:
                    self.fill_table_cpu(massive_cpu_load)
            elif text == "Частота":
                if not massive_cpu_clock:
                    self.close_window()                
                root_for_timer = "CPU"
                text_for_timer = "Clock"
                column_names = ["Устройство", "Частота"]
                self.table_widget.setRowCount(cpu_cores - 1)
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                if massive_cpu_clock:
                    self.fill_table_cpu(massive_cpu_clock)
            elif text == "Напряжение":
                if not massive_cpu_power:
                    self.close_window()                
                root_for_timer = "CPU"
                text_for_timer = "Power"
                column_names = ["Устройство", "Напряжение"]
                self.table_widget.setRowCount(len(massive_cpu_power))
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                if massive_cpu_power:
                    self.fill_table_cpu_power(massive_cpu_power)
        elif root == "Видеокарта":
            if text == "Температура":
                root_for_timer = "GPU"
                text_for_timer = "Temperature"
                fetch_sensors("tdev", massive_gpu_temp)
                gpu_cores = len(massive_gpu_temp)
                column_names = ["Устройство", "Температура"]               
                self.table_widget.setRowCount(gpu_cores * 2 + 2)
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                self.fill_table_gpu_temp()
            elif text == "Загрузка":
                if not massive_gpu_load:
                    self.close_window()
                root_for_timer = "GPU"
                text_for_timer = "Load"
                column_names = ["Устройство", "Загрузка"]
                self.table_widget.setRowCount(len(massive_gpu_load))
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                if massive_gpu_load:
                    self.fill_table_gpu(massive_gpu_load)
            elif text == "Частота":
                if not massive_gpu_clock:
                    self.close_window()
                root_for_timer = "GPU"
                text_for_timer = "Clock"
                column_names = ["Устройство", "Частота"]
                self.table_widget.setRowCount(len(massive_gpu_clock))
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                if massive_gpu_clock:
                    self.fill_table_gpu(massive_gpu_clock)
            elif text == "Напряжение":
                if not massive_gpu_power:
                    self.close_window()                
                root_for_timer = "GPU"
                text_for_timer = "Power"
                column_names = ["Устройство", "Напряжение"]
                self.table_widget.setRowCount(1)
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                if massive_cpu_power:
                    self.fill_table_gpu(massive_gpu_power)                    
        elif root == "Оперативная память":
            if text == "Числовая информация":
                ram_info = str(virtual_memory())
                ram_info = ram_info[ram_info.find("(") + 1: ram_info.find(")")].split(", ")
                root_for_timer = "RAM"
                text_for_timer = "Nums"
                column_names = ["Поле", "Значение"]
                self.table_widget.setRowCount(len(ram_info))
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                self.fill_table_ram()
        elif root == "Материнская плата":
            if text == "Температура":
                root_for_timer = "Motherboard"
                text_for_timer = "Temperature"
                column_names = ["Сенсор", "Температура"]
                self.table_widget.setRowCount(4)
                self.table_widget.setColumnCount(2)
                self.table_widget.setHorizontalHeaderLabels(column_names)
                self.fill_table_mb_temp()         
        self.timer.start(1000)
    
    def create_main_window(self, splash):
        splash.close()
        self.initialize_table(None, "Материнская плата")
        self.show()

    def show_splash_screen(self):
        splash_pix = QPixmap(getcwd() + "/recources//main_icon.png").scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
        splash.setFixedSize(500, 500)
        splash.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        splash.setEnabled(False)

        splash.show()
        return splash
    
    def open_terminal(self):
        run(["open", "-a",  "Terminal"])

    def open_graphs_window(self):
        self.graphs_window_code = GraphsWindow(self.password_for_work)

    def open_report_window(self):
        self.report_window_code = ReportWindow()

    def closeEvent(self, event):
        self.hide()
        self.stats_thread.running = False
        self.stats_thread.wait(5000)
        event.accept()