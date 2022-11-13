"""
Data Curation Tools

Author:  Tony Kabilan Okeke <tko35@drexel.edu>

Purpose:  This module contains functions for data curation.
"""

# Imports
import os
import pickle
from pathlib import Path

import fire
from GEOparse import get_GEO
from GEOparse.GEOTypes import GPL, GSE
from rich import print

import utils


def geodlparse(
    acc: str, 
    datadir: str | Path='', 
    silent: bool=False,
    make_dir: bool=False,
    cache: bool=False
) -> GSE | GPL:  #type: ignore
    """
    Download, parse and cache data from GEO.
    This fuction only downloads GSE and GPL data.

    Parameters
    ----------
    acc : str
        GEO accession
    datadir : str | Path, optional
        Directory for storing downloaded data, will default to a 
        temporary directory if not specified
    silent : bool, optional
        Whether to suppress output, by default False
    make_dir : bool, optional
        Whether to make the directory if it does not exist, 
        by default False
    cache : bool, optional
        Whether to cache the data, by default False

    Returns
    -------
    GPL | GSE
        Parsed GEO data
    """

    # Check inputs
    acc = acc.upper()
    assert isinstance(acc, str), 'acc must be a string'
    assert acc.startswith('GSE') or acc.startswith('GPL'), \
        'acc must be a GSE or GPL accession'

    assert isinstance(datadir, str) or isinstance(datadir, Path),\
        "datadir must be a string or pathlib.Path object"
    if isinstance(datadir, str):
        datadir = Path(datadir)
    if datadir == '':
        # Use a temporary directory
        datadir = utils.tempdir()
    elif not os.path.exists(datadir):
        if make_dir:  os.makedirs(datadir)
        else:  raise ValueError('Directory does not exist')
    
    assert isinstance(silent, bool), 'silent must be a boolean'
    assert isinstance(make_dir, bool), 'make_dir must be a boolean'
    
    # Define file names
    geofile = datadir.joinpath(
        f'{acc}.txt' if acc[:3] == 'GPL' else f'{acc}_family.soft.gz'
    ).resolve()
    cachefile = utils.cachedir().joinpath(f'{acc}.cache').resolve()

    # Load cached data if it exists
    if cachefile.is_file():
        try:
            if not silent: print(f'Loading cached data for {acc}')
            with open(cachefile, 'rb') as f:
                return pickle.load(f)
        except Exception as E:
            print(f"[bold red]Error loading cached data[/bold red]",
                  f"\n\n{E}", sep=' ')
    
    # Download, parse and cache data
    else:
        try:
            # Parse already downloaded data
            if os.path.isfile(geofile):
                if not silent:  print(f"Parsing {acc}")
                geodata = get_GEO(filepath=geofile.__str__(), silent=silent)

            # Download and parse data
            else:
                if not silent:  print(f"Downloading and parsing {acc}")
                geodata = get_GEO(acc, destdir=datadir, silent=silent)  #type: ignore
            
            # Cache data
            if cache:
                with open(cachefile, 'wb') as handle:
                    pickle.dump(geodata, file=handle)
            
            return geodata  #type: ignore

        except OSError as E:
            print("[bold red]Error[/bold red]: It seems you've entered",
                f"an invalid accession number.\n\n{E}", sep=' ')

        except Exception as E:
            print("[bold red]Error[/bold red]: Something went wrong.",
                f"\n\n{E}", sep=' ')


class cumida:
    """
    Class for loading datasets from the Curated Microarray Database 
    hosted by SBCB (sbcb.inf.ufrgs.br)

    Attributes
    ----------
    INDEX : str
        Path to the JSON file containing an index of all datasets in the
        database.
    BASEURL : str
        Base URL for downloading datasets from CuMiDa.

    Methods
    -------
    """

    INDEX = ''.join([
        "https://gist.githubusercontent.com/Kabilan108/",
        "3d11266abdd3c237d359dd7c11a40871/raw/"
        "34f204fc85241984f711e35f16571f222f2bb890/cumida.json"
    ])
    BASEURL = 'https://sbcb.inf.ufrgs.br'


    def __init__(self, datadir: str | Path=''):
        """
        Initialize the CuMiDa class.

        Parameters
        ----------
        datadir : str, optional
            Directory for storing downloaded data, will default to a 
            temporary directory if not specified
        """

        # Check inputs
        assert isinstance(datadir, str), 'datapath must be a string'
        if datadir == '':
            # Use a temporary directory
            datadir = utils.tempdir()
        elif not os.path.exists(datadir):
            os.makedirs(datadir);
        datadir = Path(datadir).resolve()

        # 
            
        

        pass

    def __repr__(self):
        """
        
        """

        pass

    def __str__(self):
        """
        
        """

        pass

if __name__  == '__main__':
    fire.Fire(geodlparse)
