import os, psycopg2
from abc import ABC, abstractmethod
from typing import Generator, Dict, BinaryIO
from datapipes._utilities.logger import LOGGER_NAME
from datapipes.observer import PubSub
import logging
import pandas as pd
from datetime import datetime

_LOGGER = logging.getLogger(LOGGER_NAME)


class _DataStrategy(ABC):
    """ Abstract Base Class for Data I/O strategies. Sets the required class methods and variable types.
    """
    @abstractmethod
    def load(cls,context:str,data:Dict) -> Dict:
        pass
    @abstractmethod
    def save(cls,context:str,data:Dict) -> Dict:
        pass

class StrategyCSV(_DataStrategy):
    """
    Everyone uses CSV files. This strategy loads the specified local file and
    publishes that data according to the config.yml PubSub graph.

    Args:
        key: filename of the csv.
        path: filepath of the csv.

    Returns:
        key: filename of the csv.
        data: a Pandas dataframe of the csv.

    Attributes:
        key: String
        data: a Pandas dataframe.
    """

    def __init__(self,**kwargs): #,key,path):
        self.key = kwargs['key']
        self.path = kwargs['path']

    def load(self) -> Dict:
        return self.batch_read(key=self.key,path=self.path)

    def save(self,result:Dict=None) -> Dict:
        return self.batch_write(result)

    def batch_read(self,key=None,path=None) -> Generator:
        """
        Provides all examples in a CSV file in a single batch.
        """
        _LOGGER.debug('   CREATING BATCH             | creating batch from csv file contents: %s', path)
        data = pd.read_csv(os.path.join(path, f'{key}.csv'))
        yield key, data

    def batch_write(self, data:pd.DataFrame=None): #, key:str=None, output_path:str='output', output_name:str=uuid.uuid1()):
        """
        Write all examples as a batch.
        """
        _LOGGER.debug(f'   WRITING CSV                | writing csv file from batch for {self.key}')

        os.makedirs(self.path, exist_ok=True)
        out_path_name = os.path.join(self.path, f'{self.key}.csv')
        data.to_csv( out_path_name, index=False)
        # data.to_csv(os.path.join(self._path, f'{key}.csv'), index=False)

