#!/usr/bin/python
#
# Alfred2 workflow for listing iCloud tabs
#

import os
import subprocess
import shutil
import tempfile
import plistlib
from datetime import datetime
from mechanize import Browser


def create_temporary_copy(path):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, 'safari_sync_plist_copy.plist')
    shutil.copy2(os.path.expanduser(path), temp_path)
    return temp_path


# make a temp copy of the plist file

temp_plist = create_temporary_copy(
    '~/Library/SyncedPreferences/com.apple.Safari.plist')

# Use plutil to convert binary plist to xml

os.system('plutil -convert xml1 %s' % temp_plist)


# Use plistlib to convert plist XML to a dictionary

info = plistlib.readPlist(temp_plist)

# Clean up (delete) temp file

os.remove(temp_plist)

# Pull out the device elements from the info dict for easier parsing later

devicetabs = []

for uid in info['values'].values():
    try:
        devicetabs.append([uid['value']['DeviceName'], uid['value']['Tabs']])
    except:
        pass

# Get local machine's host and computer names to exclude both from the list

hostname_proc = subprocess.Popen(['scutil --get LocalHostName'], stdout=subprocess.PIPE, shell=True)
(hostname_out, hostname_err) = hostname_proc.communicate()
hostname = hostname_out.strip()

computername_proc = subprocess.Popen(['scutil --get ComputerName'], stdout=subprocess.PIPE, shell=True)
(computername_out, computername_err) = computername_proc.communicate()
computername = computername_out.strip()

# Run the os 'open' command for each link found

alltabs = {}

for device in devicetabs:

    device_name = device[0]

    device_tabs = []

    for tab in device[1]:

        device_tabs.append(tab['URL'])

    alltabs[device_name] = device_tabs

outfile = os.path.expanduser('~/Desktop/alltabs_%s.md' % datetime.now().isoformat()[:19])

outtext = '''
## iCloud Tab Listing - %s

Links from all devices:

''' % datetime.now().isoformat()[:19]

for device in alltabs.keys():

    print 'processing links from: %s' % device

    outtext += '### %s\n\n' % device

    device_tabs = alltabs[device]

    for link in device_tabs:

        print '\t processing: %s' % link

        try:
            br = Browser()
            br.open(link)
            title = unicode(br.title())
        except:
            title = link
        outtext += '* [%s](%s)\n' % (title, link)

    outtext += '\n'

with open(outfile, 'w') as f:
    f.write(outtext.encode('utf8'))

os.system('open -a Marked %s' % outfile)
