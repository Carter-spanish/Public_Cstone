import discord
from discord.ext import commands
from discord.utils import get
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser 
from datetime import datetime, date, timedelta

class Scrum(commands.Cog):
	def __init__(self, client):
		self.client = client

	# Runs when bot is turned on. Initializes Gspread for bot.
	# Creates and shares the sheet with owner if bot does not see it.
	@commands.Cog.listener()
	async def on_ready(self):
		config = configparser.ConfigParser()
		config.read("Creds.ini")

		global sheetclient
		global book
		global worksheet
		global category

		scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive.file']
		creds = ServiceAccountCredentials.from_json_keyfile_name(config.get('sheets', 'cred_file'), scope)
		sheetclient = gspread.authorize(creds)
		category = [str(date.today()), "Team member", "Date", "Hours complete", "Backlog item"]

		# Test if Testing's Sheet exists, if it does open it, otherwise create it.
		try:
			book = sheetclient.open("1Z")
		except:
			book = sheetclient.create("1Z")
			worksheet = book.add_worksheet(title="Week 1", rows="100", cols="5")
			for x in range(5):
				worksheet.update_cell(1, x + 1, category[x])
			book.del_worksheet(book.get_worksheet(0))
			book.share(config.get('sheets', 'owner_email'), perm_type='user', role='owner')

		worksheet = book.get_worksheet(len(book.worksheets()) - 1)
		print("Scrum online.")

	## ~~~ Legacy command ~~~ ##
	# Creates a new sheet for reporting, next week after the last sheet
	@commands.command()
	async def newweek(self, ctx):
		global worksheet
		new_week = len(book.worksheets()) + 1
		worksheet = book.add_worksheet(title= "Week " + str(new_week), rows="100", cols="5")
		for x in range(4):
				worksheet.update_cell(1, x + 1, category[x])

		await ctx.send("New week has been started! Good luck this week!")
	
	# Submit a work report to the current week's sheet
	# If today is not in the same work week as the current sheet, pass to newsheet
	@commands.command()
	async def report(self, ctx, hours: int, *, item: str):
		global worksheet

		tdy = date.today()
		ltwk = datetime.strptime(worksheet.cell(1, 1).value, '%Y-%m-%d').date()
		if ((tdy - ltwk).days > 6):
			worksheet = newsheet(book, worksheet, ltwk, category)
			await ctx.send("New week started!")

		to_sheet = [ctx.author.display_name, str(tdy), hours, item]
		col = worksheet.col_values(2)
		for x in range(4):
			worksheet.update_cell(len(col) + 1, x + 2, to_sheet[x])

		await ctx.send("Thanks for reporting " + str(ctx.author.display_name) +"!")


	# Share the current book with a user that has an @gmail.com email.
	@commands.command()
	async def sharebk(self, ctx, email: str):
		global book
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
def newsheet(book, sheet, lt_wk, cg):
	wk_pst = int((date.today() - lt_wk).days / 7) 

	# Calculate date of current work week
	cur_wk = lt_wk + timedelta(days = wk_pst * 7)
	# Calculate current week number
	#wk = str(book.worksheets()[-1]).split()[2][:-1]

	new_week = int(str(book.worksheets()[-1]).split()[2][:-1]) + wk_pst

	worksheet = book.add_worksheet(title= "Week " + str(new_week), rows="100", cols="5")
	for x in range(5):
		worksheet.update_cell(1, x + 1, cg[x])
	worksheet.update_cell(1, 1, str(cur_wk))
	return worksheet