"""
Predicting Gene Ontology Enrichment of Cancer Microarray Datasets Using 
Machine Learning
BMES 483/543 Final Project

Authors: Ethan Jacob Moyer <ejm374@drexel.edu>,
         Ifeanyi Osuchukwu <imo27@drexel.edu>,
         Tony Kabilan Okeke <tko35@drexel.edu>

Purpose: This module contains functions and classes for downloading and parsing
         data from GEO and CuMiDa as well as functions for enrichment analysis
         and machine learning.
"""

# Import modules
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import GEOparse
import requests
import pickle
import json
import re
import os
from sklearn.model_selection import LeaveOneOut
from statsmodels.stats import multitest
from urllib.request import urlretrieve
from tempfile import gettempdir
from scipy import stats
from tqdm import tqdm


def get_data_path():
    """
    Return path to data directory
    """

    if os.uname().nodename == 'KabilansPC':
        return "/mnt/h/data/bmes543proj/"
    else:
        path = os.path.join(gettempdir().replace('\\', '/'), 'MLGO')
        if not os.path.isdir(path):
            os.mkdir(path)
        return path


def geodlparse(acc: str, geodir: str="data/", quiet=True):
    """
    Download, parse and cache data from GEO

    @param acc
        GEO accession
    @param geodir
        Directory for storing downloaded GEO data
    @return
        parsed GEO data
    """


    # Download files
    try:
        # Specify file names
        names = [f'{acc}.txt', f'{acc}_family.soft.gz']
        geofile = os.path.join(geodir, names[0 if acc[:3] == 'GPL' else 1])
        cachefile = os.path.join(geodir, f"{acc}.pkl")

        if os.path.isfile(cachefile):
            # Load data if it has already been cached
            try:
                if not quiet: print('Loading cached data...')
                with open(cachefile, 'rb') as cache:
                    geodata =  pickle.load(cache)
                return geodata
            except Exception as e:
                print(f"ERROR: Loading cached file failed.\n{e}")
        else:
            if os.path.isfile(geofile):
                # If data has already been downloaded, parse it and cache results
                if not quiet: print('Already downloaded. Parsing...')
                geodata = GEOparse.get_GEO(filepath=geofile, silent=True)
            else:
                # Download and parse data
                if not quiet: print('Downloading and parsing...')
                geodata = GEOparse.get_GEO(acc, destdir=geodir, silent=True)
            # Cache data
            with open(cachefile, 'wb') as cache:
                pickle.dump(geodata, file=cache)
            return geodata
    except Exception as e:
        print(f"ERROR: Enter a valid GEO Accension\n{e}")


def get_go_info(goid: str) -> dict:
    """
    Retreive the name and definition of a GO term
    """

    if not re.match(r'GO:\d{7}', goid):
        raise ValueError('Provide a valid GO identifier.')

    server = "https://rest.ensembl.org/ontology/id/"
    r = requests.get(f"{server}{goid}", headers={'Accept': 'application/json'})
    r.raise_for_status()

    return {'name': r.json()['name'], 'descr': r.json()['definition']}


