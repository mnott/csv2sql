#!/usr/bin/env python
# encoding: utf-8
r"""

Parse a CSV file and generate a table for a MySQL Database.

# Overview

This script parses a CSV (or Excel) file and generates a table for a MySQL Database.
It can directly write to the database, and it can also generate a table definition.

This is useful if you want to load a CSV (or Excel) file into a MySQL Database.
To do so, it will parse the CSV file and generate a table definition.
For each field, it will determine the maximum length of the field.


# Usage

## General Help

Call the script with the -help as argument to get the help function:

$ csv2sql.py --help

## Help about a command:

To get the help about a command, call the script with the command and the --help option:

$ csv2sql.py table --help

## Show the Table Definition of a file

### Show just the field lenghts

If you want to just parse the field lengths of a CSV file, you can do it like this:

$ csv2sql.py table my_file.csv

### Generate a Table Definition

To generate a complete table defintion, you can do it like this:

$ csv2sql.py table -t my_file.csv


#### Generate a Temporary Table

To generate a temporary table, you can do it like this:

$ csv2sql.py table -tt my_file.csv


## Parse a CSV (or Excel) file and optionally write it to a Database

### Show the Content of a CSV (or Excel) File

To show the content of a file, you can do it like this:

$ csv2sql.py parse my_file.csv

The above command will only show the first 10 rows of the CSV file.
To show more rows, you can do it like this:

$ csv2sql.py parse my_file.csv -h 100

To show all rows, you can do it like this:

$ csv2sql.py parse my_file.csv -h -1

or also like this:

$ csv2sql.py parse my_file.csv -a

### Rename Columns

If you want to just rename some columns, but output all columns, you can do it like this:

$ csv2sql.py parse -n "Tenant Product Type"=tpt -n "Solution Area"=solution_area 

### Show, Rename, and Rearrange a Subset of Columns

If you want to rearrange, and rename columns, and also only show a subset of 
the columns, you can do it like this:

$ csv2sql.py parse -c "Tenant Product Type"=tpt -c "Solution Area"=solution_area 

Note that if you did use the -n option, you can also use the -c option to
then further rearrange the columns.

### Omit Columns

If you want to omit some columns, you can do it like this:

$ csv2sql.py parse --omit "Tenant Product Type" --omit "Solution Area"

### Apply Regular Expressions to a Subset of Columns

If you want to apply regular expressions to a subset of columns, you can do it like this:

$ csv2sql parse -h 5 bla.csv -c fr_id -c TID=tenant_id -replace tenant_id='s/S_0(.*)/\1/g'

You can also apply multiple regular expressions to a column:

$ csv2sql parse -h 5 bla.csv -c fr_id -c TID=tenant_id -r tenant_id='s/S_0(.*)/\1/g' -r tenant_id='s/74/99/g'

Note that regular expressions are applied in the order they are specified, on the
optionally renamed columns.

### Type Conversions (Formats)

If you want to convert a column to a different type, you can do it like this:

$ csv2sql parse bla.csv -c fr_status -c creation_date -c posting_date -f fr_status=str -f 'posting_date=date(%Y-%m-%d)(%Y)'

Note that in the case of a date field, it is perhaps easier to see it as
a string and apply a regular expression to it:

$ csv2sql parse bla.csv -c fr_status -c creation_date -c posting_date -f fr_status=str -r posting_date='s/(\d\d\d\d)-.*/\1/'

Note that type conversions are applied on the original column names, not on the
potentially renamed columns.

Note also that if you give no type conversions, all columns are read as strings.

### Queries

If you want to generate a query, you can do it like this:

#### In Query

$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -r product_name=s/abc/def/ -q 'product_name contains "def"' -a

Note that replace statements are applied before the query is applied.

#### Not Empty Query

$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -q 'contact!=""' -a

#### Boolean Query

$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -c product_id -q 'contact!=""' -f product_id=int -q 'product_id>800300' -a

Note how we needed to convert the product_id column to an integer.

#### Here's a very complex query

$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -q 'contact!=""' -f product_id=int -q 'product_id>8003000' -q 'product_id<8004000' -q 'product_name contains "Ariba"' -q 'not contact contains "Olaf"' -a

#### Noteworthy

Not you typically need to use the -a option to query all rows, because the query
will only work on the rows that are actually shown.

### Sort the output

Here is an even more complex query showing how to sort the output:

$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -q 'contact!=""' -f product_id=int -q 'product_id>8003000' -q 'product_id<8004000' -a -q 'product_name contains "Ariba"' -q 'not contact contains "Olaf"' -o -product_id -o product_name

You can give any number of ordering options, and they will be applied in the order; 
if you want to reverse the order, you can prefix the column with a minus sign.


### Generate a CSV File

To show the content of a CSV file in CSV format, you can do it like this:

$ csv2sql.py parse --csv 

You can also directly pipe the output to a file:

$ csv2sql.py parse approvers.xlsx --csv > my_file.csv


### Generate an Excel File

To export the data to an Excel file, you can do it like this:

$ csv2sql.py parse approvers.csv --excel=my_file.xlsx


### Generate a JSON File

To export the data to a JSON file, you can do it like this:

$ csv2sql.py parse approvers.csv --json

You can also pretty print the JSON file:

$ csv2sql.py parse approvers.csv --pjson


### Generate an HTML File

To export the data to an HTML file, you can do it like this:

$ csv2sql.py parse approvers.csv --html


### Generate a Markdown File

To export the data to a Markdown file, you can do it like this:

$ csv2sql.py parse approvers.csv --markdown


### Generate a SQL Schema

To generate a SQL schema, you can do it like this:

$ csv2sql.py parse approvers.csv --sql


### Directly load the data into a Database

#### Show the database schema to be used

Before writing to the database, it may be a good idea to show the database schema
that will be used:

To directly load the data into a database, you can do it like this:

$ csv2sql.py parse approvers.csv --db

This will create a table called approvers in the database.

#### Use a prefix for the table name

If you want to use a prefix for the table name, you can do it like this:

$ csv2sql.py parse approvers.csv --db --prefix=_tp_

#### Use a different table name

If you want to use a different table name, you can do it like this:

$ csv2sql.py parse approvers.csv --db -t=approvers2

#### Use a different database

You can use a different database by specifying the database connection string and optionally the database type:

$ csv2sql.py parse approvers.csv --db --dbtype=mysql+pymysql --dbuser=user --dbpass=pass --dbhost=localhost --dbport=3306 --dbschema=mydb
$ csv2sql.py parse approvers.csv --db --dbtype=postgresql    --dbuser=user --dbpass=pass --dbhost=localhost --dbport=5432 --dbschema=mydb

#### Use a different chunk size

You can use a different chunk size by specifying the chunk size:

$ csv2sql.py parse approvers.csv --db -cs=10000

This can have a significant impact on the performance of the database.


#### Use special database connection parameters

You can use special database connection parameters like so:

$ csv2sql.py parse approvers.csv --db --dbtype=mysql+pymysql --dbspecial=charset=utf8mb4

You can also use the dbargs option to specify the database connection parameters:

$ csv2sql.py parse approvers.csv --db --dbargs='{"charset": "utf8mb4", "use_unicode": "True", "connect_timeout": 10}'

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
import numpy as np
from pandas.io import sql
from sqlalchemy import create_engine, MetaData, Table, exc
import json
import os
from os import path
from pathlib import Path

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
# Global Variables
#
# The separator to use is held in a global variable
# because it is determined by the read_file function;
# that function returns a dataframe, but needs to
# save the separator for the write_file function that
# is called later by parse.
#
_separator = None


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
    sepr:       str  = typer.Option(None,   "--separator", "-s", "--sep",   help="The separator to use"),
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

    #
    # Set the global separator
    #
    global _separator
    if sepr is not None:
        _separator = sepr

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
    sepr:       str  = typer.Option(None,      "--separator", "-s", "--sep", help="The separator to use"),
    head:       int  = typer.Option(10,        "--head",      "-h",          help="The number of rows to show. -1 for all rows"),
    all:        bool = typer.Option(False,     "--all",       "-a",          help="Whether to show all rows or not"),
    columns:    List[str] = typer.Option(None, "--columns",   "-c",          help="The columns to show and their alternate names"),
    names:      List[str] = typer.Option(None, "--names",     "-n",          help="If you just want to rename columns, but not select them"),
    omit:       List[str] = typer.Option(None, "--omit",                     help="The columns to omit"),
    query:      List[str] = typer.Option(None, "--query",     "-q",          help="The query to apply to the specified columns"),
    replace:    List[str] = typer.Option(None, "--replace",   "-r",          help="The regular expressions to apply to the specified columns"),
    formats:    List[str] = typer.Option(None, "--formats",   "-f",          help="The formats to use for the specified columns"),
    unique:     List[str] = typer.Option(None, "--unique",    "-u",          help="The columns to unique on"),
    order:      List[str] = typer.Option(None, "--order",     "-o",          help="The sort order to use for the specified columns"),
    ascsv:      bool = typer.Option(False,     "--csv",                      help="Whether to output in CSV format or not"),
    asexcel:    str  = typer.Option(None,      "--excel", "-xls", "-xlsx",   help="The excel (xlsx) file to write to"),
    asjson:     bool = typer.Option(False,     "--json",                     help="Whether to output in JSON format or not"),
    aspjson:    bool = typer.Option(False,     "--pjson",                    help="Whether to output in pretty JSON format or not"),
    ashtml:     bool = typer.Option(False,     "--html",                     help="Whether to output in HTML format or not"),
    asmd:       bool = typer.Option(False,     "--md",                       help="Whether to output in Markdown format or not"),
    assql:      bool = typer.Option(False,     "--sql",                      help="Whether to output in SQL format or not"),
    db:         bool = typer.Option(False,     "--db",        "-db",         help="Whether to write to the database or not"),
    chunk_size: int  = typer.Option(10000,     "--chunk_size","-cs",         help="The chunksize to use for writing to the database"),
    dbtable:    str  = typer.Option(None,      "--table",     "-t",          help="The database table to write to"),
    prefix:     str  = typer.Option("",        "--prefix",    "-p",          help="The prefix to use for the table name"),
    dbhost:     str  = typer.Option("tc",      "--dbhost",    "-dh",         help="The database host to connect to"),
    dbport:     int  = typer.Option(3306,      "--dbport",    "-dp",         help="The database port to connect to"),
    dbuser:     str  = typer.Option("tc",      "--dbuser",    "-du",         help="The database user to connect as"),
    dbpass:     str  = typer.Option("sap123",  "--dbpass",    "-dp",         help="The database password to connect with"),
    dbschema:   str  = typer.Option("tc",      "--dbschema",  "-ds",         help="The database schema to connect to"),
    dbspecial:  str  = typer.Option(None,      "--dbspecial", "-dss",        help="The database specials to use for the connection"),
    dbtype:     str  = typer.Option("mysql+pymysql",           "--dbtype",   help="The database type"),
    dbargs:     str  = typer.Option('{"connect_timeout": 10}', "--dbargs",   help="The database connection arguments to use"),
    files:      Optional[List[str]] = typer.Argument(None,                   help="The files to process"),
) -> None:
    """
    Parse CSV files to generate MySQL tables
    """

    #
    # Set the global separator
    #
    global _separator
    if sepr is not None:
        _separator = sepr

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
            if formats:
                #
                # If we have types, we need to apply them
                #
                converters = {}
                converter_dict = {
                    'int':   lambda x: int(re.sub(r'[^0-9.]', '', x)) if x else None,
                    'float': lambda x: float(re.sub(r'[^0-9.]', '', x)) if x else None,
                    'str':   str,
                }
                for t in formats:
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
                    df = read_file(file, sepr, -1, converters)
                else:
                    df = read_file(file, sepr, head, converters)

            #
            # If we don't have types, we can just read the file
            #
            else:
                if head == -1 or all:
                    # df = pd.read_csv(file, sep=sepr, dtype=str)
                    df = read_file(file, sepr, -1)
                else:
                    # df = pd.read_csv(file, sep=sepr, nrows=head, dtype=str)
                    df = read_file(file, sepr, head)

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
            # If we are asked to query, do it
            #
            if query:
                for q in query:
                    q = re.sub(r'(\w+) contains "(.*)"', r'\1.str.contains("\2")', q)
                    df = df.query(f"{q}", engine='python') # This is safe, as we are using pandas

            #
            # If asked to drop duplicates, do it
            #
            if unique:
                df = df.drop_duplicates(unique)

            #
            # If asked to sort, do it
            #
            if order:
                sortvalues = []
                sortorders = []
                for o in order:
                    if o.startswith("-"):
                        sortvalues.append(o[1:])
                        sortorders.append(False)
                    else:
                        sortvalues.append(o)
                        sortorders.append(True)
                df = df.sort_values(sortvalues, ascending=sortorders)

            #
            # If asked to output in HTML format, do it
            #
            if ashtml:
                print(df.to_html(index=False))

            #
            # If asked to output in markdown format, do it
            #
            elif asmd:
                print(df.to_markdown(index=False))

            #
            # If asked to output in SQL format, do it
            #
            elif assql:
                if dbtable is None: # If no table name is given, we use the file name
                    dbtable = Path(file).stem # We use the stem of the file name, without the extension
                if prefix != "": # If we have a prefix, we add it to the table name
                    dbtable = f"{prefix}{dbtable}"                
                if dbargs is not None:
                    connect_args = json.loads(dbargs)
                else:
                    connect_args = {}
                if dbspecial is not None:
                    dbspecial = f"?{dbspecial}"
                else:
                    dbspecial = ""
                engine=create_engine(f"{dbtype}://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbschema}{dbspecial}", echo=True, connect_args=connect_args)
                sql_stmt = sql.get_schema(df, dbtable, con=engine)
                print(f"{sql_stmt}")

            #
            # If asked to write to DB, do it
            #
            elif db:
                if dbtable is None: # If no table name is given, we use the file name
                    dbtable = Path(file).stem # We use the stem of the file name, without the extension
                if prefix != "": # If we have a prefix, we add it to the table name
                    dbtable = f"{prefix}{dbtable}"
                if dbargs is not None: # If we have DB args, we use them
                    connect_args = json.loads(dbargs)
                else:
                    connect_args = {}
                total_rows = len(df)
                if chunk_size > total_rows:
                    chunk_size = total_rows//1000 # Calculate the chunk size
                    if chunk_size == 0:
                        chunk_size = total_rows // 100
                        if chunk_size == 0 or chunk_size < 100:
                            chunk_size = 100
                if dbspecial is not None:
                    dbspecial = f"?{dbspecial}"
                else:
                    dbspecial = ""                            
                engine=create_engine(f"{dbtype}://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbschema}{dbspecial}", echo=False, connect_args=connect_args) # We create the engine

                #
                # First drop the table
                #
                meta = MetaData() # We create the metadata
                try:
                    table = Table(dbtable, meta, autoload_with=engine) # We load the table
                    if table.exists():
                        table.drop(bind=engine, checkfirst=True) # We drop the table
                except exc.NoSuchTableError:
                    pass #print(f"Table {dbtable} does not exist.")

                #
                # Insert the data
                #
                with Progress() as progress:
                    task = progress.add_task(f"Writing {total_rows} in chunks of {chunk_size} to {dbtable}", total=total_rows)
                    for i, chunk in enumerate(np.array_split(df, total_rows // chunk_size + 1)):
                        chunk.to_sql(dbtable, engine, if_exists='append', index=False)
                        progress.update(task, advance=chunk_size)           
                        connection = engine.raw_connection()
                        connection.commit()     
                print(f"Done writing [magenta]{total_rows}[/magenta] rows to [green]{dbtable}[/green].")
               
            #
            # If asked to output in JSON format, do it
            #
            elif asjson:
                print(df.to_json(orient='records'))

            #
            # If asked to output in pretty JSON format, do it
            #
            elif aspjson:
                print(df.to_json(orient='records', indent=4))

            #
            # If asked to output in Excel format, do it
            #
            elif asexcel is not None:
                df.to_excel(asexcel, index=False)

            #
            # If asked to output in CSV format, do it.
            # Otherwise, output in table format
            #
            elif ascsv:
                if sepr is None:
                    sepr = _separator
                df.to_csv(sys.stdout, sep=sepr, index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar='"',escapechar='\\')
            
            #
            # If all else fails, output table
            #
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
# Read a file and output it in a dataframe
#
def read_file(filename: str, separator: str = None, rows: int = -1, converters = None ) -> pd.DataFrame:
    global _separator
    file_ext = os.path.splitext(filename)[1]
    if file_ext == '.csv': # If it's a CSV file, use pandas
        if separator: # If we have a separator, use it
            if rows > -1: # If we have a number of rows, use it
                if converters: # If we have converters, use them
                    return pd.read_csv(filename, sep=separator, nrows=rows, converters=converters)
                else: # If we don't have converters, don't use them
                    return pd.read_csv(filename, sep=separator, nrows=rows, dtype=str)
            else: # If we don't have a number of rows, read the whole file
                if converters: # If we have converters, use them
                    return pd.read_csv(filename, sep=separator, converters=converters)
                else: # If we don't have converters, don't use them
                    return pd.read_csv(filename, sep=separator, dtype=str)
        else: # If we don't have a separator, try to auto-detect it
            with open(filename, 'r') as f:
                dialect = csv.Sniffer().sniff(f.readline()) # Try to auto-detect the separator
                f.seek(0) # Go back to the beginning of the file
                if _separator is None:
                    _separator = dialect.delimiter # Set the global separator
                if rows > -1: # If we have a number of rows, use it
                    if converters: # If we have converters, use them
                        return pd.read_csv(filename, sep=dialect.delimiter, nrows=rows, converters=converters)
                    else: # If we don't have converters, don't use them
                        return pd.read_csv(filename, sep=dialect.delimiter, nrows=rows, dtype=str)
                else: # If we don't have a number of rows, read the whole file
                    if converters: # If we have converters, use them
                        return pd.read_csv(filename, sep=dialect.delimiter, converters=converters)
                    else: # If we don't have converters, don't use them
                        return pd.read_csv(filename, sep=dialect.delimiter, dtype=str)
    elif file_ext in ('.xls', '.xlsx'): # If we have an Excel file, use the Excel reader     
        return pd.read_excel(filename)
    else: # If we have an unsupported file type, raise an error
        raise ValueError(f"Invalid file format: {file_ext}. Only CSV, XLS, and XLSX are supported.")


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
    with Progress() as progress: # Create a progress bar
        task = progress.add_task(f"Parsing {file}", total=nrows)
        df = read_file(file, sepr, -1)

        rows = 0
        rows_skipped = 0

        if head is not None and head > 0:
            rows_skipped = head

        #
        # Get the column names and lengths
        #
        hdrs = []
        for hdr in df.columns:
            hdr = f"{hdr}".lower()
            hdr = re.sub(r'[^^a-zA-Z0-9,]', '_', hdr)
            maxl = len(hdr) if maxl < len(hdr) else maxl
            hdrs.append(hdr)

        #
        # Iterate through the rows
        #
        for index, row in df.iterrows():
            progress.update(task, advance=1)
            rows += 1
            if rows_skipped > 0:
                rows_skipped -= 1
                continue
            col = 0
            for item in row:
                if col >= len(cols):
                    cols.append(len(f"{item}"))
                else:
                    cols[col] = len(f"{item}") if cols[col] < len(f"{item}") else cols[col]
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

