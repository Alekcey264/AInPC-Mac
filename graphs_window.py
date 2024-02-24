#Импортируем из остальных файлов проекта необходимые зависимости - классы, функции и модули
from global_import import *
from additional_classes import GraphsThread, InitializingGraphsThread

#Создаем окно с графиками
class GraphsWindow(QMainWindow):
    def __init__(self, password_for_work):
        super().__init__()

#Создаем переменные и зависимости, используемые в рамках главного окна
        self.password_for_work = password_for_work
        self.values_list = []
        self.graphs_list = []
        
#Настраиваем окно, отображающееся во время инициализации программы
        splash_for_graphs = self.show_graphs_splash_screen()

#Настраиваем и запускаем поток, инициализирующий первичные показатели датчиков системы        
        self.graphs_thread_initialize = InitializingGraphsThread(splash_for_graphs, self.password_for_work)
        self.graphs_thread_initialize.start()
        self.graphs_thread_initialize.initializing_graphs_signal.connect(self.fill_values_list_on_init, Qt.ConnectionType.QueuedConnection)
    
#Создаем поток опроса датчков компонентов системы и "подключаем" его реакцию на готовность обновления
        self.graphs_thread = GraphsThread(self.password_for_work)
        self.graphs_thread.graphs_signal.connect(self.fill_values_list_on_loop)
    
#Функция, отображающая окно инициализации
    def show_graphs_splash_screen(self):
        splash_pix = QPixmap(getcwd() + "/recources//graph_icon.png").scaled(QSize(500, 500), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
        splash.setFixedSize(500, 500)
        splash.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        splash.setEnabled(False)

        splash.show()
        return splash

#Функция, вычисляющая длину каждого элемента в массиве
    def list_len(self, list_of_lists):
        lenght = 0
        for item in list_of_lists:
            lenght += len(item)
        return lenght

#Функция, обновляющая графики    
    def update_graphs(self):
        if not self.graphs_thread.isRunning():
            self.graphs_thread.start()
        self.sort_values()
        j = 0
        for plot_widget, plot in self.plot_widgets:
            x_ax = [i for i in range(len(self.graphs_list[j]))]
            plot.setData(x_ax, self.graphs_list[j])
            j += 1

#Функция, заполняющая массив данными после получения их из потока
    def fill_values_list_on_loop(self, data):
        self.values_list = data
        self.update_graphs()

#Функция, заполняющая массив первычными данными с датчиков системы
    def fill_values_list_on_init(self, data):
        self.values_list = data[:-1]
        self.create_graphs_list()
        self.create_graphs_window(data[-1])

#Функция, запускающая появление  окна после процессора иницилизации
    def create_graphs_window(self, splash):
        splash.close()

#Настраиваем вид главного окна
        self.setWindowTitle("AInPC Графики")
        self.setFixedSize(QSize(900, 500))
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(192, 192, 192))

