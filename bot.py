#!/usr/bin/env python3

import os, discord
from discord.utils import get
from discord.ext import commands

from discord_slash import SlashCommand
from discord_slash.utils import manage_commands

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
TEAM_CODE = os.getenv("TEAM_CODE")
SPEAKER_CODE = os.getenv("SPEAKER_CODE")
ATTENDEE_CODE = os.getenv("ATTENDEE_CODE")

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)


invites = {}
invite_role = {}


@bot.event
async def on_ready():
    print(f"{bot.user} is connected to Discord!")

    for guild in bot.guilds:
        for invite in await guild.invites():
            invites[invite.code] = invite

            if invite.code == TEAM_CODE:
                invite_role[invite.code] = get(guild.roles, name="HackConf Team")
            if invite.code == SPEAKER_CODE:
                invite_role[invite.code] = get(guild.roles, name="Speaker")
            if invite.code == ATTENDEE_CODE:
                invite_role[invite.code] = get(guild.roles, name="Attendee")

    for invite_code, role in invite_role.items():
        print(f"{invites[invite_code]} -> {role}")


def find_invite(invites, code):
    for invite in invites:
        if invite.code == code:
            return invite
    return None


@bot.event
async def on_member_join(member):
    print(f"{member} has joined the server!")

    after_invites = await member.guild.invites()

    for invite_code, invite in invites.items():
        if invite.uses < find_invite(after_invites, invite.code).uses:
            print(f"{member} has used {invite.code}")
            await member.add_roles(invite_role[invite.code])

    for invite in await member.guild.invites():
        invites[invite.code] = invite


@slash.slash(
    name="poll",
    description="Poll the audience",
    options=[
        manage_commands.create_option(
            name="speaker",
            description="Name of the speaker",
            required=True,
            option_type=3,
        ),
    ],
)
async def _poll(ctx, speaker: str):
    embed = discord.Embed(title=f"Please rate {speaker}'s talk.", color=0xF7AB1C)

    options = [
        ":one: :star:",
        ":two: :star::star:",
        ":three: :star::star::star:",
        ":four: :star::star::star::star:",
        ":five: :star::star::star::star::star:",
    ]

    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

    for option in options:
        embed.add_field(name="\u200b", value=option, inline=False)

    message = await ctx.send(embed=embed)

    for reaction in reactions:
        await message.add_reaction(reaction)


@slash.slash(
    name="ask",
    description="Ask a question to the speaker",
    options=[
        manage_commands.create_option(
            name="question",
            description="The question to ask",
            required=True,
            option_type=3,
        ),
        manage_commands.create_option(
            name="sender",
            description="Who asked the question",
            required=True,
            option_type=3,
        ),
    ],
)
async def _ask(ctx, question: str, sender: str):
    embed = discord.Embed(title=f"{question}", color=0xF7AB1C)
    embed.add_field(name="Asked By:", value=sender, inline=True)

    await ctx.send(embed=embed)


@slash.slash(name="ping")
async def _ping(ctx):
    await ctx.send("Pong!")


if __name__ == "__main__":
    bot.run(TOKEN, bot=True)
