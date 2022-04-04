"""
Contains the overall factory definition.
"""
import logging, json
from typing import Callable, Dict

from datapipes._utilities.logger import LOGGER_NAME
from datapipes.observer import PubSub, Observer, ConcreteSubject #

_LOGGER = logging.getLogger(LOGGER_NAME)


# def setattr_decorator(name):
#     def wrapper(K):
#         setattr(K, name, eval(name))
#         return K
#     return wrapper

class Factory:
    """
    Factory decorator class for client algorithms configured to subscribe to the DataPipes PubSub network.
    Decorate your algorithm class with your algorithm name like so:

    @Factory.register('your_algorithm_name')
    class your_algorithm_name():

    Args:
        Name: The name of the class/funcation/algorithm being decorated. Must match the config.py reference.

    Returns:
        Instantiated Class Object: The client decorated object registered with DataPipes PubSub network.

    Attributes:
        Name: String
        Instantiated Class Object: <Client Class Object>
    """

    __registry = {}
    __temp_obj = None

    @staticmethod
    def notify(self):
        """Adds the method 'notify' to the decorated client class"""
        return self.PubSub.notify()

    @staticmethod
    def attach(self):
        """Adds the method 'attach' to the decorated client class"""
        return self.PubSub.attach()

    @staticmethod
    def detach(self):
        """Adds the method 'detach' to the decorated client class"""
        return self.PubSub.detach()

    # @staticmethod
    # def map_proxy(obj):
    #     dict = {}
    #
    #     for k in obj.__dict__.keys():
    #         dict.update({k: obj.__dict__.get(k)})
    #
    #     cls_name = str(obj).split(".")[1].split("'")[0]
    #     dict.update({"__class__": cls_name})
    #
    #     return dict

    @classmethod
    def register(cls, name:str=None) -> Callable:
        """
        Class method to register the client algorithm to the internal registry.
        Decorate your algorithm class with your algorithm name like so:

        @Factory.register('your_algorithm_name')
        class your_algorithm_name():
        """

        def inner_wrapper(wrapped_class) -> Callable:
            if name in cls.__registry:
                _LOGGER.critical(f'DataPipes Factory class {name} already exists. Will be replaced.')

            cls.__registry[name] = wrapped_class

            # setattr(wrapped_class, 'update', eval('update'))
            setattr(wrapped_class, 'notify', eval('cls.notify'))
            setattr(wrapped_class, 'attach', eval('cls.attach'))
            setattr(wrapped_class, 'detach', eval('cls.detach'))

            return wrapped_class

        return inner_wrapper

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Factory command to create the client decorated object for connection to the DataPipes PubSub network.

        Args:
            *args: Allows the client to pass any series of separate initialization veriables to the constructor.
            **kwargs: Allows the client to pass an initialization dictionary to the constructor.
        Returns:
            An instance of the client algorithm class.
        """
        if len(args) == 0:
            raise NotImplementedError(f"The Factory needs to know which registered class to instantiate.")
        args = list(args)
        name = args.pop(0)

        if name not in cls.__registry:
            raise NotImplementedError(f"class {name} does not exist in the registry")

        _LOGGER.debug(f'    OBJECT INSTANTIATED          | one {name} has been instantiated')

        registered_obj = cls._Factory__registry[name](*args, **kwargs)
        registered_obj.PubSub = PubSub()
        registered_obj.PubSub.pubsub_message = {'type':type(registered_obj).__name__}
        registered_obj.PubSub.pubsub_message['cfg'] = kwargs
        registered_obj.PubSub.pubsub_message['data'] = None

        return registered_obj
