from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from telethon.tl.types import InputPeerEmpty, Channel
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest


class ChatData:
    def __init__(self, client: object):
        """
        :param client: <class 'telethon.client.telegramclient.TelegramClient'>
        """
        self.client = client
        self.channels = None  # list of channels
        self.tg_chat = None  # selected channel
        self.date_range = None  # date interval [date_start, date_end]
        self.progress_bar = None  # GUI progress bar
        self.progress_bar_range = None  # number of days between tow dates date_start and date_end

    async def get_channel(self):
        """
        Gets list of all channels and updates the attribute self.channels
        """
        channels = []
        result = await self.client(GetDialogsRequest(offset_date=None,
                                                     offset_id=0,
                                                     offset_peer=InputPeerEmpty(),
                                                     limit=100,
                                                     hash=0
                                                     ))

        for channel in result.chats:
            if type(channel) == Channel:
                channels.append(channel)

        channels.sort(key=lambda c: c.title.lower())
        self.channels = channels

    async def get_all_data(self) -> list:
        """
        Gets all data from the chat
        :return: list of all messages (objects)
        """
        self.progress_bar_range = (self.date_range[1] - self.date_range[0]).days
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, self.progress_bar_range)

        broadcast_channel = self.tg_chat.broadcast

        offset_msg = 0
        limit_msg = 100
        date_offset = self.date_range[1] + timedelta(days=1)

        previous_date = self.date_range[1]
        progress_bar_value = 0

        all_messages = []

        while True:
            history = await self.client(GetHistoryRequest(peer=self.tg_chat,
                                                          offset_id=offset_msg,
                                                          offset_date=date_offset,
                                                          add_offset=0,
                                                          limit=limit_msg,
                                                          max_id=0,
                                                          min_id=0,
                                                          hash=0
                                                          ))

            if not history.messages:
                return all_messages
            messages = history.messages

            for message in messages:
                if message.date.date() >= self.date_range[0]:
                    if previous_date.day != message.date.date().day:
                        progress_bar_value += (previous_date - message.date.date()).days
                        self.progress_bar.setValue(progress_bar_value - 1)
                        previous_date = message.date.date()

                    all_messages.append(message)
                    if broadcast_channel and message.replies is not None and message.replies.replies:
                        all_messages.extend(await self.get_comments_from_post(message.id))
                else:
                    return all_messages

            offset_msg = messages[-1].id

    async def get_comments_from_post(self, post_id: int) -> list:
        """
        Gets all comments from the particular channel post
        :param post_id: channel post id
        :return: list of comments from post
        """
        comments_list = []
        async for message in self.client.iter_messages(self.tg_chat,
                                                       reply_to=post_id):
            comments_list.append(message)
        return comments_list

    async def send_post(self, text: str, tg_chat: str = 'me'):
        """
        Sends post to telegram chat
        :param text: text to send
        :param tg_chat: name of telegram chat where the message will be sent
        """
        await self.client.send_message(tg_chat, text, link_preview=False)


def date_range(week: int, month: int, year: int, week_stats: bool, month_stats: bool, year_stats: bool):
    """
    Sets list of 2 dates [start of searching, now]
    :param week: week number (0 - past week)
    :param month: month number (0 - past month)
    :param year: year number (0 - past year)
    :param week_stats: 'True' if GUI button is set to weekly interval
    :param month_stats: 'True' if GUI button is set to monthly interval
    :param year_stats: 'True' if GUI button is set to annual interval
    :return: date interval [start of searching, now]
    """
    date_now = datetime.now(timezone.utc).date()

    if week_stats:                              # counts days until the end of last week, month or year
        days = date_now.weekday() + 1
    elif month_stats:
        days = date_now.day
    elif year_stats:
        days = date_now.timetuple().tm_yday

    current_year = (date_now - relativedelta(years=year)).year

    date_end = date_now - relativedelta(days=days + (1 if current_year % 4 == 0 and year_stats else 0),
                                        weeks=week if week_stats else 0,
                                        months=month if month_stats else 0,
                                        years=year if year_stats else 0)
    date_start = date_end - relativedelta(days=-1 + (date_end.day if month_stats
                                                     else date_end.timetuple().tm_yday if year_stats
                                                     else 0),
                                          weeks=1 if week_stats else 0)

    return [date_start, date_end]


if __name__ == '__main__':
    print(date_range(3, 5, 3, False, False, True))
