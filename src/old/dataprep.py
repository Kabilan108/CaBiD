"""
Predicting Gene Ontology Enrichment of Cancer Microarray Datasets Using 
Machine Learning
BMES 483/543 Final Project

Authors: Ethan Jacob Moyer <ejm374@drexel.edu>,
         Ifeanyi Osuchukwu <imo27@drexel.edu>,
         Tony Kabilan Okeke <tko35@drexel.edu>

Purpuse: This script is used to generate the dataset that will be used for the
         prediction of GO enrichment.
"""

# Imports
import pandas as pd
import pickle
import tools


def main(datapath: str):
    """
    Create ML dataset and labels (GO terms)
    """

    # Select and load datasets for analysis
    cumida = tools.CuMiDa(datapath=datapath)
    selected = cumida.datasets.query("Groups == 2 & Platform == 'GPL570'")
    cumida.download(selected)

    # Load the GPL
    gpl = cumida.load_gpl('GPL570')

    # Initialize class for GO enrichment analysis
    enrich = tools.Enrichment(gpl)

    # Load datasets, identify significantly differentially expressed genes,
    # and perform GO enrichment analysis for each dataset.
    FC, GO, exclude = dict(), dict(), list()

    for geoid in cumida.dID:
        gse = cumida.load_dataset(geoid)
        sig_genes, fc = enrich.dge(gse)

        if sig_genes.size == 0:
            print(f"Excluded {geoid}. No significant DEGs found.")
            exclude.append(geoid)
            continue

        go_tests = enrich.hgm_tests(sig_genes)
        go_tests['Dataset'] = '-'.join(geoid)
        go_tests.drop(['p-value', 'q-value'], axis=1, inplace=True)

        FC[ '-'.join(geoid) ] = fc
        GO[ '-'.join(geoid) ] = go_tests

    # Write selected datasets to file
    selected \
        .drop(exclude) \
        .reset_index() \
        .to_csv('results/selected_datasets.tsv', sep='\t', index=False)

    # Construct table of GO labels
    go_table = pd.concat(GO.values())
    go_table['val'] = 1
    go_table = go_table \
        .pivot(index='Dataset', columns='GO Term', values='val') \
        .fillna(0).astype(int) \
        .rename_axis('', axis=1)\
        .rename_axis('', axis=0)
    counts = go_table.sum()
    go_table = go_table[ counts.sort_values(ascending=False).index ]
    ## Keep only unique GO terms
    go_table = go_table.T.drop_duplicates().T

    # Construct table with fold changes
    #   Features (Gene fold-changes) = columns 
    #   Samples (Datasets) = rows
    df = pd.DataFrame(FC).T
    df = df.reindex(go_table.index, axis=0)

    # Pickle data
    with open(f"{datapath}/mldata.pkl", 'wb') as file:
        pickle.dump([df, go_table], file)
        print(f"ML Data written to file ({datapath}/mldata.pkl).")

    return df, go_table


if __name__ == '__main__':
    main()