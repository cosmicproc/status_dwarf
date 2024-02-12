import functools
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Optional, Protocol

import sqlalchemy
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from status_dwarf.utils import _

db = SQLAlchemy()
session = db.session


class Status(Enum):
    UP = 1
    DOWN = 2
    SEMI_DOWN = 3
    INSUFFICIENT_DATA = 4
    NO_DATA = 5


class TargetStrategy(Enum):
    HTTP = 1
    ICMP = 2

    DEFAULT = HTTP

    @classmethod
    def str_to_strategy(cls, string) -> Optional["TargetStrategy"]:
        if string.lower() == "http" or string.lower() == "https":
            return cls.HTTP
        elif string.lower() == "ping" or string.lower() == "icmp":
            return cls.ICMP
        return cls.DEFAULT


class UTCDateTime(db.TypeDecorator):  # type: ignore[name-defined]
    impl = db.DateTime(timezone=True)

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=timezone.utc)


class StatusProtocol(Protocol):
    @property
    def status(self) -> Status: ...


class StatusMethodsMixin:
    @property
    def status_color(self: StatusProtocol) -> str:
        status = self.status
        if status == Status.UP:
            return "green"
        elif status == Status.DOWN:
            return "red"
        elif status == Status.SEMI_DOWN:
            return "yellow"
        return "gray"

    @property
    def status_text(self: StatusProtocol) -> str:
        if self.status == Status.UP:
            return _("Operational")
        elif self.status == Status.DOWN:
            return _("Inoperative")
        elif self.status == Status.SEMI_DOWN:
            return _("Mostly Operational")
        elif self.status == Status.INSUFFICIENT_DATA:
            return _("Insufficient Data")
        elif self.status == Status.NO_DATA:
            return _("No Data")
        return _("Unknown")


class TimelineItem(db.Model, StatusMethodsMixin):  # type: ignore[name-defined]
    __tablename__ = "timelineitem_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("target_table.id"),
                                           nullable=True)
    next_item_id: Mapped[int] = mapped_column(ForeignKey("timelineitem_table.id"),
                                              nullable=True)
    datetime_start: Mapped[datetime] = mapped_column(UTCDateTime)
    datetime_end: Mapped[datetime] = mapped_column(UTCDateTime)
    uptime_secs: Mapped[int] = mapped_column(Integer, default=0)
    downtime_secs: Mapped[int] = mapped_column(Integer, default=0)
    previous_item: Mapped["TimelineItem"] = relationship("TimelineItem")

    @property
    def formatted_datetime_start(self) -> str:
        return self.datetime_start.isoformat(timespec="minutes")

    @property
    def formatted_datetime_end(self) -> str:
        return self.datetime_end.isoformat(timespec="minutes")

    @property
    def coverage(self) -> timedelta:
        return self.datetime_end - self.datetime_start

    @property
    def uptime_percentage(self) -> float:
        return (self.uptime_secs / self.coverage.total_seconds()) * 100

    @property
    def downtime_percentage(self) -> float:
        return (self.downtime_secs / self.coverage.total_seconds()) * 100

    @property
    def no_data_percentage(self) -> float:
        return 100 - self.uptime_percentage - self.downtime_percentage

    @property
    def status(self) -> Status:
        if self.downtime_percentage > 10:
            return Status.DOWN
        elif self.downtime_percentage > 1:
            return Status.SEMI_DOWN
        elif self.uptime_percentage > self.no_data_percentage:
            return Status.UP
        elif self.no_data_percentage > 95:
            return Status.NO_DATA
        return Status.INSUFFICIENT_DATA

    @property
    def uptime_info(self) -> Optional[str]:
        if self.uptime_percentage > 1 and self.status != Status.UP:
            return _("Uptime: ") + f"{self.uptime_percentage / 100:.0%}"
        return None

    @property
    def downtime_info(self) -> Optional[str]:
        if self.downtime_percentage > 1:
            return _("Downtime: ") + str(timedelta(seconds=self.downtime_secs))
        return None

    @property
    def no_data_info(self) -> Optional[str]:
        if self.no_data_percentage > 1 and self.status != Status.NO_DATA:
            return _("Missing data: ") + f"{self.no_data_percentage / 100:.0%}"
        return None

    @functools.cached_property
    def uptime_until_item(self) -> int:
        if self.previous_item:
            return self.uptime_secs + self.previous_item.uptime_secs
        return self.uptime_secs

    @functools.cached_property
    def known_coverage_until_item(self) -> int:
        own_known_coverage = self.uptime_secs + self.downtime_secs
        if self.previous_item:
            return (own_known_coverage + self.previous_item.uptime_secs
                    + self.previous_item.downtime_secs)
        return own_known_coverage

    @functools.cached_property
    def average_uptime_until_item(self) -> float:
        self.__dict__.pop("uptime_until_item", None)
        self.__dict__.pop("known_coverage_until_item", None)
        return self.uptime_until_item / self.known_coverage_until_item


