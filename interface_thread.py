import asyncio

from telethon import TelegramClient
from PyQt5 import QtCore
from utils import get_text_from_box, write_to_file
from chat_stats import ChatStats


class WindowThread(QtCore.QThread):
    any_signal = QtCore.pyqtSignal(int)

    def __init__(self, client: TelegramClient, loop, chat_stats: ChatStats, buttons_channel_list: list,
                 window, parent=None):
        """
        :param client: telegram client
        :param loop: event loop
        :param chat_stats: ChatStats entity
        :param buttons_channel_list: channels list
        :param window: main window
        """
        super(WindowThread, self).__init__(parent)
        self.client = client
        self.loop = loop
        self.week_stats = chat_stats
        self.buttons_channel_list = buttons_channel_list
        self.window = window
        self.is_running = True

    def run(self):
        for num, button in enumerate(self.buttons_channel_list):  # checks which channel was selected
            if button.isChecked():
                self.week_stats.tg_chat = self.week_stats.channels[num]

        asyncio.set_event_loop(self.loop)  # sets the loop to current thread

        all_data = self.loop.run_until_complete(self.week_stats.get_all_data(self.any_signal))

        if all_data:
            message = self.week_stats.stats_template(all_data,
                                                     self.window.box_week_statistic.isChecked(),
                                                     self.window.box_month_statistic.isChecked(),
                                                     self.window.box_year_statistic.isChecked(),
                                                     self.window.box_quarter_statistic.isChecked(),
                                                     self.window.box_half_year_statistic.isChecked(), self.loop)
            self.loop.run_until_complete(self.week_stats.send_post(message))
        else:
            self.loop.run_until_complete(self.week_stats.send_post(
                f'За период {" - ".join(list(map(lambda date: date.strftime("%Y/%m/%d"), self.week_stats.date_range)))} сообщений не было'))

        self.window.pushButton.setEnabled(True)

        write_to_file('stop_words.txt', [text + '\n' for text in get_text_from_box(self.window.listWidget)])

    def stop(self):
        self.is_running = False
        self.terminate()
