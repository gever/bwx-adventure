
all: python3 \
	python3/advent.py \
	python3/bwx-game.py \
	python3/tutorial1.py \
	python3/tutorial2.py \
	python3/tutorial3.py \
	python3/tutorial4.py \
	python3/tutorial5.py \
	python3/tutorial6.py \
	python3/tutorial7.py

python3:
	mkdir -p python3

python3/%.py: %.py
	grep -v -e "@staticmethod" -e advent_devtools $< > $@
	2to3 --no-diffs -w -n $@
	perl -i -p -e "s/\Qnet_f.read()\E/net_f.read().decode('utf-8')/" $@
	perl -i -p -e "s/\Q, urllib.error\E//" $@
	perl -i -p -e "s/\Q, urllib.parse\E//" $@
	perl -i -p -e "s/\Qimport textwrap\E//" $@
	perl -i -p -e "s/\QFalse: # trinket.io\E/True: # trinket.io/" $@
	perl -i -p -e "s/\Qtextwrap.fill\E/(lambda x: x)/" $@

clean:
	rm -rf python3

test: smoke_test functional_test

smoke_test: all
	echo "run test" | python3 ./python3/tutorial2.py
	echo "run test" | python ./tutorial2.py
	echo "run test" | python3 ./python3/tutorial3.py
	echo "run test" | python ./tutorial3.py
	echo "run test" | python3 ./python3/tutorial4.py
	echo "run test" | python ./tutorial4.py
	echo "run test" | python3 ./python3/tutorial5.py
	echo "run test" | python ./tutorial5.py
	echo "run test" | python3 ./python3/bwx-game.py
	echo "run test" | python ./bwx-game.py

functional_test: all
	cd test && ./run.sh