class Target(db.Model, StatusMethodsMixin):  # type: ignore[name-defined]
    __tablename__ = "target_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(250))
    head_timeline_item: Mapped[List["TimelineItem"]] = relationship("TimelineItem")
    status: Mapped[Status] = mapped_column(sqlalchemy.Enum(Status),
                                           nullable=True)
    status_update_datetime: Mapped[datetime] = mapped_column(UTCDateTime,
                                                             default=datetime.now(
                                                                 timezone.utc))
    strategy: Mapped[TargetStrategy] = mapped_column(sqlalchemy.Enum(TargetStrategy))

    @property
    def average_uptime(self) -> Optional[str]:
        if not self.head_timeline_item:
            return None
        return f"{self.head_timeline_item[0].average_uptime_until_item:.0%}"

    @property
    def tail_timeline_item(self) -> Optional["TimelineItem"]:
        if not self.head_timeline_item:
            return None
        previous_item = self.head_timeline_item[0]
        while previous_item.previous_item:
            previous_item = previous_item.previous_item
        return previous_item

    @property
    def timeline_items(self) -> List["TimelineItem"]:
        result = []
        previous_item = self.head_timeline_item[0] if len(
            self.head_timeline_item) > 0 else None
        while previous_item:
            result.append(previous_item)
            previous_item = previous_item.previous_item
        return result

    def add_timeline_item(self, datetime_start: datetime,
                          datetime_end: datetime, no_commit=False) -> "TimelineItem":
        new_item = TimelineItem(target_id=self.id,
                                datetime_start=datetime_start,
                                datetime_end=datetime_end)
        session.add(new_item)
        session.flush()
        if self.head_timeline_item:
            self.head_timeline_item[0].next_item_id = new_item.id
            self.head_timeline_item[0].target_id = 0
        else:
            new_item.target_id = self.id

        if not no_commit:
            session.commit()

        return new_item

    def get_display_items(self) -> List["TimelineItem"]:
        tail_item_interval = (
            (self.tail_timeline_item.datetime_end -
             self.tail_timeline_item.datetime_start).total_seconds() / 3600
            if self.tail_timeline_item else None)
        block_count = current_app.config["STATUS_BLOCK_COUNT"]
        block_coverage = tail_item_interval or current_app.config[
            "STATUS_BLOCK_COVERAGE"]
        result = [item for item in self.timeline_items[:block_count] if
                  item.datetime_end < datetime.now(timezone.utc)]

        if result:
            datetime_ref = result[-1].datetime_start
        elif self.head_timeline_item:
            datetime_ref = self.head_timeline_item[0].datetime_start
        else:
            datetime_ref = datetime.now(timezone.utc)
        result += [TimelineItem(datetime_start=datetime_ref - timedelta(
            hours=(i + 1) * block_coverage), datetime_end=datetime_ref - timedelta(
            hours=i * block_coverage), uptime_secs=0, downtime_secs=0) for i in
                   range(block_count - len(result))]
        result.reverse()
        return result

    @classmethod
    def any_target_down(cls) -> bool:
        for target in cls.query.all():
            if target.status == Status.DOWN:
                return True
        return False
