import sqlite3

from subprocess import Popen, PIPE, run
from os import getcwd

DB = getcwd() + "/aipcdb_mac.db"

# Функция, получающая данные о температуре процессора, видеокарты и чипа SSD,
# и помещает эти данные в указанный массив
def fetch_sensors(type_of_sensor, massive):
    massive.clear()
    process = Popen("./fetch/temp_sensor", shell=True, stdout = PIPE, text=True)
    first_output = process.stdout.readline()
    second_output = process.stdout.readline()
    process.terminate()
    first_output = first_output.split(", ")[:-1]
    second_output = second_output.split(", ")[:-1]
    second_output = [float(item) for item in second_output]
    temp_massive = []
    for i in range(len(first_output)):
        if type_of_sensor in first_output[i]:
            temp_massive.append([first_output[i], second_output[i]])
    filters = ["tdie", "tdev", "NAND"]
    unique_elements = {}
    for sublist in temp_massive:
        key = sublist[0]
        if key not in unique_elements:
            unique_elements[key] = sublist
    unique_result = list(unique_elements.values())
    if len(unique_result) > 1:
        for fil in filters:
            if fil in unique_result[0][0]:
                if fil != "TP":
                    sorted_data = sorted(unique_result, key = lambda x: int(x[0].split(fil)[1]))
                else:
                    sorted_data = sorted(unique_result, key = lambda x: int((x[0].split(fil)[1])[-2]))                    
                break
    else:
        sorted_data = unique_result
    massive += sorted_data

# Функция, получающая данные о температуре материнской платы и помещающая эти данные
# в указанный массив
def fetch_sensors_mb_temp(massive):
    massive.clear()
    process = Popen("./fetch/temp_sensor", shell=True, stdout = PIPE, text=True)
    first_output = process.stdout.readline()
    second_output = process.stdout.readline()
    process.terminate()
    first_output = first_output.split(", ")[:-1]
    second_output = second_output.split(", ")[:-1]
    second_output = [float(item) for item in second_output]
    temp_massive = []
    for i in range(len(first_output)):
        if "TP" in first_output[i] or "gas" in first_output[i]:
            temp_massive.append([first_output[i], second_output[i]])
    unique_elements = {}
    for sublist in temp_massive:
        key = sublist[0]
        if key not in unique_elements:
            unique_elements[key] = sublist
    unique_result = list(unique_elements.values())
    g_sum = 0
    s_sum = 0
    g_len = 0
    s_len = 0
    sorted_data = []
    for i in range(len(unique_result)):
        if unique_result[i][0] == "gas gauge battery":
            sorted_data.append(unique_result[i])
        elif "TP" in unique_result[i][0]:
            if "g" == unique_result[i][0][-1]:
                g_sum += unique_result[i][1]
                g_len += 1
            elif "s" == unique_result[i][0][-1]:
                s_sum += unique_result[i][1]
                s_len += 1
    sorted_data.append(["TPs", s_sum / s_len])
    sorted_data.append(["TPg", g_sum / g_len])
    massive += sorted_data

# Функция, получающая из системы данные о физических дисках и переводящая эту информацию
# на русский язык
def initialize_disks():
    disks = run(["system_profiler", "SPNVMeDataType"], capture_output=True, text=True).stdout
    disks = disks.replace("\n\n", "\n").replace("Capacity", "Емкость").replace("TRIM Support", "Поддержка TRIM").replace("GB", "Гб").replace("bytes", "бит")
    disks = disks.replace("Model", "Модель").replace("Serial Number", "Серийный номер").replace("Yes", "Да").replace("No", "Нет").replace("Revision", "Ревизия")
    disks = disks.replace("Detachable Drive", "Внешний накопитель").replace("BSD Name", "Название BSD").replace("Partition Map Type", "Тип схемы разделов")
    disks = disks.replace("Removable Media", "Съемный носитель").replace("S.M.A.R.T. status", "Статус S.M.A.R.T.").replace("GPT (GUID Partition Table)", "GPT (Таблица разделов GUID)")
    disks = disks.replace("Volumes", "Тома").replace("Content", "Содержимое").replace("Verified", "Проверен")
    disks = disks.split("\n")
    disks = disks[:-1]
    return disks

