import warnings

import pytest
from loguru import logger

from vikit.video.building.handlers.videogen_handler import (
    VideoGenHandler,
)
from vikit.video.raw_text_based_video import RawTextBasedVideo


class TestVideoBuildingHandler:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)
        logger.add("log_test_video_building_handlers.txt", rotation="10 MB")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_VideoBuildingHandlerGenerateFomApi(self):
        vid = RawTextBasedVideo(raw_text_prompt="test")
        api_handler = VideoGenHandler(video_gen_prompt_text="test")
        video_built = await api_handler.execute_async(video=vid)
        assert video_built is not None, "Video built should not be None"
        assert (
            api_handler.is_supporting_async_mode()
        ), f"This handler should support async, but it does not: {api_handler}"
