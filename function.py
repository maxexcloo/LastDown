import codecs
import config
import gmusicapi
import mutagen
import os
import pylast
import time
import whatapi

from config import *
from gmusicapi import Mobileclient
from gmusicapi import Webclient
from mutagen.easyid3 import EasyID3

############
## Common ##
############

# Create Directories
def common_create_directories():
	# Check If Directory Exists
	if not os.path.exists(conf_output_album_folder):
		# Create Directory
		os.makedirs(conf_output_album_folder)

	# Check If Directory Exists
	if not os.path.exists(conf_output_track_folder):
		# Create Directory
		os.makedirs(conf_output_track_folder)

# Check Existence
def common_exist(path):
	# Check If Path Exists
	if os.path.isfile(path):
		# Check Path File Size
		if os.path.getsize(path) != 0:
			# Return True
			return True

	# Return False
	return False

# Windows Name Replace Function
def common_windows_name_replace(text):
	# Replace Special Forbidden Characters
	text = text.replace("*", "")
	text = text.replace(":", "")
	text = text.replace("<", "")
	text = text.replace(">", "")
	text = text.replace("?", "")
	text = text.replace("|", "")

	# Return Text
	return text

#############
## Mutagen ##
#############

# Delete MP3 ID3 Tags
def mutagen_delete(path):
	# Open MP3 & Delete ID3 Tags
	try:
		file = mutagen.File(path, easy = True)
		file.delall()
		file.save()
	# ID3 Error
	except:
		print "Error Deleting ID3 Tag: " + path

# Edit MP3 ID3 Tags
def mutagen_edit(path, artist, title, album, genre, tracknumber, year):
	# Open MP3
	try:
		file = EasyID3(path)
	# Add Missing MP3 Tags
	except mutagen.id3.ID3NoHeaderError:
		file = mutagen.File(path, easy = True)
		file.add_tags()

	# Set Tags
	file["artist"] = artist
	file["title"] = title
	file["album"] = album
	file["genre"] = genre
	file["tracknumber"] = tracknumber
	file["date"] = year

	# Save MP3
	file.save()

#############
## Last.FM ##
#############

# Authenticate
def last_authenticate():
	global last
	print "[Last.FM] Authenticating..."

	# Authenticate
	try:
		last = pylast.LastFMNetwork(api_key = auth_last_api_key, api_secret = auth_last_api_secret, username = auth_last_user, password_hash = pylast.md5(auth_last_pass))
	# Authentication Error
	except:
		print "[Critical] Last.FM Authentication Failed!"
		sys.exit(0)

# Create Session
def last_create_session():
	global last_user
	print "[Last.FM] Creating Session..."

	# Create Session & User
	try:
		last_session = pylast.SessionKeyGenerator(last)
		last_session_key = last_session.get_session_key(auth_last_user, pylast.md5(auth_last_pass))
		last_user = pylast.User(auth_last_user, last)
	# Session Error
	except:
		print "[Critical] Last.FM Session Creation Failed!"
		sys.exit(0)

# Load Recent Tracks
def last_load_recent_tracks():
	print "[Last.FM] Loading " + str(conf_last_recent_tracks) + " Recent Tracks..."

	# Check If Limit None
	if conf_last_recent_tracks == 0:
		# Set Limit
		limit = None
	# Normal Limit
	else:
		# Set Limit
		limit = conf_last_recent_tracks

	# Page Variable
	page = 0;

	# Page Loop
	while limit > 0:
		# Check Limit
		if limit > 200:
			# Find Recent Tracks
			tracks = last_user.get_recent_tracks(limit = 200, page = page)
		# Normal Limit
		else:
			# Find Recent Tracks
			tracks = last_user.get_recent_tracks(limit = limit, page = page)

		# Loop Through Tracks Array
		for i in tracks:
			# Append Track To Array
			global_tracks.append(i)

		# Check Limit
		if limit > 200:
			# Subtract Limit
			limit = limit - 200

			# Add Page
			page = page + 1
		# Normal Limit
		else:
			# Set Limit
			limit = 0

		# Sleep Rate Limit Period
		time.sleep(conf_last_rate_limit)

# Load Top Albums
def last_load_top_albums():
	print "[Last.FM] Loading Top " + str(conf_last_top_albums) + " Albums..."

	# Loop Through Time Periods
	for time_period in conf_last_top_albums_period:
		# Find Top Albums
		albums = last_user.get_top_albums(period = time_period, limit = conf_last_top_albums)

		# Loop Through Albums Array
		for i in albums:
			# Append Album To Array
			global_albums.append(i)

		# Sleep Rate Limit Period
		time.sleep(conf_last_rate_limit)

