from global_import import *
from additional_classes import ReportThread

checkbox_translations = {
            "Общая информация об устройстве": "SPHardwareDataType",
            "ATA": "SPParallelATADataType",
            "Apple Pay": "SPSecureElementDataType",
            "Bluetooth": "SPBluetoothDataType",
            "Ethernet": "SPEthernetDataType",
            "Fibre Channel": "SPFibreChannelDataType",
            "FireWire": "SPFireWireDataType",
            "NVMExpress": "SPNVMeDataType",
            "PCI": "SPPCIDataType",
            "SAS": "SPSASDataType",
            "SATA": "SPSerialATADataType",
            "SPI": "SPSPIDataType",
            "Thunderbolt/USB4": "SPThunderboltDataType",
            "USB": "SPUSBDataType",
            "Графика/Мониторы": "SPDisplaysDataType",
            "Запись дисков": "SPDiscBurningDataType",
            "Звук": "SPAudioDataType",
            "Камера": "SPCameraDataType",
            "Контроллер": "SPiBridgeDataType",
            "Память": "SPMemoryDataType",
            "Параллельный SCSI": "SPParallelSCSIDataType",
            "Принтеры": "SPPrintersDataType",
            "Устройство чтения SD карт": "SPCardReaderDataType",
            "Хранилище": "SPStorageDataType",
            "Электропитание": "SPPowerDataType",
            "Общая информация о сетях": "SPNetworkDataType",
            "WWAN": "SPWWANDataType",
            "Wi-Fi": "SPAirPortDataType",
            "Брэндмауэр": "SPFirewallDataType",
            "Размещения": "SPNetworkLocationDataType",
            "Тома": "SPNetworkVolumeDataType",
            "Общая информация о ПО": "SPSoftwareDataType",
            "Объекты запуска": "SPStartupItemDataType",
            "Отключенное ПО": "SPDisabledSoftwareDataType",
            "ПО принтеров": "SPPrintersSoftwareDataType",
            "Панели настроек": "SPPrefPaneDataType",
            "Поддержка RAW": "SPRawCameraDataType",
            "Профили": "SPConfigurationProfileDataType",
            "Разработчик": "SPDeveloperToolsDataType",
            "Службы синхронизации": "SPSyncServicesDataType",
            "Смарт-карты": "SPSmartCardsDataType",
            "Универсальный доступ": "SPUniversalAccessDataType",
            "Управляемый клиент": "SPManagedClientDataType",
            "Устаревшее ПО": "SPLegacySoftwareDataType",
            "Язык и регион": "SPInternationalDataType",
        }

class ReportWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()        

        row, col = 0, 0
        self.checkboxes = []
        for key, value in checkbox_translations.items():
            checkbox = QCheckBox(key, self)
            checkbox.setChecked(True)
            if "Общая" in key:
                col = 0
                row += 1
                layout.addWidget(checkbox, row, col)
                row += 1
            else:
                layout.addWidget(checkbox, row, col)
                col += 1
            if col > 3:
                col = 0
                row += 1
            self.checkboxes.append(checkbox)

        self.accept_button = QPushButton('Cформировать отчет', self)
        self.fill_button = QPushButton('Выбрать все', self)
        self.remove_button = QPushButton('Отменить все', self)
        self.accept_button.clicked.connect(self.showSelectedCheckboxes)
        self.fill_button.clicked.connect(self.fill_checkboxes)
        self.remove_button.clicked.connect(self.remove_checkboxes)

        layout.addWidget(self.fill_button, row + 1, 0, 1, 2)  
        layout.addWidget(self.remove_button, row + 1, 2, 1, 2)  
        layout.addWidget(self.accept_button, row + 2, 0, 1, 4)  

        self.setLayout(layout)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('AInPC Отчет')

        self.show()

    def showSelectedCheckboxes(self):
        selected_checkboxes = [checkbox_translations[checkbox.text()] for checkbox in self.checkboxes if checkbox.isChecked()]
        if selected_checkboxes:
            self.accept_button.setEnabled(False)
            self.fill_button.setEnabled(False)
            self.remove_button.setEnabled(False)
            self.report_thread = ReportThread(selected_checkboxes, checkbox_translations)
            self.report_thread.report_thread_signal.connect(self.create_report)
            self.report_thread.start()
        else:
             QMessageBox.warning(self, "Предупреждение", "Выберите хотя бы один пункт для формирования отчета.")

    def remove_checkboxes(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
        
    def fill_checkboxes(self):
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)

    def create_report(self, data):
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        file_name = f"AInPC Report {current_time}.txt"

        with open(file_name, "w") as file:
            file.write(data)
        
        info_message = QMessageBox(self)
        info_message.setWindowTitle('Информация')
        info_message.setText(f'Файл сохранен в рабочую папку с названием: {file_name}')

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(info_message.close)
        timer.start(3000)

        info_message.exec()

        self.accept_button.setEnabled(True)
        self.fill_button.setEnabled(True)
        self.remove_button.setEnabled(True)