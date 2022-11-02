"""
Utilities

Authors:  Tony Kabilan Okeke <tko35@drexel.edu>
          Ali Youssef <amy57@drexel.edu>
          Cooper Molloy <cdm348@drexel.edu>

Purpose:  This module contains utility functions.
"""

# Imports
import unicodedata
import platform
import requests
import tempfile
import shutil
import os
import re

from tqdm.auto import tqdm
from pathlib import Path


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