# Load Top Tracks
def last_load_top_tracks():
	print "[Last.FM] Loading Top " + str(conf_last_top_tracks) + " Tracks..."

	# Loop Through Time Periods
	for time_period in conf_last_top_tracks_period:
		# Find Top Tracks
		tracks = last_user.get_top_tracks(period = time_period, limit = conf_last_top_tracks)

		# Loop Through Tracks Array
		for i in tracks:
			# Append Track To Array
			global_tracks.append(i)

		# Sleep Rate Limit Period
		time.sleep(conf_last_rate_limit)

##################
## Google Music ##
##################

# Authenticate Mobile
def gmusic_authenticate_mobile():
	global gmusicmobile
	print "[Google Music] Authenticating Mobile..."

	# Authenticate Mobile
	try:
		gmusicmobile = Mobileclient()
		gmusicmobile.login(auth_gmusic_user, auth_gmusic_pass)
	# Authentication Error
	except:
		print "[Critical] Google Music Mobile Authentication Failed!"
		sys.exit(0)

# Authenticate PC
def gmusic_authenticate_pc():
	global gmusicpc
	print "[Google Music] Authenticating PC..."

	# Authenticate PC
	try:
		gmusicpc = Webclient()
		gmusicpc.login(auth_gmusic_user, auth_gmusic_pass)
	# Authentication Error
	except:
		print "[Critical] Google Music PC Authentication Failed!"
		sys.exit(0)

# Download Album
def gmusic_download_album(id, path):
	print "Downloading Album: " + id['artist'] + " - " + id['name']

	# Download Album
	try:
		# Check Directory
		if not os.path.isdir(path):
			# Create Directory
			os.makedirs(path)

		# Load Album
		for idtr in gmusicmobile.get_album_info(id['albumId'])['tracks']:
			# Set Path
			pathtr = common_windows_name_replace(path + "/" + str(idtr['trackNumber']) + ". " + idtr['artist'] + " - " + idtr['title'] + ".mp3")

			# Check If Track Exists
			if common_exist(pathtr):
				print "Track Already Exists: " + idtr['artist'] + " - " + idtr['title']
			# Download Track
			else:
				gmusic_download_track(idtr, pathtr)
	# Download Error
	except:
		print "Download Error: " + id['artist'] + " - " + id['name']

# Download Track
def gmusic_download_track(id, path):
	print "Downloading Track: " + id['artist'] + " - " + id['title']

	# Download Track
	try:
		# Open Binary Mode File & Write Stream To File
		file = codecs.open(path, 'wb')
		file.write(gmusicpc.get_stream_audio(id['storeId']))
		file.close()

		# Tag Track
		try:
			mutagen_edit(path, id['artist'], id['title'], id['album'], gmusicmobile.get_track_info(id['storeId'])['genre'], str(id['trackNumber']), str(gmusicmobile.get_album_info(id['albumId'])['year']))
		# ID3 Error
		except:
			print "Error Editing ID3 Tag: " + path
	# Download Error
	except:
		print "Download Error: " + id['artist'] + " - " + id['title']

		# Remove File
		try:
			os.remove(path)
		# File Error
		except:
			print "Error Deleting: " + path

# Get Top Albums
def gmusic_get_albums():
	print "[Google Music] Getting Albums..."

	# Loop Through Albums
	for i in global_albums:
		# Define Variables
		string = i[0].__str__()
		path = common_windows_name_replace(conf_output_album_folder + "/" + string)
		text = string.replace(" - ", " ")

		# Search Music & Find ID
		try:
			result = gmusicmobile.search_all_access(text)
			id = result['album_hits'][0]['album']
		# Search Error
		except:
			print "Album Not Found: " + string
			continue

		# Download Album
		gmusic_download_album(id, path)

		# Sleep Rate Limit Period
		time.sleep(conf_last_rate_limit)

# Get Top Tracks
def gmusic_get_tracks():
	# Print Message
	print "[Google Music] Getting Tracks..."

	# Loop Through Tracks
	for i in global_tracks:
		# Define Variables
		string = i[0].__str__()
		text = string.replace(" - ", " ")
		path = common_windows_name_replace(conf_output_track_folder + "/" + string + ".mp3")

		# Check If Track Exists
		if common_exist(path):
			print "Track Already Exists: " + string
			continue

		# Search Music & Find ID
		try:
			result = gmusicmobile.search_all_access(text)
			id = result['song_hits'][0]['track']
		# Search Error
		except:
			print "Track Not Found: " + string
			continue

		# Download Track
		gmusic_download_track(id, path)

		# Sleep Rate Limit Period
		time.sleep(conf_last_rate_limit)
