#!/usr/bin/python3
# Copyright 2023 Fe-Ti aka T.Kravchenko
import http.client
import json
from sys import argv
from pathlib import Path

def load_json(path):
    with open(path) as ifile:
        dictionary = json.loads(ifile.read())
    return dictionary

c_reload = "reload"
c_stop = "stop"
c_start = "start"
c_notify = "notify"
c_save = "save"
c_exit = "exit"

cmd_set = {c_start, c_stop, c_reload, c_save, c_exit, c_notify}
help_msg = """Specify commands:
    start       - start bot operation
    stop        - stop bot operation
    reload      - reload config, scenery and its API
    notify      - start notification routine
    save        - save user database
    exit        - stop bot and exit control daemon process
"""

if __name__ == '__main__':
    cfg_filename = "config.json"
    commands = []
    if len(argv) > 1:
        for n, key in enumerate(argv[1:]):
            # ~ print(commands, key, "-c" == key, cfg_filename)
            if key in cmd_set:
                commands.append(key)
            elif "-c" == key:
                try:
                    cfg_filename = argv[n + 2]
                except:
                    print("Parameter -c requires argument.")
                    exit(1)
            elif argv[n] == "-c":
                pass
            else:
                print(f"Error: unknown command '{key}'.\n", help_msg)
                exit(1)
    else:
        print(help_msg)
        exit()

    if Path(cfg_filename).exists():
        config = load_json(cfg_filename)
    else:
        print(f"Can't find config file. Please place it after '{cfg_filename}'")
        exit(1)

    HOST = config["address"] # Symbolic name meaning all available interfaces
    PORT = config["port"] # Arbitrary non-privileged port
    data = ""
    headers = {"Content-type": "application/json"}
    if len(commands) > 1:
        body = f"""{{"commands":{commands}}}""".replace("'", '"')
    else:
        body = f"""{{"commands":"{commands[0]}"}}"""
    body = bytes(body, 'ascii')
    conn = http.client.HTTPConnection(host=HOST, port=PORT)
    try:
        conn.request("POST", "", body=body, headers=headers)
        response = conn.getresponse()
        # ~ print(response.status, response.reason)
        data = response.read()
    finally:
        conn.close()
        print('Received', repr(data))
