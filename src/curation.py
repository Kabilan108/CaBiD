"""
CaBiD Data Curation
-------------------

This module contains functions for curation of data from GEO and CuMiDa.

Author: Tony Kabilan Okeke <tko35@drexel.edu>

Functions & Classes
-------------------
geodlparse(acc, datadir='', silent=False, make_dir=False, cache=False)
    Download, parse and cache data from GEO.
    This fuction only downloads GSE and GPL data.
CuMiDa()
    Class for downloading gene expression matrices from GEO, parsing them and
    combining them with Ensembl gene IDs from the corresponding GPL.
curate
    Download the datasets from CuMiDa and build the CaBiD database.
CaBiD_check()
    Check if the CaBiD database exists and create it if it doesn't.

__main__
---------
This module can be run as a script to download, parse and cache data from GEO.
This script will download 21 cancer gene expression datasets from CuMiDa,
each of which was run on the Affymetrix Human Genome U133 Plus 2.0 Array
(GPL570). The selected datasets each include 2 classes - a 'normal' group and
a 'cancer' group. The script will store the gene expression data for each
patient in a SQLite database (CaBiD.db).
To locate the downloaded data, run the following command in a terminal:
    python -c "import utils; print(utils.datadir())"
"""

# Import necessary modules
from GEOparse.GEOTypes import GPL, GSE
from GEOparse import get_GEO
from tqdm.auto import tqdm
from pathlib import Path
from typing import Union
from rich import print

import json, os, re, warnings
import pandas as pd
import numpy as np

# Try to import cPickle
try:
    import _pickle as pickle  # This is faster
except ImportError:
    import pickle

# Import utilities
import utils


# Suppress DtypeWarning from GEOparse
warnings.filterwarnings(
    action='ignore',
    category=pd.errors.DtypeWarning,
    module='GEOparse'
)


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


