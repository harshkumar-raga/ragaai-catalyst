from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import uuid

@dataclass
class OSInfo:
    name: str
    version: str
    platform: str
    kernel_version: str

@dataclass
class EnvironmentInfo:
    name: str
    version: str
    packages: List[str]
    env_path: str
    command_to_run: str

@dataclass
class SystemInfo:
    id: str
    os: OSInfo
    environment: EnvironmentInfo
    source_code: str

@dataclass
class ResourceInfo:
    name: str
    cores: int
    threads: int

@dataclass
class CPUResource:
    info: ResourceInfo
    interval: str
    values: List[float]

@dataclass
class MemoryInfo:
    total: float
    free: float

@dataclass
class MemoryResource:
    info: MemoryInfo
    interval: str
    values: List[float]

@dataclass
class DiskInfo:
    total: float
    free: float

@dataclass
class DiskResource:
    info: DiskInfo
    interval: str
    read: List[float]
    write: List[float]

@dataclass
class NetworkInfo:
    upload_speed: float
    download_speed: float

@dataclass
class NetworkResource:
    info: NetworkInfo
    interval: str
    uploads: List[float]
    downloads: List[float]

@dataclass
class Resources:
    cpu: CPUResource
    memory: MemoryResource
    disk: DiskResource
    network: NetworkResource

@dataclass
class Metadata:
    cost: Dict[str, Any]
    tokens: Dict[str, Any]
    system_info: SystemInfo
    resources: Resources

@dataclass
class NetworkCall:
    url: str
    method: str
    status_code: int
    response_time: float
    bytes_sent: int
    bytes_received: int
    protocol: str
    connection_id: str
    parent_id: str
    request: Dict[str, Any]
    response: Dict[str, Any]

class Interaction:
    def __init__(self, id, type: str, content: str, timestamp: str):
        self.id = id
        self.type = type
        self.content = content
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "id": self.id,
            "interaction_type": self.type,
            "content": self.content,
            "timestamp": self.timestamp
        }

@dataclass
class Error:
    code: int
    type: str
    message: str
    details: Dict[str, Any]

@dataclass
class LLMParameters:
    temperature: float
    top_p: float
    max_tokens: int

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class Cost:
    prompt_cost: float
    completion_cost: float
    total_cost: float

@dataclass
class LLMInfo:
    model: str
    parameters: LLMParameters
    token_usage: TokenUsage
    cost: Cost

@dataclass
class AgentInfo:
    agent_type: str
    version: str
    capabilities: List[str]

@dataclass
class ToolInfo:
    tool_type: str
    version: str
    memory_used: int

class Component:
    def __init__(self, id: str, hash_id: str, type: str, name: str, start_time: str, end_time: str, parent_id: int, info: Dict[str, Any], data: Dict[str, Any], network_calls: Optional[List[NetworkCall]] = None, error: Optional[Dict[str, Any]] = None, interactions: Optional[List[Union[Interaction, Dict]]] = None):
        self.id = id
        self.hash_id = hash_id
        self.type = type
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.parent_id = parent_id
        self.info = info
        self.data = data
        self.network_calls = network_calls or []
        self.interactions = []
        self.error = error
        if interactions:
            for interaction in interactions:
                if isinstance(interaction, dict):
                    self.interactions.append(
                        Interaction(
                            id=interaction.get("id", str(uuid.uuid4())),
                            type=interaction.get("interaction_type", ""),
                            content=str(interaction.get("content", "")),
                            timestamp=interaction.get("timestamp", datetime.utcnow().isoformat())
                        )
                    )
                else:
                    self.interactions.append(interaction)

    def to_dict(self):
        return {
            "id": self.id,
            "hash_id": self.hash_id,
            "type": self.type,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "parent_id": self.parent_id,
            "info": self.info,
            "data": self.data,
            "error": self.error,
            "network_calls": [call.to_dict() if hasattr(call, 'to_dict') else call for call in self.network_calls],
            "interactions": self.interactions
        }

class LLMComponent(Component):
    def __init__(self, id: str, hash_id: str, type: str, name: str, start_time: str, end_time: str, parent_id: int, info: Dict[str, Any], data: Dict[str, Any], network_calls: Optional[List[NetworkCall]] = None, error: Optional[Dict[str, Any]]=None, interactions: Optional[List[Union[Interaction, Dict]]] = None):
        super().__init__(id, hash_id, type, name, start_time, end_time, parent_id, info, data, network_calls, error, interactions)

class AgentComponent(Component):
    def __init__(self, id: str, hash_id: str, type: str, name: str, start_time: str, end_time: str, parent_id: int, info: Dict[str, Any], data: Dict[str, Any], network_calls: Optional[List[NetworkCall]] = None, error: Optional[Dict[str, Any]] = None, interactions: Optional[List[Union[Interaction, Dict]]] = None):
        super().__init__(id, hash_id, type, name, start_time, end_time, parent_id, info, data, network_calls, error, interactions)

class ToolComponent(Component):
    def __init__(self, id: str, hash_id: str, type: str, name: str, start_time: str, end_time: str, parent_id: int, info: Dict[str, Any], data: Dict[str, Any], network_calls: Optional[List[NetworkCall]] = None, error: Optional[Dict[str, Any]] = None, interactions: Optional[List[Union[Interaction, Dict]]] = None):
        super().__init__(id, hash_id, type, name, start_time, end_time, parent_id, info, data, network_calls, error, interactions)

@dataclass
class ComponentInfo:
    tool_type: Optional[str] = None
    agent_type: Optional[str] = None
    version: str = ""
    capabilities: Optional[List[str]] = None
    memory_used: Optional[int] = None
    model: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    token_usage: Optional[Dict[str, int]] = None
    cost: Optional[Dict[str, float]] = None

class Trace:
    def __init__(self, id: str, project_name: str, start_time: str, end_time: str, metadata: Optional[Metadata] = None, data: Optional[List[Dict[str, Any]]] = None, replays: Optional[Dict[str, Any]] = None):
        self.id = id
        self.project_name = project_name
        self.start_time = start_time
        self.end_time = end_time
        self.metadata = metadata or Metadata()
        self.data = data or []
        self.replays = replays

    def to_dict(self):
        return {
            "id": self.id,
            "project_name": self.project_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "data": self.data,
            "replays": self.replays,
        }