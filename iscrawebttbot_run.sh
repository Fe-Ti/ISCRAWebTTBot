#!/usr/bin/env sh
# Define cleanup procedure
cleanup() {
    /usr/bin/env python ./bot_control.py -c ./config.json shutdown
    /usr/bin/env python ./bot_control.py -c ./config.json exit
    ls -la
}

die() {
    echo "$1"; exit 1
}

# Trap SIGTERM
trap 'cleanup' SIGTERM

[ -z "$REFRESH_PERIOD" ] && export REFRESH_PERIOD=1000
[ -z "$SLEEP_TIMEOUT" ] && export SLEEP_TIMEOUT=10
[ -z "$NOTIFY_PERIOD" ] && export NOTIFY_PERIOD=43200
[ -z "$HTTPS" ] && export HTTPS="true"
[ -z "$REDMINE_URL" ] && die 'Redmine root URL unset! Set envvar $REDMINE_URL'
[ -z "$K" ] && die 'Telegram token unset! Set envvar $K'
[ -z "$T" ] && die 'Redmine user key unset! Set envvar $T'

envsubst < "$CFG" > ./config.json
cat ./config.json

/usr/bin/env python ./bot.py -k "$T" -t "$K" -c ./config.json -s

# Wait
wait $!

cleanup