class Enrichment:
    """
    Gene Ontology Enricment
    """

    def __init__(self, gpl: pd.DataFrame):
        # Create master list of GO terms
        self.GO = np.unique([x for sub in gpl.GO.values for x in sub])
        self.GO_map = {v:i for i,v in enumerate(self.GO)}
        self.GO_map_rev = {i:v for i,v in enumerate(self.GO)}

        # Replace GO terms with numeric identifiers
        self.gpl = gpl
        self.gpl.GO = self.gpl.GO.apply(lambda x: [self.GO_map[i] for i in x])

        # Retrieve all GO terms
        self.go_all = np.array([i for sub in self.gpl.GO for i in sub])
        self.M = self.gpl.GO.shape[0]  # HGM Prameter

    def dge(self, gse: pd.DataFrame, group_col: str='type', p_thr: float=0.05, 
            fc_thr: float=1.5) -> tuple:
        """
        Differential Gene Expression 
        Identify and filter out differentially expressed genes in a GSE
        This function assumes expression values are log-transformed.

        @param gse: pd.DataFrame
            Expression data frame with features (genes) as columns and
            samples as rows; any non-numeric columns should be in the 
            data frame index
        @param gpl: pd.DataFrame
            Data frame with Gene IDs and lists of enriched GO terms
        @param group_col: str
            Column containing group (sample) labels; 
            GSE should contain only 2 groups
        @param p_thr: float
            significance threshold 
        @param fc_thr: float
            fold change threshold
        @return: tuple
            list of significant genes, and Series of fold change values
        """

        # Filter out any genes that aren't in the gpl 
        # (ones that do not correspond to GO terms)
        gse = gse.loc[:, gse.columns.isin(self.gpl.ID)]

        # Compute fold change and p-values
        deg = gse.groupby(group_col).mean()
        groups = gse.index.get_level_values(group_col).unique()
        if len(groups) > 2:
            raise ValueError(f"gse['{group_col}'] should contain only 2 groups")
        fc = deg.loc[groups[0], :] / deg.loc[groups[1], :]
        pvals = stats.ttest_ind(
            gse.filter(regex=groups[0], axis=0),
            gse.filter(regex=groups[1], axis=0)
        ).pvalue
        qvals = multitest.fdrcorrection(pvals)[1]  # FDR Correction

        # Create list of significantly differentially expressed genes
        I = (fc.values > fc_thr) | (fc.values < 1/fc_thr) & (qvals < p_thr)
        sig_genes = gse.columns[I].to_numpy()

        return sig_genes, fc

    def get_hgm_params(self, go_id: int) -> tuple:
        """
        Return parameters for a hypogeometric test for a specific go term
            x: Number of significant genes that are in this term
            M: total number of genes
            n: number of genes (significant or not) that are in this term
            N: total number of significant genes (ignore those with no GO term)
        @param go_sig: np.array
            List of significant GO Terms
        @param go_id: int
            Integer corresponding to a GO Term (mapped with self.GO_map)
        @return: tuple
            Parameters for the hypergeometric test
        """

        x = (self.go_sig == go_id).sum()
        n = (self.go_all == go_id).sum()
        return x, self.M, n, self.N

    def hgm_tests(self, sig_genes) -> pd.DataFrame:
        """
        Perform Hypergeometric Tests for GO enrichment
        """

        # Retrieve list of GO terms for significant genes
        sig = self.gpl[self.gpl.ID.isin(sig_genes)].GO
        self.go_sig = np.array([i for sub in sig for i in sub])
        self.N = sig.shape[0]  # HGM Parameter

        # Create list of GO terms to test for
        candidates = np.unique(self.go_sig)
        self.candidates = candidates

        # Create dataframe for storing results
        go_tests = pd.DataFrame(candidates)
        go_tests['GO Term'] = list( map(self.GO_map_rev.get, candidates) )
        
        # Hypergeometric Test
        go_tests['params'] = go_tests[0].apply(self.get_hgm_params)
        go_tests['p-value'] = go_tests['params'] \
            .apply(lambda x: stats.hypergeom.sf(*x))
        go_tests['q-value'] = multitest.fdrcorrection(go_tests['p-value'])[1]
        go_tests.drop([0, 'params'], axis=1, inplace=True)
        go_tests = go_tests[ go_tests['q-value'] < .01 ].reset_index(drop=True)

        return go_tests


class CuMiDa:
    """
    Class for loading data from CuMiDa
    """

    # Static attributes
    rawurl = 'https://gist.githubusercontent.com/mateuz/ce30e844f1a986c027c8e45c989cca40/raw/4f3c494104f3be11f113e22afede19b7bf120087/cumida.json'
    baseurl = 'https://sbcb.inf.ufrgs.br'

    def __init__(self, datapath: str="data/"):
        # Download list of datasets
        if not os.path.exists(f"{datapath}/cumida.json"):
            urlretrieve(CuMiDa.rawurl, f"{datapath}/cumida.json");

        # Load data
        with open(f"{datapath}/cumida.json", 'r') as file:
            data = pd.DataFrame( json.load(file) )

        # Organize data
        data['ID'] = 'GSE' + data['gse']
        data['Platform'] = 'GPL' + data['platform']
        data['csv_url'] = CuMiDa.baseurl + data['downloads'].apply(pd.Series)['csv']

        # Remove datasets with GPLs that don't have GO information
        data = data[~data.Platform.isin(['GPL10553', 'GPL17810', 'GPL13607', 'GPL19197'])]

        self.datasets = data \
            [['ID', 'type', 'Platform', 'classes', 'samples', 'genes']] \
            .rename({'type': 'Type', 'classes': 'Groups',
                     'samples': 'Samples', 'genes':'Genes'}, axis=1) \
            .set_index(['ID', 'Type'])
        self.MLPerformance = data.set_index(['ID', 'Platform']).scores \
            .apply(pd.Series)
        self.__downloads = data.set_index(['ID', 'type'])['csv_url'].to_dict()
        self.__datapath = datapath

    def download(self, data: pd.DataFrame) -> tuple:
        """
        Download dataset(s) from CuMiDa
        @param data
            Subset of self.datasets to download
        @param datapath
            Path to directory for storing data
        @return
            tuple that contains dataset identifiers ('GSE', 'Type')
        """

        # Retrieve dataset URLs
        try:
            if isinstance(data, pd.DataFrame):
                urls = [ self.__downloads[x] for x in data.index.to_list() ]
                self.dID = data.index.to_list()  # Dataset identifier
            elif isinstance(data, tuple):
                urls = [ self.__downloads[data] ]
                self.dID = [ data ]
        except:
            raise KeyError("Dataset not found.")
        
        # Download files
        datapath = self.__datapath
        self.paths = [datapath + re.search(r'\w+\.csv$', url)[0] for url in urls]
        for url, path in tqdm(zip(urls, self.paths)):
            if not os.path.exists(path):
                urlretrieve(url, path);

    def load_dataset(self, ID: tuple, load_gpl: bool=False) -> list:
        """
        Load a specified dataset, along with GOBP information from
        its GPL
        @param ID
            Dataset identifier  ('GSE', 'Type')
        @return
            list containig 2 DataFrames - the dataset, and corresponding
            GO BP terms
        """

        # Fix input
        if ID[1] == 'Head/Neck':
            ID = (ID[0], 'Throat')

        # Download dataset if necessary
        datapath = self.__datapath
        file = f"{datapath}{'_'.join(ID[::-1])}.csv"
        if not os.path.exists(file):
            self.download(ID)

        # Load dataset
        data = pd.read_csv(file).set_index(['samples', 'type'])

        # Download and parse GPL
        if load_gpl:
            acc = self.datasets.loc[(ID[0], slice(None)), 'Platform'][0]
            gpl = CuMiDa.load_gpl(acc)
            return data, gpl

        return data

    def load_gpl(self, acc: str):
        """
        Load GO Information from GPL
        """

        # Download gpl
        gpl = geodlparse(acc, geodir=self.__datapath)
        maker = gpl.metadata['manufacturer'][0]

        # Select GO column for different manufacturers
        if maker == 'Affymetrix':
            idcol = 'ID'
            go_col = 'Gene Ontology Biological Process'
            pattern = r'\d{7}'
        elif maker == 'Agilent Technologies':
            idcol = 'GB_ACC'
            go_col = 'GO_ID'            
            pattern = r'(?<=GO:)\d+'
        elif maker == 'Illumina Inc.':
            idcol = 'ID'
            go_col = 'Ontology_Process'
            pattern = r'(?<=goid )\d+'

        # Select GO information
        gpl = gpl.table[[idcol, go_col]] \
            .set_axis(['ID', 'GO'], axis=1) \
            .fillna('')
        gpl['GO'] = gpl['GO'] \
            .apply(lambda x: [f"GO:{y.rjust(7, '0')}" for y in re.findall(pattern, x)])
        gpl['GO'] = gpl['GO'].mask( gpl['GO'].apply(len) == 0 )

        return gpl.dropna()


