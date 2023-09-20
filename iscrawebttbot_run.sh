#!/usr/bin/env sh
# Define cleanup procedure
cleanup() {
    /usr/bin/env python ./bot_control.py -c $CFG shutdown
    /usr/bin/env python ./bot_control.py -c $CFG exit
    ls -la
}

# Hardcoded for docker volume
if [[ -d udb ]]
    then
    echo "udb directory is found"
else then
    mkdir udb
fi

# Trap SIGTERM
trap 'cleanup' SIGTERM

/usr/bin/env python ./bot.py -k $K -t $T -c $CFG -s

# Wait
wait $!

cleanup
