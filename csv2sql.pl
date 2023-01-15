#!/usr/bin/env perl -w
#
# csv2sql
#
# Calculate column widths of a CSV file and
# optionally create a mysql create table
# statement.
#
# Usage:
#
# Assume you've a csv file that has a header line
# and some data lines. The typical issue when you
# want to insert that data into a table is that
# you have to calculate the maximum column width
# for each column. This script does that for you,
# and it even optionally creates a create table
# statement for you.
#
# Here is a sample call:
#
#   $csv2sql.pl -s "," -t ./test.csv
#
# Parameters:
#
# -s (optional, defaults to ",") - The column separator
# -t (optional) - Whether to write a create table statement. This
#                 Parameter optionally takes a value, in which case
#                 that value, and not the table name, is used as
#                 the name of the table to create.
# -i (optional) - the index to create, e.g. tenant_id. For a combined
#                 index use like -i a,b; for separate indices use
#                 -i a -i b
# -tt (optional) - Create a temporary table
# -h  (optional) - Skip n header rows before starting the parser
# -c  (optional) - Add ROW_FORMAT=COMPRESSED for non temporary tables
#
# Here is an easy way to find out what format your csv is in:
#
#   $head +2 test.csv
#
# The program should handle CRLF and BOM gracefully. Yet,
# if you find out that the last column is somewhat broken,
# you may have a problem with line endings. You can try
#
#   $dos2unix test.csv
#
# before running colwidth.
#
# (c) 2019 Matthias Nott, SAP
#
# Licensed under WTFPL
#
use strict;
use warnings;
use Data::Dumper;
use Getopt::Long;
use File::Basename;
use File::Spec;
use Text::CSV qw( csv );
use Digest::MD5 qw(md5);
use Number::Format;

my @cols;
my @hdrs;
my $maxl = 0;
my $sepr = ",";
my $table;
my $prefix = "";
my $temporary;
my @idx  = ();
my $dir; #  = "/opt/data/input";
my $file = $ARGV[$#ARGV];
my $sum_field_length = 0;
my $result = "";
my $head;
my $compressed;


GetOptions(
	's|sep|separator:s' => \$sepr,       # Separator
	't|table:s'         => \$table,      # Create Table Statement?
	'tt|temptable' 		=> \$temporary,  # Create Temporary Table Statement?
	'p|prefix:s'        => \$prefix,     # Table Name Prefix
	'd|dir:s'           => \$dir,        # Load Directory on Server
	'i|index:s'         => \@idx,        # Create Index
	'h|head:s'          => \$head,       # Skip n header rows
	'c|compressed:s'    => \$compressed, # ROW_FORMAT=COMPRESSED
);

if (! defined $file) {
	die "Please specify a file name.\n";
}

my $abs_path = File::Spec->rel2abs( $file ) ;

#
# Input
#
my $csv = Text::CSV->new ({ binary => 1, auto_diag => 1, sep_char => "$sepr", escape_char => "\\" });
open my $fh, "<:encoding(utf8)", "$file" or die "Cannot open $file: $!";

my $rows = 0;

my $rows_skipped = 0;

if (defined $head && $head > 0) {
	$rows_skipped = $head;
}

while (my $row = $csv->getline($fh)) {
	next unless --$rows_skipped < 0;
	if($rows++ == 0) {
		@hdrs = @$row;
		foreach my $hdr (@hdrs) {
			$hdr = lc($hdr);
			$hdr =~ s/[^^a-zA-Z0-9,]/_/g;
			$maxl = length($hdr) if $maxl < length($hdr);
		}
		next;
	} else {
		my $col = 0;
		for (@$row) {
			if(! defined $cols[$col]) {
				$cols[$col] = length($_);
			} else {
				$cols[$col] = length($_) if($cols[$col] < length($_));
			}
			$col++;
		}
	}
}
close($fh);

if (defined $temporary) {
	$temporary = "TEMPORARY ";
} else {
	$temporary = "";
}

#
# Output
#
# If we have to write a create table
# statement, create the header
#
if(defined $table) {
	if($table =~ /.*csv/) {
		$table = fileparse($file, (".csv"));
	}
	$table = lc($table);
	$result .= "DROP ${temporary}TABLE IF EXISTS `$prefix$table`;\n";
	$result .= "CREATE ${temporary}TABLE `$prefix$table` (\n";
}

# Output table body
$maxl += 4; # Add some space
for my $i (0 .. $#hdrs) {
	my $hdr = sprintf "%-${maxl}s", "`$hdrs[$i]`";
	$sum_field_length += $cols[$i];
	if(defined $table) {
		$result .= "  $hdr\tvarchar($cols[$i])";
		$result .= "," if ($i < $#hdrs || $#idx >= 0);
		$result .= "\n";
	} else {
		$result .= sprintf("%2s %s : %3s\n", $i+1, $hdr, $cols[$i]);
	}
}

# Output table footer
if(defined $table) {
	if($#idx >= 0) {
		for my $i (0 .. $#idx) {
			$result .= "  index(${idx[$i]})";
			$result .= "," if ($i < $#idx);
			$result .= "\n";
		}
	}
	$result .= ") ENGINE=InnoDB DEFAULT CHARSET=utf8";

	if (defined $compressed && $temporary eq "") {
		$result .= " ROW_FORMAT=COMPRESSED";
	}

	$result .= ";\n\n";

	$file = fileparse($file);
	if(defined $dir) {
		$result .= "load data infile '${dir}/$file' into table `$prefix$table`\n";
	} else {
		$result .= "load data infile '$abs_path' into table `$prefix$table`\n";
	}
	$result .= "  fields terminated by '${sepr}'\n";
	$result .= "  optionally enclosed by '\"'\n";
	$result .= "  ignore ";
	if (defined $head && $head > 0) {
		$result .= $head + 1;
	} else {
		$result .= 1;
	}
	$result .= " rows;\n";
}

my $str  = substr( md5($result ), 0, 4 );
my $hash = unpack('L', $str);  # Convert to 4-byte integer (long)

my $fmt  = new Number::Format(-thousands_sep   => '\'');
$hash = $fmt->format_number($hash);

$result .= "\n-- Sum of Field Lengths: $sum_field_length (Hash: $hash)\n";

print $result;