# Функция, получающая из системы данные об оперативной и переводящая эту информацию
# на русский язык
def initialize_ram():
    ram = run(["system_profiler", "SPMemoryDataType"], capture_output=True, text=True).stdout
    ram = ram.replace("\n\n", "\n").replace("Memory", "Объем памяти").replace("Type", "Тип").replace("GB", "Гб").replace("Manufacturer", "Производитель")
    ram = ram.split("\n")
    ram = ram[1:-1]
    return ram

# Функция, получающая из системы данные о видеокарте и переводящая эту информацию
# на русский язык
def initialize_gpu():
    gpu = run(["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True).stdout
    gpu = gpu.replace("\n\n", "\n").replace("Chipset Model", "Чипсет").replace("Display Type", "Тип монитора").replace("Connection Type", "Тип подключения").replace("Type", "Тип").replace("Bus", "Шина").replace("Built-In", "Встроенный").replace("Total Number of Cores", "Общее число ядер")
    gpu = gpu.replace("Mirror Status", "Статус видеоповтора").replace("Master Mirror", "Мастер-видеоповтор").replace("Hardware Mirror", "Аппаратный видеоповтор")
    gpu = gpu.replace("Rotation", "Поворот").replace("Supported", "Поддерживается").replace("Television", "Телевизор")
    gpu = gpu.replace("Vendor", "Производитель").replace("Metal Support", "Поддержка Metal").replace("Displays", "Дисплеи").replace("Color LCD", "Цветной ЖК-дисплей")
    gpu = gpu.replace("Resolution", "Разрешение").replace("Built-in Liquid Retina XDR Display", "Встроенный дисплей Liquid Retina XDR").replace("Yes", "Да").replace("Online", "Онлайн")
    gpu = gpu.replace("Main Display", "Основной монитор").replace("On", "Вкл.").replace("No", "Нет").replace("Mirror", "Видеоповтор").replace("Off", "Выкл.")
    gpu = gpu.replace("Automatically Adjust Brightness", "Настраивать яркость автоматически").replace("Internal", "Внутренний")
    gpu = gpu.split("\n")
    gpu = gpu[1:-1]
    return gpu

# Функция, получающая из системы данные о материнской плате и переводящая эту информацию
# на русский язык
def initialize_mb():
    mb = run(["system_profiler", "SPHardwareDataType"], capture_output=True, text=True).stdout
    mb = mb.replace("\n\n", "\n").replace("Model Name", "Название модели").replace("Model Identifier", "Идентификатор модели").replace("Model Number", "Номер модели").replace("Chip", "Чип")
    mb = mb.replace("Total Number of Cores", "Общее число ядер").replace("performance", "производительности").replace("and", "и").replace("efficiency", "эффективности")
    mb = mb.replace("Memory", "Память").replace("GB", "Гб").replace("System Firmware Version", "Версия системной прошивки").replace("OS Loader Version", "Версия загрузчика ОС")
    mb = mb.replace("Serial Number (system)", "Серийный номер системы").replace("Hardware UUID", "UUID аппаратного обеспечения").replace("Provisioning UDID", "UDID технического обеспечения")
    mb = mb.replace("Activation Lock Status", "Состояние блокировки активации").replace("Enabled", "Включено").replace("Disabled", "Выключена")
    mb = mb.split("\n")
    mb = mb[2:-1]
    mb = [item for item in mb if ("Чип: " not in item and "Общее число ядер: " not in item and "Память: " not in item)]
    return mb

# Функция, получающая из базы данных информацию о процессоре
def initialize_cpu():
    cpu_info = run('system_profiler SPHardwareDataType | grep -E "Chip|Total Number of Cores"', shell=True, capture_output=True, text=True).stdout.split("\n")
    cpu_info = cpu_info[:-1]
    cpu_info = [item.strip() for item in cpu_info]
    name = cpu_info[0][cpu_info[0].index(":") + 2:]
    count_of_p_cores = cpu_info[1][cpu_info[1].index("(") + 1:cpu_info[1].index("performance") - 1].strip()
    count_of_e_cores = cpu_info[1][cpu_info[1].index("and ") + 3:cpu_info[1].index("efficiency")].strip()
    try:
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cpu_info WHERE cpu_name = ? and cpu_count_of_p_cores = ? and cpu_count_of_e_cores = ?", (name, count_of_p_cores, count_of_e_cores))
        return cursor.fetchone()
    except sqlite3.Error as error:
        pass
    finally:
        if conn:
            conn.close()
