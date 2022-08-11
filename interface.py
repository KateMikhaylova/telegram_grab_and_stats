import asyncio

from PyQt5 import QtCore, QtWidgets
from week_stats import WeekStats
from datetime import datetime
from chat_data import date_range


class StatThread(QtCore.QThread):
    def __init__(self, client, loop, week_stats, buttons_channel_list, window):
        """
        :param client: <class 'telethon.client.telegramclient.TelegramClient'>
        :param loop: <class 'asyncio.windows_events.ProactorEventLoop'>
        :param week_stats: <class 'week_stats.WeekStats'>
        :param buttons_channel_list: list of channels in GUI
        :param window: main window interface <class 'interface.Window'>
        """
        super().__init__()
        self.client = client
        self.loop = loop
        self.week_stats = week_stats
        self.buttons_channel_list = buttons_channel_list
        self.window = window

    def run(self):
        for num, button in enumerate(self.buttons_channel_list):  # checks which channel was selected
            if button.isChecked():
                self.week_stats.tg_chat = self.week_stats.channels[num]

        asyncio.set_event_loop(self.loop)  # sets the loop to current thread

        all_data = self.loop.run_until_complete(self.week_stats.get_all_data())

        if all_data:
            message = self.week_stats.stats_template(all_data,
                                                     self.window.box_week_statistic.isChecked(),
                                                     self.window.box_month_statistic.isChecked(),
                                                     self.window.box_year_statistic.isChecked())
            self.loop.run_until_complete(self.week_stats.send_post(message))
        else:
            self.loop.run_until_complete(self.week_stats.send_post(
                f'За период {" - ".join(list(map(lambda date: date.strftime("%Y/%m/%d"), self.week_stats.date_range)))} сообщений не было'))

        self.week_stats.progress_bar.setValue(self.week_stats.progress_bar_range)  # fills the progress bar
        self.window.launched = False  # allows to launch new thread


