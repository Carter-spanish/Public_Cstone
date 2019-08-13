import discord
from discord.ext import commands
from discord.utils import get
import configparser 
from trello import TrelloApi, Boards, Lists, Cards
'''
 * Cog to get access to Trello tools
 ** self is a requirement for commands in a cog
 ** ctx is a requirement for bot to run, tells bot where it was called
 ** When a parameter in an @param section has an * directly after the name, means string input 
 	does not need to be surrounded with " " if multiple word string input. If no * then must 
 	have " " surrounding it. 

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
class Trell(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	# Starts up Trello cog, grabs api_key and token as well as gets the desired board id
	@commands.Cog.listener()
	async def on_ready(self):
		# Access API access information in Creds.ini
		config = configparser.ConfigParser()
		config.read("Creds.ini")

		# How to reference the Trello board
		global board
		global b_id
		# How to reference a list on the Trello board
		global c_list
		# How to reference a card on the Trello board
		global cards
		board = Boards(config.get('trello', 'api_key'), config.get('trello', 'token'))
		b_id = config.get('trello', 'board_id')
		c_list = Lists(config.get('trello', 'api_key'), config.get('trello', 'token'))
		cards = Cards(config.get('trello', 'api_key'), config.get('trello', 'token'))
		print("Trello online.")

	'''
	 * Print name of all lists
		@post - a message is sent to the channel bot is call listing all lists on the board
	'''
	@commands.command()
	async def lists(self, ctx):
		await ctx.send(print_list(board.get_list(b_id)))

	'''
	 * Add a new list to Trello
		@post  - a message is sent to the channel bot is called that a list is added, new list is added to board
		@param - name* - list with 'name' is added to board
	'''
	@commands.command()
	async def new_list(self, ctx, *, name: str):
		board.new_list(b_id, name)
		await ctx.send("List " + name + " added!")

	'''
	 * Print all card names in the given list
		@post  - a message is sent to the channel bot is called, either sending info or informing of failure
		@param - name* - name of the list to print card names from
	'''
	@commands.command()
	async def card_list(self, ctx, *, name: str):
		l_id = get_id(board.get_list(b_id), name)
		if l_id == "X":
			await ctx.send("Sorry but " + name + " is not a valid list!")
		else:
			await ctx.send("Cards in " + name + " are:\n" + print_list(c_list.get_card(l_id)))

	'''
	 * Print the description of a card. May expand later.
		@post  - a message is sent to the channel bot is called, either sending info or informing of failure
		@param - list_name  - name of the list the card should be in
				 card_name* - name of the card to retrieve info from
		@note  - searches for a card in a list, then print's its description. 
				 Other parts of card's dictionary can easily be added by adding:
				 	await ctx.send(c_info['*dict key*'])
	'''
	@commands.command()
	async def card_info(self, ctx, list_name: str, *, card_name: str):
		# Find card ID
		tgt = card_id(list_name, card_name)
		# If the ID wasn't found, don't do anything
		if tgt == "X":
			pass
		# If ID found, print the description
		else:
			c_info = cards.get(tgt)
			await ctx.send("Description for " + card_name + " says:\n\"" + c_info['desc'] + "\"")

def setup(client):
	client.add_cog(Trell(client))

''' 
 * Go through a list of dictionaries, grab the name from each item and print it in brackets
	@param  - items - list of dictionaries
	@return - a string of each dictionaries name element in brackets. Looks like [ this ]
'''
def print_list(items):
	all_item = ""
	for k in items:
		all_item = all_item + "[ " + k['name'] + " ] "
	return all_item

'''
 * Test if the list exists, if it does test if the card exists in the list
	@param  - list_name - the name of the list the card should be in
			  card_name - the name of the card being looked for
	@return - a string that is the reference ID for the card
	@note   - Trello does not enable searching all card's so searching for all cards in a
			  list is needed
'''
def card_id(list_name, card_name):
	# Try to get the list's ID
	l_id = get_id(board.get_list(b_id), list_name)
	# If list does not exist, return a false marker and inform the user
	if l_id == "X":
		ctx.send("Sorry but " + list_name + " is not a valid list!")
		return "X"
	# If the list does exist, check to see if the card exists	
	else:
		# Try to grab the card ID
		c_id = get_id(c_list.get_card(l_id), card_name)
		# If the card does not exist, return a false marker and inform the user
		if c_id == "X":
			ctx.send("Sorry but " + card_name + " is not a valid card in this list!")
			return "X"
		# Return the card ID
		else:
			return c_id

'''
 * Search through dictionaries to find an item with name [value] and return the ID
	@param  - search - a list of dictionaries
			  value  - the name of the item trying to be ID'd 
	@return - a string that is the reference ID of a card or list on a Trello board
	@note   - can be used for finding a card or a list's ID. Needed as a name alone is not enough
			  to reference a card or list alone on Trello.
'''
def get_id(search, value):
	# Look at each dictionary in the list
	for x in search:
		# Check if value matches the name value in the dictionary
		# If it does, return the ID from the dictionary
		if x['name'] == value:
			return x['id']
	# If it does not return a false marker
	return "X"
