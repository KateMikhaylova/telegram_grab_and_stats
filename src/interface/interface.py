from PyQt5 import QtCore
from src.chat.chat_stats import ChatStats
from src.interface.interface_thread import WindowThread
from telethon import TelegramClient
from pyrogram import Client
from src.utils import *
import os


class Window(object):
    def __init__(self):
        self.uploading = None

    def send_post(self, chat_stats: ChatStats, buttons_channel_list: list, buttons_mask_list: list,
                  telethon_client: TelegramClient, pyrogram_client: Client, loop):
        """
        Launches a thread.
        :param chat_stats: ChatStats entity
        :param buttons_channel_list: channels list
        :param buttons_mask_list: masks list
        :param telethon_client: telegram client
        :param pyrogram_client: pyrogram client
        :param loop: event loop
        """
        self.pushButton.setEnabled(False)

        chat_stats.options_update(self.box_n_words.value(),
                                  self.box_n_posts.value(),
                                  self.box_top_3_number_of_words.isChecked(),
                                  self.box_lemmatize.isChecked(),
                                  self.box_average_polls_stats.isChecked(),
                                  self.box_top_posts_stats.isChecked(),
                                  self.box_top_reactions_posts.isChecked(),
                                  self.box_top_reactions_comments.isChecked(),
                                  self.box_longest_comment.isChecked(),
                                  self.box_message_streak.isChecked(),
                                  self.box_word_cloud.isChecked(),
                                  get_text_from_box(self.listWidget))

        chat_stats.date_update(self.box_week_number.currentIndex(),
                               self.box_month_number.currentIndex(),
                               self.box_year_number.currentIndex(),
                               self.box_custom_date_start.date().getDate(),
                               self.box_custom_date_end.date().getDate(),
                               self.box_week_statistic.isChecked(),
                               self.box_month_statistic.isChecked(),
                               self.box_year_statistic.isChecked(),
                               self.box_quarter_statistic.isChecked(),
                               self.box_half_year_statistic.isChecked(),
                               self.box_custom_statistic.isChecked())

        self.progressBar.setValue(0)
        progress_bar_range = (chat_stats.date_range[1] - chat_stats.date_range[0]).days
        self.progressBar.setRange(0, progress_bar_range)

        self.uploading = WindowThread(telethon_client, pyrogram_client,
                                      loop, chat_stats, buttons_channel_list, buttons_mask_list, self, parent=None)
        self.uploading.start()
        self.uploading.any_signal.connect(self.progress_bar_counter)

    def progress_bar_counter(self, counter: int):
        """
        Sets value for progress bar.
        :param counter: current for progress bar
        """
        self.progressBar.setValue(counter)

    def setup(self, window: QtWidgets.QWidget, telethon_client: TelegramClient, pyrogram_client: Client, loop):
        """
        Creates GUI window.
        :param window: main window
        :param telethon_client: telegram client
        :param pyrogram_client: pyrogram_client
        :param loop: event loop
        """
        chat_stats = ChatStats(telethon_client)

        telethon_client.loop.run_until_complete(chat_stats.get_channel())

        window.setObjectName("Form")
        window.resize(950, 300)
        window.setMaximumSize(QtCore.QSize(950, 300))
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(window)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
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
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 184, 242))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")

        buttons = [QtWidgets.QRadioButton(self.scrollAreaWidgetContents) for _ in range(len(chat_stats.channels))]
        buttons[0].setChecked(True)
        [button.setChecked(False) for button in buttons[1:]]
        [button.setObjectName(f"radioButton_{i}") for i, button in enumerate(buttons, start=1)]
        [self.verticalLayout.addWidget(button) for button in buttons]  # creates list of channels

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.horizontalLayout_4.addLayout(self.verticalLayout_2)
        self.line = QtWidgets.QFrame(window)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_4.addWidget(self.line)
        self.frame = QtWidgets.QFrame(window)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 2)
        self.box_week_statistic = QtWidgets.QRadioButton(self.frame)
        self.box_week_statistic.setMaximumSize(QtCore.QSize(20, 16777215))
        self.box_week_statistic.setText("")
        self.box_week_statistic.setChecked(True)
        self.box_week_statistic.setObjectName("radioButton_11")
        self.gridLayout.addWidget(self.box_week_statistic, 1, 0, 1, 1)
        self.box_week_number = QtWidgets.QComboBox(self.frame)
        self.box_week_number.setMinimumSize(QtCore.QSize(0, 0))
        self.box_week_number.setObjectName("comboBox_2")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.box_week_number.addItem("")
        self.gridLayout.addWidget(self.box_week_number, 1, 1, 1, 1)
        self.box_month_statistic = QtWidgets.QRadioButton(self.frame)
        self.box_month_statistic.setMaximumSize(QtCore.QSize(20, 16777215))
        self.box_month_statistic.setText("")
        self.box_month_statistic.setChecked(False)
        self.box_month_statistic.setObjectName("radioButton_12")
        self.gridLayout.addWidget(self.box_month_statistic, 2, 0, 1, 1)
        self.box_month_number = QtWidgets.QComboBox(self.frame)
        self.box_month_number.setMinimumSize(QtCore.QSize(0, 0))
        self.box_month_number.setObjectName("comboBox_3")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.box_month_number.addItem("")
        self.gridLayout.addWidget(self.box_month_number, 2, 1, 1, 1)
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
        self.gridLayout.addWidget(self.box_year_number, 3, 1, 1, 1)

        self.box_quarter_statistic = QtWidgets.QRadioButton(self.frame)
        self.box_quarter_statistic.setChecked(False)
        self.box_quarter_statistic.setObjectName("box_quarter_statistic")
        self.gridLayout.addWidget(self.box_quarter_statistic, 4, 0, 1, 2)

        self.box_half_year_statistic = QtWidgets.QRadioButton(self.frame)
        self.box_half_year_statistic.setChecked(False)
        self.box_half_year_statistic.setObjectName("box_quarter_statistic")
        self.gridLayout.addWidget(self.box_half_year_statistic, 5, 0, 1, 2)

        self.box_custom_statistic = QtWidgets.QRadioButton(self.frame)
        self.box_custom_statistic.setChecked(False)
        self.box_custom_statistic.setObjectName("radioButton_14")
        self.gridLayout.addWidget(self.box_custom_statistic, 6, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setMaximumSize(QtCore.QSize(20, 16777215))
        self.label_2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 7, 0, 1, 1)
        self.box_custom_date_start = QtWidgets.QDateEdit(self.frame)
        self.box_custom_date_start.setObjectName("dateEdit")
        self.box_custom_date_start.setDate(datetime.now())
        self.gridLayout.addWidget(self.box_custom_date_start, 7, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setMaximumSize(QtCore.QSize(20, 16777215))
        self.label_3.setTabletTracking(False)
        self.label_3.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 8, 0, 1, 1)
        self.box_custom_date_end = QtWidgets.QDateEdit(self.frame)
        self.box_custom_date_end.setObjectName("dateEdit_2")
        self.box_custom_date_end.setDate(datetime.now())
        self.gridLayout.addWidget(self.box_custom_date_end, 8, 1, 1, 1)
        self.horizontalLayout_4.addWidget(self.frame)
        self.line_2 = QtWidgets.QFrame(window)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_4.addWidget(self.line_2)
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
        self.box_average_polls_stats = QtWidgets.QCheckBox(window)
        self.box_average_polls_stats.setChecked(False)
        self.box_average_polls_stats.setObjectName("checkBox_15")
        self.verticalLayout_3.addWidget(self.box_average_polls_stats)

        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.box_top_posts_stats = QtWidgets.QCheckBox(window)
        self.box_top_posts_stats.setChecked(False)
        self.box_top_posts_stats.setObjectName("checkBox_15")
        self.verticalLayout_6.addWidget(self.box_top_posts_stats)
        self.box_top_reactions_posts = QtWidgets.QCheckBox(window)
        self.box_top_reactions_posts.setChecked(False)
        self.box_top_reactions_posts.setObjectName("checkBox_15")
        self.verticalLayout_6.addWidget(self.box_top_reactions_posts)
        self.box_top_reactions_comments = QtWidgets.QCheckBox(window)
        self.box_top_reactions_comments.setChecked(False)
        self.box_top_reactions_comments.setObjectName("checkBox_15")
        self.verticalLayout_6.addWidget(self.box_top_reactions_comments)
        self.horizontalLayout_5.addLayout(self.verticalLayout_6)

        self.line_5 = QtWidgets.QFrame(window)
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_4")
        self.horizontalLayout_5.addWidget(self.line_5)

        self.box_n_posts = QtWidgets.QSpinBox(window)
        self.box_n_posts.setMaximum(10)
        self.box_n_posts.setProperty("value", 1)
        self.box_n_posts.setObjectName("spinBox")
        self.horizontalLayout_5.addWidget(self.box_n_posts)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        
        self.box_longest_comment = QtWidgets.QCheckBox(window)
        self.box_longest_comment.setChecked(False)
        self.box_longest_comment.setObjectName("checkBox_17")
        self.verticalLayout_3.addWidget(self.box_longest_comment)
        
        self.box_message_streak = QtWidgets.QCheckBox(window)
        self.box_message_streak.setChecked(False)
        self.box_message_streak.setObjectName("checkBox_15")
        self.verticalLayout_3.addWidget(self.box_message_streak)

        self.box_word_cloud = QtWidgets.QCheckBox(window)
        self.box_word_cloud.setChecked(False)
        self.box_word_cloud.setObjectName("checkBox_17")
        self.verticalLayout_3.addWidget(self.box_word_cloud)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(window)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.box_n_words = QtWidgets.QSpinBox(window)
        self.box_n_words.setMaximum(10)
        self.box_n_words.setProperty("value", 7)
        self.box_n_words.setObjectName("spinBox")
        self.horizontalLayout.addWidget(self.box_n_words)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.line_4 = QtWidgets.QFrame(window)
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.horizontalLayout_4.addWidget(self.line_4)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_7 = QtWidgets.QLabel(window)
        self.label_7.setObjectName('label_7')
        self.verticalLayout_4.addWidget(self.label_7)
        self.pushButton_2 = QtWidgets.QPushButton(window)
        self.pushButton_2.setMaximumSize(QtCore.QSize(60, 16777215))
        self.pushButton_2.setObjectName("pushButton_2")

        self.pushButton_2.clicked.connect(lambda: add_item_to_box(self.listWidget,
                                                                  self.lineEdit))  # adds text item from self.listWidget to stopwords box if clicked

        self.horizontalLayout_3.addWidget(self.pushButton_2, 0, QtCore.Qt.AlignLeft)
        self.lineEdit = QtWidgets.QLineEdit(window)
        self.lineEdit.setMaximumSize(QtCore.QSize(150, 16777215))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_3.addWidget(self.lineEdit, 0, QtCore.Qt.AlignLeft)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.listWidget = QtWidgets.QListWidget(window)
        self.listWidget.setMaximumSize(QtCore.QSize(200, 16777215))
        self.listWidget.setObjectName("listWidget")

        self.listWidget.addItems(
            read_from_file('src/stop_words.txt'))  # reads stopwords from file and adds to stopwords box

        self.verticalLayout_4.addWidget(self.listWidget)
        self.pushButton_3 = QtWidgets.QPushButton(window)
        self.pushButton_3.setObjectName("pushButton_3")

        self.pushButton_3.clicked.connect(lambda: self.listWidget.takeItem(
            self.listWidget.currentIndex().row()))  # removes chosen stopword from stopwords box if button was clicked

        self.verticalLayout_4.addWidget(self.pushButton_3, 0, QtCore.Qt.AlignLeft)
        self.horizontalLayout_4.addLayout(self.verticalLayout_4)

        self.line_5 = QtWidgets.QFrame(window)
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.horizontalLayout_4.addWidget(self.line_5)

        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_2")
        self.label_8 = QtWidgets.QLabel(window)
        self.label_8.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_8.setObjectName("label_8")
        self.verticalLayout_7.addWidget(self.label_8)

        self.scrollArea2 = QtWidgets.QScrollArea(window)
        self.scrollArea2.setMaximumSize(QtCore.QSize(500, 200))
        self.scrollArea2.setWidgetResizable(True)
        self.scrollArea2.setObjectName("scrollArea2")

        self.scrollAreaWidgetContents2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents2.setGeometry(QtCore.QRect(0, 0, 184, 242))
        self.scrollAreaWidgetContents2.setObjectName("scrollAreaWidgetContents2")
        self.verticalLayout6 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents2)
        self.verticalLayout6.setObjectName("verticalLayout6")

        self.pictures_text = ['случайный выбор'] + [text for text in os.listdir('img') if text.endswith('png')]
        buttons2 = [QtWidgets.QRadioButton(self.scrollAreaWidgetContents2) for _ in range(len(self.pictures_text))]
        buttons2[0].setChecked(True)
        [button.setChecked(False) for button in buttons2[1:]]
        [button.setObjectName(f"radioButton_{i}") for i, button in enumerate(buttons2, start=1)]
        [self.verticalLayout6.addWidget(button) for button in buttons2]  # creates list of mask names

        self.scrollArea2.setWidget(self.scrollAreaWidgetContents2)
        self.verticalLayout_7.addWidget(self.scrollArea2)
        self.horizontalLayout_4.addLayout(self.verticalLayout_7)

        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.line_3 = QtWidgets.QFrame(window)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_5.addWidget(self.line_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtWidgets.QPushButton(window)

        self.pushButton.clicked.connect(
            lambda: self.send_post(chat_stats, buttons, buttons2, telethon_client, pyrogram_client, loop))  # sends post to telegram account if clicked

        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.progressBar = QtWidgets.QProgressBar(window)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.horizontalLayout_2.addWidget(self.progressBar)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)

        self.retranslate_ui(window, buttons, buttons2, chat_stats)
        QtCore.QMetaObject.connectSlotsByName(window)

    def retranslate_ui(self, window: QtWidgets.QWidget, buttons: list, buttons2: list,
                       chat_stats: ChatStats):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("Form", "Solid Grab&Top"))
        self.label.setText(_translate("Form", "Группы:"))

        [button.setText(_translate("Form", f"{channel.title}")) for button, channel in
         zip(buttons, chat_stats.channels)]  # reads channel titles and assigns names to buttons

        [button.setText(_translate("Form", f"{text}")) for button, text in
         zip(buttons2, self.pictures_text)]  # reads channel titles and assigns names to buttons

        self.label_5.setText(_translate("Form", "Установка промежутка:"))
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
        self.label_2.setText(_translate("Form", "от:"))
        self.label_3.setText(_translate("Form", "до:"))
        self.label_6.setText(_translate("Form", "Дополнительный параметры:"))
        self.label_7.setText(_translate("Form", "Исключаемые слова:"))
        self.label_8.setText(_translate("Form", "Список доступных масок:"))
        self.box_top_3_number_of_words.setText(_translate("Form", "Количество слов в топ 3"))
        self.box_lemmatize.setText(_translate("Form", "Лематизация топ слов"))
        self.box_average_polls_stats.setText(_translate("Form", "Средняя статистика тестов"))
        self.box_top_posts_stats.setText(_translate("Form", "Топ постов"))
        self.box_top_reactions_posts.setText(_translate("Form", "Топ реакций(посты)"))
        self.box_top_reactions_comments.setText(_translate("Form", "Топ реакций(комментарии)"))
        self.box_longest_comment.setText(_translate("Form", "Самый длинный комментарий"))
        self.box_message_streak.setText(_translate("Form", "Стрик сообщений"))
        self.box_word_cloud.setText(_translate("Form", "Облако слов"))
        self.label_4.setText(_translate("Form", "Количество топ слов:"))
        self.pushButton_2.setText(_translate("Form", "Добавить"))
        self.pushButton_3.setText(_translate("Form", "Удалить"))
        self.pushButton.setText(_translate("Form", "Отправить статистику"))
        self.box_quarter_statistic.setText(_translate("Form", "Прошлый квартал:"))
        self.box_half_year_statistic.setText(_translate("Form", "Прошлое полугодие:"))
