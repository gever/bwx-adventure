
all: bwx-game.py3 tutorial1.py3

%.py3: %.py
	cp advent.py $@
	grep -v 'from advent' $< >> $@
	2to3 --no-diffs -w -n $@
	perl -i -p -e "s/\Qnet_f.read()\E/net_f.read().decode('utf-8')/" $@
	perl -i -p -e "s/\Q, urllib.error\E//" $@
	perl -i -p -e "s/\Q, urllib.parse\E//" $@
	perl -i -p -e "s/\Qimport textwrap\E//" $@
	perl -i -p -e "s/\QFalse: # trinket.io\E/True: # trinket.io/" $@
	perl -i -p -e "s/\Qtextwrap.fill\E/(lambda x: x)/" $@

clean:
	rm *.py3
