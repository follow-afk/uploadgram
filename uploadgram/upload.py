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


import os
import time
import asyncio
from tqdm import tqdm
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import Message
from .config import TG_AUDIO_TYPES, TG_VIDEO_TYPES
from .progress import progress_for_pyrogram
from .take_screen_shot import take_screen_shot


async def upload_dir_contents(
    tg_max_file_size: int,
    dir_path: str,
    delete_on_success: bool,
    thumbnail_file: str,
    force_document: bool,
    custom_caption: str,
    bot_sent_message: Message,
    console_progress: bool,
):
    if not os.path.exists(dir_path):
        return False

    if not os.path.isdir(dir_path):
        files_to_upload = [dir_path]
    else:
        files_to_upload = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                files_to_upload.append(os.path.join(root, file))
    
    files_to_upload.sort()
    
    for current_file in files_to_upload:
        if os.path.getsize(current_file) <= tg_max_file_size:
            response_message = await upload_single_file(
                current_file,
                thumbnail_file,
                force_document,
                custom_caption,
                bot_sent_message,
                console_progress,
            )
            if isinstance(response_message, Message) and delete_on_success:
                try:
                    os.remove(current_file)
                except OSError:
                    pass

        # Reduced sleep for faster batch processing, Telegram has its own flood control
        await asyncio.sleep(1)


async def upload_single_file(
    file_path: str,
    thumbnail_file: str,
    force_document: bool,
    custom_caption: str,
    bot_sent_message: Message,
    console_progress: bool,
):
    if not os.path.exists(file_path):
        return False
        
    start_time = time.time()
    file_name = os.path.basename(file_path)
    caption = custom_caption if custom_caption else f"<code>{file_name}</code>"

    pbar = None
    if console_progress:
        pbar = tqdm(
            total=os.path.getsize(file_path),
            unit="B",
            unit_scale=True,
            desc=f"Uploading {file_name[:20]}",
            colour="green",
            unit_divisor=1024,
            miniters=1,
        )

    file_ext = file_name.split('.')[-1].upper() if '.' in file_name else ""

    if not force_document:
        if file_ext in TG_VIDEO_TYPES:
            return await upload_as_video(
                bot_sent_message,
                file_path,
                caption,
                thumbnail_file,
                start_time,
                pbar,
            )
        elif file_ext in TG_AUDIO_TYPES:
            return await upload_as_audio(
                bot_sent_message,
                file_path,
                caption,
                thumbnail_file,
                start_time,
                pbar,
            )

    return await upload_as_document(
        bot_sent_message,
        file_path,
        caption,
        thumbnail_file,
        start_time,
        pbar,
    )


async def upload_as_document(
    message: Message,
    file_path: str,
    caption: str,
    thumbnail_file: str,
    start_time: float,
    pbar: tqdm,
):
    return await message.reply_document(
        document=file_path,
        quote=True,
        caption=caption,
        thumb=thumbnail_file,
        progress=progress_for_pyrogram,
        progress_args=(
            message,
            start_time,
            pbar,
            f"Uploading <b>{os.path.basename(file_path)}</b> as DOCUMENT"
        ),
    )


async def upload_as_video(
    message: Message,
    file_path: str,
    caption: str,
    thumbnail_file: str,
    start_time: float,
    pbar: tqdm,
):
    duration = 0
    width = 0
    height = 0
    thumb_nail_img = None
    
    try:
        parser = createParser(file_path)
        if parser:
            with parser:
                metadata = extractMetadata(parser)
                if metadata and metadata.has("duration"):
                    duration = int(metadata.get("duration").seconds)
            
            if not thumbnail_file:
                thumb_nail_img = await take_screen_shot(
                    file_path,
                    os.path.dirname(os.path.abspath(file_path)),
                    (duration / 2),
                )
    except Exception:
        pass

    if thumb_nail_img:
        try:
            thumb_parser = createParser(thumb_nail_img)
            if thumb_parser:
                with thumb_parser:
                    thumb_metadata = extractMetadata(thumb_parser)
                    if thumb_metadata:
                        width = thumb_metadata.get("width") if thumb_metadata.has("width") else 0
                        height = thumb_metadata.get("height") if thumb_metadata.has("height") else 0
        except Exception:
            pass

    try:
        return await message.reply_video(
            video=file_path,
            quote=True,
            thumb=thumbnail_file if thumbnail_file else thumb_nail_img,
            duration=duration,
            width=width,
            height=height,
            supports_streaming=True,
            caption=caption,
            progress=progress_for_pyrogram,
            progress_args=(
                message,
                start_time,
                pbar,
                f"Uploading <b>{os.path.basename(file_path)}</b> as VIDEO"
            ),
        )
    finally:
        if thumb_nail_img and os.path.exists(thumb_nail_img):
            try:
                os.remove(thumb_nail_img)
            except OSError:
                pass


async def upload_as_audio(
    message: Message,
    file_path: str,
    caption: str,
    thumbnail_file: str,
    start_time: float,
    pbar: tqdm,
):
    duration = 0
    title = None
    performer = None
    
    try:
        parser = createParser(file_path)
        if parser:
            with parser:
                metadata = extractMetadata(parser)
                if metadata:
                    if metadata.has("duration"):
                        duration = int(metadata.get("duration").seconds)
                    if metadata.has("title"):
                        title = metadata.get("title")
                    if metadata.has("artist"):
                        performer = metadata.get("artist")
                    elif metadata.has("author"):
                        performer = metadata.get("author")
                    elif metadata.has("album"):
                        performer = metadata.get("album")
    except Exception:
        pass

    return await message.reply_audio(
        audio=file_path,
        quote=True,
        caption=caption,
        duration=duration,
        performer=performer,
        title=title,
        thumb=thumbnail_file,
        progress=progress_for_pyrogram,
        progress_args=(
            message,
            start_time,
            pbar,
            f"Uploading <b>{os.path.basename(file_path)}</b> as AUDIO"
        ),
    )
