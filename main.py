import discord
import wikipedia
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

client = discord.Client()

PORT = os.environ["PORT"]
TOKEN = os.environ["DISCORD_KEY"]
INITIAL = "??"
SENTENCE_COUNT = 4


@client.event
async def on_ready():
    print(f"We've logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    string: str = message.content
    if string.startswith(INITIAL):
        rest = string.lstrip(INITIAL)
        print(f"Rest: {rest}")
        rest = rest.strip()
        print(f"Stripped: {rest}")
        summary = ""
        try:
            summary = wikipedia.summary(rest, SENTENCE_COUNT)
        except wikipedia.DisambiguationError as err:
            summary = wikipedia.summary(err.options[0], SENTENCE_COUNT)
            summary = f"Ambiguous search, defaulting to {err.options[0]}:\n\n" + summary

        await message.channel.send(summary)


def run_side_server():
    print(f"starting server on port {PORT}")
    httpd = HTTPServer(('localhost', int(PORT)), BaseHTTPRequestHandler)
    httpd.serve_forever()


thr = Thread(target=run_side_server)
thr.start()

client.run(TOKEN)
thr.join()
