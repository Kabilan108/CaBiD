"""
Tests for the curation module.

Author: Tony Okeke <tko35@drexel.edu>
"""

# Imports
import sys;  sys.path.append('src')
import curation
import utils
import shutil
from rich import print


def test_geodlparse():
    """
    Test the geodlparse function
    """

    print('\n[cyan]Testing geodlparse[/cyan]')

    datadir = utils.tempdir()

    try:
        gse = curation.geodlparse('GSE1000', datadir=datadir, 
                                  silent=True, cache=True)
        assert gse.name == 'GSE1000'
        print('\t[green]GSE Download (fresh, cache creation) passed[/green]')
    except Exception as e:
        print('\t[red]GSE Download (fresh, cache creation) failed[/red]\n', e)

    try:
        gse = curation.geodlparse('GSE1000', datadir=datadir, silent=True)
        assert gse.name == 'GSE1000'
        print('\t[green]GSE Download (load cache) passed[/green]')
    except Exception as e:
        print('\t[red]GSE Download (load cache) failed[/red]\n', e)

    try:
        gpl = curation.geodlparse('GPL570', datadir=datadir, 
                                  silent=True, cache=True)
        assert gpl.name == 'GPL570'
        print('\t[green]GPL Download (fresh, cache creation) passed[/green]')
    except Exception as e:
        print('\t[red]GPL Download (fresh, cache creation) failed[/red]\n', e)

    try:
        gpl = curation.geodlparse('GPL570', datadir=datadir, silent=True)
        assert gpl.name == 'GPL570'
        print('\t[green]GPL Download (load cache) passed[/green]')
    except Exception as e:
        print('\t[red]GPL Download (load cache) failed[/red]\n', e)

    shutil.rmtree(datadir)


if __name__ == '__main__':
    print('[bold green]Running tests...[/bold green]')

    test_geodlparse();
