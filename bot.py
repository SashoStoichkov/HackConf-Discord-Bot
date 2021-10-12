#!/usr/bin/env python3

import os, discord
from discord.utils import get
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())


invites = {}
invite_role = {}


@bot.event
async def on_ready():
    print(f"{bot.user} is connected to Discord!")

    for guild in bot.guilds:
        for invite in await guild.invites():
            invites[invite.code] = invite

            if invite.code == "uUZWy42KBW":
                invite_role[invite.code] = get(guild.roles, name="HackConf Team")
            if invite.code == "K6FvUANuur":
                invite_role[invite.code] = get(guild.roles, name="Speaker")
            if invite.code == "shkJP3NN5b":
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


if __name__ == "__main__":
    bot.run(TOKEN, bot=True)
