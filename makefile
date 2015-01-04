
all: bwx-game

bwx-game:
	cp advent.py bwx-game.py3
	grep -v 'from advent' bwx-game.py >> bwx-game.py3
	perl -i -p -e "s/\Qnet_f.read()\E/net_f.read().decode('utf-8')/" bwx-game.py3
	2to3 --no-diffs -w -n bwx-game.py3

tutorial1:
	cp advent.py tutorial1.py3
	grep -v 'from advent' tutorial1.py >> tutorial1.py3
	perl -i -p -e "s/\Qnet_f.read()\E/net_f.read().decode('utf-8')/" tutorial1.py3
	2to3 --no-diffs -w -n tutorial1.py3
