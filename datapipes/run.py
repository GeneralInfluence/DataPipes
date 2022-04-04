import logging, os, yaml, click, sys, glob
from abc import ABC, abstractmethod
from typing import Dict, Any, List, BinaryIO
import pathlib
from pathlib import Path
from types import SimpleNamespace
import json
from pkg_resources import resource_stream
from copy import deepcopy
import importlib
from importlib import import_module

from datapipes._utilities.logger import LOGGER_NAME
from datapipes._utilities import logger
from datapipes._utilities.utilities import verifyConfiguration, class_import, importModules, import_package_modules

from datapipes.dataio import DataContext
from datapipes.factory import Factory

_LOGGER = logging.getLogger(LOGGER_NAME)

#---------------------------------------------------------------
# we should use mypy for testing!
#---------------------------------------------------------------

class RunStrategy(ABC):
    """
    Base class for the cmd runner.  All runner class implementations must implement this interface.
    """

    def __init__(self):
        """ Constructor. """
        pass

    @abstractmethod
    def execute(self, cfg:List[Dict[str, Any]]):
        """ Execute the Runner which starts the application. """
        pass

class RunLocal(RunStrategy):
    """
    Run Local has to be abstrated for anyone looking to execute a pipeline.
    This means projet specific logic and variables, if necessary, must be passed in.
    """
    def __init__(self, cfg: Dict[str, Any]): # *args:List, **kwargs:Dict[str, Any]): #

        if not verifyConfiguration(cfg): raise NotImplementedError(f'Congiguration {cfg} not implemented for {type(self).__name__}. You must configure the pipeline first!')
        else: self._cfg = cfg #Dict2DictDot(cfg)

    def execute(self):  # , cfg: Dict[str, Any]):
        _LOGGER.debug('       LOCAL ENVIRONMENT            | running in local environment mode')

        # loop over each run
        for key in self._cfg['independent_runs'].keys():

            run = self._cfg['independent_runs'][key]

            # moduleName = input('Enter module name:')
            # importlib.import_module(moduleName)
            # decorators = run['algorithms'].keys()
            # path = os.path.abspath('.')
            # _LOGGER.debug(f'\n\n INITIALIZING DECORATOR    | {decorators}\n')
            # for algorithm in decorators:
            #     import_module(run['algorithms'][algorithm]['path'].split('/')[0])

            _LOGGER.debug(f'\n\n SCORING RUN                | {run}\n')

            if self._cfg['data_mode'] == 'batch':
                self._handle_batch(run)
            if self._cfg['data_mode'] == 'stream':
                self._handle_stream(run)
        return

    def _assert_experiment(self,model_name=None):
        confirmed = False
        input_name_confirmed  = model_name in self._cfg['data']['input']['model_names'].keys()
        output_name_confirmed = model_name in self._cfg['data']['output']['model_names'].keys()
        if input_name_confirmed and output_name_confirmed:
            confirmed = True
        return confirmed

    def _handle_batch(self,run_cfg):
        _LOGGER.debug(' BATCH MODE                   | handling data in batch mode')

        data_sources = run_cfg['data_sources']
        algorithms   = run_cfg['algorithms']
        data_output  = run_cfg['data_output']

        input_objects = {}
        algorithm_objects = {}
        output_objects = {}
        input_graph = []
        algorithm_graph = []

        # First you create all the objects.
        for key in data_sources.keys():

            source = data_sources[key]
            input_objects[key] = DataContext(source)
            input_graph += [{'from':key,'to':source['observers']}]

        for key in algorithms.keys():

            alg = algorithms[key]
            algorithm_objects[key] = Factory.create(key)
            algorithm_graph += [{'from':key,'to':alg['observers']}]

        for key in data_output.keys():
            out = data_output[key]
            output_objects[key] = DataContext(out)

        # Then you connect the objects.
        for connection in input_graph:
            for observer in connection['to']:
                input_objects[connection['from']].PubSub.attach(algorithm_objects[observer])

        for connection in algorithm_graph:
            subject = connection['from']
            alg_keys = algorithm_objects.keys()
            out_keys = output_objects.keys()
            for key in connection['to']:
                if key in alg_keys:
                    observer = algorithm_objects[key]
                elif key in out_keys:
                    observer = output_objects[key]
                else:
                    raise NotImplementedError(f'key {key} not implemented for {type(self).__name__}.')

                algorithm_objects[subject].PubSub.attach(observer)

        # Then you run everything
        for spigot in input_objects.keys():
            input_objects[spigot].on()

    def _handle_stream(self, cfg: Dict[str, Any]):
        _LOGGER.debug('  STREAMING MODE     | handling data in streaming mode')


class RunGCP(RunStrategy):
    def __init__(self):
        pass


class RunContext(RunStrategy):
    """
    Goal is to choose the run strategy and execute.
    Strategies include:
    1. Local + #Companies
    2. Local + #Companies + MiniKube
    3. Local + #Companies + Testing
    4. Local + #Companies + MiniKube + Testing
    5-8. Remote + et al
    """
    def __init__(self,cfg:Dict=None):
        """Initialized to no strategy unless specified."""

        if not verifyConfiguration(cfg): raise NotImplementedError(f'Congiguration {cfg} not implemented for {type(self).__name__}. You must configure the pipeline first!')
        else: self._cfg = cfg # Dict2DictDot(cfg)

        self.setStrategy(self._cfg['run_strategy'])
        # return self

    def addStrategy(self, Strategy:RunStrategy=None):
        self.strategy = Strategy(self._cfg)

    def setStrategy(self,strategy:str):
        if strategy=='local':
            self.strategy = RunLocal(self._cfg) # In an even more complicated world, if strategies cherry pick from other modules, factory pattern may be necessary
        elif strategy=='gcp':
            self.strategy = RunGCP(self._cfg)
        else:
            raise NotImplementedError(f'Strategy {strategy} not implemented for {type(self).__name__}. Strategy options include: "local" or "gcp"')

    def execute(self) -> BinaryIO:
        self.strategy.execute()

#-------------------- DATA FIREHOSE ----------------------------

class DataSpigot():

    def __init__(self,cfg:str=None, version:BinaryIO=None):
        """
        Generates Picnic Model results.
        """
        if False: # version:
            metadata = json.load(resource_stream('dlasagne', 'metadata.json'))
            print(f'Version: {metadata["component_version"]} | Input Version: {metadata["input_component_version"]}')
            return 0

        if not os.path.isfile(cfg):
            print(f'"{cfg}" is not a file.  Please check that the file exists.')
            return 1

        with open(cfg, 'r') as fp:
            self._ycfg = yaml.load(fp, Loader=yaml.FullLoader)

        logger.configure_logger(self._ycfg.get('log_level', 'info'), self._ycfg.get('log_format', 'json'))

        self._runner = RunContext(self._ycfg)

    def on(self):
        self._runner.execute()
        return 0

        # env = ycfg.get('environment')
        # runner = Factory.create(*[env, ycorp], **ycfg)
        # runner.execute()

    def off(self):
        pass

@click.command()
@click.option('--cfg', default='config.yml', help='The application YAML configuration file.')
@click.option('--version', is_flag=True, help='Print the application version.')
def dataSpigot(cfg,version):
    DataSpigot(cfg, version=version).on()

if __name__ == '__main__':
    dataSpigot()