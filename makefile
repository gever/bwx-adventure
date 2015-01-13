
all: bwx-game.py3 tutorial1.py3 tutorial2.py3

%.py3: %.py advent.py
	cat advent.py > $@
	grep -v advent_devtools $< >> $@
	2to3 --no-diffs -w -n $@
	perl -i -p -e "s/\Qfrom advent \E/# from advent /" $@
	perl -i -p -e "s/\Qnet_f.read()\E/net_f.read().decode('utf-8')/" $@
	perl -i -p -e "s/\Q, urllib.error\E//" $@
	perl -i -p -e "s/\Q, urllib.parse\E//" $@
	perl -i -p -e "s/\Qimport textwrap\E//" $@
	perl -i -p -e "s/\QFalse: # trinket.io\E/True: # trinket.io/" $@
	perl -i -p -e "s/\Qtextwrap.fill\E/(lambda x: x)/" $@

clean:
	rm *.py3

test: smoke_test functional_test

smoke_test: all
	echo "run test" | python3 ./tutorial2.py3
	echo "run test" | python ./tutorial2.py
	echo "run test" | python3 ./bwx-game.py3
	echo "run test" | python ./bwx-game.py

functional_test: all
	cd test && ./run.sh
