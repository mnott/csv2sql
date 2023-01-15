#!/bin/bash

if [ $# -lt 1 ] ; then
  echo Usage: $0 xyz.csv
  exit 1
fi

FILE=$1

dos2unix -q $FILE                                                # Just in case
perl -pi -e 's/"""/"/g' $FILE                                    # Compress triple quotes
perl -pi -e 's/"\{"([^"]*?)":"([^"]*?)"/"\1:\2"/g' $FILE         # Remove JSON and its quotes
perl -pi -e 's/(,"[^",]*)"([^",]*",)/\1\2/g' $FILE               # Remove leading inner quotes
#perl -pi -e 's/("[^",]*?)"([^",]*?)"/\1\2/g' $FILE               # Remove trailing inner quotes
perl -pi -e 's/("[^",]*?)"([^",]*?")/\1\2/g' $FILE               # Remove trailing inner quotes
perl -pi -e 's/,"([^"]*?)""$/,"\1"/g' $FILE                      # And towards the end
perl -pi -e 's/("[^",]*?)"([^",]*?")/\1\2/g' $FILE               # Remove trailing inner quotes
perl -pi -e 's/("[^",]*?")",/\1,/g' $FILE                        # "",
perl -pi -e 's/("[^",]*?")[^,]*?,/\1,/g' $FILE                   # ,"Emirates" on,
