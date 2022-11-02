"""
Utilities

Author:  Tony Kabilan Okeke <tko35@drexel.edu>

Purpose:  This module contains utility functions.
"""

# Imports
import unicodedata
import platform
import requests
import tempfile
import sqlite3
import shutil
import os
import re

from typing import Union, Tuple, Any
from pandas import DataFrame
from itertools import islice
from tqdm.auto import tqdm
from pathlib import Path
from rich import print


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
    if config.TEMPDIR is not None:
        if not os.path.exists(config.TEMPDIR):
            os.makedirs(config.TEMPDIR)

        return Path(config.TEMPDIR).resolve()

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


def downloadurl(url: str, file: str='', overwrite: bool=False) -> str:
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

    elif r.status_code == 404:
        raise Exception('URL not found')
    else:
        raise Exception('Unexpected error, status code: ' +
                        str(r.status_code))

    return file


def iohead(file: Union[str, Path], n: int=5) -> None:
    """
    Print the first n lines of a file to the console

    Parameters
    ----------
    file : str or Path
        Path to file
    n : int, optional
        Number of lines to print, by default 10
    """

    # Check inputs
    if isinstance(file, str):  file = Path(file)
    assert isinstance(file, Path), 'file must be a valid path'
    assert file.exists(), 'file does not exist'
    assert isinstance(n, int) and n > 0, 'n must be a positive integer'

    # Open file
    with open(file, 'r') as f:
        for line in islice(f, n):
            if len(line) > 80:
                print(line[:80] + '...')
            else:
                print(line.rstrip())


class SQLite:
    """
    Wrapper class for accessing SQLite databases

    Methods
    -------
    execute(query: str, params: tuple=(), commit: bool=False)
        Execute a query
    select(query: str, params: tuple=())
        Execute a select query
    close()
        Close the database connection
    """

    def __init__(self, file: Union[Path, str]):
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
            print("No rows returned")
            return None  # type: ignore
        else:
            df = DataFrame(rows)
            df.columns = [x[0] for x in cursor.description]  # type: ignore
            return df

    def close(self) -> None:
        print(f"Closing connection to {self.file}")
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

    def __repr__(self) -> str:
        return f"SQLite({self.file.name})"

    def __str__(self) -> str:
        return f"SQLite({self.file.name})"
