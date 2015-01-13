#!/bin/sh

SUBDIRS="tutorial2 bwx-game"

for world in $SUBDIRS
do
    echo "testing world: $world"
    for test in `cd $world && ls *.script`
    do
	test=${test%.*}
	echo "\trunning test: $test"
	echo | python ../$world.py -c -f -e ./$world/$test
    done
done
