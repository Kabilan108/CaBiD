"""
CaBiD Utilities
---------------

This module contains utility functions for CaBiD.

Author: Tony Kabilan Okeke <tko35@drexel.edu>

Functions & Classes
-------------------
config
    Configuration class with paths to data and cache directories
ispc
    Check if the system is a PC
cachedir
    Get the cache directory
tempdir
    Get a temporary directory
slugify
    Convert a URL to a clean filename (Based on Django's slugify)
isnonemptyfile
    Check if a file exists and is not empty
datadir
    Return the path to project data directory
downloadurl
    Download a URL to a file
CaBiD_db
    Class for connecting to and querying the CaBiD database
"""

# Imports
from typing import Any, Tuple
from pandas import DataFrame
from tqdm.auto import tqdm
from pathlib import Path
from rich import print

import os, pickle, platform, re, requests, shutil, sqlite3, tempfile, \
    unicodedata


class config:
    """
    Config options for module

    Attributes
    ----------
    CACHEDIR : str
        Directory for storing cached data (pickle files)
    DATADIR : str
        Directory for storing downloaded data
    TEMPDIR : str
        Directory for storing temporary data
    """

    CACHEDIR = tempfile.gettempdir() + '/CaBiD/cache'
    DATADIR = None
    TEMPDIR = tempfile.gettempdir() + '/CaBiD'


def ispc() -> bool:
    """
    Check if the system is a PC
    Based on bmes.ispc() by Ahmet Sacan
    """

    if not hasattr(ispc, 'value'):
        system = platform.system()
        ispc.value = system == 'Windows' or system.startswith('CYGWIN')
    return ispc.value