class StrategyPostgres(_DataStrategy):
    """
    This strategy connects to the specified Postgres database and
    publishes the table as a pandas dataframe according to the config.yml PubSub graph.

    Args:
        key: filename of the csv.
        path: filepath of the csv.

    Returns:
        key: filename of the csv.
        data: a Pandas dataframe of the csv.

    Attributes:
        key: String
        data: a Pandas dataframe.
    """

    def __init__(self,user,dbname,host):
        self._PGDB = None
        self.user = user
        self.dbname = dbname
        self.host = host
        self._pg_connect()

    def _pg_connect(self):
        """ Return an active database connection."""

        if self._PGDB is None:
            _LOGGER.debug(f'  CONNECTING TO PROVENANCE DATABASE  | Connecting to Picnic Provenance Database')
            self._PGDB =  psycopg2.connect( user='sean@picnicscore.com',
                                            dbname='provenance',
                                            host='35.196.161.37')  # password='password',
        return self._PGDB

    def batch_read(self):
        """Unimplemented"""
        pass

    def batch_write(self,sql):
        """
        Need to test the SQL injections.
        """
        _LOGGER.debug(f'  PROVENANCE DATABASE WRITE     | writing to Picnic Provenance Database')

        repository = subprocess.check_output(["basename", "`git", "rev-parse", "--show-toplevel`"])
        commit = subprocess.check_output(["git", "describe", "--always"]).strip()
        self._create_row(VERSION=f'{commit}',
                         created_date=datetime.now(),
                         has_individual_manual=True,
                         has_vendor_manual=True,
                         has_industry_manual=True,
                         has_document_manual=True,
                         status='CREATED',
                         description=f'picnic models run with repo: {repository} and version: {commit}',
                         name=f'{repository}/{commit}')

        # self._batch_keys.append(key)

        ##############################################################

    def _create_row(
        VERSION: str,
        created_date: datetime = 'NOW()',  # this ensures always use docker tz if tz not passed in manually
        has_individual_manual: bool = False,
        has_vendor_manual: bool = False,
        has_industry_manual: bool = False,
        has_document_manual: bool = False,
        status: str = 'CREATED',
        description: str = None,
        name: str = None,
        **kwargs,
    ) -> int:
        """
        :param VERSION: the version of downloader
        :type VERSION: str
        :param has_individual: whether or not row has an individual-type data type
        :type has_individual: bool
        :param has_vendor: whether or not row has an vendor-type data type
        :type has_industry: bool
        :param has_industry: whether or not row has an industry-type data type
        :type has_industry: bool
        :param has_document: whether or not row has an document-type data type
        :type has_document: bool
        :param status: CREATED or SUCCESS
        :type status: str
        :param name: the name given to the campaign
        :type name: str
        creates a row in the provdb
        returns the BIGSERIAL id
        """
        id = 0

        sql = '''
               INSERT INTO picnicmodel(
                   major_version, 
                   minor_version,
                   patch_version,
                   created_date,
                   has_individual_manual,
                   has_vendor_manual,
                   has_industry_manual,
                   has_document_manual,
                   status,
                   description,
                   name) 
               VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
               RETURNING id;
           '''

        major, minor, patch = [int(num) for num in VERSION.split('.')]
        VALUES = (
            major,
            minor,
            patch,
            created_date,
            has_individual_manual,
            has_vendor_manual,
            has_industry_manual,
            has_document_manual,
            status,
            description,
            name,
        )

        with _pg_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, VALUES)
                conn.commit()
                id = cursor.fetchone()[0]

        _LOGGER.debug(f'  PROVENANCE ROW CREATED   | created new row with id: {id}')

        return id

    def finish_row(id: int) -> None:
        """
        :param id: the id of the dataset
        :type id: int
        """
        sql = '''
               UPDATE downloader 
               SET completed_date = NOW(),
                   status = 'COMPLETED'
               WHERE id = %s;
           '''
        with _pg_connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id,))
                conn.commit()

        _LOGGER.debug(f'{id} FINISHED')


class DataContext(_DataStrategy): #,Observer,ConcreteSubject):
    """
    DataContext stores each strategy and provides the data back to the user as a standard.
    Each Strategy is a class with a constructor that accepts only **kwargs, enabling the user to add whatever strategy
    required for their particular data.

    Args:
        _config: The dictionary of variables different strategies can understand.
        _config.format: The initialization dictionary must include a key:value pair where key='format'
        and value is a string choosing one of the following options:
        'csv' -> chooses the CSV Strategy
        'postgres' -> chooses the Postgres Strategy

    Returns:
        data: each strategy returns data their way. (See each Strategy above)
    """

    def __init__(self,_config:Dict=None): #,strategy:_DataStrategy=None):
        """Initialized to no strategy unless specified."""
        self._config = _config
        self.setStrategy(self._config['format'],**self._config)
        self.PubSub = PubSub()
        self.PubSub.pubsub_message = {'type':'spigot_data'}
        self.PubSub.pubsub_message['cfg'] = self._config

    def addStrategy(self, strategy:_DataStrategy, **kwargs):
        """enabling the user to add whatever strategy required for their particular data."""
        self.strategy = strategy(**kwargs)

    def setStrategy(self, strategy:str, **kwargs):
        """Used primarily by the constructor, but could be called by the user."""
        if strategy=='csv':
            self.strategy = StrategyCSV(**kwargs)
        elif strategy=='postgres':
            self.strategy = StrategyPostgres(**kwargs)
        else:
            raise NotImplementedError(f'Strategy {strategy} not implemented for {type(self).__name__}. Strategy options include: "csv" or "postgres"')
            return 1
        return 0

    def on(self):
        key, data = next(self.load())
        self.PubSub.pubsub_message['data'] = data
        self.notify()
        return 0

    def load(self) -> BinaryIO:
        return self.strategy.load()

    def save(self,result:Dict=None) -> BinaryIO:
        return self.strategy.save(result)

    def notify(self):
        return self.PubSub.notify()

    def update(self, subjectPubSub=None):
        self.strategy.save(subjectPubSub.pubsub_message['data'])