# Cancer Biomarker Discovery (CaBiD) Project

**Authors:** [Tony Kabilan Okeke](mailto:tonykabilanokeke@gmail.com),
             [Ali Youssef](mailto:amy57@drexel.edu),
             [Cooper Molloy](mailto:cdm348@drexel.edu)

## Project Proposal

The goal of this project is to develop a web application to investigate 
variations in gene expression across various cancer types. Datasets selected 
from GEO (Gene Expression Omnibus) and CuMiDa (Curated Microarray Database) 
will be preprocessed and curated in a SQLite database. The Dash library (python) 
will then be used to develop a web application that will generate interactive 
visualizations of the curated dataset. The software will identify key 
differences in gene expression between healthy controls and patients with 
various types of cancer. The web application will include interactive heatmaps 
to illustrate the expression of various genes in the selected cancer type.

## The Dataset

34 curated microarray datasets across 11 cancer types were selected and
downloaded from the Curated Microarray Database (CuMiDa); each experiment
was run on Affymetrix GeneChip microarrays. The table below shows the
GSE accession numbers, cancer type, and sample size for each dataset.

| Cancer Type | Platform   |   Samples |   Genes | GSE Accession   |
|:-----------:|:----------:|:---------:|:-------:|:---------------:|
| Bladder     | GPL570     |        85 |   54676 | GSE31189        |
| Breast      | GPL570     |       116 |   54676 | GSE42568        |
| Breast      | GPL570     |        12 |   54676 | GSE26910        |
| Colorectal  | GPL3921    |       105 |   22278 | GSE44861        |
| Colorectal  | GPL570     |        63 |   54676 | GSE8671         |
| Colorectal  | GPL570     |        33 |   54676 | GSE32323        |
| Colorectal  | GPL570     |        18 |   54676 | GSE41328        |
| Gastric     | GPL570     |        24 |   54676 | GSE19826        |
| Gastric     | GPL570     |        20 |   54676 | GSE79973        |
| Leukemia    | GPL97      |        52 |   22646 | GSE22529_U133B  |
| Leukemia    | GPL96      |        52 |   22284 | GSE22529_U133A  |
| Leukemia    | GPL570     |        46 |   54676 | GSE71935        |
| Leukemia    | GPL571     |        25 |   22278 | GSE14317        |
| Liver       | GPL571     |       357 |   22278 | GSE14520_U133A  |
| Liver       | GPL570     |        91 |   54676 | GSE62232        |
| Liver       | GPL3921    |        41 |   22278 | GSE14520_U133_2 |
| Liver       | GPL96      |        36 |   22284 | GSE60502        |
| Lung        | GPL570     |       114 |   54676 | GSE19804        |
| Lung        | GPL570     |        90 |   54676 | GSE18842        |
| Lung        | GPL96      |        51 |   22284 | GSE7670         |
| Lung        | GPL570     |        48 |   54676 | GSE27262        |
| Pancreatic  | GPL570     |        51 |   54676 | GSE16515        |
| Prostate    | GPL8300    |       124 |   12626 | GSE6919_U95Av2  |
| Prostate    | GPL92      |       124 |   12621 | GSE6919_U95B    |
| Prostate    | GPL93      |       115 |   12647 | GSE6919_U95C    |
| Prostate    | GPL570     |        49 |   54676 | GSE46602        |
| Prostate    | GPL570     |        17 |   54676 | GSE55945        |
| Prostate    | GPL570     |        12 |   54676 | GSE26910        |
| Renal       | GPL570     |       143 |   54676 | GSE53757        |
| Renal       | GPL570     |        28 |   54676 | GSE66270        |
| Renal       | GPL97      |        20 |   22646 | GSE6344_U133B   |
| Renal       | GPL96      |        20 |   22284 | GSE6344_U133A   |
| Throat      | GPL570     |       103 |   54676 | GSE42743        |
| Throat      | GPL570     |        40 |   54676 | GSE12452        |

## Folder Structure

```
.
├── design.pdf          [Contains project sketch and flowchart]
├── env.yml             [Contains project dependencies]
├── index.yml           [Contains project details]
├── INSTRUCTIONS.md     [Contains instructions for BMES 550 project]
├── LICENSE.md          [Project license]
├── notes.md            [Contains meeting notes and todo items]
├── presentation.pptx   [Contains presentation slides]
├── README.md           [Contains project description and installation instructions]
├── report.docx         [Contains project report]
├── report.pdf          [Contains project report]
├── src                 [Contains project source code]
│   ├── dataprep.py     [Script for preparing the machine learning dataset]
│   ├── project.ipynb   [Notebook for running analysis]
│   └── tools.py        [Module with custom functions and classes]
└── thumb.png           [Project thumbnail]
```

## API-Keys

## Usage

This project depends on the `wxPython` package which requires additional
installation steps for Linux machines. See the
[wxPython documentation](https://wxpython.org/pages/downloads/) for more details.
The instructions below will work on Windows and MacOS.

```bash
# Set up conda environment
conda env create -f env.yml
conda activate cabid

# Run the app
```

## File path assumptions
