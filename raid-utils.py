# bot.py of raid-bot -
# a bot that allows raiding discord servers via webhook spamming

import discord
import sys
import random
import string
import time
import asyncio
import json

# loads config file, exits client if not found
cfg = None
try:
    with open("config.example.json", "r") as cfgFile:
        cfg = json.load(cfgFile)
except FileNotFoundError:
    print(
        'take "config.example.json", rename it to "config.json" and edit the config before running the client')

client = discord.Client()

channels = None


# the meat of the bot


async def webhook_handler(message, webhook_name, avatar_url):
    # select a random channel
    global channels
    channel = random.choice(channels)
    # create the initial webhook
    hook = await channel.create_webhook(name=webhook_name, avatar=None)
    # loop to infinitely send messages
    while True:
        # try to send it
        try:
            # send a message
            await hook.send(message, avatar_url=avatar_url)
            # take a break
            time.sleep(1)
        except:
            # delete it
            await hook.delete()
            # make a new one
            hook = await channel.create_webhook(name=webhook_name, avatar=None)
        return


@client.event
async def on_ready():
    try:
        # show that we logged in
        print(f"logged in as { client.user }...")
        # put all servers into a list
        server = client.guilds
        # show them
        for x in range(0, len(server)):
            print(f"{ x }: { server[x].name }")
        # ask the user to select one
        server = server[int(input("select a server: "))]
        # loop
        while True:
            # show the menu
            print("------------------------------------")
            print(" raid-utils v1 | by superwhiskers   ")
            print("------------------------------------")
            print("                                    ")
            print(" (1) - dump audit logs              ")
            print(" (2) - spam a message in the server ")
            print(" (3) - exit                         ")
            print("                                    ")
            print("------------------------------------")
            option = input(": ")
            if option == "1":
                # let them know we are dumping them
                print("dumping audit logs...")
                # dump audit logs
                log = ""
                async for entry in server.audit_logs():
                    log += f"""
~~ entry ~~
user: { entry.user }
action: { entry.action }
target: { entry.target }
reason: { entry.reason }
timestamp: { entry.created_at }
category: { entry.category }
extra: { entry.extra }
before: { entry.before }
after: { entry.after }
"""
                # add it to the file
                with open("audit.log", "a+", -1, "utf-8-sig") as myfile:
                    sanitized_log = "".join(filter(lambda x: x in string.printable, log))
                    myfile.write(sanitized_log)

            elif option == "2":
                code = str(random.randint(100, 999))
                print("are you sure? this will most definitely get you and the bot banned")
                print(f"enter the following code to perform this action: { code }")
                confirmation = input(": ")
                if code == confirmation:
                    print("how many simultaneous webhooks shall i spawn?")
                    hooks = input(": ")
                    print("what should the webhooks be named?")
                    name = input(": ")
                    print("what should the message be?")
                    message = input(": ")
                    print("what should the url for the avatar be?")
                    avatar_url = input(": ")
                    print("okay, beginning spam...")
                    # filter out non-text channels
                    global channels
                    channels = []
                    for x in server.channels:
                        if type(x) == discord.TextChannel:
                            channels.append(x)
                    # get the event loop
                    loop = asyncio.get_event_loop()
                    # make a task list
                    tasks = []
                    for x in range(int(hooks)):
                        tasks.append(asyncio.ensure_future(webhook_handler(message, name, avatar_url)))
                    # do it
                    loop.run_until_complete(asyncio.wait(tasks))
                    # kill it
                    loop.close()
                    # do it again
                    loop.run_until_complete(asyncio.wait(tasks))
                    # kill it again
                    loop.close()
                else:
                    print("incorrect code...")

            elif option == "3":
                sys.exit(0)

    except RuntimeError:
        print()

# run the bot
if __name__ == "__main__":
    # run the bot
    client.run(cfg["token"], bot=cfg["bot"])
