from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Callable, Dict
from datapipes._utilities.logger import LOGGER_NAME
import logging

_LOGGER = logging.getLogger(LOGGER_NAME)

class Subject(ABC):
    """ The Subject interface declares a set of methods for managing subscribers."""

    @abstractmethod
    def attach(self, observer: 'Observer') -> None:
        """ Attach an observer to the subject."""
        pass

    @abstractmethod
    def detach(self, observer: 'Observer') -> None:
        """ Detach an observer from the subject. """
        pass

    @abstractmethod
    def notify(self) -> None:
        """ Notify all observers about an event. """
        pass


class ConcreteSubject(Subject):
    """
    The Subject owns some important state and notifies observers when the state changes.
    """
    def __init__(self):
        self._state: int = None
        """
        For the sake of simplicity, the Subject's state, essential to all
        subscribers, is stored in this variable.
        """

        self._observers: List['Observer'] = []
        """
        List of subscribers. In real life, the list of subscribers can be stored
        more comprehensively (categorized by event type, etc.).
        """

# We can attach things by decorating them, this should be part of the inner_wrapper for the decorator.
# We can have each algorithm choose to observe based on whether it's listed in the yaml file.
    # CS._state is initialized so all observers are marked as "updated" = None/0
    # when dataio is done, it calls CS.dataReady which changes CS._state to not updated
    # (updated could require tests or assertions of output passed)
    # This would be done in run.py, reading the yaml file and attaching those observers, and calling CS.dataready()
    def attach(self, observer: 'Observer') -> None:
        _LOGGER.debug(f'   NEW PUB/SUB SUBSCRIBER       | Attached an observer to -> {self}')
        self._observers.append(observer)

    def detach(self, observer: 'Observer') -> None:
        _LOGGER.debug(f'   REMOVED PUB/SUB SUBSCRIBER   | Removed an observer from -> {self}')
        self._observers.remove(observer)

    """
    The subscription management methods.
    """

    def notify(self) -> None:
        """ Trigger an update in each subscriber. """
        # _LOGGER.debug(f' PUBLISHING RESULTS          | {type(self).__name__}: Notifying observers...')
        for observer in self._observers:
            self.notify_one(observer)
            # observer.update(self)

    def notify_one(self, observer: 'Observer'=None) -> None:
        """ Trigger an update in a specific subscriber. """
        _LOGGER.debug(f' PUBLISHING RESULTS          | {type(self).__name__} -> Notified -> {type(observer).__name__}')
        observer.update(self)

    def dataReady(self) -> None:
        """
        I can see this being used for basic munging of data once it's gathered from different sources.
        Or perhaps there are summary views of data that actually make sense to have here, like a report of what you're subscribing to.

        Could this be the algorithm code? It's the algorithm that's a ConcreteSubject of interest by others, and it
        attaches, detaches, and notifies people of it's changes...

        Usually, the subscription logic is only a fraction of what a Subject can
        really do. Subjects commonly hold some important business logic, that
        triggers a notification method whenever something important is about to
        happen (or after it).
        """
        self._state = randrange(0, 10)

        _LOGGER.debug(f"{self}: State changed to: {self._state}. \nNotifying observers.")
        self.notify()


