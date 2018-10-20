echo 

scriptdir=$(dirname $0)
updater_pid=$(cat $scriptdir/../data/ps)

echo Kill this process? [y/n]
echo 
ps -Af | head -n 1
ps -Af | grep "$updater_pid.*python" | head -n 1

echo 
