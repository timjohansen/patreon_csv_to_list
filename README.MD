# Patreon CSV To List
This is a simple Python app for translating a CSV file of Patreon subscribers into a sorted list for use in video credits.  
This started as a simple script to save time at work, but later turned into a project for learning how to make a GUI. Due to that, it could use more polish, but it seems to get the job done well enough for now. 
<br>

## Getting Started
This script was made on Python 3.11 and should run on any computer with a recent version installed. If you run the script and an empty window appears, you probably need to update.  

Load the CSV file provided by Patreon, select your options (listed below), and generate the list to be copied into your preferred video editing software.

## Options
### Mix Tiers Together / Keep Tiers Separated:
The first option will take every name in the CSV file and sort them into one big list. The second will sort them into smaller lists for each tier.

### Number of columns:
If you want the list to be displayed in the credits as multiple columns, change this number.

### Sort patron list:
**Alphabetically:** sorts names from A-Z, disregarding most other characters list asterisks or emoji.  
**By Pledge Amount:** sorts the list from the highest pledge to lowest.  
WARNING: This option assumes all pledges are in the same currency. Use 'alphabetically' if they are not.  

### Replace empty name fields with:  
This option determines how to handle a patron who doesn't have a name associated with their account.  

**Nothing:** Skips the patron entirely.  
**Full email:** Uses the patron's email address in place of their name.  
**Partial email:** Uses the patron's email address, but only the portion to the left of the @ symbol. For example, 'hstar@fake.site' would be shortened to 'hstar'

### Categorize patrons into tiers by:  
It's possible for a patron to be listed at lower tier than their pledge qualifies them for. This can work around that.  
**Listed Tier:** Sorts patrons according to their tier as listed in the CSV file.  
**Pledge Amount** Sorts patrons into the tier they *should* be in according to their monthly pledge amount. The CSV does not contain the minimum pledge for each tier, so these need to be typed in manually, unfortunately.  
<br>

## Disclaimer
There obviously aren't a lot of CSV files filled with user information floating around the Internet, so all testing was done on the one I had access to through my job. I can't guarantee it'll work with all current or future CSV files. But hey, the source code's MIT licensed, so feel free to change it as needed.

## Hopeful TODO list
Add more comments/make more readable  
Polish up the GUI  
Possibly make a web-based version that can run in a browser as a Javascript and CSS exercise
