from cmath import log
import shutil
import logging
import telebot
import instaloader
import glob
from credentials import *
import re

logging.basicConfig(format='[%(levelname)s] %(asctime)s: %(message)s', level=logging.DEBUG)
bot = telebot.TeleBot(TOKEN)
L = instaloader.Instaloader(download_video_thumbnails=False, save_metadata=False, post_metadata_txt_pattern="")
L.login(USERNAME, PASSWORD)
help_message = "/download <link> [index] [options...] - download instagram post\n/caption <link> - get caption of instagram post\n/help - show this message\n\noptions:\n-c --caption - download with caption\n-p --pcaption - download with pcaption\n-t --thumbnail - download with thumbnail"

class LocalPost:
	def __init__(self, shortcode, caption, pcaption):
		self.shortcode = shortcode
		self.caption = caption
		self.pcaption = pcaption



class Option:
	def __init__(self, is_caption, is_pcaption, is_thumbnail, index):
		self.is_caption = is_caption
		self.is_pcaption = is_pcaption
		self.is_thumbnail = is_thumbnail
		self.index = index

def download_post(link: str, thumbnail=False):
	shortcode = re.split("https://www.instagram.com/[a-z]+/", link)[1].split("/")[0]
	logging.debug(f"Shortcode: {shortcode}")

	L.download_video_thumbnails = thumbnail
	
	post = instaloader.Post.from_shortcode(context=L.context, shortcode=shortcode)
	L.download_post(post, shortcode)
	L.download_video_thumbnails = False
	local_post = LocalPost(shortcode, post.caption, post.pcaption)
	return local_post

def is_gallery(path: str):
	return len(glob.glob(path + "/????-??-??_??-??-??_UTC_*.*")) > 1
		
def send_medias(chat_id: int | str, files: str):
	for file in files:
		if file.endswith(".mp4"):
			bot.send_video(chat_id, video=open(file, "rb"))
			logging.debug(f"Video sent to {chat_id}")
		elif file.endswith(".jpg"):
			bot.send_photo(chat_id, photo=open(file, "rb"))
			logging.debug(f"Photo sent to {chat_id}")

def decide_files(local_post: LocalPost, option: Option):
	files = glob.glob(local_post.shortcode + "/*")
	logging.debug(f"Files: {files}")
	is_gallery_t = is_gallery(local_post.shortcode)
	logging.debug(f"Is {local_post.shortcode} gallery: {is_gallery_t}")
	logging.debug(f"Index: {option.index}")

	if len(files) > 1 and is_gallery_t:
		files = glob.glob(local_post.shortcode + f"/????-??-??_??-??-??_UTC_{option.index}.*")
	elif len(files) > 1 and not is_gallery_t:
		files = glob.glob(local_post.shortcode + f"/????-??-??_??-??-??_UTC.*")
	elif len(files) == 1:
		files = glob.glob(local_post.shortcode + "/*")
	else:
		files = None
	logging.debug(f"Files: {files}")

	return files
	

def send_downloaded(chat_id: int | str, local_post: LocalPost, option: Option):
	files = decide_files(local_post, option)
	if files is None:
		bot.send_message(chat_id, "Post not found")
		return

	send_medias(chat_id, files)
	
	if option.is_caption:
		bot.send_message(chat_id, local_post.caption)
		logging.debug(f"Caption sent to {chat_id}")
	if option.is_pcaption:
		bot.send_message(chat_id, local_post.pcaption)
		logging.debug(f"Pcaption sent to {chat_id}")

	shutil.rmtree(local_post.shortcode)
	logging.debug(f"Folder deleted: {local_post.shortcode}")


def check_params(message: str):
	params = message.split(" ")
	index = "*"
	if len(params) <= 1 or not (params[1].startswith("https://www.instagram.com/") or params[1].startswith("https://instagram.com/")):
		logging.debug(f"Invalid link: {params[1]}")
		logging.debug(f"Params length: {len(params)}")
		return None, None
	link = params[1]
	for param in params:
		# only numbers regex
		if re.findall("^[0-9]*$", param):
			print(f"param: {param}")
			index = int(param)
	option = Option("-c" in params or "--caption" in params, "-p" in params or "--pcaption" in params, "-t" in params or "--thumbnail" in params, index)
	return option, link


def send_help_message(chat_id: int | str):
	bot.send_message(chat_id, help_message)

@bot.message_handler(commands=['help'])
def help(message):
	logging.debug(f"help command triggered from {message.chat.id}")
	bot.reply_to(message, help_message)

def handle_story(chat_id: int | str, link: str):
	username = re.split("https://instagram.com/[a-z]+/", link)[1].split("/")[0]
	logging.debug(f"Username: {username}")
	mediaid = re.split("https://instagram.com/[a-z]+/", link)[1].split("/")[1].split("?")[0]
	logging.debug(f"Mediaid: {mediaid}")
	profile = instaloader.Profile.from_username(context=L.context, username=username)
	for stroy in L.get_stories([profile.userid]):
		for item in stroy.get_items():
			if mediaid == str(item.mediaid):
				L.download_storyitem(item, str(mediaid))

	files = glob.glob(str(mediaid) + "/*")
	send_medias(chat_id, files)
	shutil.rmtree(str(mediaid))
	logging.debug(f"Folder deleted: {str(mediaid)}")

@bot.message_handler(commands=['download', 'd'])
def download(message):
	logging.debug(f"download command triggered from {message.chat.id}")
	option, link = check_params(message.text)
	if link is None:
		send_help_message(message.chat.id)
		return
	elif link.startswith("https://www.instagram.com/stories") or link.startswith("https://instagram.com/stories"):
		link = link.replace("www.", "")
		handle_story(message.chat.id, link)
		return

	local_post = download_post(link, option.is_thumbnail)
	send_downloaded(message.chat.id, local_post, option)

@bot.message_handler(commands=['caption', 'c'])
def caption(message):
	logging.debug(f"caption command triggered from {message.chat.id}")
	option, link = check_params(message.text)
	if link is None:
		send_help_message(message.chat.id)
		return
	local_post = download_post(link, option.is_thumbnail)
	bot.send_message(message.chat.id, local_post.caption)
	shutil.rmtree(local_post.shortcode)
	logging.debug(f"Folder deleted: {local_post.shortcode}")

@bot.message_handler(commands=['ping', 'p'])
def ping(message):
	logging.debug(f"ping command triggered from {message.chat.id}")
	bot.reply_to(message, "pong")


bot.infinity_polling()