class Window(object):
    def __init__(self):
        self.launched = False  # 'True' if button was pressed, otherwise 'False'
        self.uploading = None

    def send_post(self, week_stats, buttons_channel_list, client, loop):
        """
        Launches a thread.
        :param week_stats: entity of the class <class 'week_stats.WeekStats'>
        :param buttons_channel_list:
        :param client: <class 'telethon.client.telegramclient.TelegramClient'>
        :param loop: <class 'asyncio.windows_events.ProactorEventLoop'>
        """
        if not self.launched:  # checks if the launch button was pressed
            self.launched = True

            week_stats.n_words = self.box_n_words.value()

            if self.box_top_3_number_of_words.isChecked():
                week_stats.top_3_number_of_words = True
            else:
                week_stats.top_3_number_of_words = False

            if self.box_lemmatize.isChecked():
                week_stats.lemmatize = True
            else:
                week_stats.lemmatize = False

            if self.box_custom_statistic.isChecked():
                week_stats.date_range = [datetime(*self.box_custom_date_start.date().getDate()).date(), # sets custom date range
                                         datetime(*self.box_custom_date_end.date().getDate()).date()]
            else:
                week_stats.date_range = date_range(self.box_week_number.currentIndex(),
                                                   self.box_month_number.currentIndex(),
                                                   self.box_year_number.currentIndex(),
                                                   self.box_week_statistic.isChecked(),
                                                   self.box_month_statistic.isChecked(),
                                                   self.box_year_statistic.isChecked())

            week_stats.progress_bar = self.progressBar

            self.uploading = StatThread(client, loop, week_stats, buttons_channel_list, self)
            self.uploading.start()

    def setupUi(self, window, client, loop):
        """
        Creates GUI window.
        :param window: main window <class 'PyQt5.QtWidgets.QWidget'>
        :param client: <class 'telethon.client.telegramclient.TelegramClient'>
        :param loop: <class 'asyncio.windows_events.ProactorEventLoop'>
        """
        week_stats = WeekStats(client)

        client.loop.run_until_complete(week_stats.get_channel())

        window.setObjectName("Form")
        window.resize(515, 250)
        window.setMaximumSize(QtCore.QSize(700, 250))

        self.verticalLayout_4 = QtWidgets.QVBoxLayout(window)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(window)
        self.label.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.scrollArea = QtWidgets.QScrollArea(window)
        self.scrollArea.setMaximumSize(QtCore.QSize(500, 200))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 144, 242))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")

        buttons = [QtWidgets.QRadioButton(self.scrollAreaWidgetContents) for _ in range(len(week_stats.channels))]
        buttons[0].setChecked(True)
        [button.setChecked(False) for button in buttons[1:]]
        [button.setObjectName(f"radioButton_{i}") for i, button in enumerate(buttons, start=1)]
        [self.verticalLayout.addWidget(button) for button in buttons]  # creates list of channels

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        self.line = QtWidgets.QFrame(window)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_3.addWidget(self.line)
        self.frame = QtWidgets.QFrame(window)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setMaximumSize(QtCore.QSize(20, 16777215))
        self.label_2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 5, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setMaximumSize(QtCore.QSize(20, 16777215))
        self.label_3.setTabletTracking(False)
        self.label_3.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 6, 0, 1, 1)
        self.box_week_statistic = QtWidgets.QRadioButton(self.frame)
        self.box_week_statistic.setMaximumSize(QtCore.QSize(20, 16777215))
        self.box_week_statistic.setText("")
        self.box_week_statistic.setChecked(True)
        self.box_week_statistic.setObjectName("radioButton_11")
        self.gridLayout.addWidget(self.box_week_statistic, 1, 0, 1, 1)
        self.box_month_statistic = QtWidgets.QRadioButton(self.frame)
        self.box_month_statistic.setMaximumSize(QtCore.QSize(20, 16777215))
        self.box_month_statistic.setText("")
        self.box_month_statistic.setChecked(False)
        self.box_month_statistic.setObjectName("radioButton_12")
        self.gridLayout.addWidget(self.box_month_statistic, 2, 0, 1, 1)
        self.box_week_number = QtWidgets.QComboBox(self.frame)
        self.box_week_number.setMinimumSize(QtCore.QSize(0, 0))
        self.box_week_number.setObjectName("comboBox_2")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.gridLayout.addWidget(self.box_week_number, 1, 1, 1, 2)
        self.box_month_number = QtWidgets.QComboBox(self.frame)
        self.box_month_number.setMinimumSize(QtCore.QSize(0, 0))
        self.box_month_number.setObjectName("comboBox_3")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.gridLayout.addWidget(self.box_month_number, 2, 1, 1, 2)
        self.box_year_statistic = QtWidgets.QRadioButton(self.frame)
        self.box_year_statistic.setMaximumSize(QtCore.QSize(20, 16777215))
        self.box_year_statistic.setText("")
        self.box_year_statistic.setChecked(False)
        self.box_year_statistic.setObjectName("radioButton_13")
        self.gridLayout.addWidget(self.box_year_statistic, 3, 0, 1, 1)
        self.box_year_number = QtWidgets.QComboBox(self.frame)
        self.box_year_number.setMinimumSize(QtCore.QSize(0, 0))
        self.box_year_number.setObjectName("comboBox")
        self.box_year_number.addItem("")
        self.box_year_number.addItem("")
        self.box_year_number.addItem("")
        self.box_year_number.addItem("")
        self.box_year_number.addItem("")
        self.box_year_number.addItem("")
        self.gridLayout.addWidget(self.box_year_number, 3, 1, 1, 2)
        self.box_custom_statistic = QtWidgets.QRadioButton(self.frame)
        self.box_custom_statistic.setChecked(False)
        self.box_custom_statistic.setObjectName("radioButton_14")
        self.gridLayout.addWidget(self.box_custom_statistic, 4, 0, 1, 3)
        self.box_custom_date_start = QtWidgets.QDateEdit(self.frame)
        self.box_custom_date_start.setObjectName("dateEdit")
        self.box_custom_date_start.setDate(datetime.now())
        self.gridLayout.addWidget(self.box_custom_date_start, 5, 1, 1, 2)
        self.box_custom_date_end = QtWidgets.QDateEdit(self.frame)
        self.box_custom_date_end.setObjectName("dateEdit_2")
        self.box_custom_date_end.setDate(datetime.now())
        self.gridLayout.addWidget(self.box_custom_date_end, 6, 1, 1, 2)
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 3)
        self.horizontalLayout_3.addWidget(self.frame)
        self.line_2 = QtWidgets.QFrame(window)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_3.addWidget(self.line_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_6 = QtWidgets.QLabel(window)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_3.addWidget(self.label_6)
        self.box_top_3_number_of_words = QtWidgets.QCheckBox(window)
        self.box_top_3_number_of_words.setChecked(False)
        self.box_top_3_number_of_words.setObjectName("checkBox_16")
        self.verticalLayout_3.addWidget(self.box_top_3_number_of_words)
        self.box_lemmatize = QtWidgets.QCheckBox(window)
        self.box_lemmatize.setChecked(True)
        self.box_lemmatize.setObjectName("checkBox_15")
        self.verticalLayout_3.addWidget(self.box_lemmatize)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(window)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.box_n_words = QtWidgets.QSpinBox(window)
        self.box_n_words.setProperty("value", 7)
        self.box_n_words.setObjectName("spinBox")
        self.horizontalLayout.addWidget(self.box_n_words)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.line_3 = QtWidgets.QFrame(window)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_4.addWidget(self.line_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtWidgets.QPushButton(window)

        self.pushButton.clicked.connect(lambda: self.send_post(week_stats, buttons, client, loop))

        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.progressBar = QtWidgets.QProgressBar(window)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.horizontalLayout_2.addWidget(self.progressBar)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.retranslateUi(window, buttons, week_stats)
        QtCore.QMetaObject.connectSlotsByName(window)

    def retranslateUi(self, Form, buttons, week_stats):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Solid Grab&Top"))
        self.label.setText(_translate("Form", "Группы:"))
        [button.setText(_translate("Form", f"{channel.title}")) for button, channel in
         zip(buttons, week_stats.channels)]
        self.label_2.setText(_translate("Form", "от:"))
        self.label_3.setText(_translate("Form", "до:"))
        self.box_week_number.setItemText(0, _translate("Form", "прошлая неделя"))
        self.box_week_number.setItemText(1, _translate("Form", "1 неделя назад"))
        self.box_week_number.setItemText(2, _translate("Form", "2 недели назад"))
        self.box_week_number.setItemText(3, _translate("Form", "3 недели назад"))
        self.box_week_number.setItemText(4, _translate("Form", "4 недели назад"))
        self.box_week_number.setItemText(5, _translate("Form", "5 недель назад"))
        self.box_month_number.setItemText(0, _translate("Form", "Прошлый месяц"))
        self.box_month_number.setItemText(1, _translate("Form", "1 месяц назад"))
        self.box_month_number.setItemText(2, _translate("Form", "2 месяца назад"))
        self.box_month_number.setItemText(3, _translate("Form", "3 месяца назад"))
        self.box_month_number.setItemText(4, _translate("Form", "4 месяца назад"))
        self.box_month_number.setItemText(5, _translate("Form", "5 месяцев назад"))
        self.box_year_number.setItemText(0, _translate("Form", "Прошлый год"))
        self.box_year_number.setItemText(1, _translate("Form", "1 год назад"))
        self.box_year_number.setItemText(2, _translate("Form", "2 года назад"))
        self.box_year_number.setItemText(3, _translate("Form", "3 года назад"))
        self.box_year_number.setItemText(4, _translate("Form", "4 года назад"))
        self.box_year_number.setItemText(5, _translate("Form", "5 лет назад"))
        self.box_custom_statistic.setText(_translate("Form", "Пользовательский:"))
        self.label_5.setText(_translate("Form", "Установка промежутка:"))
        self.label_6.setText(_translate("Form", "Дополнительный параметры:"))
        self.box_top_3_number_of_words.setText(_translate("Form", "Количество слов в топ 3"))
        self.box_lemmatize.setText(_translate("Form", "Лематизация топ слов"))
        self.label_4.setText(_translate("Form", "Количество топ слов:"))
        self.pushButton.setText(_translate("Form", "Отправить статистику"))
