import asyncio
import json
import datetime
import discord
from discord.ext import commands
from requests import get
from bs4 import BeautifulSoup
from keep_alive import keep_alive

config_file = open('config.json', 'r')
config = json.loads(config_file.read())
config_file.close()

general_file = open('general.json', 'r')
general = json.loads(general_file.read())
general_file.close()

users_stats_file = open('users_stats.json', 'r')
users_stats = json.loads(users_stats_file.read())
users_stats_file.close()

client = commands.Bot(command_prefix=config['command_prefix'],
                      intents=discord.Intents.all())
client.remove_command('help')

szczesliwy_aliases = [
    'Szczesliwy', 'szczęśliwy', 'Szczęśliwy', 'Numerek', 'numerek'
]
dyzurni_aliases = ['Dyzurni', "dyżurni", "Dyżurni"]
zakazenia_aliases = ["Zakazenia", 'zakażenia', "Zakażenia"]
help_aliases = ['Help', 'pomoc', 'Pomoc']


@client.event
async def on_ready():
    print('Bot is ready')


@client.command(aliases=szczesliwy_aliases)
async def szczesliwy(ctx):
    print(ctx.guild.member_count)
    for item in general:
        current_date = datetime.date.today().strftime("%d.%m")
        if current_date == item['date']:
            if item['numerek'] != "null":
                await ctx.send('```Dzisiaj szczesliwy numerek to: {0} i {1}```'.format(item['numerek'][0], item['numerek'][1]))
                return
            else:
                await ctx.send('```Dzis mamy swieto lub weekend```')
                return


@client.command(aliases=dyzurni_aliases)
async def dyzurni(ctx):
    for item in general:
        current_date = datetime.date.today().strftime("%d.%m")
        if current_date == item['date']:
            if item['numerek'] != "null":
                await ctx.send('```Dzisiaj dyzurni to: {0} i {1}```'.format(item['dyzurni'][0], item['dyzurni'][1]))
                return
            else:
                await ctx.send('```Dzis mamy swieto lub weekend```')
                return


@client.command(aliases=zakazenia_aliases)
async def zakazenia(ctx):
    for item in general:
        current_date = datetime.date.today().strftime("%d.%m")
        if current_date == item['date']:
            await ctx.send('```Dzisiejsza liczba zakazen: {0}```'.format(item['zakazenia']))
            return


@client.command(aliases=help_aliases)
async def help(ctx, *input):
    if input:
        if input[0] == 'help':
            await ctx.send(f'''```
            %%help - Pokazuje ta wiadomosc
            Aliasy: {help_aliases}```''')
        elif input[0] == 'szczesliwy':
            await ctx.send(f'''```
            %%szczesliwy - Pokazuje dzisiejszy szczesliwy numerek
            Aliasy: {szczesliwy_aliases}```''')
        elif input[0] == 'dyzurni':
            await ctx.send(f'''```
            %%dyzurni - Pokazuje dzisiejszych dyzurnych
            Aliasy: {dyzurni_aliases}```''')
        elif input[0] == 'zakazenia':
            await ctx.send(f'''```
            %%zakazenia - Pokazuje aktualna ilosc zakazen (credits: koronawirusunas.pl)
            Aliasy: {zakazenia_aliases}```''')
    else:
        await ctx.send('''```
        Komendy:
        help       - Pokazuje ta wiadomosc
        szczesliwy - Pokazuje dzisiejszy szczesliwy numerek
        dyzurni    - Pokazuje dzisiejszych dyzurnych
        zakazenia  - Pokazuje aktualna ilosc zakazen (credits: koronawirusunas.pl)```'''
                    )


