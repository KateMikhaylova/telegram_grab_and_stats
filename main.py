import sys
import configparser
import asyncio

from interface import Window
from PyQt5 import QtWidgets
from telethon import TelegramClient
from pyrogram import Client


config = configparser.ConfigParser()
config.read('settings.ini')
phone = config['Telegram']['phone']
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    telethon_client = TelegramClient(phone, int(api_id), api_hash, loop=loop)
    pyrogram_client = Client(phone, api_id=api_id, api_hash=api_hash)

    with telethon_client:
        app = QtWidgets.QApplication(sys.argv)
        window = QtWidgets.QWidget()
        ui = Window()
        ui.setup(window, telethon_client, pyrogram_client, loop)
        window.show()
        sys.exit(app.exec_())
