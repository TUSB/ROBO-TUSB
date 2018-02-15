import json
import functools
import discord
import time
import asyncio
import sqlib
import urllib.request

import requests
import types

ENDPOINT = 'https://www.cotogoto.ai/webapi/noby.json'
MY_KEY = ''

def get_config(key: str):
    with open('./data/config.json', 'r', encoding='utf8') as f:
        config = json.load(f)
        return config[key]


def concat_elements(iterable: list or tuple or dict, space: str=" "):
    if iterable is None:
        return None
    elif len(iterable) == 0:
        return ""

    return functools.reduce(lambda x, y: f"{x}{space}{y}", iterable)


def get_commands():
    with open('./data/commands.json', 'r', encoding='utf8') as f:
        return json.load(f)


# def get_cmd_by_alias(alias: str):
#     commands = get_commands()
#     for cmd in commands:
#         if alias in commands[cmd]['aliases']:
#             return cmd


# def get_aliases(cmd: str, prefix: str=None):
#     commands = get_commands()
#     aliases = commands[cmd]['aliases']

#     if prefix is not None:
#         aliases = tuple(map(lambda alias: prefix + alias, aliases))
#     else:
#         aliases = tuple(aliases)

#     return aliases


def get_help_text(prefix):
    commands = get_commands()
    return concat_elements(commands['help'], space="").format(prefix=prefix)


def get_help_embed(prefix):
    commands = get_commands()

    # if alias in commands:
    #     cmd = alias
    # else:
    #     cmd = get_cmd_by_alias(alias)

    help_text = get_help_text(prefix)
    embed = discord.Embed(
        title="cmd",
        description=help_text,
        color=int(get_config('color'), 16)
    )
    embed.set_footer(
        text=get_config('default_footer')
    )
    return embed


# def get_all_aliases(prefix=None):
#     commands = get_commands()
#     aliases = []
#     for cmd in commands:
#         for alias in get_aliases(cmd, prefix=prefix):
#             aliases.append(alias)

#     return tuple(aliases)


# def alias_in(content: str, cmd: str, prefix=None):
#     aliases = get_aliases(cmd, prefix=prefix)
#     return content.lower().startswith(aliases)


def get_cmd_content(content: str):
    content = content.split(' ')
    if len(content) > 1:
        content = concat_elements(content[1:])
        return content
    else:
        return ""


# def get_aliases_str(cmd: str, prefix=None):
#     aliases = get_aliases(cmd, prefix=prefix)
#     aliases_str = concat_elements(aliases, space=', ')
#     return aliases_str


# def get_aliases_embed(alias: str, prefix=None):
#     cmd = get_cmd_by_alias(alias)
#     aliases_str = get_aliases_str(cmd, prefix=prefix)

#     aliases_embed = discord.Embed(
#         title=f"`{cmd}` aliases",
#         description=aliases_str,
#         color=int(get_config('color'), 16)
#     )
#     aliases_embed.set_footer(
#         text=get_config('default_footer')
#     )
#     return aliases_embed


def get_leading_options(options: dict):
    options = list(map(lambda o: (o, options[o]), options))
    options = sorted(options, key=lambda o: o[1], reverse=True)

    highest = options[0][1]

    leading_emojis = list(map(lambda o: o[0], filter(lambda o: o[1] == highest, options)))

    if len(leading_emojis) == len(options):
        leading_emojis = ["`引き分け`"]

    return concat_elements(leading_emojis, ", "), highest


