from global_import import *

class HyperlinkLabel(QLabel):
    def __init__(self, text, link):
        super().__init__()
        self.setText(f'<a href="{link}">{text}</a>')
        self.setOpenExternalLinks(True)

class StatsThread(QThread):
    stats_signal = pyqtSignal(list)
    def __init__(self, password):
        QThread.__init__(self)
        self.running = False
        self.type_of_info = None
        self.password = password

    def set_type(self, root, text):
        self.root = root
        self.text = text
        
    def run(self):
        self.running = True
        while self.running:
            filtered_lines = []
            if self.root == "CPU":
                command = "sudo -S powermetrics -n1 --samplers cpu_power"
                process = Popen(command, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE, universal_newlines = True)
                stdout, stderr = process.communicate(self.password + '\n')
                lines = stdout.split('\n')
                if self.text == "Load":
                    filtered_lines = [line[line.find(":") + 1 : line.find("(")].strip() for line in lines if "CPU" in line and "active residency" in line]
                    container = [filtered_lines, self.root, self.text]
                    self.stats_signal.emit(container)
                elif self.text == "Clock":
                    filtered_lines = [line[line.find(":") + 1:].strip() for line in lines if "CPU" in line and "frequency" in line]
                    container = [filtered_lines, self.root, self.text]
                    self.stats_signal.emit(container)
                elif self.text == "Power":
                    filtered_lines = [line[line.find(":") + 1:].strip() for line in lines if "CPU Power" in line]
                    container = [filtered_lines, self.root, self.text]
                    self.stats_signal.emit(container)
            elif self.root == "GPU":
                command = "sudo -S powermetrics -n1 --samplers gpu_power"
                process = Popen(command, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE, universal_newlines = True)
                stdout, stderr = process.communicate(self.password + '\n')
                lines = stdout.split('\n')
                if self.text == "Load":
                    filtered_lines = [line[line.find(":") + 1 : line.find("(")].strip() for line in lines if "GPU" in line and "active residency" in line]
                    container = [filtered_lines, self.root, self.text]
                    self.stats_signal.emit(container)
                elif self.text == "Clock":
                    filtered_lines = [line[line.find(":") + 1:].strip() for line in lines if "GPU" in line and "frequency" in line]
                    container = [filtered_lines, self.root, self.text]
                    self.stats_signal.emit(container)
                elif self.text == "Power":
                    filtered_lines = [line[line.find(":") + 1:].strip() for line in lines if "GPU Power" in line]
                    container = [filtered_lines, self.root, self.text]
                    self.stats_signal.emit(container)

class InitializingThread(QThread):
    init_signal = pyqtSignal(list)
    def __init__(self, splash, password):
        QThread.__init__(self)
        self.splash = splash
        self.password = password

    def run(self):
        file_path = Path(getcwd() + '/fetch/temp_sensor')
        if not file_path.exists():
            compile_command = f"clang -Wall -v {getcwd()}/fetch/temp_sensor.m -framework IOKit -framework Foundation -o {getcwd()}/fetch/temp_sensor"
            process = run(compile_command.split(), check=True, stdout=PIPE, stderr=PIPE, text=True)
        command = "sudo -S powermetrics -n1 --samplers cpu_power,gpu_power"
        process = Popen(command, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE, universal_newlines = True)
        stdout, stderr = process.communicate(self.password + '\n')
        lines = stdout.split('\n')
        list_of_cpu_load = [line[line.find(":") + 1 : line.find("(")].strip() for line in lines if "CPU" in line and "active residency" in line]
        list_of_cpu_clock = [line[line.find(":") + 1:].strip() for line in lines if "CPU" in line and "frequency" in line]
        list_of_cpu_power = [line[line.find(":") + 1:].strip() for line in lines if "CPU Power" in line]
        list_of_gpu_load = [line[line.find(":") + 1 : line.find("(")].strip() for line in lines if "GPU" in line and "active residency" in line]
        list_of_gpu_clock = [line[line.find(":") + 1:].strip() for line in lines if "GPU" in line and "frequency" in line]
        list_of_gpu_power = [line[line.find(":") + 1:].strip() for line in lines if "GPU Power" in line]

        container = [list_of_cpu_load, list_of_cpu_clock, list_of_cpu_power, list_of_gpu_load, list_of_gpu_clock, list_of_gpu_power, self.splash]
        self.init_signal.emit(container)

