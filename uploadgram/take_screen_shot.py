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
from .config import TG_VIDEO_TYPES
from .run_shell_command import run_command


async def take_screen_shot(
    video_file: str,
    output_directory: str,
    timestamp: float
):
    """Generates a thumbnail from a video file at a specific timestamp."""
    
    # Use a unique filename to avoid collisions
    output_file_name = os.path.join(
        output_directory,
        f"thumb_{int(time.time())}.jpg"
    )
    
    file_ext = video_file.split('.')[-1].upper() if '.' in video_file else ""
    
    if file_ext in TG_VIDEO_TYPES:
        # Optimization: -ss before -i is much faster as it uses seek
        ffmpeg_command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-ss", str(timestamp),
            "-i", video_file,
            "-vframes", "1",
            "-q:v", "2",  # High quality
            output_file_name
        ]
        
        await run_command(ffmpeg_command)
        
    if os.path.exists(output_file_name):
        return output_file_name
    return None
