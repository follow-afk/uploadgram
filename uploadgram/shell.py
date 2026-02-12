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
import asyncio
import argparse
from typing import Union
from .uploadgram import Uploadgram
from .upload import upload_dir_contents


async def upload(
    client: Uploadgram,
    files: str,
    to: Union[str, int],
    delete_on_success: bool = False,
    thumbnail_file: str = None,
    force_document: bool = False,
    custom_caption: str = None,
    console_progress: bool = False,
    message_thread_id: int = None,
):
    # send a message to verify write permission and act as status indicator
    status_message = await client.send_message(
        chat_id=to,
        text="`Initializing upload...`",
        message_thread_id=message_thread_id
    )

    # Max file size: 4GB for premium, 2GB for others
    # Check if client.me exists (it should after start())
    is_premium = getattr(client.me, "is_premium", False)
    tg_max_file_size = 4194304000 if is_premium else 2097152000

    await upload_dir_contents(
        tg_max_file_size,
        files,
        delete_on_success,
        thumbnail_file,
        force_document,
        custom_caption,
        status_message,
        console_progress
    )
    
    try:
        await status_message.delete()
    except Exception:
        pass


async def moin(args):
    client = Uploadgram()
    await client.start()

    try:
        dest_chat = args.chat_id
        if not dest_chat:
            dest_chat = input("Enter chat_id to send the files to: ")
        
        if dest_chat.isnumeric() or dest_chat.startswith("-100"):
            dest_chat = int(dest_chat)
        
        # Validate chat
        chat = await client.get_chat(dest_chat)
        dest_chat = chat.id

        dir_path = args.dir_path
        if not dir_path:
            dir_path = input("Enter path to upload to Telegram: ")
        
        while not os.path.exists(dir_path):
            print(f"Path does not exist. Current directory contents: {os.listdir('.')}")
            dir_path = input("Please enter valid path to upload: ")
        
        dir_path = os.path.abspath(dir_path)

        await upload(
            client,
            dir_path,
            dest_chat,
            delete_on_success=args.delete_on_success,
            thumbnail_file=args.t,
            force_document=args.fd,
            custom_caption=args.caption,
            console_progress=args.progress,
            message_thread_id=args.topic
        )
    finally:
        await client.stop()


def main():
    parser = argparse.ArgumentParser(
        prog="UploadGram",
        description="Upload to Telegram from the Terminal (Optimized for v2.x)"
    )
    parser.add_argument(
        "chat_id",
        type=str,
        help="Target chat ID or username",
    )
    parser.add_argument(
        "dir_path",
        type=str,
        help="Path to file or directory to upload",
    )
    parser.add_argument(
        "--delete_on_success",
        action="store_true",
        help="Delete file after successful upload",
    )
    parser.add_argument(
        "--fd",
        action="store_true",
        help="Force uploading as documents",
    )
    parser.add_argument(
        "--t",
        type=str,
        help="Path to custom thumbnail",
        default=None,
    )
    parser.add_argument(
        "--caption",
        type=str,
        help="Custom caption for the files",
        default=None,
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show upload progress in terminal",
    )
    parser.add_argument(
        "--topic",
        type=int,
        help="Forum topic ID",
        default=None,
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(moin(args))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
