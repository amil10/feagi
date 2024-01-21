# Copyright 2016-2024 The FEAGI Authors. All Rights Reserved.
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


import os
from fastapi import APIRouter

from ...schemas import *
from ...commons import *


router = APIRouter()


# #########  Robot   ###########
# ##############################
@router.post("/parameters")
async def robot_controller_tunner(message: RobotController):
    """
    Enables changes against various Burst Engine parameters.
    """

    message = message.dict()
    message = {'robot_controller': message}
    api_queue.put(item=message)


@router.post("/model")
async def robot_model_modification(message: RobotModel):
    """
    Enables changes against various Burst Engine parameters.
    """

    message = message.dict()
    message = {'robot_model': message}
    api_queue.put(item=message)


@router.get("/gazebo/files")
async def gazebo_robot_default_files():

    default_robots_path = "./evo/defaults/robot/"
    default_robots = os.listdir(default_robots_path)
    return {"robots": default_robots}
