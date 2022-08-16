import sys
import configparser
import asyncio

from interface import Window
from PyQt5 import QtWidgets
from telethon import TelegramClient


config = configparser.ConfigParser()
config.read('settings.ini')
phone = config['Telegram']['phone']
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    client = TelegramClient(phone, int(api_id), api_hash, loop=loop)

    with client:
        app = QtWidgets.QApplication(sys.argv)
        window = QtWidgets.QWidget()
        ui = Window()
        ui.setup(window, client, loop)
        window.show()
        sys.exit(app.exec_())
