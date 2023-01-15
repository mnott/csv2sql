# csv2sql

Parse a CSV file and generate a table for a MySQL Database.


# Overview

This script parses a CSV file and generates a table for a MySQL Database.
This is useful if you want to load a CSV file into a MySQL Database.
To do so, it will parse the CSV file and generate a table definition.
For each field, it will determine the maximum length of the field.


# Usage

Call the script with the -help as argument
to get the help function:

```bash
$ csv2sql.py --help
```

# Example

If you want to just parse the field
lengths of a CSV file, you can do it like this:

```bash
$ csv2sql.py parse my_file.csv
```


# Generate a Table

To generate a complete table, you can do it like this:

```bash
$ csv2sql.py -t my_file.csv
```


# Generate a Temporary Table

To generate a temporary table, you can do it like this:

```bash
$ csv2sql.py -tt my_file.csv
```


# Show the Content of a CSV File

To show the content of a CSV file, you can do it like this.

```bash
$ csv2sql.py show my_file.csv
```

The above command will only show the first 10 rows of the CSV file.
To show more rows, you can do it like this:

```bash
$ csv2sql.py show my_file.csv -r 100
```

To show all rows, you can do it like this:

```bash
$ csv2sql.py show my_file.csv -r -1
```


# Generate a CSV File

To show the content of a CSV file in CSV format, you can do it like this:

```bash
$ csv2sql.py show --csv my_file.csv
```

# Show, Rename, and Rearrange a Subset of Columns

If you want to rearrange, and rename columns, and also only show a subset of
the columns, you can do it like this:

```bash
$ csv2sql.py show -c "Tenant Product Type"=tpt -c "Solution Area"=solution_area
```
