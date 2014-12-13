from config import *
from function import *

# Application Bootstrap
if __name__ == "__main__":
	# Create Directories
	common_directories()

	# Last.fm Authentication
	lastfm_authenticate()

	# Last.fm Session Creation
	lastfm_create_session()

	# Last.fm Recent Track Check
	if conf_lastfm_recent_tracks > 0:
		# Last.fm Load Recent Tracks
		lastfm_load_recent_tracks()

	# Last.fm Top Album Check
	if conf_lastfm_top_albums > 0:
		# Last.fm Load Top Albums
		lastfm_load_top_albums()

	# Last.fm Top Track Check
	if conf_lastfm_top_tracks > 0:
		# Last.fm Load Top Tracks
		lastfm_load_top_tracks()

	# Google Music Authenticate Mobile
	google_music_authenticate_mobile()

	# Google Music Authenticate PC
	google_music_authenticate_pc()

	# Google Music Get Albums
	google_music_get_albums()

	# Google Music Get Tracks
	google_music_get_tracks()
