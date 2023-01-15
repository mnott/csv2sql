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
$ csv2sql.py table my_file.csv
```


# Generate a Table

To generate a complete table, you can do it like this:

```bash
$ csv2sql.py table -t my_file.csv
```


# Generate a Temporary Table

To generate a temporary table, you can do it like this:

```bash
$ csv2sql.py table -tt my_file.csv
```


# Show the Content of a CSV File

To show the content of a CSV file, you can do it like this.

```bash
$ csv2sql.py parse my_file.csv
```

The above command will only show the first 10 rows of the CSV file.
To show more rows, you can do it like this:

```bash
$ csv2sql.py parse my_file.csv -h 100
```

To show all rows, you can do it like this:

```bash
$ csv2sql.py parse my_file.csv -h -1
```

or alls like this:

```bash
$ csv2sql.py parse my_file.csv -a
```

# Rename Columns

If you want to just rename some columns, but output all columns, you can do it like this:

```bash
$ csv2sql.py parse -n "Tenant Product Type"=tpt -n "Solution Area"=solution_area
```


# Show, Rename, and Rearrange a Subset of Columns

If you want to rearrange, and rename columns, and also only show a subset of
the columns, you can do it like this:

```bash
$ csv2sql.py parse -c "Tenant Product Type"=tpt -c "Solution Area"=solution_area
```

Note that if you did use the -n option, you can also use the -c option to
then further rearrange the columns.


# Omit Columns

If you want to omit some columns, you can do it like this:

```bash
$ csv2sql.py parse -o "Tenant Product Type" -o "Solution Area"
```


# Apply Regular Expressions to a Subset of Columns

If you want to apply regular expressions to a subset of columns, you can do it like this:

```bash
$ csv2sql parse -h 5 bla.csv -c fr_id -c TID=tenant_id -replace tenant_id='s/S_0(.*)/\1/g'
```

You can also apply multiple regular expressions to a column:

```bash
$ csv2sql parse -h 5 bla.csv -c fr_id -c TID=tenant_id -r tenant_id='s/S_0(.*)/\1/g' -r tenant_id='s/74/99/g'
```

Note that regular expressions are applied in the order they are specified, on the
optionally renamed columns.


# Type Conversions

If you want to convert a column to a different type, you can do it like this:

```bash
$ csv2sql parse bla.csv -c fr_status -c creation_date -c posting_date -t fr_status=str -t 'posting_date=date(%Y-%m-%d)(%Y)'
```

Note that in the case of a date field, it is perhaps easier to see it as
a string and apply a regular expression to it:

```bash
$ csv2sql parse bla.csv -c fr_status -c creation_date -c posting_date -t fr_status=str -r posting_date='s/(\d\d\d\d)-.*/\1/'
```

Note that type conversions are applied on the original column names, not on the
potentially renamed columns.

Note also that if you give no type conversions, all columns are read as strings.


# Generate a CSV File

To show the content of a CSV file in CSV format, you can do it like this:

```bash
$ csv2sql.py parse --csv my_file.csv
```