class CuMiDa:
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
    index : pd.DataFrame
        Index of all datasets available from CuMiDa.
    datadir : str | Path
        Directory for storing downloaded data.
    gse_dir : str | Path
        Directory for storing downloaded GSE data.
    gpl_dir : str | Path
        Directory for storing downloaded GPL data.

    Methods
    -------
    download(acc: str, datadir: str | Path='', silent: bool=False, 
             make_dir: bool=False)
        Download a dataset from CuMiDa.
    load(dataset: tuple)
        Load a specified dataset, along with gene annotations from its GPL.
    """

    INDEX = ('https://gist.githubusercontent.com/Kabilan108/'
             '3d11266abdd3c237d359dd7c11a40871/raw/'
             'ff2af81ae70afaba99233400f9d79e30eb40942e/cumida.json')
    BASEURL = 'https://sbcb.inf.ufrgs.br'


    def __init__(self, datadir: Union[str, Path]='') -> None:
        """
        Initialize the CuMiDa class.

        Parameters
        ----------
        datadir : str or Path, optional
            Directory for storing downloaded data, will default to the
            project's data directory, utils.datadir() if not specified
        """

        # Check inputs
        assert isinstance(datadir, str) or isinstance(datadir, Path), \
            'datapath must be a string or PosixPath'
        if datadir == '': datadir = utils.datadir()
        if isinstance(datadir, str): datadir = Path(datadir)
        if not os.path.exists: os.makedirs(datadir);
        self.datadir = datadir.resolve()

        # Retrieve the index of datasets
        self._makeindex();

        # Create subdirectory for gene expression matrices and platforms
        self.gse_dir = self.datadir / 'GSE'
        self.gpl_dir = self.datadir / 'GPL'
        if not os.path.exists(self.gse_dir): os.makedirs(self.gse_dir)
        if not os.path.exists(self.gpl_dir): os.makedirs(self.gpl_dir)


    def _makeindex(self) -> None:
        """
        Create a dataframe containing the index of all datasets
        available from CuMiDa.
        """

        # Download the index
        file = (self.datadir / 'datasets.json').resolve().__str__()
        index = utils.downloadurl(self.INDEX, file, progress=False)

        # Load the dataset index
        with open(self.datadir / 'datasets.json', 'rb') as f:
            self.index = pd.DataFrame(json.load(f))

        # Clean up the columns
        self.index['ID'] = 'GSE' + self.index['gse'].astype(str)
        self.index['Platform'] = 'GPL' + self.index['platform'].astype(str)
        self.index['URL'] = self.BASEURL + \
            self.index['downloads'].apply(pd.Series)['csv']
        self.index = (self.index
            .rename(columns={'type': 'Type', 'classes': 'Classes', 
                             'samples': 'Samples', 'genes': 'Genes',
                             'manufacturer': 'Manufacturer'})
            [['ID', 'Platform', 'Manufacturer', 'Type', 'Classes', 'Samples', 
              'Genes', 'URL']]
            .sort_values(by=['Platform', 'Type'])
            .set_index(['ID', 'Type']))
        self._downloads = self.index['URL'].to_dict()


    def download(self, selected: pd.DataFrame | tuple | list) -> None:
        """
        Download selected datasets from CuMiDa.

        Parameters
        ----------
        selected : pd.DataFrame | tuple
            A subset of `self.index` containing the datasets to download.
            Or a tuple of (ID, Type) for a single dataset or a list of tuples.

        Returns
        -------
        None
        """

        try:
            if isinstance(selected, pd.DataFrame):
                urls = [self._downloads[x] for x in selected.index]
                self._selected = selected.index.to_list()
            elif isinstance(selected, tuple):
                urls = [self._downloads[selected]]
                self._selected = [selected]
            elif isinstance(selected, list):
                urls = [self._downloads[x] for x in selected]
                self._selected = selected
            else:
                raise TypeError('selected must be a DataFrame or tuple')
        except KeyError:
            raise KeyError('Dataset not found in CuMiDa index')

        # Download the GSE matrices from CuMiDa
        self.file_paths = [
            self.gse_dir / re.search(r'\w+\.csv', x)[0] for x in urls  #type: ignore
        ]
        if len(self.file_paths) > 1:
            with tqdm(total=len(urls), desc='Downloading GSEs') as pbar:
                for url, file in zip(urls, self.file_paths):
                    utils.downloadurl(url, file.__str__(), progress=False);
                    pbar.update(1)
        else:
            utils.downloadurl(urls[0], self.file_paths[0].__str__(), progress=False);

        # Download the GPLs from GEO
        self._gpl_accs = np.unique([
            self.index.loc[x]['Platform'] for x in self._selected
        ])
        self._gpls = dict()
        with tqdm(total=len(self._gpl_accs), desc='Downloading GPLs') as pbar:
            for acc in self._gpl_accs:
                self._gpls[acc] = geodlparse(acc, self.gpl_dir.__str__(), silent=True)
                pbar.update(1)


    def load(self, dataset: tuple) -> pd.DataFrame:
        """
        Load a specified dataset.

        Parameters
        ----------
        dataset : tuple
            A tuple of (ID, Type) for a single dataset.
        
        Returns
        -------
        gse : pd.DataFrame
        """

        # Check inputs
        assert isinstance(dataset, tuple), 'dataset must be a tuple'
        assert len(dataset) == 2, 'dataset must be a tuple of (ID, Type)'
        assert dataset in self.index.index, 'dataset not found in CuMiDa index'

        # Load the GSE
        path = self.gse_dir / f"{'_'.join(dataset[::-1])}.csv"
        gse = pd.read_csv(path).set_index(['samples', 'type'])

        try:
            # Rename GSE columns with GenBank IDs where possible
            gpl = self._gpls[self.index.loc[dataset]['Platform']].table
            gpl['GB_ACC'] = gpl['GB_ACC'].fillna(gpl['ID'])
            gse.columns = gse.columns.map(gpl.set_index('ID')['GB_ACC'])

            # Add numeric suffices to duplicate column names
            idx = (gse.columns.to_series()
                .groupby(level=0)
                .transform('cumcount'))
            gse.columns = gse.columns + '.' + idx.astype(str)

            # Sort columns alphabetically
            gse = gse.reindex(sorted(gse.columns), axis=1)
        except KeyError as E:
            print(f'No GenBank IDs found for {dataset[0]}')
            print(E)

        return gse


    def __repr__(self) -> str:
        """Return a string representation of the CuMiDa class"""

        return f'CuMiDa(datadir={self.datadir})'


    def __str__(self) -> str:
        """String representation of the CuMiDa class"""

        return self.__repr__()


def curate() -> None:
    # Initialize CuMiDa
    cumida = CuMiDa()

    # Select datasets from the CuMiDa index
    I = (cumida.index['Platform'] == 'GPL570') & (cumida.index['Classes'] == 2)
    selected = cumida.index.loc[I].index.tolist()

    # Download the selected datasets
    cumida.download(selected);

    # Initialize database connection
    dbpath = utils.datadir() / 'CaBiD.db'
    db = utils.CaBiD_db(dbpath)

    # Drop any existing tables
    db.drop_table('datasets')
    db.drop_table('expression')

    # Create the tables
    db.execute("""
    CREATE TABLE IF NOT EXISTS `datasets` (
        `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
        `GSE` VARCHAR(8) NOT NULL,
        `CANCER` VARCHAR(10) NOT NULL
    );
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS `expression` (
        `ID` INTEGER PRIMARY KEY AUTOINCREMENT,
        `DATASET_ID` INT NOT NULL,
        `SAMPLE_TYPE` VARCHAR(32) NOT NULL,
        `EXPRESSION` BLOB NOT NULL,
        FOREIGN KEY(`DATASET_ID`) REFERENCES `datasets`(`ID`)
    );
    """)

    # Populate the database with the selected datasets
    with tqdm(total=len(selected), desc="Building Database") as pbar:
        for i, gse_idx in enumerate(selected, start=1):
            # Populate the `datasets` table
            db.execute("""
            INSERT INTO `datasets` (`GSE`, `CANCER`) VALUES (?, ?);
            """, gse_idx)

            # Load the GSE matrix
            gse = cumida.load(gse_idx)

            # Populate the `expression` table
            samples = (gse.apply(lambda row: db.binarize(row), axis=1)
                .to_frame()
                .reset_index()
                .drop(columns='samples')
                .rename(columns={'type': 'SAMPLE_TYPE', 0: 'EXPRESSION'}))
            samples['DATASET_ID'] = i
            samples.to_sql('expression', db.conn, if_exists='append', index=False)

            pbar.update(1)


def CaBiD_check() -> None:
    """
    Check if the CaBiD database exists and create it if it doesn't.
    """
    dbpath = utils.datadir() / 'CaBiD.db'
    if not dbpath.exists():
        curate();
    else:
        with utils.CaBiD_db(dbpath) as db:
            if not (db.check_table('expression') and db.check_table('datasets')):
                curate();


if __name__ == '__main__':
    curate();
