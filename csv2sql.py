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

Call the script with the -help as argument
to get the help function:

$ csv2sql.py --help

# Example

If you want to just parse the field
lengths of a CSV file, you can do it like this:

$ csv2sql.py table my_file.csv


# Generate a Table

To generate a complete table, you can do it like this:

$ csv2sql.py table -t my_file.csv


# Generate a Temporary Table

To generate a temporary table, you can do it like this:

$ csv2sql.py table -tt my_file.csv


# Show the Content of a CSV File

To show the content of a CSV file, you can do it like this.

$ csv2sql.py parse my_file.csv

The above command will only show the first 10 rows of the CSV file.
To show more rows, you can do it like this:

$ csv2sql.py parse my_file.csv -h 100

To show all rows, you can do it like this:

$ csv2sql.py parse my_file.csv -h -1

or alls like this:

$ csv2sql.py parse my_file.csv -a

# Rename Columns

If you want to just rename some columns, but output all columns, you can do it like this:

$ csv2sql.py parse -n "Tenant Product Type"=tpt -n "Solution Area"=solution_area 


# Show, Rename, and Rearrange a Subset of Columns

If you want to rearrange, and rename columns, and also only show a subset of 
the columns, you can do it like this:

$ csv2sql.py parse -c "Tenant Product Type"=tpt -c "Solution Area"=solution_area 

Note that if you did use the -n option, you can also use the -c option to
then further rearrange the columns.


# Omit Columns

If you want to omit some columns, you can do it like this:

$ csv2sql.py parse -o "Tenant Product Type" -o "Solution Area"


# Apply Regular Expressions to a Subset of Columns

If you want to apply regular expressions to a subset of columns, you can do it like this:

$ csv2sql parse -h 5 bla.csv -c fr_id -c TID=tenant_id -replace tenant_id='s/S_0(.*)/\1/g'

You can also apply multiple regular expressions to a column:

$ csv2sql parse -h 5 bla.csv -c fr_id -c TID=tenant_id -r tenant_id='s/S_0(.*)/\1/g' -r tenant_id='s/74/99/g'

Note that regular expressions are applied in the order they are specified, on the
optionally renamed columns.


# Type Conversions

If you want to convert a column to a different type, you can do it like this:

$ csv2sql parse bla.csv -c fr_status -c creation_date -c posting_date -t fr_status=str -t 'posting_date=date(%Y-%m-%d)(%Y)'

Note that in the case of a date field, it is perhaps easier to see it as
a string and apply a regular expression to it:

$ csv2sql parse bla.csv -c fr_status -c creation_date -c posting_date -t fr_status=str -r posting_date='s/(\d\d\d\d)-.*/\1/'

Note that type conversions are applied on the original column names, not on the
potentially renamed columns.

Note also that if you give no type conversions, all columns are read as strings.


# Generate a CSV File

To show the content of a CSV file in CSV format, you can do it like this:

