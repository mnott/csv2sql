#!/usr/bin/env python
# encoding: utf-8
r"""

Parse a CSV file and generate a table for a MySQL Database.

# Overview

This script parses a CSV file and generates a table for a MySQL Database.
This is useful if you want to load a CSV file into a MySQL Database.
To do so, it will parse the CSV file and generate a table definition.
For each field, it will determine the maximum length of the field.

# Usage

Call the script with the -h as argument to get the help function:

$ csv2sql.py -h

# Example

If you want to just parse the field lengths of a CSV file, you can do it like this:

$ csv2sql.py my_file.csv

# To generate a complete table, you can do it like this:

$ csv2sql.py -t my_file.csv

# To generate a temporary table, you can do it like this:

$ csv2sql.py -tt -t my_file.csv



"""

#
# Imports
#
import warnings
import sys
import pprint
import re
import csv
import hashlib
import struct
import pandas as pd

from os import path

#
# More Beautiful Tracebacks and Pretty Printing
#
import pydoc
from io import StringIO
from rich import print;
from rich import traceback;
from rich import pretty;
from rich.progress import Progress
import rich.table # used to print a table
from rich.console import Console
pretty.install()
traceback.install()


#
# Command Line Interface
#
from typing import List, Optional
import typer

app = typer.Typer(
    add_completion = False,
    rich_markup_mode = "rich",
    no_args_is_help=True,
    help="Parse CSV files to generate MySQL tables",
    epilog="""
    To get help about the parser, call it with the --help option:
./csv2sql.py parse --help
    """
)

@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)


#
# Main
#
#@app.callback(invoke_without_command=True)
@app.command()
def parse (
    ctx:        typer.Context,
    sepr:       str  = typer.Option(",",    "--separator", "-s", "--sep",   help="The separator to use"),
    table:      bool = typer.Option(False,  "--table", "-t",                help="Whether to create a table or not"),
    temporary:  bool = typer.Option(False,  "--temptable", "-tt",           help="Whether to create a temporary table or not"),  
    prefix:     str  = typer.Option("",     "--prefix", "-p",               help="The prefix to use for the table name"),
    dir:        str  = typer.Option(None,   "--dir", "-d",                  help="The load directory on the Server"),
    head:       int  = typer.Option(0,      "--head", "-h",                 help="The number of header lines to skip"),
    compressed: bool = typer.Option(False,  "--compressed", "-c",           help="Whether to use ROW_FORMAT=COMPRESSED or not"),
    idx:        Optional[List[str]] = typer.Option(None, "--index", "-i",   help="The index to use for the table"),
    files:      Optional[List[str]] = typer.Argument(None,                  help="The files to process"),
) -> None:
    """
    Parse CSV files to generate MySQL tables
    """
    if len(files) == 0: # len(ctx.args) == 0:
        print("Please specify a file name.")
        sys.exit(1)
    else:
        for file in files: #ctx.args:
            run(file, sepr, table, temporary, prefix, dir, head, compressed, idx)
    

#
# Show the Content of a CSV File and optionally convert it to a csv file
#
#@app.callback(invoke_without_command=True)
@app.command()
def show (
    ctx:        typer.Context,
    sepr:       str  = typer.Option(",",       "--separator", "-s", "--sep", help="The separator to use"),
    rows:       int  = typer.Option(None,      "--rows", "-r",               help="The number of rows to show"),
    columns:    List[str] = typer.Option(None, "--columns", "-c",            help="The columns to show and their alternate names"),
    ascsv:      bool = typer.Option(False,     "--csv",                      help="Whether to output in CSV format or not"),
    files:      Optional[List[str]] = typer.Argument(None,                   help="The files to process; optionally use = to specify the table name"),
) -> None:
    """
    Parse CSV files to generate MySQL tables
    """
    if len(files) == 0: # len(ctx.args) == 0:
        print("Please specify a file name.")
        sys.exit(1)
    else:
        rename = {}
        selected_columns = []
        if columns:
            for col in columns:
                if col.find("=") == -1:
                    selected_columns.append(col)
                else:
                    temp = col.split("=")
                    rename[temp[0]] = temp[1]
                    selected_columns.append(temp[1])
        for file in files: #ctx.args:
            if rows is None:
                df = pd.read_csv(file, sep=sepr)
            else:
                df = pd.read_csv(file, sep=sepr, nrows=rows)
            df = df.fillna("")
            if rename:
                df = df.rename(columns=rename)
            if selected_columns:
                df = df[selected_columns]
            if ascsv:
                df.to_csv(sys.stdout, sep=sepr, index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar='"',escapechar='\\')
            else:
                table = rich.table.Table(show_header=True, header_style="bold magenta")
                for col in df.columns:
                    table.add_column(col, justify="left", style="cyan", no_wrap=False)
                for row in df.head(rows).itertuples(index=False):
                    table.add_row(*[str(i) for i in row])
                print(table)




def file_len(file_path):
    with open(file_path, "r") as f:
        for i, l in enumerate(f):
            pass
    return i + 1









