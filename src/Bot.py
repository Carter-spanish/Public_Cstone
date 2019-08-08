import discord
from discord.ext import commands
from discord.utils import get
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser 

# Allows reference to the bot, sets the char to call a command as $
client = commands.Bot(command_prefix = '$')

config = configparser.ConfigParser()
config.read('Creds.ini')

#@client.event
#async def on_ready():
	
# Disabling default help comman to implement mine with explanation.
client.remove_command("help")
@client.command()
async def help(ctx):
    embed = discord.Embed(title="CapstoneBot", description="A Bot to encorporate Trello and Google Sheets. List of commands are:", color=0xFF00FF)

    embed.add_field(name="$report X Y", value = "Report your completing of a backlog item! X must be an int, represents hours spent working. Y is the item you completed.", inline=False)
    embed.add_field(name="$sharebk X", value = "Shares the Scrumbook with all entered emails. Emails must end with @gmail.com to be shared.", inline=False)
    embed.add_field(name="$name X", value = "Change your display name to X. Note: if you are the owner of the server this command will NOT work for you.", inline=False)

    await ctx.send(embed=embed)

# From testing different properties of ctx, just sends the server name.
@client.command()
async def wheream(ctx):
	await ctx.send("You are in " + ctx.guild.name)

# Allows the user to rename themself (changes display name)
# Bot DOES NOT have permission to change server owner's username.
@client.command()
async def name(ctx, *, new_name: str):
	try:
		await ctx.author.edit(nick= new_name)
		await ctx.send("So your name is " + new_name + "!")
	except:
		await ctx.send("Sorry, but I can't change your nickname for some reason!\n(If you are the owner of the server I can't rename you!)")

# Allows for commands to be placed in cogs and loaded
@client.command()
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')

# Unload cogs when done
@client.command()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')

# Get all of the cog file names
for filename in os.listdir('./cogs'):
	# All cogs are python files
	if filename.endswith('.py'):
		# Only want the file name, do not want .py
		client.load_extension(f'cogs.{filename[:-3]}')

client.run(config.get('discord', 'client_token'))