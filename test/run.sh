#!/bin/sh

for world in `find . -type d \( ! -iname "." \)`
do
    echo "testing world: $world"
    for test in `cd $world && ls *.script`
    do
	test=${test%.*}
	echo "\trunning test: $test"
	echo | python ../$world.py -c -f -e ./$world/$test
	if [ $? != 0 ]
	then
	    exit 1
	fi
    done
done