class GraphsThread(QThread):
    graphs_signal = pyqtSignal(list)
    def __init__(self, password):
        QThread.__init__(self)
        self.running = False
        self.password = password

    def fetch_sensors_for_graphs(self):
        process = Popen("./fetch/temp_sensor", shell=True, stdout=PIPE, text=True)
        first_output = process.stdout.readline()
        second_output = process.stdout.readline()
        process.terminate()
        first_output = first_output.split(", ")[:-1]
        second_output = second_output.split(", ")[:-1]
        second_output = [float(item) for item in second_output]
        tdie, tdev, tps, tpg, gas, nand = [], [], [], [], [], []
        filters = ["tdie", "tdev", "TP", "gas", "NAND"]
        for i in range(len(first_output)):
            if "tdie" in first_output[i]:
                tdie.append([first_output[i], second_output[i]])
            elif "tdev" in first_output[i]:
                tdev.append([first_output[i], second_output[i]])
            elif "TP" in first_output[i]:
                if first_output[i][-1] == "s":
                    tps.append([first_output[i], second_output[i]])
                else:
                    tpg.append([first_output[i], second_output[i]])
            elif "gas" in first_output[i]:
                gas.append([first_output[i], second_output[i]])
            elif "NAND" in first_output[i]:
                nand.append([first_output[i], second_output[i]])
        list_of_sensors = [tdie, tdev, tps, tpg, gas, nand]
        temp_list = []
        for item in list_of_sensors:
            unique_elements = {}
            for sublist in item:
                key = sublist[0]
                if key not in unique_elements:
                    unique_elements[key] = sublist
            unique_result = list(unique_elements.values())
            if len(unique_result) > 1:
                for fil in filters:
                    if fil in unique_result[0][0]:
                        if fil != "TP":
                            sorted_data = sorted(unique_result, key=lambda x: int(x[0].split(fil)[1]))
                        else:
                            sorted_data = sorted(unique_result, key=lambda x: int((x[0].split(fil)[1])[-2]))                    
                        break
            else:
                sorted_data = unique_result
            list_for_nums = []
            for inner_item in sorted_data:
                list_for_nums.append(inner_item[1])
            temp_list.append(list_for_nums)
        return temp_list

    def fetch_terminal_for_graphs(self):
        command = "sudo -S powermetrics -n1 --samplers cpu_power,gpu_power"
        process = Popen(command, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE, universal_newlines = True)
        stdout, stderr = process.communicate(self.password + '\n')
        lines = stdout.split('\n')
        temp_list = []
        temp_list.append([float(line[line.find(":") + 1 : line.find("%")].strip()) for line in lines if "CPU" in line and "active residency" in line])
        temp_list.append([float(line[line.find(":") + 1 : line.find("MHz")].strip()) for line in lines if "CPU" in line and "frequency" in line])
        temp_list.append([float(line[line.find(":") + 1 : line.find("mW")].strip()) for line in lines if "CPU Power" in line])
        temp_list.append([float(line[line.find(":") + 1 : line.find("%")].strip()) for line in lines if "GPU" in line and "active residency" in line])
        temp_list.append([float(line[line.find(":") + 1 : line.find("MHz")].strip()) for line in lines if "GPU" in line and "frequency" in line])
        temp_list.append([[float(line[line.find(":") + 1 : line.find("mW")].strip()) for line in lines if "GPU Power" in line][0]])
        return temp_list

    def fetch_memory(self):
        ram_info = virtual_memory()
        return ram_info[2]
    
    def run(self):
        self.running = True
        while self.running:
            container = []
            sensors = self.fetch_sensors_for_graphs()
            terminal = self.fetch_terminal_for_graphs()
            memory = self.fetch_memory()
            sensors[1] = [sensors[1][i // 2] for i in range(len(sensors[1]) * 2)]
            container = [sensors[0][:-1], [sensors[0][-1]], terminal[1], terminal[0], terminal[2], sensors[1], terminal[4], terminal[3], terminal[5], 
                        [memory], [get_average(sensors[3])], [get_average(sensors[4])], sensors[5]]
            self.graphs_signal.emit(container)

class InitializingGraphsThread(QThread):
    initializing_graphs_signal = pyqtSignal(list)
    def __init__(self, splash, password):
        QThread.__init__(self)
        self.splash = splash
        self.password = password

    def fetch_sensors_for_graphs(self):
        process = Popen("./fetch/temp_sensor", shell=True, stdout=PIPE, text=True)
        first_output = process.stdout.readline()
        second_output = process.stdout.readline()
        process.terminate()
        first_output = first_output.split(", ")[:-1]
        second_output = second_output.split(", ")[:-1]
        second_output = [float(item) for item in second_output]
        tdie, tdev, tps, tpg, gas, nand = [], [], [], [], [], []
        filters = ["tdie", "tdev", "TP", "gas", "NAND"]
        for i in range(len(first_output)):
            if "tdie" in first_output[i]:
                tdie.append([first_output[i], second_output[i]])
            elif "tdev" in first_output[i]:
                tdev.append([first_output[i], second_output[i]])
            elif "TP" in first_output[i]:
                if first_output[i][-1] == "s":
                    tps.append([first_output[i], second_output[i]])
                else:
                    tpg.append([first_output[i], second_output[i]])
            elif "gas" in first_output[i]:
                gas.append([first_output[i], second_output[i]])
            elif "NAND" in first_output[i]:
                nand.append([first_output[i], second_output[i]])
        list_of_sensors = [tdie, tdev, tps, tpg, gas, nand]
        temp_list = []
        for item in list_of_sensors:
            unique_elements = {}
            for sublist in item:
                key = sublist[0]
                if key not in unique_elements:
                    unique_elements[key] = sublist
            unique_result = list(unique_elements.values())
            if len(unique_result) > 1:
                for fil in filters:
                    if fil in unique_result[0][0]:
                        if fil != "TP":
                            sorted_data = sorted(unique_result, key=lambda x: int(x[0].split(fil)[1]))
                        else:
                            sorted_data = sorted(unique_result, key=lambda x: int((x[0].split(fil)[1])[-2]))                    
                        break
            else:
                sorted_data = unique_result
            list_for_nums = []
            for inner_item in sorted_data:
                list_for_nums.append(inner_item[1])
            temp_list.append(list_for_nums)
        return temp_list

    def fetch_terminal_for_graphs(self):
        command = "sudo -S powermetrics -n1 --samplers cpu_power,gpu_power"
        process = Popen(command, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE, universal_newlines = True)
        stdout, stderr = process.communicate(self.password + '\n')
        lines = stdout.split('\n')
        temp_list = []
        temp_list.append([float(line[line.find(":") + 1 : line.find("%")].strip()) for line in lines if "CPU" in line and "active residency" in line])
        temp_list.append([float(line[line.find(":") + 1 : line.find("MHz")].strip()) for line in lines if "CPU" in line and "frequency" in line])
        temp_list.append([float(line[line.find(":") + 1 : line.find("mW")].strip()) for line in lines if "CPU Power" in line])
        temp_list.append([float(line[line.find(":") + 1 : line.find("%")].strip()) for line in lines if "GPU" in line and "active residency" in line])
        temp_list.append([float(line[line.find(":") + 1 : line.find("MHz")].strip()) for line in lines if "GPU" in line and "frequency" in line])
        temp_list.append([[float(line[line.find(":") + 1 : line.find("mW")].strip()) for line in lines if "GPU Power" in line][0]])
        return temp_list
    
    def fetch_memory(self):
        ram_info = virtual_memory()
        return ram_info[2]

    def run(self):
        container = []
        sensors = self.fetch_sensors_for_graphs()
        terminal = self.fetch_terminal_for_graphs()
        memory = self.fetch_memory()
        sensors[1] = [sensors[1][i // 2] for i in range(len(sensors[1]) * 2)]
        container = [sensors[0][:-1], [sensors[0][-1]], terminal[1], terminal[0], terminal[2], sensors[1], terminal[4], terminal[3], terminal[5], 
                     [memory], [get_average(sensors[3])], [get_average(sensors[4])], sensors[5]]
        container.extend([self.splash])
        self.initializing_graphs_signal.emit(container)
   
#Сенсоры - Процессор, видеокарта, левое, правое, батарея, NAND
#Терминал - Загрузка ЦПУ, Частота ЦПУ, Напряжение ЦПУ, Загрузка ГПУ, Частота ГПУ, Напряжение ГПУ

#[Температура процессора] -> [Температура видеокарты] -> [Левое вентиляционное отверстие] -> [Правое вентиляционное отверстие] ->
#[Батарея] -> [NAND чип] -> [Загрузка процессора] -> [Частота процессора] -> [Напряжение на процессоре] -> [Загрузка видеокарты]
#[Частота видеокарты] -> [Напряжение на видеокарте]
        
class ReportThread(QThread):
    report_thread_signal = pyqtSignal(str)
    def __init__(self, params, book):
        QThread.__init__(self)
        self.params = params
        self.book = book
        
    def run(self):
        output = ""
        for item in self.params:
            temp = run(["system_profiler", item], capture_output=True, text=True).stdout
            temp = temp[temp.find("\n\n") + 2:]
            matching_key = next(key for key, value in self.book.items() if value == item)
            if not temp:
                temp = f"В системе нет информации о {matching_key}, проверьте подключение устройства.\n"
            output += (matching_key + ":\n" + temp + "\n")
        self.report_thread_signal.emit(output)