async def refresh_vote_msg(message: discord.Message, options: dict, duration: int, coro_client: discord.Client,
                           clock=True, notify=False):

    leading_options = get_leading_options(options)

    if clock:
        clock_emoji = f":clock{duration % 12 if duration % 12 != 0 else 12}:"
    else:
        clock_emoji = ""

    if leading_options[1] == 1:
        vote_plural = ""
    else:
        vote_plural = "s"

    if duration == 0:
        if len(leading_options[0]) > 1:
            winner_plural = "s"
        else:
            winner_plural = ""

        winners = "最終結果: {1[0]} / {1[1]} 票".format(winner_plural, leading_options, vote_plural)

        msg = await coro_client.edit_message(message, new_content=f"受付終了しました。\n{winners}")

        if notify:
            await coro_client.send_message(message.channel, f":bell: 受付終了しました。 :bell: \n")

    else:
        if notify:
            notification = "通知を`オン`にしました。 :bell: \n"
        else:
            notification = ""

        msg = await coro_client.edit_message(message, new_content=
            "残り時間 {0} 分. {clock_emoji} \n"
            "{notification}"
            "現在の有効打: {1[0]} / {1[1]} 票."
            "".format(duration, leading_options, vote_plural,
            clock_emoji=clock_emoji,notification=notification)
        )
    return msg


async def timer(client: discord.Client, vote_id: str, notify: bool=False):
    t_needed = 0
    while not client.is_closed:
        await asyncio.sleep(60 - t_needed)
        t_start = time.time()
        vote = sqlib.votes.get(vote_id)
        msg_id, options, duration, channel_id = vote
        duration -= 1

        sqlib.votes.update(msg_id, {"duration": duration})
        channel = client.get_channel(channel_id)

        try:
            message = await client.get_message(channel, msg_id)
        except AttributeError:
            print("AttributeError")
            continue

        await refresh_vote_msg(message, json.loads(options), duration, client, notify=notify)

        if duration == 0:
            break

        t_end = time.time()
        t_needed = t_end - t_start


def handle_commands(client):
    def decorated(func):
        @functools.wraps(func)
        async def wrapper(message):
            client_member = message.server.get_member(client.user.id)
            if not client_member.permissions_in(message.channel).send_messages:
                return None

            prefix = sqlib.server.get(message.server.id, 'prefix')
            if prefix is None:
                prefix = get_config('prefix')
                sqlib.server.add_element(message.server.id, {'prefix': prefix})
            else:
                prefix = prefix[0]

            # all_aliases = get_all_aliases(prefix=prefix)
            embed_color = int(get_config('color'), 16)
            footer = get_config('default_footer')

            if True:  # checks if message is a command
                await client.send_typing(message.channel)

                if True:
                    content = get_cmd_content(message.content)

                    if True:
                        help_embed = get_help_embed( prefix)

                    else:
                        commands = get_commands()

                        help_embed = discord.Embed(
                            title="Help",
                            description="コマンドリスト.",
                            color=embed_color,
                            url=get_config("website")
                        )
                        for cmd in commands:
                            help_embed.add_field(
                                name=cmd,
                                value=get_help_text(cmd, prefix),
                                inline=False
                            )
                        help_embed.set_footer(
                            text=footer
                        )
                        help_embed.set_thumbnail(url=get_config("thumbnail"))

                    await client.send_message(message.channel, embed=help_embed)
                    # if message.author.server_permissions.administrator:  /* Adminチェック*/
                    #     await client.send_message(message.channel, "お前アドミン")
                    #     await client.send_message(message.author, "embed=help_embed") /*個人送信*/

                else:
                    content = get_cmd_content(message.content)
                    cmd_without_prefix = message.content.split(' ')[0][
                                         len(prefix):]  # splits command from prefix and other content
                    if content.lower().startswith('help'):
                        help_embed = get_help_embed(cmd_without_prefix)
                        await client.send_message(message.channel, embed=help_embed)  # sends cmd specific help
                    else:
                        return await func(message)

            elif client.user in message.mentions:
                await client.send_message(
                    message.channel,
                    f"Type `{sqlib.server.get(message.server.id, 'prefix')[0]}help` to see the command list!"
                )
                return await func(message)

            return None  # exits if it's not in command list -> !!! Add new commands to 'commands.json' !!!

        return wrapper
    return decorated
