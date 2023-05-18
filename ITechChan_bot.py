from sys import argv
from time import sleep

from origamibot import OrigamiBot as Bot
from origamibot.listener import Listener


class BotsCommands:
    def __init__(self, bot: Bot):  # Can initialize however you like
        self.bot = bot

    def start(self, message):   # /start command
        self.bot.send_message(
            message.chat.id,
            'Hello user!\nThis is an example bot.')

    def echo(self, message, value: str):  # /echo [value: str] command
        self.bot.send_message(
            message.chat.id,
            value
            )

    def add(self, message, a: float, b: float):  # /add [a: float] [b: float]
        self.bot.send_message(
            message.chat.id,
            str(a + b)
            )

    def _not_a_command(self):   # This method not considered a command
        print('I am not a command')


class MessageListener(Listener):  # Event listener must inherit Listener
    def __init__(self, bot):
        self.bot = bot
        self.m_count = 0

    def on_message(self, message):   # called on every message
        self.m_count += 1
        print(f'Total messages: {self.m_count}')

    def on_command_failure(self, message, err=None):  # When command fails
        if err is None:
            self.bot.send_message(message.chat.id,
                                  'Command failed to bind arguments!')
        else:
            self.bot.send_message(message.chat.id,
                                  'Error in command:\n{err}')


if __name__ == '__main__':
    token = (argv[1] if len(argv) > 1 else input('Enter bot token: '))
    bot = Bot(token)   # Create instance of OrigamiBot class

    # Add an event listener
    bot.add_listener(MessageListener(bot))

    # Add a command holder
    bot.add_commands(BotsCommands(bot))

    # We can add as many command holders
    # and event listeners as we like

    bot.start()   # start bot's threads
    while True:
        sleep(1)
        # Can also do some useful work i main thread
        # Like autoposting to channels for example
