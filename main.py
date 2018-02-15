from handler import *

client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print("=============")

    all_votes = sqlib.votes.get_all()
    pending_votes = list(filter(lambda v: v[2] > 0, all_votes))

    for vote in pending_votes:
        client.loop.create_task(timer(client, vote[0]))

    # post_to_apis(client)


@client.event
@handle_commands(client)
async def on_message(message):
    prefix = sqlib.server.get(message.server.id, 'prefix')[0]
    print(message.content)
    if alias_in(message.content, 'vote', prefix=prefix):
        content = get_cmd_content(message.content)

        title = "投票"
        options = None
        duration = get_config('default_duration')
        # notify_when_ending = False
        notify_when_ending = True
        async def command_error(reason=" :confused: "):
            await client.send_message(message.channel, "Command error: *{0}*\n"
                                                       "Type `{prefix}vote help` を参照してください"
                                                       "".format(reason, prefix=prefix))

        if content.count('"') > 1:
            subcommands = list(map(lambda x: x.strip(), content.split('"')))
            last_item = subcommands.pop()  # delete empty item at the end

            if "--notify" in last_item or "-N" in last_item:
                notify_when_ending = True

            skip_next = False

            try:
                for i in range(len(subcommands)):
                    if skip_next:
                        skip_next = False
                        continue

                    subcmd = subcommands[i]
                    nextone = subcommands[i+1]

                    if any(x in subcmd for x in ["-T", "--title"]):
                        title = nextone
                        skip_next = True

                    elif any(x in subcmd for x in ["-O", "--options"]):
                        options = nextone
                        skip_next = True

                    elif any(x in subcmd for x in ["-D", "--duration"]):
                        duration = int(nextone)
                        skip_next = True

                    if any(x in subcmd for x in ["-N", "--notify"]):
                        notify_when_ending = True

                if options is None:
                    await command_error("オプションが設定されていません.")
                    return 0

                if duration < 1:
                    await command_error("1分以上にしてください")
                    return None
                elif duration > 60:
                    await command_error("60分以下にしてください")
                    return None

            except ValueError:
                await command_error("期間は数字でなければなりません。")
                return 0
            except Exception:
                await command_error("Syntax Error")
                return 0

        else:
            content = content.split("|")

            if len(content) == 2:
                title = content[0]
                options = content[1]
            else:
                options = content[0]

        vote_embed = discord.Embed(
            title=title,
            description="リアクションで投票してください",
            color=int(get_config('color'), 16)
        )
        vote_embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        vote_embed.set_footer(text=message.author)

        options = options.split(';')
        if len(options) > 20:
            await command_error("選択肢が多すぎます. (max. 20)")
            return 0
        elif len(options) < 2:
            await command_error("選択肢は最低でも2個以上必要です")
            return 0

        emojis = []
        for i in range(len(options)):  # generates unicode emojis and embed-fields
            hex_str = hex(224 + (6 + i))[2:]
            reaction = b'\\U0001f1a'.replace(b'a', bytes(hex_str, "utf-8"))
            reaction = reaction.decode("unicode-escape")
            emojis.append(reaction)

            if len(options[i]) == 0:
                await command_error("オプション内容が入力されていません.")
                return None

            vote_embed.add_field(
                name=reaction,
                value=options[i],
                inline=True
            )

        msg = await client.send_message(message.channel, embed=vote_embed)

        emoji_dict = {}
        for emoji in emojis:
            await client.add_reaction(msg, emoji)
            emoji_dict[emoji] = 0

        sqlib.votes.add_element(msg.id, {"options": json.dumps(emoji_dict),
                                         "duration": duration,
                                         "channel": msg.channel.id})

        await refresh_vote_msg(msg, emoji_dict, int(duration), client, notify=notify_when_ending)
        client.loop.create_task(timer(client, msg.id, notify=notify_when_ending))


    elif alias_in(message.content, "prefix", prefix=prefix):
        if not message.author.server_permissions.administrator:
            await client.send_message(message.channel, "権限がありません.")
            return None

        content = get_cmd_content(message.content).lower()

        if len(content) == 0:
            await client.send_message(message.channel, "Prefix too short.")
        elif len(content) > 2:
            await client.send_message(message.channel, "Prefix too long. (max. 2 chars)")
        else:
            sqlib.server.update(message.server.id, {'prefix': content})
            await client.send_message(message.channel, f"Okay, new prefix is `{content}`.")

async def update_votes(reaction, user):
    if user.id != client.user.id:
        duration = sqlib.votes.get(reaction.message.id, "duration")

        if duration is None:  # proves if message is in database
            return None
        else:
            duration = duration[0]

        if duration == 0:
            return None

        options = json.loads(sqlib.votes.get(reaction.message.id, "options")[0])

        emoji = reaction.emoji
        if emoji in options:
            votes = reaction.count - 1

            options[emoji] = votes
            sqlib.votes.update(reaction.message.id, {"options": json.dumps(options)})

            if ":bell:" in reaction.message.content:
                notify = True
            else:
                notify = False

            await refresh_vote_msg(reaction.message, options, duration, client, notify=notify)


@client.event
async def on_reaction_add(reaction, user):
    await update_votes(reaction, user)


@client.event
async def on_reaction_remove(reaction, user):
    await update_votes(reaction, user)



async def uptime_count():
    await client.wait_until_ready()
    global up_hours
    global up_minutes
    up_hours = 0
    up_minutes = 0

    while not client.is_closed:
        await asyncio.sleep(60)
        up_minutes += 1
        if up_minutes == 60:
            up_minutes = 0
            up_hours += 1


client.loop.create_task(uptime_count())
client.run(get_config('token'))
