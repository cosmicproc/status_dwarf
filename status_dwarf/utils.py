import json
from datetime import datetime, timedelta
from json import JSONDecodeError
from pathlib import Path

from flask import request, current_app


def div_ceil(num: float, divisor: float) -> int:
    """
    Divide and round up

    Example: div_ceil(3, 2) = 2
    """
    return -int(num // -divisor)


def sub_datetime_rounded(dt1: datetime, dt2: datetime) -> timedelta:
    """
    Subtract two datetime but regard high microsecond values as a second
    """
    result = dt1 - dt2
    if result.microseconds > 900000:
        result += timedelta(seconds=1)
    return result - timedelta(microseconds=result.microseconds)


def strip_protocol(address):
    return address.split("://")[-1]


class Translator:
    def __init__(self):
        self.i18n = {}

    def load_i18n(self) -> None:
        i18n_dir = Path(__file__).resolve().parent / "i18n"
        with open(i18n_dir / "i18n.json", "rb") as file:
            try:
                self.i18n = json.load(file)
            except JSONDecodeError:
                self.i18n = {}

    def get_lang(self) -> str:
        return request.accept_languages.best_match(list(self.i18n.keys())) or "en"

    def __call__(self, text: str) -> str:
        if not current_app.config["TRANSLATIONS_ENABLED"]:
            return text

        if not self.i18n:
            self.load_i18n()

        lang = self.get_lang()
        return self.i18n.get(lang, {}).get(text, text)


_ = Translator()