def eval(clf, X, y):
    """
    This function returns the cross validation accuracy
    using the leave one out method.
    """

    loo = LeaveOneOut()
    scores = []

    if len(y.shape) >= 2:
        for i in range(y.shape[1]):
            t = y[:,i]
            for train_idx, test_idx in loo.split(X):
                X_train, X_test = X[train_idx], X[test_idx]
                y_train, y_test = t[train_idx], t[test_idx]

                clf.fit(X_train, y_train)

                scores.append( clf.score(X_test, y_test) )

            accuracy = np.mean(scores)
            std = np.std(scores)
    else:
        for train_idx, test_idx in loo.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            clf.fit(X_train, y_train)

            scores.append( clf.score(X_test, y_test) )

    accuracy = np.mean(scores)
    std = np.std(scores)

    return accuracy, std


def forwardsel(clf, X, y ):
    """
    Perform forward feature selection and return the best features
    """

    bestfeatures = []
    bestaccuracy = -1
    beststd = -1
    
    for i in range(X.shape[1]):
        bestaccuracy_iter = -1
        bestfeature_iter = -1
        beststd_iter = -1
        
        for col in range(X.shape[1]):
            if col in bestfeatures:
                # If col is already in features, continue/skip
                continue
            else:
                x = np.take(X, bestfeatures + [col], axis=1)
                accuracy, std = eval(clf, x, y)

            if accuracy > bestaccuracy_iter:
                bestaccuracy_iter = accuracy
                bestfeature_iter = col
                beststd_iter = std

        if bestaccuracy_iter > bestaccuracy:
            bestfeatures.append(bestfeature_iter)
            bestaccuracy = bestaccuracy_iter
            beststd = beststd_iter
        else:
            break 

    return bestaccuracy, beststd, bestfeatures


def accuracy_plot(go, score, err=None, xlab='', ylab='', title='', filename=None):
    """
    Create bar graph showing model accuracy
    """

    goterms = go.keys()
    x_pos = np.arange(len(goterms))
    acc = [ go[goterm][score] for goterm in goterms ]
    if err is not None:
        err = [ go[goterm][err] for goterm in goterms ]

    _, ax = plt.subplots(figsize=(6,4))
    ax.bar(x_pos, acc, yerr=err, align='center', alpha=.5, ecolor='black', capsize=8)
    ax.set_xlabel(xlab, fontsize=11)
    ax.set_ylabel(ylab, fontsize=11)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(goterms, rotation=90)
    ax.set_title(title, fontsize=12)
    ax.yaxis.grid(True)
    plt.tight_layout()
    
    if filename is not None:
        plt.savefig(filename)

    plt.show()