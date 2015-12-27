#!/bin/bash

COLUMN=0
REVERSE=1
FLOAT=1
NO_HEADER=0
usage()
{
cat <<EOF
 EOF
usage: $0 options

This script run the test1 or test2 over a machine.

OPTIONS:
   -h      Show this message
   -g      sort as string (default is float)
   -r      sort ascending (default descending)
EOF
}

while getopts “ht:c:gnr” OPTION
do
     case $OPTION in
         h)
             usage
             exit 1
             ;;
	 c)
	     COLUMN=$OPTARG
	     ;;
	 g)
	     FLOAT=0
	     ;;
	 r)
	     REVERSE=0
	     ;;
	 n)
	     NO_HEADER=1
	     ;;
	 a)
	     ADD_COLS=$OPTARG
	     ;;
	 # c)
	 #     CUT_COLS=$OPTARG
	 #     ;;
         ?)
             usage
             exit
             ;;
     esac
done

if [[ $NO_HEADER -ne 0 ]]
then
    hdr=""
else
    read -r hdr;
fi
    
if [[ "$COLUMN" =~ ^-?[0-9]+$ ]]
then
    COLUMN=$(($COLUMN+1))
else
    COLUMN=$(python -c "print \"$hdr\".split(',').index(\"$COLUMN\") + 1")
fi

CMD="echo $hdr; sort -t, -k$COLUMN,$COLUMN"

if [[ $FLOAT -ne 0 ]]
then
    CMD=$CMD" -g"
fi

if [[ $REVERSE -ne 0 ]]
then
    CMD=$CMD" -r"
fi

CMD=$CMD" /dev/stdin"

eval $CMD
