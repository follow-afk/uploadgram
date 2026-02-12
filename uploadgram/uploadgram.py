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


from pyrogram import Client, __version__, enums
from .get_config import get_config


class Uploadgram(Client):
    """ modded client optimized for speed and compatibility with Pyrogram v2.x """

    def __init__(self):
        # Optimized for high-speed uploads in Pyrogram v2.x
        # Parameters updated for compatibility with latest Pyrogram
        super().__init__(
            name="UploadGram",
            api_id=int(get_config("UG_TG_APP_ID")),
            api_hash=get_config("UG_TG_API_HASH"),
            parse_mode=enums.ParseMode.HTML,
            sleep_threshold=int(get_config("UG_TG_ST", 60)),
            workers=int(get_config("UG_TG_WS", 24)),
            max_concurrent_transmissions=int(get_config("UG_TG_MCTS", 10)),
            no_updates=True,
            device_model="Samsung SM-G998B",
            app_version="10.11.2 (4665)",
            system_version="SDK 31",
            lang_code="en"
        )

    async def start(self):
        await super().start()
        print(
            f"{self.me.first_name} based on Pyrogram v{__version__} started."
        )

    async def stop(self, *args):
        usr_bot_me = self.me
        await super().stop()
        print(f"{usr_bot_me.first_name} stopped. Bye.")