@client.command(aliases=["Setup"])
async def setup(ctx):
    print('a')
    for guild in users_stats:
        print('a')
        if guild['guild_id'] == ctx.guild.id:
            print('b')
            return

    category = await ctx.guild.create_category('📈 Stats 📈')
    users_channel = await ctx.guild.create_voice_channel(name=f"Users: {sum(not member.bot for member in client.get_guild(ctx.guild.id).members)}", category=category)
    await users_channel.set_permissions(ctx.guild.default_role, connect = False)
    await users_channel.set_permissions(client.user, manage_channels = True, connect = True, view_channel = True)
    status_channel = await ctx.guild.create_voice_channel(name=f"🟢{sum(member.status == discord.Status.online and not member.bot for member in client.get_guild(ctx.guild.id).members)} ⛔{sum(member.status == discord.Status.do_not_disturb and not member.bot for member in client.get_guild(ctx.guild.id).members)} 🌙{sum(member.status == discord.Status.idle and not member.bot for member in client.get_guild(ctx.guild.id).members)}", category=category)
    await status_channel.set_permissions(ctx.guild.default_role, connect = False)
    await status_channel.set_permissions(client.user, manage_channels = True, connect = True, view_channel = True)
    bots_channel = await ctx.guild.create_voice_channel(name=f"Bots: {sum(member.bot for member in client.get_guild(ctx.guild.id).members)}", category=category)
    await bots_channel.set_permissions(ctx.guild.default_role, connect = False)
    await bots_channel.set_permissions(client.user, manage_channels = True, connect = True, view_channel = True)

    users_stats.append({
        "guild_id": ctx.guild.id,
        "users_id": users_channel.id,
        "users": sum(not member.bot for member in client.get_guild(ctx.guild.id).members),
        "status_id": status_channel.id,
        "status": {
            "online": sum(member.status == discord.Status.online and not member.bot for member in client.get_guild(ctx.guild.id).members),
            "dnd": sum(member.status == discord.Status.do_not_disturb and not member.bot for member in client.get_guild(ctx.guild.id).members),
            "idle": sum(member.status == discord.Status.idle and not member.bot for member in client.get_guild(ctx.guild.id).members)
        },
        "bots_id": bots_channel.id,
        "bots": sum(member.bot for member in client.get_guild(ctx.guild.id).members)
    })

    save_file = open('users_stats.json', 'w')
    save_file.write(json.dumps(users_stats, indent=4))
    save_file.close()


def check_for_infections():
    current_date_unformatted = datetime.datetime(
        datetime.datetime.now().year,
        datetime.datetime.now().month,
        datetime.datetime.now().day,
        datetime.datetime.now().hour,
        datetime.datetime.now().minute)
    current_date = datetime.date.today().strftime("%d.%m")
    scheduled_task = datetime.datetime(datetime.datetime.now().year,
                                       datetime.datetime.now().month,
                                       datetime.datetime.now().day, 10, 40)
    limit_task = datetime.datetime(datetime.datetime.now().year,
                                   datetime.datetime.now().month,
                                   datetime.datetime.now().day, 20, 00)
    print(
        f'Current time: {current_date_unformatted}\nMinimal time: {scheduled_task}\nMaximal time: {limit_task}\nIs going to check infections: {scheduled_task <= current_date_unformatted <= limit_task}'
    )
    if scheduled_task <= current_date_unformatted <= limit_task:
        print("Checked for infections")
        for item in general:
            if current_date == item['date']:
                URL = "https://koronawirusunas.pl"
                bs = BeautifulSoup(get(URL).content, features="lxml")
                infections = bs.find_all(class_="badge-danger")[1].text
                item['zakazenia'] = infections
                if item['zakazenia'] == "null" or item['zakazenia'] == "":
                    for item2 in general:
                        current_date2 = add_days(-1).strftime("%d.$m")
                        if current_date2 == item2.date:
                            item['zakazenia'] = item2['zakazenia']

        save_file = open('general.json', 'w')
        save_file.write(json.dumps(general, indent=4))
        save_file.close()
    else:
        print("Not checked for infections")
        for item in general:
            if current_date == item['date']:
                if item['zakazenia'] == "null" or item['zakazenia'] == '':
                    for item2 in general:
                        current_date2 = add_days(-1).strftime("%d.$m")
                        if current_date2 == item2['date']:
                            item['zakazenia'] = item2['zakazenia']

                save_file = open('general.json', 'w')
                save_file.write(json.dumps(general, indent=4))
                save_file.close()


