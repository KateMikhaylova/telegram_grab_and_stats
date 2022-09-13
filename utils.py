from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone
from PyQt5 import QtWidgets


def read_from_file(path: str):
    """
    Reads from file.
    :param path: file path
    :return: file text
    """
    with open(path, 'r', encoding='UTF-8') as file:
        text = [text[:-1] for text in file.readlines()]
    return text


def write_to_file(path: str, text: list):
    """
    Writes to file.
    :param path: file path
    :param text: stopwords list
    """
    with open(path, 'w', encoding='UTF-8') as file:
        file.writelines(text)


def add_item_to_box(box: QtWidgets.QListWidget, text_line: QtWidgets.QLineEdit):
    """
    Adds text item to stop_words box
    :param box: stopwords box
    :param text_line: text from line to write
    """
    if text_line.text():
        box.addItem(text_line.text())
        text_line.setText('')


def get_text_from_box(box: QtWidgets.QListWidget):
    """
    :param box: stopwords box
    :return: items list from stopwords box
    """
    return [box.item(index).text() for index in range(box.count())]


def date_range(week: int, month: int, year: int, week_stats: bool, month_stats: bool, year_stats: bool,
               quarter_stats: bool, half_year_stats: bool):
    """
    Sets list of 2 dates [start of searching, now]
    :param week: week number (0 - past week)
    :param month: month number (0 - past month)
    :param year: year number (0 - past year)
    :param week_stats: 'True' if GUI button is set to weekly interval
    :param month_stats: 'True' if GUI button is set to monthly interval
    :param year_stats: 'True' if GUI button is set to annual interval
    :param quarter_stats: 'True' if GUI button is set to quarter interval
    :param half_year_stats: 'True' if GUI button is set to half-year interval
    :return: date interval [start of searching, now]
    """
    date_now = datetime.now(timezone.utc).date()

    if week_stats:                              # counts days until the end of last week, month or year
        days = date_now.weekday() + 1
    elif month_stats:
        days = date_now.day
    elif year_stats or quarter_stats or half_year_stats:
        days = date_now.timetuple().tm_yday

    current_year = (date_now - relativedelta(years=year)).year

    date_end = date_now - relativedelta(days=days + (1 if current_year % 4 == 0 and year_stats else 0),
                                        weeks=week if week_stats else 0,
                                        months=month if month_stats else 0,
                                        years=year if (year_stats
                                                       or quarter_stats
                                                       or half_year_stats)
                                        else 0)
    date_start = date_end - relativedelta(days=-1 + (date_end.day if month_stats
                                                     else date_end.timetuple().tm_yday if (year_stats
                                                                                           or quarter_stats
                                                                                           or half_year_stats)
                                                     else 0),
                                          weeks=1 if week_stats else 0)

    if quarter_stats:
        quarter = 91.5 if current_year % 4 == 0 else 91.25
        if quarter < days <= quarter * 2:
            date_start += relativedelta(years=1)
            date_end += relativedelta(months=-9, years=1)
        elif quarter * 2 < days <= quarter * 3:
            date_start += relativedelta(months=2, years=1)
            date_end += relativedelta(months=-6, years=1)
        elif quarter * 3 < days <= quarter * 4:
            date_start += relativedelta(months=5, years=1)
            date_end += relativedelta(months=-3, years=1)
        else:
            date_start += relativedelta(months=8)
    elif half_year_stats:
        half_year = 183 if current_year % 4 == 0 else 182.5
        if days > half_year:
            date_start += relativedelta(years=1)
            date_end += relativedelta(months=-6, years=1)
        else:
            date_start += relativedelta(months=6)

    return [date_start, date_end]
