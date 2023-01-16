# csv2sql

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

```bash
$ csv2sql.py --help
```

## Help about a command:

To get the help about a command, call the script with the command and the --help option:

```bash
$ csv2sql.py table --help
```

## Show the Table Definition of a file

### Show just the field lenghts

If you want to just parse the field lengths of a CSV file, you can do it like this:

```bash
$ csv2sql.py table my_file.csv
```

### Generate a Table Definition

To generate a complete table defintion, you can do it like this:

```bash
$ csv2sql.py table -t my_file.csv
```


#### Generate a Temporary Table

To generate a temporary table, you can do it like this:

```bash
$ csv2sql.py table -tt my_file.csv
```


## Parse a CSV (or Excel) file and optionally write it to a Database

### Show the Content of a CSV (or Excel) File

To show the content of a file, you can do it like this:

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

or also like this:

```bash
$ csv2sql.py parse my_file.csv -a
```

### Rename Columns

If you want to just rename some columns, but output all columns, you can do it like this:

```bash
$ csv2sql.py parse -n "Tenant Product Type"=tpt -n "Solution Area"=solution_area
```

### Show, Rename, and Rearrange a Subset of Columns

If you want to rearrange, and rename columns, and also only show a subset of
the columns, you can do it like this:

```bash
$ csv2sql.py parse -c "Tenant Product Type"=tpt -c "Solution Area"=solution_area
```

Note that if you did use the -n option, you can also use the -c option to
then further rearrange the columns.

### Omit Columns

If you want to omit some columns, you can do it like this:

```bash
$ csv2sql.py parse --omit "Tenant Product Type" --omit "Solution Area"
```

### Apply Regular Expressions to a Subset of Columns

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

### Type Conversions (Formats)

If you want to convert a column to a different type, you can do it like this:

```bash
$ csv2sql parse bla.csv -c fr_status -c creation_date -c posting_date -f fr_status=str -f 'posting_date=date(%Y-%m-%d)(%Y)'
```

Note that in the case of a date field, it is perhaps easier to see it as
a string and apply a regular expression to it:

```bash
$ csv2sql parse bla.csv -c fr_status -c creation_date -c posting_date -f fr_status=str -r posting_date='s/(\d\d\d\d)-.*/\1/'
```

Note that type conversions are applied on the original column names, not on the
potentially renamed columns.

Note also that if you give no type conversions, all columns are read as strings.

### Queries

If you want to generate a query, you can do it like this:

#### In Query

```bash
$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -r product_name=s/abc/def/ -q 'product_name contains "def"' -a
```

Note that replace statements are applied before the query is applied.

#### Not Empty Query

```bash
$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -q 'contact!=""' -a
```

#### Boolean Query

```bash
$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -c product_id -q 'contact!=""' -f product_id=int -q 'product_id>800300' -a
```

Note how we needed to convert the product_id column to an integer.

#### Here's a very complex query

```bash
$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -q 'contact!=""' -f product_id=int -q 'product_id>8003000' -q 'product_id<8004000' -q 'product_name contains "Ariba"' -q 'not contact 
contains "Olaf"' -a
```

#### Noteworthy

Not you typically need to use the -a option to query all rows, because the query
will only work on the rows that are actually shown.

### Sort the output

Here is an even more complex query showing how to sort the output:

```bash
$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -q 'contact!=""' -f product_id=int -q 'product_id>8003000' -q 'product_id<8004000' -a -q 'product_name contains "Ariba"' -q 'not contact 
contains "Olaf"' -o -product_id -o product_name
```

You can give any number of ordering options, and they will be applied in the order;
if you want to reverse the order, you can prefix the column with a minus sign.


### Generate a CSV File

To show the content of a CSV file in CSV format, you can do it like this:

```bash
$ csv2sql.py parse --csv
```

You can also directly pipe the output to a file:

```bash
$ csv2sql.py parse approvers.xlsx --csv > my_file.csv
```


### Generate an Excel File

To export the data to an Excel file, you can do it like this:

```bash
$ csv2sql.py parse approvers.csv --excel=my_file.xlsx
```


### Generate a JSON File

To export the data to a JSON file, you can do it like this:

```bash
$ csv2sql.py parse approvers.csv --json
```

You can also pretty print the JSON file:

```bash
$ csv2sql.py parse approvers.csv --pjson
```


### Generate an HTML File

To export the data to an HTML file, you can do it like this:

```bash
$ csv2sql.py parse approvers.csv --html
```


### Generate a Markdown File

To export the data to a Markdown file, you can do it like this:

```bash
$ csv2sql.py parse approvers.csv --markdown
```


### Generate a SQL Schema

To generate a SQL schema, you can do it like this:

```bash
$ csv2sql.py parse approvers.csv --sql
```


### Directly load the data into a Database

#### Show the database schema to be used

Before writing to the database, it may be a good idea to show the database schema
that will be used:

To directly load the data into a database, you can do it like this:

```bash
$ csv2sql.py parse approvers.csv --db
```

This will create a table called approvers in the database.

#### Use a prefix for the table name

If you want to use a prefix for the table name, you can do it like this:

```bash
$ csv2sql.py parse approvers.csv --db --prefix=_tp_
```

#### Use a different table name

If you want to use a different table name, you can do it like this:

```bash
$ csv2sql.py parse approvers.csv --db -t=approvers2
```

#### Use a different database

You can use a different database by specifying the database connection string and optionally the database type:

```bash
$ csv2sql.py parse approvers.csv --db --dbtype=mysql+pymysql --dbconn=user:password@dbhost:3306/mydb
$ csv2sql.py parse approvers.csv --db --dbtype=postgresql    --dbconn=user:password@dbhost:5432/mydb
```

#### Use special database connection parameters

You can use special database connection parameters by specifying the database connection string and optionally the database type:

```bash
$ csv2sql.py parse approvers.csv --db --dbtype=mysql+pymysql --dbconn=user:password@dbhost:3306/mydb?charset=utf8mb4
```

You can also use the dbargs option to specify the database connection parameters:

```bash
$ csv2sql.py parse approvers.csv --db --dbargs='{"charset": "utf8mb4", "use_unicode": "True", "connect_timeout": 10}'
```