#Настриваем область отображения графиков
        graph_row_widget = QWidget()
        row_layout = QHBoxLayout()
        scroll_area = QScrollArea(self)
        scroll_widget = QWidget(scroll_area)
        scroll_layout = QVBoxLayout(scroll_widget)
        central_widget = QWidget()
        layout = QVBoxLayout()
        scroll_area = QScrollArea(self)
        scroll_widget = QWidget(scroll_area)
        scroll_layout = QVBoxLayout(scroll_widget)
        plot_names = ("Температура ядра процессора", "Средняя температура процессора", "Частота ядра процессора", 
                      "Загрузка ядра процессора", "Напряжение процессора", "Температура ядра видеокарты", 
                      "Частота ядра видеокарты", "Загрузка ядра видеокарты", "Напряжение видеокарты",
                      "Загрузка оперативной памяти", "Температура левого вентиляционного отверстия", 
                      "Температура правого вентиляционного отверстия", "Температура чипа NAND")
        self.plot_widgets = []
        n = 0
        lenght = self.list_len(self.values_list)
        if lenght // 2:
            row_count = lenght // 2 + 1
        else:
            row_count = lenght // 2
        name_num = 0
        graph_counter = 0
        values_counter = [len(item) for item in self.values_list]
        for _ in range(0, row_count):
            if n == lenght:
                break
            graph_row_widget = QWidget()
            row_layout = QHBoxLayout()
            for _ in range(2):
                plot_widget = pyqtgraph.PlotWidget()
                plot_widget.setMouseEnabled(x = False, y = False)
                plot_widget.setBackground("w")
                plot_widget.showGrid(x = True, y = True)
                plot_widget.setFixedWidth(405)
                plot_widget.plotItem.setFixedWidth(395)
                plot_widget.setFixedHeight(220)
                plot_widget.plotItem.setFixedHeight(215)
                if name_num in (0, 2, 3, 5) or len(self.values_list[-1]) != 1:
                    name = plot_names[name_num] + f" #{graph_counter + 1}"
                else:
                    name = plot_names[name_num]
                plot_widget.plotItem.setTitle(name, size = "14pt", color = (0, 0, 0))
                graph_counter += 1
                if graph_counter == values_counter[name_num]:
                    name_num += 1
                    graph_counter = 0
                plot_widget.plotItem.setLabel('bottom', '<b>Время (сек.)<\b>', color = (0, 0, 0))
                x_axis = plot_widget.getAxis("bottom")
                x_axis.setStyle(showValues = True)
                if "температура" in name.lower():
                    pen = pyqtgraph.mkPen(color = (255, 0, 0), width = 4.5)
                    plot_widget.plotItem.setLabel('left', '<b>Значение (\u00B0C)<\b>', color = (0, 0, 0))
                elif "Частота" in name:
                    pen = pyqtgraph.mkPen(color = (0, 0, 0), width = 4.5)
                    if "ядра" in name:
                        plot_widget.plotItem.setLabel('left', '<b>Значение (ГГц)<\b>', color = (0, 0, 0))
                    elif "памяти" in name:
                        plot_widget.plotItem.setLabel('left', '<b>Значение (МГц)<\b>', color = (0, 0, 0))
                elif "Загрузка" in name:
                    pen = pyqtgraph.mkPen(color = (0, 255, 0), width = 4.5)
                    plot_widget.plotItem.setLabel('left', '<b>Значение (%)<\b>', color = (0, 0, 0), )
                elif "Напряжение" in name:
                    pen = pyqtgraph.mkPen(color = (0, 0, 255), width = 4.5)
                    plot_widget.plotItem.setLabel('left', '<b>Значение (мВ)<\b>', color = (0, 0, 0), )
                plotx = plot_widget.plot([], [], pen = pen)
                plot_widget.viewport().setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
                self.plot_widgets.append((plot_widget, plotx))
                row_layout.addWidget(plot_widget)
                n = n + 1
                if n == lenght:
                    break
            graph_row_widget.setLayout(row_layout)
            scroll_layout.addWidget(graph_row_widget)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.update_graphs()
        self.graphs_thread.start()

        self.show()

#Разбираем значения из листа для корректного отображения
    def unparse_list(self, input_list):
        temp_list = []
        for item in input_list:
            for i in range(len(item)):
                temp_list.append(item[i])
        return temp_list

#Заполняем массив хранящий графики, всеми элементами
    def create_graphs_list(self):
        temp_list = self.unparse_list(self.values_list)
        for item in temp_list:
            self.graphs_list.append([item])
        
#Сортируем значения, чтобы отображались последние 60 значений
    def sort_values(self):
        temp_list = self.unparse_list(self.values_list)
        for i in range(len(self.graphs_list)):
            self.graphs_list[i].append(temp_list[i])
            if len(self.graphs_list[i]) > 60:
                del self.graphs_list[i][0]

#Функция, принудительно останавливающая поток при закрытии программы
    def stop_thread(self):
        self.graphs_thread.stop()

#Функция, отвечающая за безопасное выключение программы
    def closeEvent(self, event):
        self.hide()
        self.graphs_thread.running = False
        self.stop_thread()
        super().closeEvent(event)