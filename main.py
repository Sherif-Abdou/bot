import discord
import wikipedia
import os

client = discord.Client()

# TOKEN = "NzUyOTEwNDIwMzkzNTkwOTU0.X1egeA.kRpRi6-ATUwj35t08SBGKgcdYZY"
TOKEN = os.environ["DISCORD_KEY"]
SENTENCE_COUNT = 4


@client.event
async def on_ready():
    print(f"We've logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    string: str = message.content
    if string.startswith("?#s "):
        rest = string.lstrip("?#s ")
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


client.run(TOKEN)
