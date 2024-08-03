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

import warnings

import pytest

import tests.testing_tools as tools
from vikit.common.context_managers import WorkingFolderContext
from vikit.video.building.build_order import \
    get_lazy_dependency_chain_build_order
from vikit.video.composite_video import CompositeVideo
from vikit.video.prompt_based_video import PromptBasedVideo
from vikit.video.raw_text_based_video import RawTextBasedVideo
from vikit.video.transition import Transition
from vikit.video.video_build_settings import VideoBuildSettings


class TestVideoBuildingStrategies:

    def setUp(self) -> None:
        warnings.simplefilter("ignore", category=ResourceWarning)
        warnings.simplefilter("ignore", category=UserWarning)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_video_tree_default_strategy_single_composite(self):
        """
        Test that the video tree is correctly generated, with right order,
        using a simple video tree
        """
        build_settings = VideoBuildSettings(test_mode=True)
        composite = CompositeVideo()
        rtbv = RawTextBasedVideo("test")
        composite.append_video(rtbv)

        # Here we are testing the ordered list of video to be build
        # conforms to the expected order
        video_build_order = get_lazy_dependency_chain_build_order(
            video_build_order=[],
            video_tree=[composite],
            build_settings=build_settings,
            already_added=set(),
        )

        assert video_build_order is not None
        # here we check the leaf has been generated first, then the root composite
        assert (
            len(video_build_order) == 2
        ), f"Should have 2 videos, instead we had {len(video_build_order)}"

        assert video_build_order[0].id == rtbv.id
        assert video_build_order[1].id == composite.id
        assert isinstance(video_build_order[0], RawTextBasedVideo)
        assert isinstance(video_build_order[1], CompositeVideo)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_video_tree_default_strategy_mixed_composites(self):
        """
        Test that the video tree is correctly generated, with right order,
        using a  video tree including root and child composite videos

        Using Lazy Dependency chain
        """
        build_settings = VideoBuildSettings(test_mode=True)
        build_settings._ml_models_gateway = build_settings.get_ml_models_gateway()
        pbv = PromptBasedVideo(
            tools.test_prompt_library["moss_stones-train_boy"]
        )  # 4 subtitles -> 4 composite videos of 3 vids each
        await pbv.compose(build_settings=build_settings)

        assert pbv is not None, "Inner composite should be generated"

        # Here we are testing the ordered list of video to be build
        # conforms to the expected order
        video_build_order = get_lazy_dependency_chain_build_order(
            video_build_order=[],
            video_tree=[pbv],
            build_settings=build_settings,
            already_added=set(),
        )
        assert (
            len(pbv.video_list) == 4
        ), f"Should have 4 subtitles for trainboy prompt, instead we had {len(pbv.video_list)}"
        assert video_build_order is not None

        # In this test, we have 4 subtitles, so with a promptbasedvideo we should have 4 prompts * 2 rawtextbasedvideo
        #  + 4 transitions + 4 child composite videos + one parent root composite video
        assert (
            len(video_build_order) == 17
        ), f"Should have 17 videos, instead we had {len(video_build_order)}"

        # Check we have the right order: for the first subtitle, we should have
        #  rawtextbasedvideo ->  second rawtextbasedvideo ->  transition
        # -> parent/owner composite video
        # -> second subtitle rawtextbasedvideo -> etc...
        assert video_build_order[0].id == pbv.video_list[0].video_list[0].id
        assert video_build_order[1].id == pbv.video_list[0].video_list[2].id
        assert video_build_order[2].id == pbv.video_list[0].video_list[1].id

        assert isinstance(video_build_order[0], RawTextBasedVideo)
        assert isinstance(video_build_order[1], RawTextBasedVideo)
        assert isinstance(video_build_order[2], Transition)

        # the second composite for the first subtitle
        assert video_build_order[3].id == pbv.video_list[0].id  # first child composite
        assert isinstance(video_build_order[3], CompositeVideo)

        assert (
            video_build_order[4].id == pbv.video_list[1].video_list[0].id
        ), f"Second subtitle first rawtextbasedvideo should be next, instead we had {video_build_order[4].id}"
        assert video_build_order[5].id == pbv.video_list[1].video_list[2].id
        assert video_build_order[6].id == pbv.video_list[1].video_list[1].id

        assert isinstance(
            video_build_order[4], RawTextBasedVideo
        ), f"Instead we had {type(video_build_order[5])}"
        assert isinstance(
            video_build_order[5], RawTextBasedVideo
        ), f"Instead we had {type(video_build_order[6])}"
        assert isinstance(
            video_build_order[6], Transition
        ), f"Instead we had {type(video_build_order[7])}"

        assert isinstance(video_build_order[7], CompositeVideo)
        assert isinstance(video_build_order[16], CompositeVideo)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_lazy_dependency_chain_build_order(self):
        # Create a sample video tree
        video1 = RawTextBasedVideo("a")
        video2 = RawTextBasedVideo("b")
        video3 = RawTextBasedVideo("c")
        video4 = RawTextBasedVideo("d")
        video5 = RawTextBasedVideo("e")

        # Set video dependencies
        video1.video_dependencies = [video2, video3]
        video3.video_dependencies = [video4, video5]

        # Create a sample build settings
        build_settings = VideoBuildSettings()

        # Call the function
        build_order = get_lazy_dependency_chain_build_order(
            video_tree=[video1],
            build_settings=build_settings,
            already_added=set(),
            video_build_order=[],
        )

        # Assert the build order
        assert build_order == [video2, video4, video5, video3, video1]