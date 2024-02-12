import asyncio
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from flask import current_app
from flask_apscheduler import APScheduler  # type: ignore[import-untyped]

from status_dwarf.models import session, Target, Status, TargetStrategy
from status_dwarf.utils import div_ceil, sub_datetime_rounded, strip_protocol

scheduler = APScheduler()


async def icmp_heartbeat(address: str) -> bool:
    address = strip_protocol(address)
    proc = await asyncio.create_subprocess_shell(f'ping -c 1 -t 1 "{address}"',
                                                 stdout=subprocess.DEVNULL)
    await proc.communicate()
    return proc.returncode == 0


async def http_heartbeat(address: str, user_agent: Optional[str] = None) -> bool:
    custom_headers = {"User-Agent": user_agent} if user_agent else None
    async with httpx.AsyncClient() as client:
        try:
            response = await client.head(address, headers=custom_headers)
            return not response.is_error
        except httpx.TransportError:
            return False


async def check_target(target: Target) -> None:
    with scheduler.app.app_context():
        interval = current_app.config["INTERVAL_SECONDS"]
        item_coverage = current_app.config["STATUS_BLOCK_COVERAGE"]
    interval_start = datetime.now(timezone.utc) - timedelta(seconds=interval / 2)
    interval_end = datetime.now(timezone.utc) + timedelta(seconds=interval / 2)
    matching_timeline_items = [i for i in target.timeline_items if
                               i.datetime_start < interval_end and
                               i.datetime_end > interval_start]
    if not matching_timeline_items:
        alignment = interval_start.replace(day=interval_start.day + 1, hour=0, minute=0,
                                           second=0, microsecond=0)
        datetime_start = alignment - timedelta(
            hours=(alignment - interval_start).total_seconds() // (
                item_coverage * 3600) + 1) * item_coverage
        if target.head_timeline_item:
            diff = (((interval_start - target.head_timeline_item[
                0].datetime_end).total_seconds() // 3600)
                    % item_coverage)
            datetime_start = interval_start - timedelta(hours=diff)

        new_item = target.add_timeline_item(datetime_start, datetime_start + timedelta(
            hours=item_coverage), no_commit=True)
        matching_timeline_items = [new_item]
    else:
        max_datetime_end = max(matching_timeline_items,
                               key=lambda x: x.datetime_end).datetime_end
        if max_datetime_end < interval_end:
            amount_to_add = div_ceil(
                (interval_end - max_datetime_end).total_seconds() // 3600,
                item_coverage)
            for i in range(amount_to_add):
                new_item = target.add_timeline_item(max_datetime_end + timedelta(
                    hours=item_coverage * i), max_datetime_end + timedelta(
                    hours=item_coverage * (i + 1)), no_commit=True)
                matching_timeline_items.append(new_item)
    with scheduler.app.app_context():
        custom_user_agent = current_app.config["CUSTOM_USER_AGENT"]
    is_up = False
    if target.strategy == TargetStrategy.HTTP:
        is_up = await http_heartbeat(target.address, custom_user_agent)
    elif target.strategy == TargetStrategy.ICMP:
        is_up = await icmp_heartbeat(target.address)
    old_status = target.status
    target.status = Status.UP if is_up else Status.DOWN
    if old_status != target.status:
        target.status_update_datetime = datetime.now(timezone.utc)
    for item in matching_timeline_items:
        coverage = max(sub_datetime_rounded(min(item.datetime_end, interval_end),
                                            max(item.datetime_start,
                                                interval_start)).total_seconds(), 0)
        if is_up:
            item.uptime_secs += int(coverage)
        else:
            item.downtime_secs += int(coverage)
    session.commit()


async def check_status() -> None:
    with scheduler.app.app_context():
        await asyncio.gather(*(
            check_target(target) for target in
            session.query(Target).all()))


def monitor_task() -> None:
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.run(check_status())
