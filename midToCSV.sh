#! /bin/bash

for file in *.mid
do
	echo $file
	noMid=${file%????}
	csvName="$noMid.csv"
	./midicsv $file $csvName
done
