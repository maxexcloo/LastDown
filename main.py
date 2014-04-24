from config import *
from function import *

# Application Bootstrap
if __name__ == "__main__":
	# Create Directories
	common_create_directories()

	# Last.FM Authentication
	last_authenticate()

	# Last.FM Session Creation
	last_create_session()

	# Last.FM Recent Track Check
	if conf_last_recent_tracks > 0:
		# Last.FM Load Recent Tracks
		last_load_recent_tracks()

	# Last.FM Top Albums Check
	if conf_last_top_albums > 0:
		# Last.FM Load Top Albums
		last_load_top_albums()

	# Last.FM Top Tracks Check
	if conf_last_top_tracks > 0:
		# Last.FM Load Top Tracks
		last_load_top_tracks()

	# Google Music Check Status
	if conf_gmusic_enabled:
		# Authenticate Mobile
		gmusic_authenticate_mobile()

		# Authenticate PC
		gmusic_authenticate_pc()

		# Get Albums
		gmusic_get_albums()

		# Get Tracks
		gmusic_get_tracks()
