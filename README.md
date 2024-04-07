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

Available keys:

* `←: Left Arrow` - Move tetromino left
* `→: Right Arrow` - Move tetromino right
* `↑: Up Arrow` - Rotate tetromino
* `↓: Down Arrow` - Increase rate of decent for tetromino

## 🤝 Contributing

### Clone the repo

```bash
git clone https://github.com/Revan68/Tetris
```

### Update filepaths

In score.py on line 10, you will have to change the filepath for the font to where you saved the images folder. See below examples.

```python
self.font = pygame.font.Font("ADD YOUR FILE PATH FOR THE FONT IN THE IMAGES FOLDER TITLED pixel-operator.ttf", 30)
```
The below example is what I use for the file path on my machine.

```python
self.font = pygame.font.Font("/workspace/github.com/LukaRaspudic/Tetris/images/pixel-operator.ttf", 30)
```
In preview.py on line 12, you will have to reapeat the steps above by updating the file path for images. See below examples.

```python
self.shape_surfaces = {shape: load(f'ADD YOUR FILE PATH HERE THAT LEADS TO IMAGES/images/{shape}.png').convert_alpha() for shape in tetrominos.keys()}
```
The below example is what I use for the file path on my machine.

```python
self.shape_surfaces = {shape: load(f'/workspace/github.com/LukaRaspudic/Tetris/images/{shape}.png').convert_alpha() for shape in tetrominos.keys()}
```

### Run the project

```bash
python3 main.py
```
or
```bash
python main.py
```

### Enyoy the game 😄

### Submit a pull request

If you'd like to contribute, please fork the repository and open a pull request to the `main` branch.