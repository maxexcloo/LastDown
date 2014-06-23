import codecs
import config
import gmusicapi
import mutagen
import os
import pylast
import string
import time
import unicodedata
from config import *
from gmusicapi import Mobileclient
from gmusicapi import Webclient
from mutagen.easyid3 import EasyID3

############
## Common ##
############

# Directory Creation
def common_directories():
	# Check If Directory Exists
	if not os.path.exists(conf_output_album_folder):
		# Create Directory
		os.makedirs(conf_output_album_folder)

	# Check If Directory Exists
	if not os.path.exists(conf_output_track_folder):
		# Create Directory
		os.makedirs(conf_output_track_folder)

# Existence Check
def common_exist(path):
	# Check If Path Is File
	if os.path.isfile(path):
		# Check Path File Size
		if os.path.getsize(path) != 0:
			# Return True If Not Null
			return True

	# Return False
	return False

# Logging Function
def common_log(type, text):
	# Print Message With Category
	if type != "":
		print "[" + type + "] " + text
	# Print Message Without Category
	else:
		print text

# Path Sanitisation
def common_path(path):
	return "".join(c for c in unicodedata.normalize("NFKD", unicode(path)) if c in "!#&'(),-.=%+[]_ " or c in string.ascii_letters or c in string.digits).strip()

#############
## Mutagen ##
#############

# Delete ID3 Tags
def mutagen_delete(path):
	# Open MP3 & Delete ID3 Tags
	try:
		file = mutagen.File(path, easy = True)
		file.delall()
		file.save()
	# ID3 Deletion Error
	except:
		common_log("Mutagen", "Error Deleting ID3 Tags: " + path)

# Edit MP3 ID3 Tags
def mutagen_edit(path, artist, album, title, genre, track, year):
	# Open MP3
	try:
		file = EasyID3(path)
	# Add Missing ID3 Tags
	except mutagen.id3.ID3NoHeaderError:
		file = mutagen.File(path, easy = True)
		file.add_tags()

	# Set Tags
	file["artist"] = artist
	file["album"] = album
	file["title"] = title
	file["genre"] = genre
	file["tracknumber"] = track
	file["date"] = year

	# Save MP3
	file.save()

#############
## Last.fm ##
#############

# Authenticate
def last_authenticate():
	common_log("Last.fm", "Authenticating...")
	global last

	# Authenticate
	try:
		last = pylast.LastFMNetwork(api_key = auth_last_api_key, api_secret = auth_last_api_secret, username = auth_last_user, password_hash = pylast.md5(auth_last_pass))
	# Authentication Error
	except:
		common_log("Critical", "Last.fm Authentication Failed!")
		sys.exit(0)

# Create Session
def last_create_session():
	common_log("Last.fm", "Creating Session...")
	global last_user

	# Create Session
	try:
		last_session = pylast.SessionKeyGenerator(last)
		last_session_key = last_session.get_session_key(auth_last_user, pylast.md5(auth_last_pass))
		last_user = pylast.User(auth_last_user, last)
	# Session Error
	except:
		common_log("Critical", "Last.fm Session Creation Failed!")
		sys.exit(0)

# Load Recent Tracks
def last_load_recent_tracks():
	common_log("Last.fm", "Loading " + str(conf_last_recent_tracks) + " Recent Tracks...")
	page = 0;

	# Check Limit
	if conf_last_recent_tracks == 0:
		limit = None
	# Normal Limit
	else:
		limit = conf_last_recent_tracks

	# Page Loop
	while limit > 0:
		# Check Limit & Find Recent Tracks
		if limit > 200:
			tracks = last_user.get_recent_tracks(limit = 200, page = page)
		# Normal Limit
		else:
			tracks = last_user.get_recent_tracks(limit = limit, page = page)

		# Loop Through Tracks & Append
		for i in tracks:
			global_tracks.append(i)

		# Check Limit
		if limit > 200:
			limit = limit - 200
			page = page + 1
		# Normal Limit
		else:
			limit = 0

		# Sleep For Rate Limit Period
		time.sleep(conf_last_rate_limit)

# Load Top Albums
def last_load_top_albums():
	common_log("Last.fm", "Loading Top " + str(conf_last_top_albums) + " Albums...")

	# Loop Through Time Periods
	for time_period in conf_last_top_albums_period:
		# Find Top Albums
		albums = last_user.get_top_albums(period = time_period, limit = conf_last_top_albums)

		# Loop Through Albums & Append
		for i in albums:
			global_albums.append(i)

		# Sleep For Rate Limit Period
		time.sleep(conf_last_rate_limit)

