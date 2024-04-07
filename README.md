# Palpatunes

This is a discord music bot using the discord, yt-dlp and ffmpeg libraries.

The main reason for me creating this project was due to my discord wanting a music bot that can play anything from youtube. So I volunteered to make one for the community and run it on a server. To run this bot you will need to first visit https://discord.com/developers and create a developer account. Once the account has been created you will then need to generate a token to use the bot. Once you have followed the instructions below you will have a working bot to use in discord. Enjoy! 😄

## 🚀 Quick Start

### Install the below libraries using pip install

```bash
pip install discord.py
pip install yt-dlp
pip install discord.py pynacl
sudo apt install ffmpeg
```

### Update filepaths

In Plapatunes.py there is a token variable on line 13. You need to put in your discord bot token there for the bot to run. Below is the section you need to update.

```python
token = 'ADD YOUR TOKEN HERE'
```

## Run Palpatunes.py in terminal

```bash
python3 Palpatunes.py
```
or
```bash
python Palpatunes.py
```
You should see the bot start up in the terminal. Once that is done just invite the bot into discord and enjoy!

## 📖 Usage

Available commands:

* `!play` - Adds song to queue
* `!skip` - Skips currently playing song
* `!stop` - Stops the bot
* `!queue` - Displays a list of all songs in queue

When using the bot command !play you can either add a youtube link to play the selected song or you can type the name and artis of the song. See example below.

!play https://www.youtube.com/watch?v=DtVBCG6ThDk&list=PLSUp7mU4ws_SRCaa0pThURd1yPMB8KP-K&index=17

or

!play Rocked Man Elton John

## 🤝 Contributing

### Clone the repo

```bash
git clone https://github.com/LukaRaspudic/Palpatunes-Discord-Music-Bot
```

### Run the project

```bash
python3 Palpatunes.py
```
or
```bash
python Palpatunes.py
```

### Enyoy the bot 😄

### Submit a pull request

If you'd like to contribute, please fork the repository and open a pull request to the `main` branch.