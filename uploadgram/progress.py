#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
#  Copyright (C) 2021 The Authors
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

""" progress helper optimized for speed """


import math
import time
from asyncio import sleep
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from .humanbytes import humanbytes
from .time_formatter import time_formatter

# Cache to avoid frequent UI updates which slow down the upload
PROGRESS_CACHE = {}

async def progress_for_pyrogram(
    current: int,
    total: int,
    message: Message,
    start_time: float,
    pbar: bool,
    ud_type: str,
):
    now = time.time()
    diff = now - start_time
    
    # Update local tqdm progress bar if available
    if pbar is not None:
        # pbar.update is incremental in tqdm, but Pyrogram provides absolute current
        # We handle this by tracking the last seen current in the cache if needed,
        # but usually pbar.n = current is simpler for absolute updates.
        pbar.n = current
        pbar.refresh()
        if current == total:
            pbar.set_description("uploaded")

    # Update Telegram message progress
    # We only update every 5 seconds to avoid FloodWait and speed up the upload process
    message_id = f"{message.chat.id}_{message.id}"
    last_update_time = PROGRESS_CACHE.get(message_id, 0)
    
    if now - last_update_time > 5.0 or current == total:
        PROGRESS_CACHE[message_id] = now
        
        try:
            percentage = (current * 100 / total) if total > 0 else 0
            elapsed_time = round(diff)
            if elapsed_time <= 0:
                return
                
            speed = current / elapsed_time
            time_to_completion = round((total - current) / speed) if speed > 0 else 0
            estimated_total_time = elapsed_time + time_to_completion

            elapsed_time_str = time_formatter(elapsed_time)
            estimated_total_time_str = time_formatter(estimated_total_time)

            progress_bar = "[{0}{1}] \nP: {2}%\n".format(
                "".join(["█" for _ in range(math.floor(percentage / 5))]),
                "".join(["░" for _ in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )

            tmp = progress_bar + "{0} of {1}\nSpeed: {2}/s\nETA: {3}\n".format(
                humanbytes(current),
                humanbytes(total),
                humanbytes(speed),
                estimated_total_time_str if estimated_total_time_str != "" else "0 seconds",
            )
            
            await message.edit_text(text=f"{ud_type}\n {tmp}")
        except FloodWait as e:
            await sleep(e.value)
        except Exception:
            pass
