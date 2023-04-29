from datetime import date, datetime


def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()