# Load Top Tracks
def last_load_top_tracks():
	common_log("Last.fm", "Loading Top " + str(conf_last_top_tracks) + " Tracks...")

	# Loop Through Time Periods
	for time_period in conf_last_top_tracks_period:
		# Find Top Tracks
		tracks = last_user.get_top_tracks(period = time_period, limit = conf_last_top_tracks)

		# Loop Through Tracks & Append
		for i in tracks:
			global_tracks.append(i)

		# Sleep For Rate Limit Period
		time.sleep(conf_last_rate_limit)

##################
## Google Music ##
##################

# Authenticate Mobile
def gmusic_authenticate_mobile():
	common_log("Google Music", "Authenticating Mobile...")
	global gmusicmobile

	# Authenticate Mobile
	try:
		gmusicmobile = Mobileclient()
		gmusicmobile.login(auth_gmusic_user, auth_gmusic_pass)
	# Authentication Error
	except:
		common_log("Critical", "Google Music Mobile Authentication Failed!")
		sys.exit(0)

# Authenticate PC
def gmusic_authenticate_pc():
	common_log("Google Music", "Authenticating PC...")
	global gmusicpc

	# Authenticate PC
	try:
		gmusicpc = Webclient()
		gmusicpc.login(auth_gmusic_user, auth_gmusic_pass)
	# Authentication Error
	except:
		common_log("Critical", "Google Music PC Authentication Failed!")
		sys.exit(0)

# Download Album
def gmusic_download_album(id, path):
	common_log("", "Downloading Album: " + id['artist'] + " - " + id['name'])

	# Download Album
	try:
		# Check Directory & Create Directory
		if not os.path.isdir(path):
			os.makedirs(path)

		# Load Album & Download Tracks
		for idtr in gmusicmobile.get_album_info(id['albumId'])['tracks']:
			pathtr = path + "/" + idtr['artistId'][0] + " - " + idtr['storeId'] + ".mp3"

			# Check If Track Exists
			if common_exist(pathtr):
				common_log("", "Track Already Exists: " + idtr['artist'] + " - " + idtr['title'])
			# Download Track
			else:
				gmusic_download_track(idtr, pathtr)
	# Download Error
	except:
		common_log("", "Download Error: " + id['artist'] + " - " + id['name'])

# Download Track
def gmusic_download_track(id, path):
	common_log("", "Downloading Track: " + id['artist'] + " - " + id['title'])

	# Download Track
	try:
		# Open Binary Mode File & Write Stream To File
		file = codecs.open(path, "wb")
		file.write(gmusicpc.get_stream_audio(id['storeId']))
		file.close()

		# Tag Track
		try:
			mutagen_edit(path, id['artist'], id['album'], id['title'], gmusicmobile.get_track_info(id['storeId'])['genre'], str(id['trackNumber']), str(gmusicmobile.get_album_info(id['albumId'])['year']))
		# Mutagen Error
		except:
			common_log("Mutagen", "Error Editing ID3 Tags: " + path)
	# Download Error
	except:
		common_log("", "Download Error: " + id['artist'] + " - " + id['title'])

		# Remove File
		try:
			os.remove(path)
		# Remove File Error
		except:
			common_log("", "Error Deleting: " + path)

# Get Top Albums
def gmusic_get_albums():
	common_log("Google Music", "Getting Albums...")

	# Loop Through Albums
	for i in global_albums:
		name = i[0].__str__()
		text = name.replace(" - ", " ")

		# Search Music & Find ID
		try:
			result = gmusicmobile.search_all_access(text)
			id = result['album_hits'][0]['album']
		# Search Error
		except:
			common_log("", "Album Not Found: " + name)
			continue

		# Download Album
		path = conf_output_album_folder + "/" + id['artistId'][0] + " - " + id['albumId']
		gmusic_download_album(id, path)

		# Sleep For Rate Limit Period
		time.sleep(conf_last_rate_limit)

# Get Top Tracks
def gmusic_get_tracks():
	common_log("Google Music", "Getting Tracks...")

	# Loop Through Tracks
	for i in global_tracks:
		name = i[0].__str__()
		text = name.replace(" - ", " ")

		# Search Music & Find ID
		try:
			result = gmusicmobile.search_all_access(text)
			id = result['song_hits'][0]['track']
			path = conf_output_track_folder + "/" + id['artistId'][0] + " - " + id['storeId'] + ".mp3"
			pathal = conf_output_album_folder + "/" + id['artistId'][0] + " - " + id['albumId'] + "/" + id['artistId'][0] + " - " + id['storeId'] + ".mp3"
		# Search Error
		except:
			common_log("", "Track Not Found: " + name)
			continue

		# Check If Track Exists
		if common_exist(path) or common_exist(pathal):
			common_log("", "Track Already Exists: " + name)
			continue

		# Download Track
		gmusic_download_track(id, path)

		# Sleep For Rate Limit Period
		time.sleep(conf_last_rate_limit)
