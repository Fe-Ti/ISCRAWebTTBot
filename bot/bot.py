# Copyright 2023 Fe-Ti aka T.Kravchenko

# Goals for the first version:
# - use Redmine JSON REST API (maybe in future supoort XML)
# - provide a simple bot logic which will be able to:
#     - create/delete:
#         - projects
#         - issues
#     - assign issues to user
#     - add watchers to issues
#     - get:
#       - project list
#       - issues:
#           - by number
#           - listed in project (with filtering);
#           - assigned to user
#           - which are watched by user

# Goals for early Alpha:
# + Run test scenery without api calls
# + Run test scenery with functions
# +- Write 'prod' scenery
# - Run 'prod' scenery

# Then think about next goals
# Copyright 2023 Fe-Ti aka T.Kravchenko
m_count = 0
# Echo server program
import http
import signal
import json
import importlib
from sys import argv
from time import sleep
from pathlib import Path

import telebot
from telebot import types

from redminebotlib import RedmineBot
from redminebotlib.data_structs import Message, User

import scenery_api_realisation as sar
import scenery as sc

def load_json(path):
    with open(path) as ifile:
        dictionary = json.loads(ifile.read())
    return dictionary

def save_scenery_to_json(scenery, filename):
    with open(filename, 'w') as sc_file:
        sc_file.write(json.dumps(scenery))


START_MSG = """Привет, {first_name}. Меня зовут Тасфия ‒ я бот таск-трекера Искры.
Введи "!справка" для получения справочной информации."""
def get_start_msg(message):
    return START_MSG.format(first_name = message.chat.first_name)

def process_command(commands, sc_bot, cfg_filename):
    c_reload = "reload"
    c_stop = "stop"
    c_start = "start"
    c_save = "save"
    c_notify = "notify"
    c_exit = "exit"
    if type(commands) is str:
        commands = [commands]
    for cmd in commands:
        print("cmd:", cmd)
        if cmd == c_start:
            scbot.start()
        elif cmd == c_stop:
            scbot.stop()
        elif cmd == c_reload:
            config = load_json(cfg_filename)
            importlib.reload(sc)
            save_scenery_to_json(sc.scenery_source, config["scenery_path"])
            scenery = load_json(config["scenery_path"])
            importlib.reload(sar)
            api_realisation = sar.SceneryApiRealisation(templates=sar.ApiRealisationTemplates())
            if scbot.is_running:
                scbot.stop()
            scbot.reload(config=config, scenery=scenery, api_realisation=api_realisation)
            scbot.start()
        elif cmd == c_save:
            scbot.save()
        elif cmd == c_notify:
            scbot.notificating_routine()
        elif cmd == c_exit:
            if scbot.is_running:
                scbot.stop()
            raise KeyboardInterrupt
        else:
            raise ValueError("Command error. Try: stop start reload save")

# ~ class JBCHandler(http.server.BaseHTTPRequestHandler):
    # ~ scbot = None
    # ~ cfg_filename = None

    # ~ def do_GET(self):
        # ~ self.send_response(200)
        # ~ self.send_header("Content-Type", "application/json")
        # ~ self.end_headers()
        # ~ if scbot.is_running:
            # ~ self.wfile.write(b"""{"response":"Bot is up and running.","success":true}""")
        # ~ else:
            # ~ self.wfile.write(b"""{"response":"Bot is stopped.","success":true}""")

    # ~ def do_POST(self):
        # ~ # read the content-length header
        # ~ content_length = int(self.headers.get("Content-Length"))
        # ~ # read that many bytes from the body of the request
        # ~ try:
            # ~ data = self.rfile.read(content_length).decode("ascii")
            # ~ commands = json.loads(data)["commands"]
        # ~ except Exception as error:
            # ~ self.send_response(400)
            # ~ self.send_header("Content-Type", "application/json")
            # ~ self.end_headers()
            # ~ self.wfile.write(bytes(f"""{{"response":"{error}","success":false}}""", "ascii"))
            # ~ return
        # ~ try:
            # ~ process_command(commands, self.scbot, cfg_filename)
            # ~ self.send_response(200)
            # ~ self.send_header("Content-Type", "application/json")
            # ~ self.end_headers()
            # ~ self.wfile.write(b"""{"response":"Successfully passed commands to bot.","success":true}""")
        # ~ except KeyboardInterrupt as error:
            # ~ self.send_response(200)
            # ~ self.send_header("Content-Type", "application/json")
            # ~ self.end_headers()
            # ~ self.wfile.write(bytes(f"""{{"response":"Shutting down...","success":true}}""", "ascii"))
            # ~ raise error
        # ~ except Exception as error:
            # ~ self.send_response(500)
            # ~ self.send_header("Content-Type", "application/json")
            # ~ self.end_headers()
            # ~ self.wfile.write(bytes(f"""{{"response":"{error}","success":false}}""", "ascii"))

