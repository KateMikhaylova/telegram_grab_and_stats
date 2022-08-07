import configparser

from telethon import TelegramClient
from week_stats import WeekStats

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    phone = config['Telegram']['phone']
    api_id = config['Telegram']['api_id']
    api_hash = config['Telegram']['api_hash']

    client = TelegramClient(phone, int(api_id), api_hash)

    week_stats = WeekStats(client)

    with client:
        client.loop.run_until_complete(week_stats.get_channel())
        all_data = client.loop.run_until_complete(week_stats.get_all_data())
        message = week_stats.stats_template(all_data)
        client.loop.run_until_complete(week_stats.send_post(message))
