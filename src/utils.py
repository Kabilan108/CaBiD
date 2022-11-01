"""
Utilities

Authors:  Tony Kabilan Okeke <tko35@drexel.edu>
          Ali Youssef <amy57@drexel.edu>
          Cooper Molloy <cdm348@drexel.edu>

Purpose:  This module contains utility functions.
"""

# Imports
import requests

from tqdm.auto import tqdm
from pathlib import Path


def downloadurl(url: str, file: str='', overwrite: bool=False) -> str:
    """
    Download and save file from a given URL

    Parameters
    ----------
    url : str
        URL to retreive file from
    file : str, optional
        Path to file where download will be stored, by default ''
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
                desc=file, 
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
