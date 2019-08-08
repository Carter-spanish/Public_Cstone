# Discord-Capstone
---
## Required Packages
* discord
* Google Drive API
* Google Sheets API

## Things you need to do:
### Fill out Creds.ini.
#### 1. Discord
---
For discord you must apply for bot account [here.](https://discordapp.com/developers/applications/)
<details>
	<summary> If you aren't familiar with the setup process click here!</summary>
	
		1. On this page while you are logged in, click the **New Application** button, name the bot, and click **Save Changes**.
		2. Click on the **Bot** tab on the left. In this tab click on the **Add Bot** button. 
		3. While still in the **Bot** tab, choose permissions for the bot. At minimum the bot requires **Send Messages**, however **Administrator** is the easiest option. 
		4. Click **Click to Reveal Token** underneath the **Username** field and copy it. Paste it in Creds.ini in the discord section by client_token. 
		5. Click on the Oauth2 button. In this tab, in the Scopes box, click **bot** in the **Scopes** section, then choose permissions in the **Bot Permissions** section that pops up to match what you chose before.
		6. Copy the link in the **Scopes** section and paste it in your browser. This will take you to a page to add the bot to a server you own. Choose a server and click **Authorize**. Congratulations your bot is now hooked up!
</details>

#### 2. Google Sheets
---
