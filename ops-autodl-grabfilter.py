#!/usr/bin/python

# This script is used in conjunction with a program such as autodl-irssi, allowing filtering to be done based on
# torrent / artist attributes.

# ARGUMENTS:
# 1: API Auth Key
# 2: Required snatches from all involved artists combined
# 3: Torrent URL
# 4: Deluge url:port
# 5: Deluge username
# 6: Deluge password
# 7: Torrent path
# 8: Torrent name
# 9: Test mode (Set to 1, default is 0)

import requests
import json
import sys
import os


# Central processing.
def main():
    global test_mode
    api_key = sys.argv[1]
    required_snatches = sys.argv[2]
    torrent_url = sys.argv[3]
    deluge_url = sys.argv[4]
    deluge_username = sys.argv[5]
    deluge_password = sys.argv[6]
    torrent_path = sys.argv[7]
    torrent_name = sys.argv[8]
    if len(sys.argv) == 10:
        test_mode = 1
        print('Running in test mode.')
    else:
        test_mode = 0
    total_snatches = 0
    # Retrieve the torrent ID from the torrent URL
    torrent_id = get_torrent_id(torrent_url)
    print('Torrent ID is', torrent_id)
    # Retrieve the artist ID from the torrent ID
    artists = get_artists(api_key, torrent_id)
    # Iterate through each artist and add total their snatches.
    for artist in artists:
        print('Getting snatches for artist: ' + artist['name'])
        artist_id = artist['id']
        artist_snatches = get_artist_snatches(api_key, artist_id)
        # Check if a value was returned
        if artist_snatches:
            total_snatches += artist_snatches
            ### Disable this to combine ALL artists, rather than using the first returned.
            break
        else:
            continue
    # Compare total snatches with required snatches.
    if int(total_snatches) >= int(required_snatches):
        # Push torrent to torrent client.
        print('Torrent matches criteria, pushing to torrent client.')
        push_to_deluge(deluge_url, deluge_username, deluge_password, torrent_url, torrent_path, torrent_name, api_key)
    else:
        print('Total artist snatches (' + str(total_snatches) + ') less than required snatches ('
              + str(required_snatches) + ').')
        sys.exit()


# Returns the torrent ID from the URL provided by autodl-irssi
# Takes a torrent url.
def get_torrent_id(torrent_url):
    # Could be done with regex, but it hurts my brain.
    # Splits the URL at '&' symbols, then removed 'id=' from the returned value.
    torrent_id = torrent_url.split('&')[1][3:]
    return torrent_id


# Returns a list of dictionaries, each containing an artist.
# Takes an api_key and torrent_id as inputs.
def get_artists(api_key, torrent_id):
    # Get torrent info from API
    print('Fetching torrent information from API.')
    try:
        # Create headers and request data to be sent
        h = {'Authorization': 'token ' + api_key}
        r = requests.get(url='https://orpheus.network/ajax.php?action=torrent&id=' + str(torrent_id), headers=h).text
    except Exception as e:
        print('Error querying API: ', e)
        sys.exit()
    request_json = json.loads(r)
    # Check if response was successful
    if request_json['status'] in 'failure':
        print('Torrent could not be found.')
        sys.exit()
    else:
        return request_json['response']['group']['musicInfo']['artists']


# Returns the total number of snatches for a particular artist.
# Takes an api_key and artist_id as inputs.
def get_artist_snatches(api_key, artist_id):
    # Create headers and request data to be sent
    # Get torrent info from API
    try:
        h = {'Authorization': 'token ' + api_key}
        r = requests.get(url='https://orpheus.network/ajax.php?action=artist&id=' + str(artist_id), headers=h).text
    except Exception as e:
        print('Error querying API: ', e)
        sys.exit()
    # Check if response was successful
    if not r:
        print('Artist could not be found.')
        return
    else:
        request_json = json.loads(r)
        return request_json['response']['statistics']['numSnatches']


# Push a .torrent file to deluge
# Takes an url (deluge daemon url), a username, a password, and the path to the torrent file.
def push_to_deluge(deluge_url, username, password, torrent_url, torrent_path, torrent_name, api_key):
    deluge_command = 'connect' + ' ' + deluge_url + ' ' + username + ' ' + password + '; add ' + torrent_path
    deluge_command = '"' + deluge_command + '"'
    try:
        print('Match found: ', torrent_name)
        with open("/var/log/ops-autodl-grabfilter.log", "a") as logfile:
            logfile.write("\nMATCH FOUND: " + torrent_name)
        # Push to deluge if not running in test mode.
        if not test_mode:
            # Make the torrent FL by sending a GET request with '&usetoken=1' appended
            h = {'Authorization': 'token ' + api_key}
            requests.get(url=torrent_url + '&usetoken=1', headers=h)
            os.system('deluge-console ' + deluge_command)
    except Exception as e:
        print('Error pushing torrent to deluge:', e)
        sys.exit()


if __name__ == '__main__':
    main()
