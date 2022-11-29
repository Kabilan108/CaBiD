"""
CaBiD Differential Gene Expression Analysis
-------------------------------------------

This module contains functions for performing differential gene expression
analysis on the CuMiDa datasets, and generating results tables and figures.

Author: Tony Kabilan Okeke <tko35@drexel.edu>

Functions & Classes
-------------------
sort_normal
    Sort a pandas series so that normal samples are first
dge
    Perform differential gene expression analysis on a GSE dataset
"""

# Import modules
import seaborn as sns
import pandas as pd
import numpy as np
import re
from statsmodels.stats import multitest
from scipy import stats


def sort_normal(X: pd.Series):
    """Sort a Series so that normal samples are first"""

    def sorter(rgx: str, txt: str) -> str:
        """Sorting key for sorting a list of strings by a regex match"""
        r = re.search(rgx, txt)
        return r.group(0) if r else '{'

    return pd.Index([sorter('normal', x) for x in X])


def dge(gse: pd.DataFrame, fc_thr: float=2.0, p_thr: float=0.05):
    """
    Perform differential gene expression analysis on a GSE dataset.
    A Welch's t-test is performed for each gene, and the p-values are corrected
    for false discovery rate using the Benjamini-Hochberg method.

    Parameters
    ----------
    gse : pd.DataFrame
        A GSE dataset.
    fc_thr : float, optional
        A fold change threshold for differentially expressed genes, by default 2.0
    p_thr : float, optional
        A p-value threshold for differentially expressed genes, by default 0.05
    """

    # Compute fold changes and p-values
    dge = (gse.groupby('SAMPLE_TYPE').mean()
        .sort_index(key=sort_normal))
    fc = dge.iloc[0,:] - dge.iloc[1,:]  # Subtract because log transformed
    pvals = stats.ttest_ind(
        gse.filter(regex='normal', axis=0),
        gse.filter(regex='^((?!normal).)*$', axis=0),
        equal_var=False
    )

    # P-value correction
    adj_pvals = multitest.fdrcorrection(pvals.pvalue)[1]

    # Create dge table
    dge = pd.DataFrame({
        'fc': fc,
        'pval': pvals.pvalue,
        'adj pval': adj_pvals,
        '-log10(adj pval)': -np.log10(adj_pvals),
        'de': (adj_pvals < p_thr) & (abs(fc) > fc_thr)
    }).reset_index().rename(columns={'index': 'gene'})
    dge['de'] = dge['de'].replace({True: 'Significant', False: 'Non Significant'})

    return dge


def plot_volcano(ax, dge):
    """
    Create a volcano plot
    """

    ax.clear()
    sns.scatterplot(
        data=dge, x='fc', y='-log10(adj pval)', hue='de',
        ax=ax, s=20, alpha=0.5, palette=['#999999', '#ff0000']
    )
    ax.axhline(-np.log10(0.05), color='#999999', linestyle='--')
    ax.axvline(2, color='#999999', linestyle='--')
    ax.axvline(-2, color='#999999', linestyle='--')
    sns.move_legend(
        ax, "lower center", ncol=3, title=None,
        frameon=False, bbox_to_anchor=(.5, 1),
    )
    ax.grid()
    ax.set_xlabel('Fold Change')
    ax.set_ylabel('-log10(adj pvalue)')
    sns.despine()