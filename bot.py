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

import signal
import json
import importlib
from sys import argv
from time import sleep
from pathlib import Path

from origamibot import OrigamiBot as Bot
from origamibot.listener import Listener

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

class BotsCommands:
    def __init__(self, bot: Bot, scenery_bot):  # Can initialize however you like
        self.bot = bot
        self.scenery_bot = scenery_bot

    def start(self, message):   # /start command
        uid = str(message.chat.id)
        if uid not in self.scenery_bot.user_db:
            self.scenery_bot.add_user(uid)
            self.bot.send_message(
                message.chat.id,
                get_start_msg(message))
            self.scenery_bot.user_db[uid].state = self.scenery_bot.scenery_states["init1"]
            self.scenery_bot.process_user_message(Message(uid,"nothing"))
        else:
            self.bot.send_message(
                message.chat.id,
                f"""{message.chat.first_name}, на тебя дело уже заведено.
Отправь мне "!справка", если не помнишь как со мной работать.""")


class MessageListener(Listener):  # Event listener must inherit Listener
    def __init__(self, bot, scenery_bot):
        self.bot = bot
        self.scenery_bot = scenery_bot
        self.scenery_bot.set_reply_function(self.__reply_user)
        self.m_count = 0

    def __reply_user(self, message):
        self.bot.send_message(int(message.user_id), message.content)#, parse_mode="Markdown")

    def on_message(self, message):   # called on every message
        self.m_count += 1
        print(f'Total messages: {self.m_count}')

        user_id = str(message.chat.id)
        if type (message.text) is str:
            if (user_id not in self.scenery_bot.user_db) and not(message.text.startswith("/start")):
                self.bot.send_message (
                message.chat.id,
                "Без /start я работать не буду!")
                return
            elif message.text.startswith("/"):
                pass
            else:
                self.scenery_bot.process_user_message(Message(
                    user_id,
                    message.text
                    ))


    def on_command_failure(self, message, err=None):  # When command fails
        if err is None:
            self.bot.send_message(message.chat.id,
                                  'Э-э-эм... не поняла')
        else:
            self.bot.send_message(message.chat.id,
                                  f"В команде есть ошибка:\n{err}")
        raise err


if __name__ == '__main__':
    if Path("config.json").exists():
        config = load_json("config.json")
    else:
        print("Can't find config file. Please place it as './config.json'")
        exit(1)
    run_interactive = False
    recompile_scenery = False
    
    if len(argv) > 2:
        if "-i" in argv:
            run_interactive = True
        if "-r" in argv:
            recompile_scenery = True
    
    if recompile_scenery or not Path(config["scenery_path"]).exists():
        save_scenery_to_json(sc.scenery_source, config["scenery_path"])
    scenery = load_json(config["scenery_path"])
    
    token = (argv[1] if len(argv) > 1 else input('Enter bot token: '))

    bot = Bot(token)   # Create instance of OrigamiBot class
    
    api_realisation = sar.SceneryApiRealisation(templates=sar.ApiRealisationTemplates())
    scbot = RedmineBot(scenery, config, api_realisation=api_realisation)   # Create instance of scenery bot

    # Add an event listener
    bot.add_listener(MessageListener(bot,scbot))
    # Add a command holder
    bot.add_commands(BotsCommands(bot, scbot))
    
    def handler(signum, frame):
        global scbot, bot
        scbot.shutdown()
        # ~ bot.stop()
        raise KeyboardInterrupt
    signal.signal(signal.SIGINT, handler)

    bot.start()   # start bot's threads
    scbot.start()   # start bot's threads
    
    
    c_reload = "reload"
    c_recompile = "recompile"
    c_stop = "stop"
    c_start = "start"
    c_shutdown = "shutdown"

    if run_interactive:
        while True:
            try:
                cmd = input(">>").strip()
                if cmd == c_start:
                    scbot.start()
                elif cmd == c_stop:
                    scbot.stop()
                elif cmd == c_recompile:
                    importlib.reload(sc)
                    save_scenery_to_json(sc.scenery_source, config["scenery_path"])
                elif cmd == c_reload:
                    config = load_json("config.json")
                    scenery = load_json(config["scenery_path"])
                    importlib.reload(sar)
                    api_realisation = sar.SceneryApiRealisation(templates=sar.ApiRealisationTemplates())
                    if scbot.is_running:
                        scbot.stop()
                    scbot.reload(config=config, scenery=scenery, api_realisation=api_realisation)
                    scbot.start()
                elif cmd == c_shutdown:
                    scbot.shutdown()
                    break
                else:
                    print("Command error. Try: stop start reload shutdown")
            except Exception as error:
                print(error)
    else:
        while True:
            time.sleep(1)
