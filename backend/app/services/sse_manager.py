"""Server-Sent Events (SSE) manager for real-time streaming."""

import asyncio
import json
from typing import Dict, Set, AsyncGenerator, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class SSEConnection:
    """Represents an SSE connection."""
    connection_id: str
    session_id: str
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    created_at: datetime = field(default_factory=datetime.utcnow)


class SSEManager:
    """Manager for Server-Sent Events connections."""

    def __init__(self):
        self._connections: Dict[str, SSEConnection] = {}
        self._session_connections: Dict[str, Set[str]] = {}

    def create_connection(self, session_id: str) -> SSEConnection:
        """Create a new SSE connection for a session."""
        connection = SSEConnection(
            connection_id=str(uuid.uuid4()),
            session_id=session_id,
        )
        self._connections[connection.connection_id] = connection

        if session_id not in self._session_connections:
            self._session_connections[session_id] = set()
        self._session_connections[session_id].add(connection.connection_id)

        return connection

    def remove_connection(self, connection_id: str) -> None:
        """Remove an SSE connection."""
        if connection_id in self._connections:
            connection = self._connections[connection_id]
            session_id = connection.session_id

            del self._connections[connection_id]

            if session_id in self._session_connections:
                self._session_connections[session_id].discard(connection_id)
                if not self._session_connections[session_id]:
                    del self._session_connections[session_id]

    async def send_event(
        self,
        session_id: str,
        event_type: str,
        data: dict,
        event_id: str = None
    ) -> None:
        """Send an event to all connections for a session."""
        if session_id not in self._session_connections:
            return

        event = {
            "type": event_type,
            "data": data,
            "id": event_id or str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
        }

        for connection_id in self._session_connections[session_id]:
            if connection_id in self._connections:
                await self._connections[connection_id].queue.put(event)

    async def event_generator(
        self,
        connection: SSEConnection
    ) -> AsyncGenerator[str, None]:
        """Generate SSE events for a connection."""
        try:
            while True:
                try:
                    # Wait for an event with timeout
                    event = await asyncio.wait_for(
                        connection.queue.get(),
                        timeout=30.0
                    )

                    # Format as SSE
                    yield format_sse_event(
                        event_type=event["type"],
                        data=event["data"],
                        event_id=event.get("id"),
                    )

                except asyncio.TimeoutError:
                    # Send keepalive
                    yield ": keepalive\n\n"

        except asyncio.CancelledError:
            pass
        finally:
            self.remove_connection(connection.connection_id)

    def get_connection_count(self, session_id: str) -> int:
        """Get the number of active connections for a session."""
        return len(self._session_connections.get(session_id, set()))


def format_sse_event(
    event_type: str,
    data: Any,
    event_id: str = None,
    retry: int = None
) -> str:
    """Format data as an SSE event string."""
    lines = []

    if event_id:
        lines.append(f"id: {event_id}")

    if retry:
        lines.append(f"retry: {retry}")

    lines.append(f"event: {event_type}")

    if isinstance(data, dict):
        data_str = json.dumps(data)
    else:
        data_str = str(data)

    lines.append(f"data: {data_str}")
    lines.append("")  # Empty line to end the event

    return "\n".join(lines) + "\n"


# Global SSE manager instance
sse_manager = SSEManager()
