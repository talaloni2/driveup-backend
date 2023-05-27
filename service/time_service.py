from datetime import datetime

import pytz


class TimeService:
    # noinspection PyMethodMayBeStatic

    @property
    def timezone(self):
        return pytz.timezone("Asia/Jerusalem")

    def now(self):
        return datetime.now(self.timezone)

    def utcnow(self):
        return datetime.utcnow()
