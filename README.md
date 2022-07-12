# telinsta
Telegram bot for downloading Instagram posts.

## Install
Clone the repository
```sh
git clone https://github.com/mucahitkurtlar/telinsta.git
```
Change working directory into repository
```sh
cd telinsta
```
Create a file named `credentials.py` and fill it with these lines:
```py
TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" # Telegram bot token
USERNAME = "XXXXXXXXXXXXX" # Instagram username
PASSWORD = "XXXXXXXXXXXXXXXXXXXXXXXX" # Instagram password
```
### Attention!
<b>Please don't use your main Instagram account.</b> It can be blocked. Create another one for automation.

### Docker
You can run this project as container.
<br>
Build the image
```sh
./build.sh
```
Run the container
```sh
docker run --name telinsta -v $(pwd)/credentials.py:/opt/telinsta/credentials.py mucahitkurtlar/telinsta
```
### Native
Firstly, install requirements
```sh
pip install -r requirements.txt
```
Run `main.py`
```sh
python3 main.py
```

## Usage
```
/download <link> [index] [options...] - download instagram post
/caption <link> - get caption of instagram post
/help - show this message

options:
-c --caption - download with caption
-p --pcaption - download with pcaption
-t --thumbnail - download with thumbnail
```
### Examples
`/d https://www.instagram.com/p/Cd1HoW4LJMg/ 2 -t` download 2nd media with thumbnail
<br>

`/c https://www.instagram.com/p/CeD6P3aDIi6/` download post's caption

## TODO
- ☑ Handle `igshid` payload on URL 
- ☑ Reels support
- ☐ Profile picture support
- ☑ Story support