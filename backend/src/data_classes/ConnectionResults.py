import json
from dataclasses import dataclass
from typing import List
from src.data_classes.Connection import Connection


@dataclass
class ConnectionResults:
    query_id: int
    error: dict
    connections: List[Connection]

    @staticmethod
    def to_json(connection_results):
        return json.dumps({"query_id": connection_results.query_id, "result": {
            "connections": [Connection.to_serializable(c) for c in connection_results.connections]},
            "error": connection_results.error},
                          ensure_ascii=False)
