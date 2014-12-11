triviabot
=========

A trivia IRC bot, written in Python. Requires Python 2.7.

Setting up
=========
On *nix based operating systems (assuming you have Python 2.7):
```
$ git clone https://github.com/Snowstormer/triviabot.git
$ cd triviabot/
$ cp config.json.example config.json
$ python bot.py
```

Of course, you'd have to edit the config first to make it actually work, the example config.

```json
{
	"server": "irc.myserver.com",
	"port": 6667,
	"nickname": "Triviabot",
	"password": "",
	"account": "",
	"channel": "#Trivia",
	"admins": ["admin"],
	"prefix": "!",
	
	"enabledtopics": ["all", "animals", "astronomy", "countries", "culture", "general", "geography", "history", "internet", "languages", "mathematics", "music", "politics", "science"]
}
```

Everything is pretty self-explanatory - if your bot has no NickServ password, leave `password` blank. Leaving `account` blank will default it to the bot's nickname.

If you wish to disable any of the topics, just remove them from the `enabledtopics` list and you're good to go.