def cachedir() -> Path:
    """
    Get the cache directory

    Returns
    -------
    Path
        Path to cache directory
    """

    # Check if temporary directory is set
    if config.CACHEDIR is not None:
        if not os.path.exists(config.CACHEDIR):
            os.makedirs(config.CACHEDIR)

        return Path(config.CACHEDIR).resolve()

    # Create a temporary directory
    path = (Path(tempfile.gettempdir()) / 'CaBiD/cache').resolve()
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def tempdir() -> Path:
    """
    Get a temporary directory

    Returns
    -------
    Path
        Path to a temporary directory
    """

    # Check if temporary directory is set
    if config.TEMPDIR is not None:
        if not os.path.exists(config.TEMPDIR):
            os.makedirs(config.TEMPDIR)

        return Path(config.TEMPDIR).resolve()

    # Create a temporary directory
    path = (Path(tempfile.gettempdir()) / 'CaBiD').resolve()
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def slugify(value: str, allow_unicode: bool=False) -> str:
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or
    repeated dashes to single dashes. Remove characters that aren't
    alphanumerics, underscores, or hyphens. Convert to lowercase. 
    Also strip leading and trailing whitespace, dashes, and underscores.
    """

    # Check inputs
    assert isinstance(value, str), 'filename must be a string'
    assert isinstance(allow_unicode, bool), 'allow_unicode must be a boolean'

    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = (unicodedata.normalize('NFKD', value)
            .encode('ascii', 'ignore')
            .decode('ascii'))
    
    value = re.sub(r'[^\w.\s-]', '', value).strip().lower()

    return re.sub(r'[-\s]+', '-', value)


def isnonemptyfile(file: str) -> bool:
    """
    Check if a file exists and is not empty
    """

    assert isinstance(file, str) or isinstance(file, Path), \
        'file must be a string'

    return os.path.isfile(file) and os.path.getsize(file) > 0


def datadir() -> Path:
    """
    Return the path to a data directory
    Based on bmes.datadir() by Ahmet Sacan
    """

    # Check if data directory is set
    if config.DATADIR is not None:
        if not os.path.exists(config.DATADIR):
            os.makedirs(config.DATADIR)

        return Path(config.DATADIR).resolve()

    # Store path as an attribute
    if not hasattr(datadir, 'path'):
        datadir.path = ''
    path = datadir.path

    if not path:
        if ispc():
            path = Path(os.environ['USERPROFILE']) / 'CaBiD'
        else:
            path = Path(os.environ['HOME']) / '.cabid'
        
        if not os.path.exists(path):
            os.makedirs(path)

        datadir.path = path

    return path


def downloadurl(url: str, file: str='', overwrite: bool=False,
                progress: bool=True) -> str:
    """
    Download and save file from a given URL
    Modified from bmes.downloadurl by Ahmet Sacan

    Parameters
    ----------
    url : str
        URL to retreive file from
    file : str, optional
        Path to file (or directory) where download will be stored,
        by default ''
    overwrite : bool, optional
        Should existing files be overwritten, by default False
    progress : bool, optional
        Should a progress bar be displayed, by default True

    Returns
    -------
    str
        Path to the downloaded file
    """

    # Check inputs
    assert isinstance(url, str), 'url must be a string'
    assert isinstance(file, str), 'file must be a string'
    assert isinstance(overwrite, bool), 'overwrite must be a boolean'

    # If URL is not a remote address, assume it is a local file
    if not re.search(r'^(http[s]?|ftp):\/\/', url):
        if not file:
            return url
        if not overwrite:
            if isnonemptyfile(file):  return file
            shutil.copyfile(url, file)
            return file

    # Get file name from URL and append to file path
    if not file:
        urlname = url.split('?')[0].split('/')[-1]
        file = (tempdir() / slugify(urlname)).resolve()  # type: ignore
    elif file.endswith('/'):
        file = (Path(file) / slugify(url)).resolve()  # type: ignore
    else:
        file = Path(file).resolve()  # type: ignore

    # Return file if it exists and overwrite is False
    if isnonemptyfile(file) and not overwrite:  return file

    # Download the file
    r = requests.get(url, stream=True, allow_redirects=True,
                     timeout=(3, 27))
    if r.status_code == 200:
        size = int(r.headers.get('content-length', 0))
        
        # Create a progress bar
        if progress:
            with open(file, 'wb') as f:
                with tqdm(
                    total=size, 
                    unit='B', 
                    unit_scale=True, 
                    desc=file.name,  # type: ignore
                    initial=0
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
        else:
            with open(file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

    elif r.status_code == 404:
        raise Exception('URL not found')
    else:
        raise Exception('Unexpected error, status code: ' +
                        str(r.status_code))

    return file


class CaBiD_db:
    """
    This class provides access to the CaBiD database and provides special
    methods for querying the database.

    Methods
    -------
    execute(query: str, params: tuple=(), commit: bool=False)
        Execute a query
    select(query: str, params: tuple=())
        Execute a select query
    retrieve_dataset(dataset: tuple)
        Retrieve a dataset from the database
    check_table(table: str)
        Check if a table exists in the database
    drop_table(table: str)
        Drop a table from the database
    binarize(obj: Any)
        Convert an object to a binary string (pickle)
    close()
        Close the database connection
    """

    def __init__(self, file: Path | str) -> None:
        """
        Initialize the SQLite class and connect to the database

        Parameters
        ----------
        file : Path of str
            Path to SQLite database file
        """

        # Check inputs
        if isinstance(file, str):  file = Path(file)
        
        self.file = file
        self.conn = sqlite3.connect(file)
        self.conn.row_factory = sqlite3.Row  # Fetchall returns dict


    def execute(self, query: str, params: Tuple[Any, ...]=()) -> None:
        """
        Execute a query

        Parameters
        ----------
        query : str
            Query to execute
        params : Tuple[Any, ...], optional
            Parameters to pass to query, by default ()
        """

        # Check inputs
        assert isinstance(query, str), 'query must be a string'
        assert isinstance(params, tuple), 'params must be a tuple'

        if query.lower().startswith('select'):
            raise Exception('Use select method for select queries')
        else:
            try:
                self.conn.execute(query, params)
                self.conn.commit()
            except sqlite3.Error as e:
                print(e)


    def select(self, query: str, params: Tuple[Any, ...]=()) -> DataFrame:
        """
        Execute a select query and return the results as a DataFrame

        Parameters
        ----------
        query : str
            Query to execute
        params : Tuple[Any, ...], optional
            Parameters to pass to query, by default ()

        Returns
        -------
        DataFrame
            Results of the query
        """

        # Check inputs
        assert isinstance(query, str), 'query must be a string'
        assert isinstance(params, tuple), 'params must be a tuple'

        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            print(e)
            return None  # type: ignore

        if len(rows) == 0:
            raise Exception('No results found')
        else:
            df = DataFrame(rows)
            df.columns = [x[0] for x in cursor.description]  # type: ignore
            return df


    def retrieve_dataset(self, dataset: tuple) -> DataFrame:
        """
        This method will retrieve a gene expression dataset from the CaBiD
        database. It will then convert the gene expresssion data (stored in
        binary format as pickle objects) into a pandas DataFrame with the 
        sample type (cancer or normal) as the index and the gene IDs as the
        columns.

        Parameters
        ----------
        dataset : tuple
            Tuple of the form (gse, cancer_type)

        Returns
        ------
        dataset : pd.DataFrame
        """

        # Check inputs
        assert isinstance(dataset, tuple), 'dataset must be a tuple'
        assert len(dataset) == 2, 'dataset must be a tuple of length 2'
        assert dataset[0].startswith('GSE'), 'dataset[0] must be a GSE ID'

        # Query the database
        data = self.select((
            "SELECT E.* FROM `expression` AS E, `datasets` AS D "
            "WHERE D.GSE = '%s' AND D.CANCER = '%s' AND E.DATASET_ID = D.ID"
        ) % dataset)

        # Convert the binary data to a DataFrame
        try:
            data = (data['EXPRESSION']
                .apply(lambda x: pickle.loads(x))
                .set_index(data['SAMPLE_TYPE']))
        except KeyError:
            raise Exception('Dataset not found in CaBiD database')
        except Exception as e:
            raise Exception('Error converting data to DataFrame: ' + str(e))

        return data


    def check_table(self, table: str) -> bool:
        """
        Check if a table exists in the database.

        Parameters
        ----------
        table : str
            The name of the table to check for.

        Returns
        -------
        exists : bool
            True if the table exists, False otherwise.
        """

        # Check if the table exists and is not empty
        try:
            self.select((
                "SELECT tbl_name FROM sqlite_master "
                f"WHERE type='table' AND tbl_name='{table}'"
            ))
            self.select(f"SELECT * FROM {table} LIMIT 1")
        except:
            return False

        return True

    
    def drop_table(self, table: str) -> None:
        """
        Drop a table from the database

        Parameters
        ----------
        table : str
            Name of table to drop
        """

        # Check inputs
        assert isinstance(table, str), 'table must be a string'

        self.execute(f'DROP TABLE IF EXISTS {table}');


    def binarize(self, obj: Any) -> sqlite3.Binary:
        """
        Convert an object to a pickled binary object

        Parameters
        ----------
        obj : Any
            Object to convert
        
        Returns
        -------
        sqlite3.Binary
            Pickled binary object
        """

        return sqlite3.Binary(pickle.dumps(obj, protocol=5))


    def close(self) -> None:
        """Close the database connection"""
        print(f"Closing connection to {self.file}")
        self.conn.close()


    def __enter__(self):
        """Enter the runtime context related to this object"""
        return self


    def __exit__(self, type, value, traceback):
        """Exit the runtime context related to this object"""
        self.conn.commit()
        self.conn.close()


    def __repr__(self) -> str:
        """Return a string representation of the object"""
        return f"SQLite({self.file.name})"


    def __str__(self) -> str:
        """Return a string representation of the object"""
        return f"SQLite({self.file.name})"