async def check_for_members():
    current_date_unformatted = datetime.datetime(
        datetime.datetime.now().year,
        datetime.datetime.now().month,
        datetime.datetime.now().day,
        datetime.datetime.now().hour,
        datetime.datetime.now().minute)
    current_date = datetime.date.today().strftime("%d.%m")
    scheduled_task = datetime.datetime(datetime.datetime.now().year,
                                       datetime.datetime.now().month,
                                       datetime.datetime.now().day, 6, 00)
    limit_task = datetime.datetime(datetime.datetime.now().year,
                                   datetime.datetime.now().month,
                                   datetime.datetime.now().day, 23, 00)

    print(
        f'Current time: {current_date_unformatted}\nMinimal time: {scheduled_task}\nMaximal time: {limit_task}\nIs going to check users: {scheduled_task <= current_date_unformatted <= limit_task}'
    )
    if not (scheduled_task <= current_date_unformatted <= limit_task): return

    for guild in users_stats:
        users = sum(not member.bot for member in client.get_guild(guild['guild_id']).members)
        if guild['users'] != users:
            guild['users'] = users
            save_file = open('users_stats.json', 'w')
            save_file.write(json.dumps(users_stats, indent=4))
            save_file.close()

        bots = sum(member.bot for member in client.get_guild(guild['guild_id']).members)
        if guild['bots'] != bots:
            guild['bots'] = bots
            save_file = open('users_stats.json', 'w')
            save_file.write(json.dumps(users_stats, indent=4))
            save_file.close()

        online_members = sum(
            member.status == discord.Status.online and not member.bot
            for member in client.get_guild(guild['guild_id']).members)
        if guild['status']['online'] != online_members:
            guild['status']['online'] = online_members
            save_file = open('users_stats.json', 'w')
            save_file.write(json.dumps(users_stats, indent=4))
            save_file.close()

        dnd_members = sum(
            member.status == discord.Status.do_not_disturb and not member.bot
            for member in client.get_guild(guild['guild_id']).members)
        if guild['status']['dnd'] != dnd_members:
            guild['status']['dnd'] = dnd_members
            save_file = open('users_stats.json', 'w')
            save_file.write(json.dumps(users_stats, indent=4))
            save_file.close()

        idle_members = sum(
            member.status == discord.Status.idle and not member.bot
            for member in client.get_guild(guild['guild_id']).members)
        if guild['status']['idle'] != idle_members:
            guild['status']['idle'] = idle_members
            save_file = open('users_stats.json', 'w')
            save_file.write(json.dumps(users_stats, indent=4))
            save_file.close()

        for channel in client.get_guild(guild['guild_id']).channels:
            if channel.id == guild['status_id']:
                await channel.edit(
                    name=
                    f'🟢{guild["status"]["online"]} ⛔{guild["status"]["dnd"]} 🌙{guild["status"]["idle"]}'
                )
            elif channel.id == guild['users_id']:
                await channel.edit(
                    name=
                    f'Users: {guild["users"]}'
                )
            elif channel.id == guild['bots_id']:
                await channel.edit(
                    name=
                    f'Bots: {guild["bots"]}'
                )


def add_days(days_to_add):
    end_date = datetime.datetime.strptime(
        datetime.datetime.now().strftime("%d.%m"),
        "%d.%m") + datetime.timedelta(days=days_to_add)
    return end_date


def set_users_stats_element(guild_id, element, value):
    for guild in users_stats:
        if guild['guild_id'] == guild_id:
            guild[element] = value
            break
    save_file = open('users_stats.json', 'w')
    save_file.write(json.dumps(users_stats, indent=4))
    save_file.close()


def get_users_stats_element(guild_id):
    for guild in users_stats:
        if guild['guild_id'] == guild_id:
            return guild


async def check_for_infections_loop():
    await client.wait_until_ready()
    while True:
        check_for_infections()
        await asyncio.sleep(600)


async def check_for_members_loop():
    await client.wait_until_ready()
    while True:
        await check_for_members()
        await asyncio.sleep(10)

client.loop.create_task(check_for_members_loop())
client.loop.create_task(check_for_infections_loop())

keep_alive()
client.run(config['token'])