#
# Command: Doc
#
@app.command()
def doc (
    ctx:        typer.Context,
    title:      str  = typer.Option(None,   help="The title of the document"),
    toc:        bool = typer.Option(False,  help="Whether to create a table of contents"),
) -> None:
    print("doc")
    """
    Re-create the documentation and write it to the output file.
    """
    import importlib
    import importlib.util
    import sys
    import os
    import doc2md

    def import_path(path):
        module_name = os.path.basename(path).replace("-", "_")
        spec = importlib.util.spec_from_loader(
            module_name,
            importlib.machinery.SourceFileLoader(module_name, path),
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        return module

    mod_name = os.path.basename(__file__)
    if mod_name.endswith(".py"):
        mod_name = mod_name.rsplit(".py", 1)[0]
    atitle = title or mod_name.replace("_", "-")
    module = import_path(__file__)
    docstr = module.__doc__
    result = doc2md.doc2md(docstr, atitle, toc=toc, min_level=0)
    print(result)



#
# Process a file
#
def run(file, sepr, table, temporary, prefix, dir, head, compressed, idx): 
    cols = []
    hdrs = []
    maxl = 0
    sum_field_length = 0
    result = ""

    tablename=file
    if file.find("=") > -1:
        temp = file.split("=")
        file = temp[0]
        tablename = temp[1]

    abs_path = path.abspath(file)

    nrows = file_len(file)
    with Progress() as progress:
        task = progress.add_task(f"Parsing {file}", total=nrows)
        csv_reader = csv.reader(open(file, 'r', encoding='utf8'), delimiter=sepr, quotechar='\"')

        rows = 0
        rows_skipped = 0

        if head is not None and head > 0:
            rows_skipped = head

        #
        # Get the column names and lengths
        #
        for row in csv_reader:
            progress.update(task, advance=1)
            rows += 1
            if rows_skipped > 0:
                rows_skipped -= 1
                continue
            if rows == 1:
                hdrs = row
                for hdr in hdrs:
                    hdr = hdr.lower()
                    hdr = re.sub(r'[^^a-zA-Z0-9,]', '_', hdr)
                    maxl = len(hdr) if maxl < len(hdr) else maxl
                continue
            else:
                col = 0
                for item in row:
                    if col >= len(cols):
                        cols.append(len(item))
                    else:
                        cols[col] = len(item) if cols[col] < len(item) else cols[col]
                    col += 1

    #
    # Create the table header
    #
    if temporary:
        table = True
        temporary = "TEMPORARY "
    else:
        temporary = ""

    if table:
        if tablename.endswith('.csv'):
            tablename = path.splitext(tablename)[0]
        tablename = tablename.lower()
        result += f"DROP {temporary}TABLE IF EXISTS `{prefix}{tablename}`;\n"
        result += f"CREATE {temporary}TABLE `{prefix}{tablename}` (\n"


    #
    # Create the table content
    #
    maxl += 4  # Add some space
    for i, hdr in enumerate(hdrs):
        hdr = f"`{hdr}`".ljust(maxl)
        sum_field_length += cols[i]
        if table:
            result += f"  {hdr} varchar({cols[i]})"
            result += "," if i < len(hdrs)-1 or len(idx) >= 0 else ""
            result += "\n"
        else:
            result += f"{i+1:2} {hdr} : {cols[i]:3}\n"

    #
    # Create the table footer
    #
    if table:
        if(len(idx) > 0):
            for i, idx_col in enumerate(idx):
                result += f"  index({idx_col})"
                result += "," if i < len(idx)-1 else ""
                result += "\n"
        result += ") ENGINE=InnoDB DEFAULT CHARSET=utf8"

        if compressed and temporary == "":
            result += f" ROW_FORMAT=COMPRESSED"

        result += ";\n\n"

        file = path.basename(file)
        if dir is not None:
            result += f"load data infile '{dir}/{file}' into table `{prefix}{tablename}`\n"
        else:
            result += f"load data infile '{abs_path}' into table `{prefix}{tablename}`\n"
        result += f"  fields terminated by '{sepr}'\n"
        result += "  optionally enclosed by '\"'\n"
        result += "  ignore "
        if head is not None and head > 0:
            result += f"{head + 1}"
        else:
            result += "1"
        result += " rows;\n"


    #
    # Create the hash
    #
    hash_str = hashlib.md5(result.encode()).hexdigest()[:4]
    hash_int = struct.unpack('<L', hash_str.encode())[0]
    hash_str = f"{hash_int:,}"

    #
    # Add the total field length and the hash to the result
    #
    formatted_rows = "{:,}".format(rows)
    formatted_length = "{:,}".format(sum_field_length)
    result += f"\n-- Rows: {formatted_rows}. Sum of Field Lengths: {formatted_length}. Hash: {hash_str}.\n"

    #
    # Return the result
    #
    print(result)


#
# Command: Doc
#
@app.command()
def doc (
    ctx:        typer.Context,
    title:      str  = typer.Option(None,   help="The title of the document"),
    toc:        bool = typer.Option(False,  help="Whether to create a table of contents"),
) -> None:
    print("doc")
    """
    Re-create the documentation and write it to the output file.
    """
    import importlib
    import importlib.util
    import sys
    import os
    import doc2md

    def import_path(path):
        module_name = os.path.basename(path).replace("-", "_")
        spec = importlib.util.spec_from_loader(
            module_name,
            importlib.machinery.SourceFileLoader(module_name, path),
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        return module

    mod_name = os.path.basename(__file__)
    if mod_name.endswith(".py"):
        mod_name = mod_name.rsplit(".py", 1)[0]
    atitle = title or mod_name.replace("_", "-")
    module = import_path(__file__)
    docstr = module.__doc__
    result = doc2md.doc2md(docstr, atitle, toc=toc, min_level=0)
    print(result)


#
# Entry Point
#
if __name__ == '__main__':
    try:
        app()
    except SystemExit as e:
        if e.code != 0:
            raise

