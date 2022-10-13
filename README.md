# <--Project Title-->

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

```bash
# Set up conda environment
conda env create -f environment.yml
conda activate project

```

## File path assumptions
