import codecs
import config
import mutagen
import os
import pylast
import string
import sys
import time
import urllib
from config import *
from gmusicapi import Mobileclient
from gmusicapi import Webclient
from mutagen.easyid3 import EasyID3
from unidecode import unidecode

############
## Common ##
############

# Directory Creation
def common_directories():
	# Check If Album Directory Exists
	if not os.path.exists(conf_output_album_folder):
		# Create Album Directory
		os.makedirs(conf_output_album_folder)

	# Check If Track Directory Exists
	if not os.path.exists(conf_output_track_folder):
		# Create Track Directory
		os.makedirs(conf_output_track_folder)

# Existence Check
def common_exist(path):
	# Check If Path Is A File
	if os.path.isfile(path):
		# Check Path File Size
		if os.path.getsize(path) != 0:
			# Return True If Not Empty, File Exists
			return True

	# Return False, File Doesn't Exist
	return False

# Logging Function
def common_log(type, text):
	try:
		# Check If Type Text Exists
		if type != "":
			# Print Message With Type
			print "[" + type + "] " + text
		# Type Doesn't Exist
		else:
			# Print Message Without Type
			print text
	except:
		pass

# Path Sanitisation
def common_path(text):
	try:
		return "".join(c for c in unidecode(text) if c in "!#&'(),-.=%+[]_ " or c in string.ascii_letters or c in string.digits).strip()
	except:
		return "".join(c for c in text if c in "!#&'(),-.=%+[]_ " or c in string.ascii_letters or c in string.digits).strip()

#############
## Last.fm ##
#############

# Authenticate
def lastfm_authenticate():
	common_log("Last.fm", "Authenticating...")
	global lastfm

	# Authenticate
	try:
		lastfm = pylast.LastFMNetwork(api_key = auth_lastfm_api_key, api_secret = auth_lastfm_api_secret, username = auth_lastfm_user, password_hash = pylast.md5(auth_lastfm_pass))
	# Authentication Error
	except:
		common_log("Critical", "Last.fm Authentication Failed!")
		sys.exit(0)

# Create Session
def lastfm_create_session():
	common_log("Last.fm", "Creating Session...")
	global lastfm_user

	# Create Session
	try:
		lastfm_session = pylast.SessionKeyGenerator(lastfm)
		lastfm_session_key = lastfm_session.get_session_key(auth_lastfm_user, pylast.md5(auth_lastfm_pass))
		lastfm_user = pylast.User(auth_lastfm_user, lastfm)
	# Session Error
	except:
		common_log("Critical", "Last.fm Session Creation Failed!")
		sys.exit(0)

# Load Recent Tracks
def lastfm_load_recent_tracks():
	common_log("Last.fm", "Loading " + str(conf_lastfm_recent_tracks) + " Recent Tracks...")
	page = 0;

	# Check Limit
	if conf_lastfm_recent_tracks == 0:
		limit = None
	# Normal Limit
	else:
		limit = conf_lastfm_recent_tracks

	# Loop While Tracks Exist
	while limit > 0:
		# Check Track Count
		if limit > 200:
			# Find Recent Tracks
			tracks = lastfm_user.get_recent_tracks(limit = 200, page = page)
		# Normal Track Count
		else:
			# Find Recent Tracks
			tracks = lastfm_user.get_recent_tracks(limit = limit, page = page)

		# Loop Through Tracks
		for i in tracks:
			# Append Tracks To Array
			global_tracks.append(i)

		# Check Track Count
		if limit > 200:
			limit = limit - 200
			page = page + 1
		# Normal Track Count
		else:
			limit = 0

		# Sleep For Rate Limit Period
		time.sleep(conf_lastfm_rate_limit)

# Load Top Albums
def lastfm_load_top_albums():
	common_log("Last.fm", "Loading Top " + str(conf_lastfm_top_albums) + " Albums...")

	# Loop Through Time Periods
	for time_period in conf_lastfm_top_albums_period:
		# Find Top Albums
		albums = lastfm_user.get_top_albums(period = time_period, limit = conf_lastfm_top_albums)

		# Loop Through Albums
		for i in albums:
			# Append Albums To Array
			global_albums.append(i)

		# Sleep For Rate Limit Period
		time.sleep(conf_lastfm_rate_limit)

# Load Top Tracks
def lastfm_load_top_tracks():
	common_log("Last.fm", "Loading Top " + str(conf_lastfm_top_tracks) + " Tracks...")

	# Loop Through Time Periods
	for time_period in conf_lastfm_top_tracks_period:
		# Find Top Tracks
		tracks = lastfm_user.get_top_tracks(period = time_period, limit = conf_lastfm_top_tracks)

		# Loop Through Tracks
		for i in tracks:
			# Append Tracks To Array
			global_tracks.append(i)

		# Sleep For Rate Limit Period
		time.sleep(conf_lastfm_rate_limit)

