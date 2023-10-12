"""
CaBiD Differential Gene Expression Analysis
-------------------------------------------

This module contains functions for performing differential gene expression
analysis on the CuMiDa datasets, and generating results tables and figures.

Author: Cooper Molloy <dm348@drexel.edu>

Functions & Classes
-------------------
sort_normal
    Sort a pandas series so that normal samples are first
dge
    Perform differential gene expression analysis on a GSE dataset
plot_volcano
    Create a volcano plot
plot_heatmap
    Create a heatmap of differentially expressed genes
"""

# Import modules
from matplotlib import colors, gridspec, patches, pyplot as plt
from statsmodels.stats import multitest
from scipy.cluster import hierarchy
from scipy.spatial import distance
from scipy import stats

import seaborn as sns
import pandas as pd
import numpy as np
import re


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
    dge = (pd.DataFrame({
        'fc': fc,
        'pval': pvals.pvalue,
        'adj pval': adj_pvals,
        '-log10(adj pval)': -np.log10(adj_pvals),
        'de': (adj_pvals < p_thr) & (abs(fc) > fc_thr)
    }).reset_index()
        .rename(columns={'index': 'gene'}))
    dge['de'] = dge['de'].replace({True: 'Significant', False: 'Non Significant'})

    return dge


def plot_volcano(ax, dge, fc_thr: float=2.0, p_thr: float=0.05):
    """
    Create a volcano plot
    """

    ax.clear()
    sns.scatterplot(
        data=dge, x='fc', y='-log10(adj pval)', hue='de',
        ax=ax, s=20, alpha=0.5, palette=['#999999', '#ff0000']
    )
    ax.axhline(-np.log10(p_thr), color='#999999', linestyle='--')
    ax.axvline(fc_thr, color='#999999', linestyle='--')
    ax.axvline(-fc_thr, color='#999999', linestyle='--')
    sns.move_legend(
        ax, "upper center", ncol=3, title=None,
        frameon=False,  bbox_to_anchor=(.5, 1.2),
    )
    ax.set_xlabel('Fold Change (Normal - Tumoral)')
    ax.set_ylabel('-log10(adj p-val)')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


def plot_heatmap(fig, axes, data):
    """
    Create a heatmap of all genes
    """

    # Clear figure
    fig.clf()

    # Create grid spec
    gs = gridspec.GridSpec(
        2, 4, width_ratios=[0.1, 0.04, 1, 0.02], height_ratios=[0.25, 1],
        wspace=0.02, hspace=0.02
    )

    # Define axes
    axes = dict(
        samp_dendro=fig.add_subplot(gs[1, 0]),
        gene_dendro=fig.add_subplot(gs[0, 2]),
        anot=fig.add_subplot(gs[1, 1]),
        hmap=fig.add_subplot(gs[1, 2]),
        cbar=fig.add_subplot(gs[1, 3]),
    )

    # Filter out genes by variance (keep the 99th percentile)
    data = data.loc[:, data.var() > data.var().quantile(0.99)]
    
    # Get values
    X = data.values

    # Cluster samples and plot dendrogram
    Y = hierarchy.linkage(X)
    with plt.rc_context({'lines.linewidth': 0.8}):
        Z1 = hierarchy.dendrogram(Y, orientation='left', ax=axes['samp_dendro'])
    axes['samp_dendro'].set_xticks([])
    axes['samp_dendro'].set_yticks([])
    for x in ['top', 'bottom', 'left', 'right']:
        axes['samp_dendro'].spines[x].set_visible(False)

    # Cluster genes and plot dendrogram
    Y = hierarchy.linkage(X.T)
    with plt.rc_context({'lines.linewidth': 0.4}):
        Z2 = hierarchy.dendrogram(Y, orientation='top', ax=axes['gene_dendro'])
    axes['gene_dendro'].set_xticks([])
    axes['gene_dendro'].set_yticks([])

    # Reorder data
    X = X[Z1['leaves'], :][:, Z2['leaves']]
    xlab = data.index.values[Z1['leaves']]

    # Annotation bar
    ## Create matrix for annotation bar
    annot = np.matrix([1 if re.search(r'normal', lab) else 0 for lab in xlab]).T
    ## Create color map
    cmap = colors.ListedColormap(['#33c442', '#c43333'])  # type: ignore
    norm = colors.BoundaryNorm([0, 0.5, 1], cmap.N)  # type: ignore
    ## Plot annotation bar
    axes['anot'].imshow(annot, aspect='auto', cmap=cmap, norm=norm)

    # Plot the heatmap
    sns.heatmap(X, cmap='YlOrBr_r', ax=axes['hmap'], cbar=False)

    # Add a colorbar
    axes.update({
        'cbar': fig.colorbar(axes['hmap'].collections[0], cax=axes['cbar'])
    })

    # Despine axes and remove ticks
    for axis in axes.values():
        if axis is axes['cbar']: continue
        for x in ['top', 'bottom', 'left', 'right']:
                axis.spines[x].set_visible(False)
        axis.set_xticks([])
        axis.set_yticks([])

    # Add legend below heatmap
    axes['hmap'].legend(
        handles=[
            patches.Patch(color='#33c442', label='Normal'),
            patches.Patch(color='#c43333', label='Tumor'),
        ],
        loc='upper center', bbox_to_anchor=(0.5, -0.005), ncol=2,
        frameon=False
    )
