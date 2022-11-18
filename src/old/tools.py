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

