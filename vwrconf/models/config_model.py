# vwrconf/models/config_model.py

from typing import List, Optional, Literal
from pydantic import BaseModel
import copy

class Defaults(BaseModel):
    ssh_user: Optional[str] = None
    port: Optional[int] = 22
    method: Optional[Literal["ssh", "agent"]] = "ssh"
    readonly: bool = False


class Client(BaseModel):
    id: str
    host: str
    label: str
    readonly: bool = False
    tags: Optional[List[str]] = []
    port: Optional[int] = None
    method: Optional[Literal["ssh", "agent"]] = "ssh"
    notes: Optional[str] = None
    ssh_user: Optional[str] = None


class Config(BaseModel):
    defaults: Defaults = Defaults()
    clients: List[Client]

    def copy_with_clients(self, clients):
        new_config = copy.copy(self)
        new_config.clients = clients
        return new_config

