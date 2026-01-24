"""
ACK/NACK Protocol - Layer 1 (Core)

Generic acknowledgment mechanism for coordinating asynchronous operations
between sender and receiver components.

Architecture:
- AcknowledgmentTracker: Coordinator for managing pending acknowledgments
- AcknowledgmentReceiver: Base class for components waiting for acknowledgments
- AcknowledgmentSender: Base class for components sending acknowledgments

This layer is completely independent of:
- Browser/API/Service implementations
- Publisher/Subscriber pattern
- Any domain-specific logic

See docs/diagrams/task-acknowledgment-architecture.mermaid for full architecture.
"""

#                  M""""""""`M            dP
#                  Mmmmmm   .M            88
#                  MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                  MMP  .MMMMM  88    88  88888"    88'  `88
#                  M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                  M         M  `88888P'  dP   `YP  `88888P'
#                  MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                  * * * * * * * * * * * * * * * * * * * * *
#                  * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                  * -  Copyright © 2026 (Z) Programing  - *
#                  *    -  -  All Rights Reserved  -  -    *
#                  * * * * * * * * * * * * * * * * * * * * *

from .AcknowledgmentReceiver import AcknowledgmentReceiver
from .AcknowledgmentSender import AcknowledgmentSender
#
from .AcknowledgmentTracker import AcknowledgmentTracker

__all__ = ['AcknowledgmentTracker', 'AcknowledgmentReceiver', 'AcknowledgmentSender']
