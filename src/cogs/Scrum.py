import discord
from discord.ext import commands
from discord.utils import get
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser 
from datetime import datetime, date, timedelta

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

class Scrum(commands.Cog):
	def __init__(self, client):
		self.client = client

	# Runs when bot is turned on. Initializes Gspread for bot.
	# Creates and shares the sheet with owner if bot does not see it.
	@commands.Cog.listener()
	async def on_ready(self):
		# Access API access information in Creds.ini
		config = configparser.ConfigParser()
		config.read("Creds.ini")

		# Needed to work with workbook
		global book
		# Needed to reference a worksheet
		global worksheet
		# List to set up categories in a new worksheet
		global category

		# Next 3 lines are basic set up of GSpread access. Modified from Google's given code.
		scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive.file']
		creds = ServiceAccountCredentials.from_json_keyfile_name(config.get('sheets', 'cred_file'), scope)
		sheetclient = gspread.authorize(creds)
		category = [str(date.today()), "Team member", "Date", "Hours complete", "Backlog item"]

		# Test if Testing's Sheet exists, if it does open it, otherwise create it.
		try:
			book = sheetclient.open(config.get('sheets', 'book_name'))
		except:
			book = sheetclient.create(config.get('sheets', 'book_name'))
			worksheet = book.add_worksheet(title="Week 1", rows="100", cols="5")
			for x in range(5):
				worksheet.update_cell(1, x + 1, category[x])
			book.del_worksheet(book.get_worksheet(0))
			book.share(config.get('sheets', 'owner_email'), perm_type='user', role='owner')

		worksheet = book.get_worksheet(len(book.worksheets()) - 1)
		print("Scrum online.")
	
	# Submit a work report to the current week's sheet
	# If today is not in the same work week as the current sheet, pass to newsheet
	'''
	 * Submit a report to the current week's spread sheet
		@post  - reporter is thanked for reporting. name, day, hours spent working and item are added to spreadsheet.
				 if week is different than the current worksheet's date, creates a new workweek
		@param - hour  - an int representing the number of hours spent working on the item
				 item  - a string representing what backlog item was completed
		@note  - Track what day today is, find out what the most recent workweek was.
				 If today is within 7 days of the recent workweek, add to that sheet.
				 If today is more than 7 days, calculate how many weeks and automatically adjust 
				 new workweek to match that difference.
	'''
	@commands.command()
	async def report(self, ctx, hours: int, *, item: str):
		# Declared as global again so it can be editted globally
		global worksheet

		# Get today's date then the last workweek's date
		tdy = date.today()
		ltwk = datetime.strptime(worksheet.cell(1, 1).value, '%Y-%m-%d').date()
		# See how many days it has been, if 7+ create a new week and calculate how many weeks
		if ((tdy - ltwk).days > 6):
			worksheet = newsheet(book, worksheet, ltwk, category)
			await ctx.send("New week started!")

		# Form list of items to be reported
		to_sheet = [ctx.author.display_name, str(tdy), hours, item]
		# Find how many rows to go down
		col = worksheet.col_values(2)
		for x in range(4):
			worksheet.update_cell(len(col) + 1, x + 2, to_sheet[x])

		await ctx.send("Thanks for reporting " + str(ctx.author.display_name) +"!")


	'''
	 * Share the workbook with an @gmail.com email address.
		@post  - workbook is shared to an email
		@param - email  - email to share workbook to
		@note  - has to be @gmail.com to work with Gspread and have it be happy.
	'''
	@commands.command()
	async def sharebk(self, ctx, email: str):
		# Check if @gmail.com is in the email, if it is send it and inform the channel
		# otherwise tell the channel they entered a non-@gmail.com address
		if "@gmail.com" in email:
			book.share(email, perm_type='user', role='writer')
			await ctx.send("The workbook has been shared with " + email + ".")
		else:
			await ctx.send(email + " isn't a @gmail.com address!")

def setup(client):
	client.add_cog(Scrum(client))

# Only come here if the last week was more than 7 days ago
# Calculates what week it is now and creates a sheet on that date
# Sheet name will be based on how many weeks it has been since last sheet with report

'''
 * Print the description of a card. May expand later.
	@post  - a new week is added to the workbook
	@param - lt_wk  - last workweek's date 
			 cg - list of categories for the new sheet to be filled with
	@note  - Needed so the user doesn't need to manually add a workweek sheet.
			 Also makes it streamlined to keep track of the week.
'''
def newsheet(book, sheet, lt_wk, cg):
	# Calculate number of weeks it has been since last workweek
	wk_pst = int((date.today() - lt_wk).days / 7) 

	# Calculate start date of current work week
	cur_wk = lt_wk + timedelta(days = wk_pst * 7)
	# Calculate current week number
	#wk = str(book.worksheets()[-1]).split()[2][:-1]

	new_week = int(str(book.worksheets()[-1]).split()[2][:-1]) + wk_pst

	worksheet = book.add_worksheet(title= "Week " + str(new_week), rows="100", cols="5")
	for x in range(5):
		worksheet.update_cell(1, x + 1, cg[x])
	worksheet.update_cell(1, 1, str(cur_wk))
	return worksheet