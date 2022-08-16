```
ops-autodl-grabfilter - v1.0
A Python script for filtering torrents grabbed by autodl-irssi on OPS.

This script is used in conjunction with a program such as autodl-irssi, allowing filtering to be done based on
torrent / artist attributes. Argparse is not used as this script should ONLY be called from an automation tool.

Call from autodl with:
    upload-command = /usr/bin/python3
    upload-type = exec
    upload-args = "/scripts/ops-grabfilter.py" "ops-api-key" "1500" "$(TorrentUrl)" "delge-url:port" "deluge-user" "deluge-pass" "$(TorrentPathName)" "$(TorrentName)"

ARGUMENTS:
    1: API Auth Key
    2: Required snatches from all involved artists combined
    3: Torrent URL
    4: Deluge url:port
    5: Deluge username
    6: Deluge password
    7: Torrent path
    8: Torrent name
    9: Test mode (Set to 1, default is 0)
```