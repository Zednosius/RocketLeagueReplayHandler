pyinstaller --onefile --windowed RocketLeagueReplayHandler.py
cp Updates.txt dist/Updates.txt
cp log.config dist/log.config
cd dist
zip RLRH_v%1-alpha.zip log.config LICENSE RocketLeagueReplayHandler.exe Updates.txt
cd ..