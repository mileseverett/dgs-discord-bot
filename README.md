# DGS Discord Bot
A discord bot to serve all of DGS's needs. Created mostly by Miles with help from EB and currently maintained by Miles/EB.

## Functions

#### Public commands
- $vouchinfo: Shows the number of vouches for a specific person (when used in a non-whitelisted channel)
- $source: Gives the link to the GitHub page

#### Vouch/Anti-vouch commands (any Wing+)
- $vouch: Used to vouch a 2-stripe
- $antivouch: Used to anti-vouch a 2-stripe
- $vouchinfo: Shows all of the vouches and anti-vouches for a given 2-stripe, with reasons where applicable. This is the same as the public command, but gives more information in whitelisted channels.
- $unvouch: Remove a vouch

#### Administrative commands (Reviewer+)
##### Vouches
- $vouchbuffer: See all vouches needing approval
- $acceptvouch: Accept a singular vouch (by vouchID)
- $acceptallvouches: Accept all current vouches in the buffer
- $rejectallvouches: Remove all current vouches in the buffer
- $updatingmessageinit: This initalizes a table to display vouches
- $updatemessage: Updates the table of vouches to the most current version of vouches
- $removeuser: Removes all of a user's vouches
- $removevouch: Removes a specific vouch for a user
- $adminvouch: Lets admins populate a vouch for someone else. Useful for populating vouches prior to the bot implementation.
- $renamevouchee: Allows you to change the name of a vouchee

##### Whitelisting
- $channelcheck: Check if the current channel is "whitelisted" (allows all Wing+ commands)
- $removewhitelistchannel: Makes the current channel not whitelisted
- $whitelistchannel: Makes the current channel whitelisted

#### Mass Speeds
- $msstart: Initialize a mass speeds session. Will make a message that can be reacted to.
- $msend: Ends the current mass speeds session.
- $msteams: Generates and outputs weighted randomized teams based on DGS rank.

## Contributing
If you want to help contribute you can clone the repo and make local changes. You can run the bot locally to test your changes (we have an existing discord server or you can make your own), and the bot runs off of AWS. If you need access to the "production" version contact Miles or EB.

To clone:
```bash
git clone https://github.com/mileseverett/dgs-discord-bot.git
```

To run the bot locally for testing/developing just run bot.py. Code assuming the bot files are in your current directory:

```python
pip install discord
```

```bash
py bot.py
```

## Have ideas?
Send them to Miles/EB or post in the discord. Current possible future plans include automating DGS hiscores. Anything not DG related that would be nice?
