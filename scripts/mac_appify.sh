#!/bin/bash

pyinstaller -p bwx_adventure \
	    --log-level WARN \
	    --clean \
	    --onefile \
	    $1

rm -rf build
rm *.spec
