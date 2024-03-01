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

### Sample just a small part of the file

You can use the `-m` option to sample just a small part of the file:

```bash
$ csv2sql.py table -m 100 my_file.csv
```

Note that this will not give you the correct field lengths, but it will give you a
more or less good idea of the field lengths - depending on how big your sample is.
For a guaranteed correct result, you should use the `-m -1` option or not use
the `-m` option at all. The `-a` option is a shortcut for `-m -1`.


### Generate a Table Definition

To generate a complete table defintion, you can do it like this:

```bash
$ csv2sql.py table -t my_file.csv
```

### Generate a Temporary Table

To generate a temporary table, you can do it like this:

```bash
$ csv2sql.py table -tt my_file.csv
```

### Change the Table Name

To change the table name, you can do it like this:

```bash
$ csv2sql.py table -t my_file.csv=my_table_name
```

By default, the table name is the name of the CSV file, without the extension.

### Add a Prefix to the Table Name

To add a prefix to the table name, you can do it like this:

```bash
$ csv2sql.py table -t my_file.csv -p _tmp_
```

By default, the prefix is empty.

### Overwrite the input directory

To overwrite the input directory, you can do it like this:

```bash
$ csv2sql.py table -t my_file.csv -d /opt/data/input/import
```

By default, the input directory is the current directory.

### Define the number of lines to skip

To define the number of lines to skip, you can do it like this:

```bash
$ csv2sql.py table -t my_file.csv -h 2
```

### Rename Columns

If you want to just rename some columns, you can do it like this:

```bash
$ csv2sql.py table -n "Tenant Product Type"=tpt -n "Solution Area"=solution_area -n 12=product_id
```

Note that you can rename by name or by column index (1-based).

### Format Columns

If you want to format some columns, you can do it like this:

```bash
$ csv2sql.py table -f "Tenant Product Type"="varchar(?) DEFAULT NULL" -f product_id="int(?) DEFAULT NULL" -f "Solution Area"="varchar(256) DEFAULT NULL"
```

Note that you can use the ? as a placeholder for the maximum length of the column.

### Specify default DEFAULT values

If you want to specify default DEFAULT values for all columns, you can do it like this:

```bash
$ csv2sql.py table -D "DEFAULT NULL"
```

This is going to be added to each column definition unless it was given a format (see above).

### Use indices

If you want to use indices, you can do it like this:

```bash
$ csv2sql.py table -t my_file.csv -i tpt -i solution_area,product_id
```

If you use more than one column, an index be composite.

### Use COMPRESSED row format

If you want to use the COMPRESSED row format, you can do it like this:

```bash
$ csv2sql.py table -t -c my_file.csv
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
$ csv2sql.py parse my_file.csv -m 100
```

### Paging

There are two ways to page through the results:

- You can define the number of rows to even read from the input file,
  and how many rows to skip at the beginning:

```bash
$ csv2sql.py parse my_file.csv -m 10 -h 5
```

The above command reads 10 rows from the input file, skipping the first 5 rows.

If you want to read all rows, you can do it like this:

```bash
$ csv2sql.py parse my_file.csv -m -1
```

or

```bash
$ csv2sql.py parse my_file.csv -a
```

The `-a` option is a shortcut for `-m -1`. It will become familiar to you
as this is what is often needed when you want to filter the input file.


- You can define the number of rows that you want to output, independent from
  the number of rows that you read from the input file:

```bash
$ csv2sql.py parse my_file.csv -M 10 -H 5
```

The above command shows 10 rows of the output, skipping the first 5 rows.


### Rename Columns

If you want to just rename some columns, but output all columns, you can do it like this:

```bash
$ csv2sql.py parse -n "Tenant Product Type"=tpt -n "Solution Area"=solution_area -n 12=product_id
```