if __name__ == '__main__':
    run_interactive = False
    run_socket = False
    recompile_scenery = False
    token = ""
    redmine_token = ""
    tg_token_len = 46
    rm_token_len = 40
    cfg_filename = "config.json"

    if len(argv) > 1:
        for n, key in enumerate(argv):
            if "-i" == key:
                run_interactive = True
            elif "-s" == key:
                run_socket = True
            elif "-r" == key:
                recompile_scenery = True
            elif "-t" == key:
                try:
                    token = argv[n + 1]
                except:
                    print("Parameter -t requires argument.")
                    exit(1)
            elif "-k" == key:
                try:
                    redmine_token = argv[n + 1]
                except:
                    print("Parameter -k requires argument.")
                    exit(1)
            elif "-c" == key:
                try:
                    cfg_filename = argv[n + 1]
                except:
                    print("Parameter -c requires argument.")
                    exit(1)
    else:
        print("""Simple keys:
    -i      -   interactive mode
    -r      -   force scenery recompile
    -s      -   socket mode (control via socket)
Keys with args:
    -c CFG_FILE - configuration file in JSON format
    -t TG_TOKEN - Telegram API token
    -k RM_TOKEN - Redmine API token (is used to access enumerations)
""")

    if len(token) != tg_token_len:
        print(f"Telegram API token should be {tg_token_len} characters in length.")
        exit(1)
    elif len(redmine_token) != rm_token_len:
        print(f"Redmine API token should be {rm_token_len} characters in length.")
        exit(1)

    if Path(cfg_filename).exists():
        config = load_json(cfg_filename)
    else:
        print(f"Can't find config file. Please place it as '{cfg_filename}'")
        exit(1)

    if recompile_scenery or not Path(config["scenery_path"]).exists():
        save_scenery_to_json(sc.scenery_source, config["scenery_path"])
    scenery = load_json(config["scenery_path"])

    api_realisation = sar.SceneryApiRealisation(templates=sar.ApiRealisationTemplates())
    scbot = RedmineBot(scenery, config, redmine_token, api_realisation=api_realisation)   # Create instance of scenery bot



    # ~ TOKEN = '7040913312:AAHEmwtFkelr869Ae5NGcgsL3O6FxDOwNJM'
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def handle_cmd(message):
        # ~ bot.reply_to(message, get_start_msg(message))
        uid = str(message.chat.id)
        if uid not in scbot.user_db:
            scbot.add_user(uid)
            bot.send_message(
                message.chat.id,
                get_start_msg(message))
            scbot.user_db[uid].state = scbot.scenery_states["init1"]
            scbot.process_user_message(Message(uid,"nothing"))
        else:
            bot.send_message(
                message.chat.id,
                f"""{message.chat.first_name}, на тебя дело уже заведено.
Отправь мне "!справка", если не помнишь как со мной работать.""")

    @bot.message_handler(content_types=['text'])
    def handle_img(message):
        global scbot, m_count
        m_count += 1
        # ~ print(f'Total messages: {self.m_count}')
        print(f"Processing message {m_count}")
        user_id = str(message.chat.id)
        if type (message.text) is str:
            if (user_id not in scbot.user_db) and not(message.text.startswith("/start")):
                bot.send_message (
                message.chat.id,
                "Без /start я работать не буду.")
                return
            elif message.text.startswith("/"):
                pass
            else:
                scbot.process_user_message(Message(
                    user_id,
                    message.text
                    ))
        print(f"Finished message {m_count}.")

    def reply_function(message):
        global bot
        if not message.hint: 
            bot.send_message(int(message.user_id), f"" + message.content, reply_markup=types.ReplyKeyboardRemove())
        else:
            markup = types.ReplyKeyboardMarkup(row_width=3)
            markup.add(*[types.KeyboardButton(i) for i in message.hint])
            bot.send_message(int(message.user_id), message.content, reply_markup=markup)

    scbot.set_reply_function(reply_function)

    def handler(signum, frame):
        global scbot, bot
        scbot.save()
        if scbot.is_running:
            scbot.stop()
        raise KeyboardInterrupt
    signal.signal(signal.SIGINT, handler)

    scbot.start()   # start bot's threads
    for i in range(10000000):
        a = i+1
    print(scbot.issue_statuses)
    bot.infinity_polling(interval=0, timeout=20)


    # ~ if run_interactive:
        # ~ while True:
            # ~ try:
                # ~ cmd = input(">>").strip()
                # ~ process_command(cmd, scbot)
            # ~ except Exception as error:
                # ~ print(error)
    # ~ elif run_socket:
        # ~ # VERY basic HTTP-JSON server
        # ~ HOST = config["address"]
        # ~ PORT = config["port"]
        # ~ JBCHandler.scbot = scbot # Know what, they will all reference the same bot :)
        # ~ JBCHandler.cfg_filename = cfg_filename
        # ~ httpd = http.server.HTTPServer((HOST, PORT,), JBCHandler)
        # ~ try:
            # ~ httpd.serve_forever()
        # ~ except KeyboardInterrupt:
            # ~ print("Shutting down.")
            # ~ exit(0)
    # ~ else:
        # ~ while True:
            # ~ sleep(1)
