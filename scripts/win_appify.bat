:: Creates a standalone executable (a game app) from a python script game.
:: For example, if there is a game contained in the script awesomegame.py
:: Running the following command from the command line:
::     call scripts\win_appify.bat game.py
:: would create a game app game.exe in the dist folder.
::
:: IMPORTANT NOTE, the above command must be run in the top directory of this repository.
:: That means when you run the command 
::	dir
:: you should see at least the following:
::	bwx_adventure
::	LICENSE
::	README.md
::	scripts

pyinstaller -p bwx_adventure ^
	--log-level=WARN ^
	--clean ^
	--onefile ^
	%1
rmdir build /s
del *.spec