Note that you can rename by name or by column index (1-based).

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
$ csv2sql parse -m 5 bla.csv -c fr_id -c TID=tenant_id -replace tenant_id='s/S_0(.*)/\1/g'
```

You can also apply multiple regular expressions to a column:

```bash
$ csv2sql parse -m 5 bla.csv -c fr_id -c TID=tenant_id -r tenant_id='s/S_0(.*)/\1/g' -r tenant_id='s/74/99/g'
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

Note that proper quoting is required. For exmaple:

#### Equals Query

```bash
$ csv2sql parse tpt_assignments_input.xlsx  -f "#Tenants"=int -f "#Customers"=int -m 1 -n "Tenant Product Type"=tpt -q 'tpt="A"'
```

#### Boolean Query

```bash
$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -c product_id -q 'contact!=""' -f product_id=int -q 'product_id>800300' -a
```

Note how we needed to convert the product_id column to an integer.

#### Equals Query for numerical values

```bash
$ csv2sql parse tpt_assignments_input.xlsx -n "#Tenants=n_tenants" -q "n_tenants=7243" -f "#Tenants"=int -a
```

#### In Query

```bash
$ csv2sql parse tpt_assignments_input.xlsx -n "Tenant Product Type"=tpt -q 'tpt.isin(["A","A5"])' -a
```

#### Here's a very complex query

```bash
$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -q 'contact!=""' -f product_id=int -q 'product_id>8003000' -q 'product_id<8004000' -q 'product_name contains "Ariba"' -q 'not contact contains "Olaf"' -a
```

#### Starts With Query

```bash
$ csv2sql parse sold_to_party.csv -q 'customer_name.str.startswith("Kennametal")' -a
```

#### Noteworthy

Note you typically need to use the -a option to query all rows, because the query
will only work on the rows that are actually shown.

Note also that if you have spaces in your column names, you first need to rename
the column before using a query on it.

Note also that for string functions, you may want to explicitly convert the column to str first:

```bash
$ csv2sql parse sold_to_party.csv -q 'customer_name.str.startswith("Kennametal")' -f customer_name=str -a
```

### Sort the output

Here is an even more complex query showing how to sort the output:

```bash
$ csv2sql parse approvers.csv -c contact -c product_id -c product_name -q 'contact!=""' -f product_id=int -q 'product_id>8003000' -q 'product_id<8004000' -a -q 'product_name contains "Ariba"' -q 'not contact contains "Olaf"' -o 
-product_id -o product_name
```

You can give any number of ordering options, and they will be applied in the order;
if you want to reverse the order, you can prefix the column with a minus sign.

Note that if you have a numeric value, in order to sort it numerically, you need
to convert it to an integer or float:

```bash
$ csv2sql parse tpt_assignments_input.csv -m 12 -f "#Tenants"=int -o -"#Tenants"
```

Here is how you can sort in a case sensitive manner:

csv2sql parse sold_to_party.csv -f customer_name=str -q 'customer_name contains "GmbH"' -o -customer_id --case -a

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
$ csv2sql.py parse approvers.csv --db --dbtype=mysql+pymysql --dbuser=user --dbpass=pass --dbhost=localhost --dbport=3306 --dbschema=mydb
$ csv2sql.py parse approvers.csv --db --dbtype=postgresql    --dbuser=user --dbpass=pass --dbhost=localhost --dbport=5432 --dbschema=mydb
```

#### Use a different chunk size

You can use a different chunk size by specifying the chunk size:

```bash
$ csv2sql.py parse approvers.csv --db -cs=10000
```

This can have a significant impact on the performance of the database.


#### Use special database connection parameters

You can use special database connection parameters like so:

```bash
$ csv2sql.py parse approvers.csv --db --dbtype=mysql+pymysql --dbspecial=charset=utf8mb4
```

You can also use the dbargs option to specify the database connection parameters:

```bash
$ csv2sql.py parse approvers.csv --db --dbargs='{"charset": "utf8mb4", "use_unicode": "True", "connect_timeout": 10}'
```


### Drop the table from the database

If you want to drop the table from the database, you can do it like this:

```bash
$ csv2sql.py drop -p _tmp_ -t fpm
```
