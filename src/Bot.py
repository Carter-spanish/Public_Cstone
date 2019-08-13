import discord
from discord.ext import commands
from discord.utils import get
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser 

'''
 * Cog to get access to Google Spread tools
 ** self is a requirement for commands in a cog
 ** ctx is a requirement for bot to run, tells bot where it was called
 ** When a parameter in an @param section has an * directly after the name, means string input 
 	does not need to be surrounded with " " if multiple word string input. If no * then must 
 	have " " surrounding it. 
	
	*** Command card_info in Trell.py ***
 	> For example:
 			$card_info To Do this card 
 	> would pass as:
 			list_name: To
 			card_name: Do this card
 	> Correct input would be:
 			$card_info "To Do" this card ~OR~ $card_info "To Do" "this card"   
 	> For a pass like:
 			list_name: To Do
 			card_name: this card
 *
 * Code written by Carter English
'''

# Allows reference to the bot, sets the char to call a command as $
client = commands.Bot(command_prefix = '$')

# Access API access information in Creds.ini
config = configparser.ConfigParser()
config.read('Creds.ini')
	
# Disabling default help command to implement mine with explanation.
client.remove_command("help")

'''
 * Custom implementation of help command
	@post  - a message is sent to the channel bot is called, sending explanation of each command
	@note  - Custom help command is needed due to custom commands that default help command can't fill correctly
'''
@client.command()
async def help(ctx):
    embed = discord.Embed(title="CapstoneBot", description="A Bot to encorporate Trello and Google Sheets. List of commands are:", color=0xFF00FF)

    embed.add_field(name="$report X Y*", value = "Report your completing of a backlog item! X is the number hours spent working (an int!) Y is the item you completed.", inline=False)
    embed.add_field(name="$sharebk X", value = "Shares the Scrumbook with all entered emails. Emails must end with @gmail.com to be shared.", inline=False)
    embed.add_field(name="$name X", value = "Change your display name to X. Note: if you are the owner of the server this command will NOT work for you.", inline=False)
    embed.add_field(name="$lists", value = "Prints out the names of all lists on the Trello board.", inline=False)
    embed.add_field(name="$new_list X*", value = "Add a new list to the Trello board with name X.", inline=False)
    embed.add_field(name="$card_list X*", value = "Prints out a list of card names from list X.", inline=False)
    embed.add_field(name="$card_info X Y*", value = "Prints out some information about card Y in list X.", inline=False)
    embed.add_field(name="Legend: ", value = "Any variable above that has an * next to it means it can be multiple words without \" \". If there is no * then please surround the input with \" \".", inline=False)


    await ctx.send(embed=embed)

'''
 * Simply prints out the name of the server.
	@post  - a message is sent to the channel bot is called, sending the name of the server
	@note  - added for experimenting with ctx early on. 
'''
@client.command()
async def wheream(ctx):
	await ctx.send("You are in " + ctx.guild.name)

'''
 * Command to rename the user sending it. NOT USABLE BY OWNER OF SERVER.
 	@pre   - User CANNOT be owner.
	@post  - display name is changed and printed
	@param - new_name*  - desired display name
	@note  - useful for keeping track since username reporting is a lot uglier
'''
@client.command()
async def name(ctx, *, new_name: str):
	try:
		await ctx.author.edit(nick= new_name)
		await ctx.send("So your name is " + new_name + "!")
	except:
		await ctx.send("Sorry, but I can't change your nickname for some reason!\n(If you are the owner of the server I can't rename you!)")

'''
 * Tools for utilizing command cogs
 ** Cog tools from Lucas on Youtube: https://youtu.be/vQw8cFfZPx0
'''

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