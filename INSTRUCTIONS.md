# Project Guidelines and Deliverables

Your project should implement a Graphical User Interface or a Web Interface and
should include Database Programming. Each of the tasks available in your GUI or
Web interface should also be available programmatically, through functions.

## Coding Guidelines

- Include a README.md file (see [markdown syntax](https://help.github.com/articles/basic-writing-and-formatting-syntax/))
  that lists the the files in your project with a short description of what each
  file is.
  - Provide installation instructions for someone who wants to use run your
    code on their computer.
  - Provide command lines for installing any required Python packages.
  - Give links to any required software that need to be installed manually.
  
- Don't implement your application as one giant script or function.
  - Identify parts of your code that can be implemented as separate,
    self-contained, testable functions.
  - As much as your programming langague allows, use a separate file for each
    function.

- If you are getting data from the web, get it on-demand within your code (i.e.,
  download if it has not been downloaded before).
  - Store these files in a temporary folder or in a data folder.
  - If you are working in Matlab, python, or php, use the `bmes.tempdir()` or
    `bmes.datadir()` functions provided by the instructor. In other programming
    languages, implement similar functions.

- If you are using data files, don't use full-paths to access them. Others
  downloading your project files should be able to execute regardless of where
  they place the project files.
  - Make as few assumptions as possible regarding the file system your code is
    running and specify these assumptions in your README file.

- Keep large data files (e.g., image files, database files, GEO files) in a
  separate location on your computer than the project files.
  - Data files that individually or collectively exceed 10MB are considered
    large.

- Include database initialization code. When your program is executed, create
  and populate any missing database tables. You may use an Excel or Text file
  to keep initial data to populate the database with.

- If the database does not contain any non-reproduceable data (most projects
  fall into this category), keep the database in a folder outside your project
  (use `bmes.tempdir()` or `bmes.datadir()`).

- Be mindful of what information is “leaking”. E.g., do not include any journal
  and conference papers that are not in the public domain (instead, provide a
  URL for such publications).

- The projects may be made publicly available. Include your first name in your
  project documents and program files. Including your last name and email are
  optional.

- Web Projects should include an entry point: index.php or index.html. Desktop
  applications should have an entry file/script reflecting the name of the
  project. e.g., `'maingui_vaccinationhistory.mlapp'`

- If your project involves passwords, you must not store clear-text password on
  your computer. Someone having access to your computer should not be able to
  retrieve these passwords.

- If your project involves personal API keys or tokens (e.g., Google API token,
  Dropbox auth token, etc.), you must keep such tokens outside your project
  folder. Your README file should instruct the person installing your
  application to get their own tokens and where to store them.

## GUI/Webpage Sketch

For GUI or Webpage applications, provide a sketch of your application. This can
be a hand drawn sketch or one drawn in a software (e.g., powerpoint). Save your
sketch as sketch.png or sketch.jpg.

## Project Design

- Prepare a *flowchart* & design of your project, showing the user interaction,
  and relationship between the functions you will implement.

- Also include a *database schema*, listing tables and their fields.
  - You can use Powerpoint, Word, or any other program of your choice to create
    the graph and list your scripts/functions. You may also use a legible
    hand-drawing of the flowchart.

- Name your file `design.XYZ` (e.g., design.pptx or design.docx).
  - Use a single file for your flowchart & design if possible.
  - Make sure to label the relevant parts of your flowchart with your
    script/function names.

- In your design document, for each script/function, specify the input and
  output arguments and give a short description of what the function does; and
  who in your team will be working on that function.
  - Saying everybody works on every function is not acceptable, each
    script/function should have a primary author who is responsible for it.

- Sample Project Designs: [design.drosophilabrain.pdf](https://sacan.biomed.drexel.edu/lib/exe/fetch.php?rev=&media=course:bcomp2:proj:design.drosophilabrain.pdf) (database schema missing), [design.crisprgrna.docx](https://sacan.biomed.drexel.edu/lib/exe/fetch.php?rev=&media=course:bcomp2:proj:design.crisprgrna.docx)

## Project Presentation

- Create your presentation in a file named presentation.pptx. If you use Google
  Docs, export it as presentation.pptx. If you are using a slideshow editor that
  cannot export as a powerpoint file, then export it as presentation.pdf.

- You are to give a 10-15 minute presentation of your project. Your presentation
  will be graded based on how well you accomplish the following sections.

- **Title page** [5%, 0min]
  - Title, your name(s) (last names are recommended/optional).
  - If your project is based on a publication, include its reference.

- **Introduction - Problem description, Motivation** [5%, 1min, very brief]:
  - Why are we studying this problem?
  - What is the biomedical need? Public health stats, if available.

- **Introduction - Biology/Physiology** [15%, 2min]
  - Describe the underlying biology/physiology/physics/computerScience.
  - Find figures illustrating the system (remember to cite the sources).

- **Introduction - Goals** [15%, 2min]
  - What do you/authors hope to find/accomplish with this study?
  - Who are the target end users and use cases?
  - If successful, how will your findings/result influence our understanding or
    medical practice?

- **Experiments and Methods** [20%, 4min]
  - Describe the experiments/surveys that produced the datasets you are
    analyzing in your project.
  - Describe your analysis workflow. e.g, normalization, types of statistical
    tests, thresholds, etc.
  - Describe the methods and software you used. Describe any third party
    library/tool/module you utilized. If we covered it in the course, you do
    not need to go into detail.
  - *Using an ER diagram, show and describe the database schema.*

- **Results** [20%, 5min]
  - Demonstrate your application.
  - If this is a data analysis project, show your main findings.
  - Use figures (e.g., bar charts) instead of tables to present your results.
  - If applicable, compare your results to those from related publications.

- **Discussion** [20%, 2min]
  - If this is an analysis project, do your results make sense biologically?
    Find studies that support your findings. (E.g., you found 10 genes in your
    Alzheimer's dataset analysis, check literature to see if these genes are
    known for their involvement in Alzheimer's).
  - What are the limitations of your study?
  - What follow up studies can be performed to improve upon your findings or to
    extend your method/application?

## Project Report

- Submit a 2 to 3-page report.docx file. If you need to include multiple
  snapshots and images to demonstrate your application, you may go up to 5
  pages (there should still be 2 to 3-page worth of text in your report). Use
  the [template file](https://sacan.biomed.drexel.edu/lib/exe/fetch.php?rev=&media=course:bcomp2:proj:appreport_template.docx)
  to write your report. The template file describes the sections you need to
  include in your report.

- If you use Google Docs or other editor to write your report, please export
  your report as a Word document.

- The break-down of the grading of the report will be similar to the presentation.

## `index.yml` Summary File

Create a file named index.yml and enter your project's information
(title/author/abstract). The projects may become publicly available. For author
information, your first name(s) is required; last name(s) is recommended/optinal.
When entering abstract in multiple lines, place two spaces in each of the lines
after the first. See below for contents of an example `index.yml` file. You can
download this sample file as a template to change your information with.

```yaml
title: Pathway based functional analysis of IBD patients using metagenomic 
  analysis of human gut microbiome
author: Dhruv Sakalley, Brian, Ashley Wolf
abstract: Each of the additional lines of the abstract should be indented with 2
  spaces. The abstract should be ASCII-only, e.g., if you copy-paste from Word,
  replace smart-quotes with regular quotes. Replace non-ASCII special characters
  and symbols with ASCII characters. Human Gut Microbiome contains collection of
  diverse species which help carry out various functions for the proper
  functioning of the human body. However, IBD is a condition where the diversity
  of this microbiome is significantly altered. Little is known about the causes
  and effects of these variations in the present literature. The next generation
  sequencing techniques provide suitable data for Metagenomic analysis leading
  to identification of uncluttered microorganisms, and make it possible to get
  detailed functional insights into the functional footprint of these altered
  microorganisms. This study uses of KEGG pathways for mapping functionality of
  the diverse gene sets in order to better understand function level changes
  caused due to the altered microbiome in case of IBD.
```

## Project Thumbnail

Create an image file **thumb.png** that can be used as a cover image for your
project. Thumbnail image size should be between 100-1000 pixels wide and
100-1000 pixels high. The width should be greater or equal to height.
