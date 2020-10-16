from datetime import datetime


class ITransfer:
    start_stop_name: str
    end_stop_name: str
    start_datetime: datetime
    end_datetime: datetime
