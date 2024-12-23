#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2024 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

from functools import wraps
from typing import Any, List, Optional


def singleton(cls):
    """Singleton decorator"""
    instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


@singleton
class Publisher:
    """Publisher (Subject) in Observer pattern"""
    
    def __init__(self):
        self.global_subscribers = []
        self.event_specific_subscribers = {}
    
    def subscribe(self, subscriber, event: Optional[str] = None):
        """Subscribe to all events or a specific event"""
        if event is None:
            self.global_subscribers.append(subscriber)
        else:
            if event not in self.event_specific_subscribers:
                self.event_specific_subscribers[event] = []
            if subscriber not in self.event_specific_subscribers[event]:
                self.event_specific_subscribers[event].append(subscriber)
    
    def unsubscribe(self, subscriber):
        """Unsubscribe from all events"""
        if subscriber in self.global_subscribers:
            self.global_subscribers.remove(subscriber)
        for subscribers in self.event_specific_subscribers.values():
            if subscriber in subscribers:
                subscribers.remove(subscriber)
    
    def notify(self, event: str, data: Any = None, *args, **kwargs):
        """Notify subscribers of an event"""
        # Notify global subscribers
        for subscriber in self.global_subscribers:
            subscriber.update(event, data, *args, **kwargs)
        
        # Notify event-specific subscribers
        if event in self.event_specific_subscribers:
            for subscriber in self.event_specific_subscribers[event]:
                subscriber.update(event, data, *args, **kwargs)
    
    def connect(self, widget, signal_name: str, event: str, data: Any = None, **kwargs):
        """Connect a Qt signal to an event"""
        slot = getattr(widget, signal_name, None)
        if slot is None:
            return
        
        slot.connect(
                lambda *args, **signal_kwargs: self.notify(
                        event,
                        data,
                        *args,
                        **{**kwargs, **signal_kwargs}
                )
        )


class Subscriber:
    """Base class for subscribers (observers)"""
    
    def __init__(self, events: List[str]):
        self.events = events
        self.is_global_subscriber = False
        
        # Auto-subscribe to events
        publisher = Publisher()
        for event in events:
            publisher.subscribe(self, event)
    
    def update(self, event: str, data: Any = None, *args, **kwargs):
        """Handle an event"""
        method_name = f'on_{event}'
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if data is not None:
                method(data, *args, **kwargs)
            else:
                method(*args, **kwargs)