class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """
    def update(self, subject: Subject) -> None:
        """ Receive update from subject.
        ...we could include common update logic here... """
        _LOGGER.debug(f"{self}: Reacting to the event: {subject}.")
        pass


# def PubSubDecorator(cls):
class PubSub(): #ConcreteSubject,Observer):
    """
    Publish Subscribe decorator for object instantiated by the Data Factory.
    """
    def __init__(self): #,wrapped_class): #*args,**kwargs):
        ConcreteSubject.__init__(self)
        Observer.__init__(self)
        # wrapped_class.__metaclass__ = cls

        self._state: int = 0
        self._observers: List['Observer'] = []

    def attach(self, observer: 'Observer') -> None:
        _LOGGER.debug(f'   NEW PUB/SUB SUBSCRIBER       | Attached an observer to -> {self}')
        self._observers.append(observer)

    def detach(self, observer: 'Observer') -> None:
        _LOGGER.debug(f'   REMOVED PUB/SUB SUBSCRIBER   | Removed an observer from -> {self}')
        self._observers.remove(observer)

    def notify(self) -> None:
        """ Trigger an update in each subscriber. """
        # _LOGGER.debug(f' PUBLISHING RESULTS          | {type(self).__name__}: Notifying observers...')
        for observer in self._observers:
            self.notify_one(observer)
            # observer.update(self)

    def notify_one(self, observer: 'Observer' = None) -> None:
        """ Trigger an update in a specific subscriber. """
        _LOGGER.debug(
            f' PUBLISHING RESULTS          | {type(self).__name__} -> Notified -> {type(observer).__name__}')
        observer.update(self)

    # def update(self, subject: Subject) -> None:
    #     """ Receive update from subject."""
    #     _LOGGER.debug(f"{self}: Reacting to the event: {subject}.")
    #     pass

    def dataReady(self) -> None:
        """
        I can see this being used for basic munging of data once it's gathered from different sources.
        Or perhaps there are summary views of data that actually make sense to have here, like a report of what you're subscribing to.

        Could this be the algorithm code? It's the algorithm that's a ConcreteSubject of interest by others, and it
        attaches, detaches, and notifies people of it's changes...

        Usually, the subscription logic is only a fraction of what a Subject can
        really do. Subjects commonly hold some important business logic, that
        triggers a notification method whenever something important is about to
        happen (or after it).
        """
        self._state = randrange(0, 10)

        _LOGGER.debug(f"{self}: State changed to: {self._state}. \nNotifying observers.")
        self.notify()

    # def wrap_update(self,update):
    #     def outer(self):
    #         return update(self)
    #     return outer
    # def wrap_notify(self,notify):
    #     def outer(self):
    #         return notify(self)
    #     return outer
    # def wrap_attach(self,attach):
    #     def outer(self):
    #         return attach(self)
    #     return outer
    # def wrap_detach(self,detach):
    #     def outer(self):
    #         return detach(self)
    #     return outer

    # def __new__(cls, name, bases, attrs):
    #     """Assert and wrap!"""
    #     if ('update' not in attrs) or ('notify' not in attrs) or ('attach' not in attrs) or ('detach' not in attrs):
    #         raise NotImplementedError(f"Skipping class {type(cls).__name__}. Connecting to DataPipes PubSub network requires implementing methods <update>, <notify>, <attach>, and <detach>.")
    #     else:
    #         attrs['update'] = cls.wrap_update(attrs['update'])
    #         attrs['notify'] = cls.wrap_notify(attrs['notify'])
    #         attrs['attach'] = cls.wrap_attach(attrs['attach'])
    #         attrs['detach'] = cls.wrap_detach(attrs['detach'])

        # def inner_wrapper(wrapped_class,*args,**kwargs) -> Callable:
            # super(self,wrapped_class).__init__(*args,**kwargs)
            # wrapped_class.__init__(self,*args,**kwargs)
            # return wrapped_class

        # return inner_wrapper(*args,**kwargs)

    # __publishers = {}
    #
    # __subscribers = {}
    #
    # @classmethod
    # def subscribe(cls, name:str=None) -> Callable:
    #     def inner_wrapper(wrapped_class) -> Callable:
    #         if name in cls.__subscribers:
    #             _LOGGER.critical(f"DataPipes Subscriber class {name} already exists. Will be replaced.")
    #
    #         cls.__subscribers[name] = wrapped_class
    #         return wrapped_class
    #
    #     return inner_wrapper

    # def update(self, subject: Subject, message: Dict) -> str:
    #     # Do I update with the subject, or with a standard message?
    #     # assert subject
    #     return subject.operation(message)
    #
    #
    # def notify(self) -> None:
    #     # We update everyone with ourselves as the message, but why?
    # def attach(self, observer: 'Observer') -> None:
    #     # This is already done by inheriting ConcreteSubject and Observer
    #     # So what needs to be done, anything?
    # def detach(self, observer: 'Observer') -> None:
    #     # Will we ever use this? Will an algorithm decide to detach itself?



"""
These are the backbone, the managers that take action depending on the type of test. 
So as each algorithm finishes, it can tell this backbone, which kicks off the next task.
Having modules communicate directly with each other could conceivably be done for data io and each algorithm...
Once the data io loaded and processed the information, it would 'notify' the observers, 
which are added according to the yaml file, and those updates would be their processing of that data; 
This would replace the loops in run.py with while statements where the 

The other ways of thinking about it I can't help...
Each observer could be an algorithm, and their particular Observer.update() function could be 
how they interface with the expected data (such as choosing a subselection of the columns) before the real math.
These Observers get kicked off by the ConcreteSubject.notify(), and when the algorithms are done the backbone
updates its _state   
 
Concrete Observers react to the updates issued by the Subject they had been
attached to.
"""

# So there are different types of observers, each indicates the type of information they're interested in reacting to.
class ConcreteObserverA(Observer):
    def update(self, subject: Subject) -> None:
        if subject._state < 3:
            print("ConcreteObserverA: Reacted to the event")


class ConcreteObserverB(Observer):
    def update(self, subject: Subject) -> None:
        if subject._state == 0 or subject._state >= 2:
            print("ConcreteObserverB: Reacted to the event")


# This is useful until it's translated to our purposes.
# At first glance, this logic could exist in the decorator with the inner_wrapping.
#
# if __name__ == "__main__":
#     # The client code.
#
#     # "subject" creates the interface for an object to subscribe to some contrete subject.
#     subject = ConcreteSubject()
#
#     #
#     observer_a = ConcreteObserverA()
#     subject.attach(observer_a)
#
#     observer_b = ConcreteObserverB()
#     subject.attach(observer_b)
#
#     subject.some_business_logic()
#     subject.some_business_logic()
#
#     subject.detach(observer_a)
#
#     subject.some_business_logic()