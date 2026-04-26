from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4

from .ReplyChannel import ReplyChannel


@dataclass
class Message:
    """Structured envelope for DaemonWorker queue items.

    Rules:
    - `topic`   : event/command name (str, non-empty)
    - `payload` : arbitrary data dict delivered to the handler
    - `isAsync` : set by the SENDER (Publisher.notifyAsync) — not the handler.
                  True  → delivery routed via TaskManagerService (fire-and-forget).
                  False → delivery inline on Dispatcher thread (or MainThreadBridge for UI).
    - `replyTo` : optional one-shot channel for request/reply patterns.
                  None  → fire-and-forget (no reply expected).

    Contract for subclassers of DaemonWorker
    -----------------------------------------
    - Enqueue only `Message` instances (enforced at runtime via isinstance check).
    - `onItem(msg: Message)` receives the fully-typed envelope.
    """

    topic: str
    payload: dict = field(default_factory=dict)
    messageId: str = field(default_factory=lambda: uuid4().hex)
    isAsync: bool = False
    replyTo: Optional['ReplyChannel'] = None

    def __post_init__(self):
        if not self.topic:
            raise ValueError('Message.topic must be a non-empty string')
        if not isinstance(self.payload, dict):
            raise TypeError(f'Message.payload must be a dict, got {type(self.payload).__name__}')
