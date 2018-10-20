scriptdir=$(dirname $0)

echo Starting FootieScores updater in background...
nohup python $scriptdir/../footie_scores/start_updater.py 2>&1 > logs/app.log &

echo $! > data/ps
echo Updater started with PID $!
