"""
Tests for the utils module.

Author: Tony Okeke <tko35@drexel.edu>
"""

# Imports
import sys;  sys.path.append('src')
import utils

from rich import print


def test_SQLite():
    """
    Test SQLite
    """
    
    print('\n[cyan]Testing SQLite[/cyan]')

    try:
        path = (utils.tempdir() / 'test.db').resolve()
        db = utils.SQLite(path)
        db.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
        db.execute('INSERT INTO test (name) VALUES (?)', ('test',))
        db.execute('INSERT INTO test (name) VALUES (?)', ('test2',))
        df = db.select('SELECT * FROM test')
        assert df.shape == (2, 2)
        assert df['name'].tolist() == ['test', 'test2']
        db.close()
        path.unlink()
        print('\t[green]SQLite (normal) test passed[/green]')
    except Exception as e:
        print('\t[red]SQLite (normal) test failed[/red]\n', e)

    try:
        path = (utils.tempdir() / 'test.db').resolve()
        with utils.SQLite(path) as db:
            db.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
            db.execute('INSERT INTO test (name) VALUES (?)', ('test',))
            db.execute('INSERT INTO test (name) VALUES (?)', ('test2',))
            df = db.select('SELECT * FROM test')
            assert df.shape == (2, 2)
            assert df['name'].tolist() == ['test', 'test2']
            path.unlink()
        print('\t[green]SQLite (context manager) test passed[/green]')
    except Exception as e:
        print('\t[red]SQLite (context manager) test failed[/red]\n', e)


if __name__ == '__main__':
    print('[bold green]Running tests...[/bold green]')

    test_SQLite();