##################
## Google Music ##
##################

# Authenticate Mobile
def google_music_authenticate_mobile():
	common_log("Google Music", "Authenticating Mobile...")
	global google_music_mobile

	# Authenticate Mobile
	google_music_mobile = Mobileclient()
	logged_in = google_music_mobile.login(auth_google_music_user, auth_google_music_pass)

	# Authentication Error
	if not logged_in:
		common_log("Critical", "Google Music Mobile Authentication Failed!")
		sys.exit(0)

# Authenticate PC
def google_music_authenticate_pc():
	common_log("Google Music", "Authenticating PC...")
	global google_music_pc

	# Authenticate PC
	google_music_pc = Webclient()
	logged_in = google_music_pc.login(auth_google_music_user, auth_google_music_pass)

	# Authentication Error
	if not logged_in:
		common_log("Critical", "Google Music PC Authentication Failed!")
		sys.exit(0)

# Download Album
def google_music_download_album(id, path):
	common_log("", "Downloading Album: " + id['artist'] + " - " + id['name'])

	# Download Album
	try:
		# Check Directory & Create Directory
		if not os.path.isdir(path):
			os.makedirs(path)

		# Check Album Art
		if not common_exist(path + "folder.jpg"):
			# Download Album Art
			try:
				urllib.urlretrieve (id['albumArtRef'], path + "/folder.jpg")
			# Download Error
			except:
				common_log("", "Error Downloading Album Art For: " + id['artist'] + " - " + id['title'])

		# Load Album & Download Tracks
		for idtrack in google_music_mobile.get_album_info(id['albumId'])['tracks']:
			pathtrack = path + "/" + common_path(str(idtrack['trackNumber']).zfill(2) + ". " + idtrack['title'] + ".mp3")

			# Check If Track Exists
			if common_exist(pathtrack):
				common_log("", "Track Already Exists: " + idtrack['artist'] + " - " + idtrack['title'])
			# Download Track
			else:
				google_music_download_track(idtrack, pathtrack)
	# Download Error
	except:
		common_log("", "Download Error: " + id['artist'] + " - " + id['name'])

# Download Track
def google_music_download_track(id, path):
	common_log("", "Downloading Track: " + id['artist'] + " - " + id['title'])

	# Download Track
	try:
		# Open Binary Mode File & Write Stream To File
		file = codecs.open(path, "wb")
		file.write(google_music_pc.get_stream_audio(id['storeId']))
		file.close()

		# Tag Track
		try:
			# Open Track
			try:
				file = EasyID3(path)
			# Add Missing ID3 Tags
			except mutagen.id3.ID3NoHeaderError:
				file = mutagen.File(path, easy = True)
				file.add_tags()

			# Set Tags
			file["album"] = id['album']
			file["artist"] = id['artist']
			file["date"] = str(google_music_mobile.get_album_info(id['albumId'])['year'])
			try:
				file["disknumber"] = str(id['discNumber'])
			except: 
				pass
			file["genre"] = google_music_mobile.get_track_info(id['storeId'])['genre']
			file["title"] = id['title']
			file["tracknumber"] = str(id['trackNumber']).zfill(2)

			# Save MP3
			file.save()
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
def google_music_get_albums():
	common_log("Google Music", "Getting Albums...")

	# Loop Through Albums
	for i in global_albums:
		text = i[0].__str__()

		# Search Music & Find ID
		try:
			result = google_music_mobile.search_all_access(text)
			id = result['album_hits'][0]['album']
		# Search Error
		except:
			common_log("", "Album Not Found: " + text)
			continue

		# Download Album
		path = conf_output_album_folder + "/" + common_path(id['albumArtist'] + " - " + id['name'])
		google_music_download_album(id, path)

		# Sleep For Rate Limit Period
		time.sleep(conf_lastfm_rate_limit)

# Get Top Tracks
def google_music_get_tracks():
	common_log("Google Music", "Getting Tracks...")

	# Loop Through Tracks
	for i in global_tracks:
		text = i[0].__str__()

		# Search Music & Find ID
		try:
			result = google_music_mobile.search_all_access(text)
			id = result['song_hits'][0]['track']
			path = conf_output_track_folder + "/" + common_path(id['albumArtist'] + " - " + id['title'] + ".mp3")
			pathalbum = conf_output_album_folder + "/" + common_path(id['albumArtist'] + " - " + id['album']) + "/" + common_path(str(id['trackNumber']).zfill(2) + ". " + id['title'] + ".mp3")
		# Search Error
		except:
			common_log("", "Track Not Found: " + text)
			continue

		# Check If Track Exists
		if common_exist(path) or common_exist(pathalbum):
			common_log("", "Track Already Exists: " + text)
			continue

		# Download Track
		google_music_download_track(id, path)

		# Sleep For Rate Limit Period
		time.sleep(conf_lastfm_rate_limit)
