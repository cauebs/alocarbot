# ALOCARbot

Telegram bot for fetching and showing classes for UFSC students.

## Installation

```
pipsi install git+https://github.com/cauebs/alocarbot#egg=alocarbot
```

Add your CAGR credentials and your bot's token to `$HOME/.config/alocarbot.json`:

```
{
    "username": "caue.bs",
    "password": "iloveyogurt",
    "token": "bot token",
    "db_path": "path/to/file.db"
}
```

## Usage

Run the bot with
```
python -m alocarbot
```
