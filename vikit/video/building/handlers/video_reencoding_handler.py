# Copyright 2024 Vikit.ai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from loguru import logger

from vikit.common.handler import Handler
from vikit.wrappers.ffmpeg_wrapper import reencode_video


class VideoReencodingHandler(Handler):

    async def execute_async(self, video):
        """
        Process the video to reencode and normalize binaries, i.e. make it so the
        different video composing a composite have the same format

        Args:
            args: The arguments: video, build_settings

        Returns:
            CompositeVideo: The composite video

        """
        logger.info(f"about to reencode video: {video.id}, {video.media_url}")
        if not video.media_url:
            raise ValueError(f"Video {video.id} has no media url")

        logger.debug(f"Video video.media_url : {video.media_url}")

        # Special case here: the video used for testing should always be reencoded as coming from hetegenous sources
        if video.build_settings.test_mode:
            video._needs_video_reencoding = True

        if video._needs_video_reencoding:
            video.metadata.is_reencoded = True
            video.media_url = await reencode_video(
                video_url=video.media_url,
                target_video_name=video.get_file_name_by_state(
                    build_settings=video.build_settings
                ),
            )
            logger.trace(f"Video reencoded: {video.id}, {video.media_url}")
        else:
            logger.warning(
                f"Video {video.id} does not need reencoding, handler should not have been called"
            )

        return video
