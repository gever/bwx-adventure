
all: bwx-game.py3 tutorial1.py3

%.py3: %.py
	cp advent.py $@
	grep -v 'from advent' $< >> $@
	perl -i -p -e "s/\Qnet_f.read()\E/net_f.read().decode('utf-8')/" $@
	2to3 --no-diffs -w -n $@
