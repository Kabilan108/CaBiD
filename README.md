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

## Project Sketch

![Project Sketch](Project Sketch.jpg)

## Database Schema

![Database Schema](ERD.png)

## Usage

Run the following commands in your terminal to set up the environment for
running our application, build the database, and run the application.  

> **Note:** The CaBiD GUI depends on wxPython, which may not be compatible with
> some Linux distributions. If you are using Linux, you may need to install
> gtk3 and wxPython from [source](https://wxpython.org/pages/downloads/).
> Also, for grading purposes, please use the `bmes550` branch of this repository.

```bash
# Clone the repository
git clone -b bmes550 git@github.com:Kabilan108/CaBiD.git
cd CaBiD

# Set up conda environment
conda env create -f env.yml
conda activate cabid

# Download necessary data and build the project database
python src/curation.py
```

## The Dataset

21 cancer gene expression datasets were selected from the Curated Microarray
Database, [CuMiDa](https://sbcb.inf.ufrgs.br/cumida). Each dataset was
generated on the Affymetrix Human Genome U133 Plus 2.0 Array (GPL570). The
selected datasets each include 2 classes - a 'normal' group and a 'cancer'
group. The GPL570 array contains 54,676 probes. The table below shows the GSE
accession numbers, cancer types, and sample sizes for each dataset.

| Cancer Type |   Samples | GEO Accession |
|:-----------:|:---------:|:-------------:|
| Bladder     |        85 | GSE31189      |
| Breast      |       116 | GSE42568      |
| Breast      |        12 | GSE26910      |
| Colorectal  |        63 | GSE8671       |
| Colorectal  |        33 | GSE32323      |
| Colorectal  |        18 | GSE41328      |
| Gastric     |        24 | GSE19826      |
| Gastric     |        20 | GSE79973      |
| Leukemia    |        46 | GSE71935      |
| Liver       |        91 | GSE62232      |
| Lung        |       114 | GSE19804      |
| Lung        |        90 | GSE18842      |
| Lung        |        48 | GSE27262      |
| Pancreatic  |        51 | GSE16515      |
| Prostate    |        49 | GSE46602      |
| Prostate    |        17 | GSE55945      |
| Prostate    |        12 | GSE26910      |
| Renal       |       143 | GSE53757      |
| Renal       |        28 | GSE66270      |
| Throat      |       103 | GSE42743      |
| Throat      |        40 | GSE12452      |

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
