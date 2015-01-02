
2to3:
	cp advent.py game3.py
	grep -v 'from advent' bwx-game.py >> game3.py
	perl -i -p -e "s/\Qnet_f.read()\E/net_f.read().decode('utf-8')/" game3.py
	2to3 -w game3.py
