from datetime import datetime

import pytz


class TimeService:
    # noinspection PyMethodMayBeStatic
    def now(self):
        return datetime.now(pytz.timezone("Asia/Jerusalem"))

    def utcnow(self):
        return datetime.utcnow()
