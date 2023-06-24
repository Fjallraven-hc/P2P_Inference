from enum import IntEnum
from typing import Any, Dict, List
import requests
from abc import ABC, abstractmethod
import socket
from fastapi import WebSocket

BufferSize = 4096

class PackageType(IntEnum):
    Login = 0               # Server login request

    Verification = 1        # Scheduler return verification

    ServerState = 2

    Request = 3             # Request size <= Buffer size
    RequestHead = 4
    # RequestPayload = 5

    Response = 5            # Response size <= Buffer size
    ResponseHead = 6
    # ResponsePayload = 8

    PulseCheck = 7          # check the pulse.

class ModelServer:
    def __init__(self,
                 model: str,
                 wsoc: WebSocket = None,
                 info: Dict = None) -> None:
        self.model = model
        self.wsoc = wsoc
        self.info = info

def server_register(username: str, password: str, email: str, url: str):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = 'username={}&password={}&re_password={}&email={}'.format(username, password, password, email)
    response = requests.post(url, headers=headers, data=data)
    return response


def get_token(username: str, password: str, url: str):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'username': username,
        'password': password,
    }

    response = requests.post(url, headers=headers, data=data)
    # 如果用户名不存在，这里‘authorization'字段不存在，
    return response.headers['authorization']

model_list = [
    "Stable Diffution v1.4"
]

model_server_list:Dict[str, List[ModelServer]] = {
    "Stable Diffution v1.4": []
}

class RemoteFunction(ABC):
    '''
        Base class of all gradio remote function in AntGrid.
    '''


    def __init__(self, username: str = None,
                 model: str = None,
                 soc: socket.socket = None) -> None:
        self.username = username
        self.model = model
        self.soc = soc

    @abstractmethod
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return None


__all__ = ["PackageType", "ModelServer","server_register", "get_token", "model_list"]
