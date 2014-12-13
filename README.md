triviabot
=========

A trivia IRC bot, written in Python. Requires Python 2.7.

Setting up
=========
On *nix based operating systems (assuming you have Python 2.7 (and git, if not, shame on you)):
```
$ git clone https://github.com/Snowstormer/triviabot.git
$ cd triviabot/
$ cp config.example.json config.json
$ python bot.py
```

Of course, you'd have to edit the config first to make it actually work, the example config is similar to this:

```json
{
	"--NEED HELP?--": "--If you are unsure how to edit this config file, please visit the GitHub page for help.--",
	"server": "irc.myserver.com",
	"port": 6667,
	"nickname": "Triviabot",
	"password": "",
	"account": "",
	"channel": "#Trivia",
	"admins": ["admin"],
	"prefix": "!",

	"--OPTIONAL CONFIGURATION--": "--You don't have to edit anything below here, but you can if you so wish.--",
	"enabledtopics": ["topic", "topic", "topic"],
	"savepoints": false
}
```

Everything is pretty self-explanatory - if your bot has no NickServ password, leave `password` blank. Leaving `account` blank will default it to the bot's nickname.

If you wish to disable any of the topics, just remove them from the `enabledtopics` array and you're good to go.

Setting `savepoints` to true will make the bot keep all earned points even after the game is stopped or the bot disconnects through a points file (`points.json`), deleting this file will reset the points.

Custom topics
=============
Adding custom topics is not hard, just create a new file in the `topics` directory called `(topic).json` - for example, `example.json`.

This is the basic structure of a topic file:

```json
{
	"Question": ["answer"],
	"Question 2": ["answer 2", "rewsna"]
}
```

As for question, you can put anything - however answers have some guidelines. To make answers not throw an error, you **have to** place them inside a array, yes, even if there's only one answer it has to be in a array.

Answers in the topic files that come with the bot are (mostly) all lowercase - this used to be a requirement, but is not anymore.

Finally, you have to add your topic into the `config.json`. Just plop it into the `enabledtopics` array at any place - the array is sorted when displayed anyway.

If you think your topic is good enough to be in the core, you can submit a pull request.