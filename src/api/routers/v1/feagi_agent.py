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


from fastapi import APIRouter, HTTPException, Request

from ....inf import runtime_data
from ....inf.messenger import Sub

router = APIRouter()


# ######  Peripheral Nervous System Endpoints #########
# #####################################################

def assign_available_port():
    ports_used = []
    port_ranges = (40001, 40050)
    for agent_id, agent_info in runtime_data.agent_registry.items():
        print(agent_id, agent_info, agent_info['agent_type'], type(agent_info['agent_type']))
        if agent_info['agent_type'] != 'monitor':
            ports_used.append(agent_info['agent_data_port'])
    print("ports_used", ports_used)
    for port in range(port_ranges[0], port_ranges[1]):
        if port not in ports_used:
            return port
    return None


@router.get("/list")
async def agent_list():
    agents = set(runtime_data.agent_registry.keys())
    if agents:
        return agents
    else:
        return {}


@router.get("/properties")
async def agent_properties(agent_id: str):
    print("agent_id", agent_id)
    print("agent_registry", runtime_data.agent_registry)
    agent_info = {}
    if agent_id in runtime_data.agent_registry:
        agent_info["agent_type"] = runtime_data.agent_registry[agent_id]["agent_type"]
        agent_info["agent_ip"] = runtime_data.agent_registry[agent_id]["agent_ip"]
        agent_info["agent_data_port"] = runtime_data.agent_registry[agent_id]["agent_data_port"]
        agent_info["agent_router_address"] = runtime_data.agent_registry[agent_id]["agent_router_address"]
        agent_info["agent_version"] = runtime_data.agent_registry[agent_id]["agent_version"]
        agent_info["controller_version"] = runtime_data.agent_registry[agent_id]["controller_version"]
        return agent_info
    else:
        raise HTTPException(status_code=404, detail="Requested agent not found!")


@router.post("/register")
async def agent_registration(request: Request, agent_type: str, agent_id: str, agent_data_port: int,
                             agent_version: str, controller_version: str):

    if agent_id in runtime_data.agent_registry:
        agent_info = runtime_data.agent_registry[agent_id]
    else:
        agent_info = dict()
        agent_info["agent_id"] = agent_id
        agent_info["agent_type"] = agent_type
        # runtime_data.agent_registry[agent_id]["agent_ip"] = agent_ip
        agent_info["agent_ip"] = request.client.host
        if agent_type == 'monitor':
            agent_router_address = f"tcp://{request.client.host}:{agent_data_port}"
            agent_info["listener"] = Sub(address=agent_router_address, bind=False)
            print("Publication of brain activity turned on!")
            runtime_data.brain_activity_pub = True
        else:
            agent_data_port = assign_available_port()
            agent_router_address = f"tcp://*:{agent_data_port}"
            agent_info["listener"] = Sub(address=agent_router_address, bind=True)

        agent_info["agent_data_port"] = agent_data_port
        agent_info["agent_router_address"] = agent_router_address
        agent_info["agent_version"] = agent_version
        agent_info["controller_version"] = controller_version

    print(f"AGENT Details -- {agent_info}")
    runtime_data.agent_registry[agent_id] = agent_info

    print("New agent has been successfully registered:", runtime_data.agent_registry[agent_id])
    agent_info = runtime_data.agent_registry[agent_id].copy()
    agent_info.pop('listener')
    return agent_info


@router.delete("/deregister")
async def agent_removal(agent_id: str):

    if agent_id in runtime_data.agent_registry:
        agent_info = runtime_data.agent_registry.pop(agent_id)
        agent_info['listener'].terminate()
    else:
        raise HTTPException(status_code=404, detail="Requested agent not found!")
