import discord
import wikipedia
import os
import logging
from re import subn, match
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy.plotting.plot import plot3d
from googletrans import Translator
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from src import Handler

init_printing(use_unicode=True)
x, y = symbols("x, y")
translator = Translator()
logging.basicConfig(format='%(asctime)s %(message)s ', filename="logs.log", level=logging.INFO)

client = discord.Client()

PORT = os.environ["PORT"]
TOKEN = str(os.environ["DISCORD_KEY"])
INITIAL = "??"
HEMANTH_ID=615020027627962408 
SENTENCE_COUNT = 4

help_text = ""
with open("./help.txt", "r") as f:
    help_text = f.read()


@client.event
async def on_ready():
    print(f"We've logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.author.id == HEMANTH_ID and message.content == "fr":
        await message.channel.send("I have been summoned by the gods to tell Hemanth to shut up, no one cares")
        return

    string: str = message.content
    if not string.startswith(INITIAL):
        return

    for reg, fun in Handler.handlers:
        if await fun(string=string, channel=message.channel):
            break

    if string.startswith(INITIAL+"wiki"):
        rest = string.lstrip(INITIAL+"wiki")
        rest = rest.strip()
        logging.info(f"searched for: {rest}")
        summary = ""
        try:
            await message.channel.send("Searching...")
            summary = wikipedia.summary(rest, SENTENCE_COUNT)
        except wikipedia.DisambiguationError as err:
            logging.warning("Disambiguation Error")
            summary = wikipedia.summary(err.options[0], SENTENCE_COUNT)
            summary = f"Ambiguous search, defaulting to {err.options[0]}:\n\n" + summary
        except wikipedia.PageError as err:
            logging.warning("Page Error")
            summary = f"Invalid Search Term: {rest}"
        await message.channel.send(summary)
    elif string.startswith(INITIAL+"help"):
        await message.channel.send(help_text)


def run_side_server():
    httpd = HTTPServer(('localhost', int(PORT)), BaseHTTPRequestHandler)
    httpd.serve_forever()


# thr = Thread(target=run_side_server)
# thr.start()
if __name__ == "__main__":
    client.run(TOKEN)
# thr.join()