$ csv2sql.py parse --csv my_file.csv

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
    To get help about the parser, call it with the --help option.
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
def table (
    ctx:        typer.Context,
    sepr:       str  = typer.Option(",",    "--separator", "-s", "--sep",   help="The separator to use"),
    table:      bool = typer.Option(False,  "--table",     "-t",            help="Whether to create a table or not"),
    temporary:  bool = typer.Option(False,  "--temptable", "-tt",           help="Whether to create a temporary table or not"),  
    prefix:     str  = typer.Option("",     "--prefix",    "-p",            help="The prefix to use for the table name"),
    dir:        str  = typer.Option(None,   "--dir",       "-d",            help="The load directory on the Server"),
    head:       int  = typer.Option(0,      "--head",      "-h",            help="The number of header lines to skip"),
    compressed: bool = typer.Option(False,  "--compressed", "-c",           help="Whether to use ROW_FORMAT=COMPRESSED or not"),
    idx:        Optional[List[str]] = typer.Option(None, "--index", "-i",   help="The index to use for the table"),
    files:      Optional[List[str]] = typer.Argument(None,                  help="The files to process; optionally use = to specify the table name"),
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
# Parse the Content of a CSV File and optionally convert it to a csv file
#
#@app.callback(invoke_without_command=True)
@app.command()
def parse (
    ctx:        typer.Context,
    sepr:       str  = typer.Option(",",       "--separator", "-s", "--sep", help="The separator to use"),
    head:       int  = typer.Option(10,        "--head",      "-h",          help="The number of rows to show. -1 for all rows"),
    all:        bool = typer.Option(False,     "--all",       "-a",          help="Whether to show all rows or not"),
    columns:    List[str] = typer.Option(None, "--columns",   "-c",          help="The columns to show and their alternate names"),
    names:      List[str] = typer.Option(None, "--names",     "-n",          help="If you just want to rename columns, but not select them"),
    omit:       List[str] = typer.Option(None, "--omit",      "-o",          help="The columns to omit"),
    replace:    List[str] = typer.Option(None, "--replace",   "-r",          help="The regular expressions to apply to the specified columns"),
    types:      List[str] = typer.Option(None, "--types",     "-t",          help="The types to use for the specified columns"),
    ascsv:      bool = typer.Option(False,     "--csv",                      help="Whether to output in CSV format or not"),
    files:      Optional[List[str]] = typer.Argument(None,                   help="The files to process"),
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
        #
        # If asked to select columns, do it, and rename them if asked
        #
        if columns:
            for col in columns:
                if col.find("=") == -1:
                    selected_columns.append(col)
                else:
                    temp = col.split("=")
                    rename[temp[0]] = temp[1]
                    selected_columns.append(temp[1])

        #
        # If asked to rename columns, do it
        #
        if names:
            for col in names:
                if col.find("=") == -1:
                    print("Please specify a column name and its alternate name using =")
                    sys.exit(1)
                else:
                    temp = col.split("=")
                    rename[temp[0]] = temp[1]

        #
        # Read the files
        #
        for file in files: #ctx.args:
            #
            # Read the file
            #            
            if types:
                #
                # If we have types, we need to apply them
                #
                converters = {}
                converter_dict = {
                    'int':   lambda x: int(re.sub(r'[^0-9.]', '', x)) if x else None,
                    'float': lambda x: float(re.sub(r'[^0-9.]', '', x)) if x else None,
                    'str':   str,
                }
                for t in types:
                    col, col_type = t.split("=")
                    #
                    # If the type is date, we need to parse the format
                    # This is hard: we need to find the date format, and the output format.
                    # We then need to create lambda functions that will convert the date to the output format.
                    # As we need to create a given format for each given column, we need to use eval() to create the lambda function.
                    # This is not safe, but as a simple command line tool, not too much of a problem.
                    #
                    if col_type.startswith("date"):
                        m = re.search('date\((.*?)\)\((.*?)\)', col_type)
                        if m:
                            date_type = m.group(1)
                            output_format = m.group(2)
                            converter_dict[col] = eval(f"lambda x: pd.to_datetime(x, format=\"{date_type}\").strftime(\"{output_format}\") if x else None")
                            col_type="date"
                        else:
                            print(f"Missing date format for column {col}. Skipping.")
                    if col_type in converter_dict: # For a normal type, we just use the converter
                        converters[col] = converter_dict[col_type]
                    elif col_type == "date": # For a date, we use the converter we created above
                        converters[col] = converter_dict[col]
                    else: # For anything else, we skip
                        print(f"Invalid type {col_type} for column {col}. Skipping.")

                #
                # Read in the file
                #
                if head == -1 or all:
                    df = pd.read_csv(file, sep=sepr, converters=converters)
                else:
                    df = pd.read_csv(file, sep=sepr, nrows=head, converters=converters)
            #
            # If we don't have types, we can just read the file
            #
            else:
                if head == -1 or all:
                    df = pd.read_csv(file, sep=sepr, dtype=str)
                else:
                    df = pd.read_csv(file, sep=sepr, nrows=head, dtype=str)

            #
            # Deal with missing values
            #
            df = df.fillna("")

            #
            # If asked to rename columns, do it
            #
            if rename:
                df = df.rename(columns=rename)

            #
            # If asked to select, and reorder columns, do it
            #
            if selected_columns:
                df = df[selected_columns]

            #
            # If asked to omit columns, do it
            #
            if omit:
                for col in omit:
                    if col in df.columns:
                        df = df.drop(col, axis=1)


            #
            # If asked to do regexes, do them
            #
            if replace:
                replace_columns = {}
                for rep in replace:
                    temp = rep.split("=")
                    if len(temp) == 2:
                        replace_columns[temp[0]] = temp[1]
                    else:
                        replace_columns[temp[0]] = temp[1]
                    if replace_columns:
                        for col in replace_columns:
                            if col in df.columns:
                                rep = replace_columns[col]
                                match = re.match(r's/([^/]*)/([^/]*)/([g|i]*)', rep)
                                if match:
                                    search, replace, flags = match.groups()
                                    if 'g' in flags:
                                        df[col] = df[col].apply(lambda x: re.sub(search, replace, x))
                                    else:
                                        df[col] = df[col].apply(lambda x: re.sub(search, replace, x, 1))
                                else:
                                    print(f"Invalid replace string {rep}")

            #
            # If asked to output in CSV format, do it.
            # Otherwise, output in table format
            #
            if ascsv:
                df.to_csv(sys.stdout, sep=sepr, index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar='"',escapechar='\\')
            else:
                table = rich.table.Table(show_header=True, header_style="bold magenta")
                for col in df.columns:
                    table.add_column(col, justify="left", style="cyan", no_wrap=False)
                #
                # If asked to output a certain number of lines, but not all, do it
                #
                if head > -1 and not all:
                    for row in df.head(head).itertuples(index=False):
                        table.add_row(*[str(i) for i in row])
                #
                # Else if asked to output all lines, do it
                #
                else:
                    for row in df.itertuples(index=False):
                        table.add_row(*[str(i) for i in row])
                print(table)


#
# Count the number of lines in a file
#
def file_len(file_path):
    with open(file_path, "r") as f:
        for i, l in enumerate(f):
            pass
    return i + 1


#
# Process a file
#
def run(file, sepr, table, temporary, prefix, dir, head, compressed, idx): 
    cols = []
    hdrs = []
    maxl = 0
    sum_field_length = 0
    result = ""
    hash_result = ""

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
        add_line = ""
        if table:
            add_line += f"  {hdr} varchar({cols[i]})"
            add_line += "," if i < len(hdrs)-1 or len(idx) >= 0 else ""
            add_line += "\n"
        else:
            add_line += f"{i+1:2} {hdr} : {cols[i]:3}\n"
        result += add_line
        hash_result += add_line


    #
    # Create the hash
    #
    hash_str = hashlib.md5(hash_result.encode()).hexdigest()[:4]
    hash_int = struct.unpack('<L', hash_str.encode())[0]
    hash_str = f"{hash_int:,}"


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

