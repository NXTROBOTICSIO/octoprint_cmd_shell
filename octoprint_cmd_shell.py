#!/usr/bin/env python

import cmd, requests, json, ConfigParser

#--------------------------------------------------------- APPLICATION VARIABLE SETUP BEGIN
# instantiate ini file parser and read setting(s) from file
Config = ConfigParser.ConfigParser()
Config.read('octoprint.ini')
# get key:value pair from named section in ini file
try:
  apiKey     = Config.get('ApiKey','keyString')
  srvProto   = Config.get('Server','srvProto')
  octoServer = Config.get('Server','octoServer')
  apiFileMsg = Config.get('Server','apiFileMsg')
  apiVerMsg  = Config.get('Server','apiVerMsg')
  apiStatMsg = Config.get('Server','apiStatMsg')
  apiJobMsg  = Config.get('Server','apiJobMsg')
except:
  print("\nError: octoprint.ini does not exist in the local directory or the file format is incorrect!\n")
  exit(1)

# the below variable will be used in the near future (feel free to remove if it bothers you). It's a good
# reminder and placeholder. 
apiHeaders = {
    'X-Api-Key': apiKey
}
#--------------------------------------------------------- APPLICATION VARIABLES SETUP END

respV = ""
respS = ""

class octoShell(cmd.Cmd):
    intro = '\nWelcome to the Octoprint shell.   Type help or ? to list commands.\n'
    prompt = '(octo-shell) '

    def fileList(self):
	"""Returns the file listing of file stored locally (not on the SD card)"""
	resp = requests.get(srvProto+octoServer+apiFileMsg+'?apikey='+apiKey)
	if resp.status_code != 200: # This means something went wrong.
  		raise ApiError('GET'+apiMsg+' {}'.format(resp.status_code))
	data = resp.json()
	# create a file list so we can easily sort the file names
	fileList = []
	for each in data['files']:
  		fileList.append(each['name'])
	# sort the list
	fileList.sort()
	# output the list to the screen (this is basic with no pagination or extras whatsoever)
	print
	for files in fileList:
  		print files
	print

    def getRespVersionInfo(self): #version info
	"""Returns the Octoprint Server and API versions"""
	respV = requests.get(srvProto+octoServer+apiVerMsg+'?apikey='+apiKey)
	if respV.status_code != 200: # This means something went wrong.
		print('\Error retrieiving API and server version info. Code: {}\n'.format(respV.status_code))
		exit(1)
        return(respV)

    def getRespStatusInfo(self): #status info
	"""Returns the current status of the printer"""
	respS = requests.get(srvProto+octoServer+apiStatMsg+'?apikey='+apiKey)
	if respS.status_code != 200: # This means something went wrong.
		print('\nError retrieving printer informtion. Confirm that OctoPrint has an active connection to the printer. Code: {}\n'.format(respS.status_code))
		exit(1)
	return(respS)

    def getRespJobInfo(self): #job info
	"""Returns information on the currently active print job"""
	respJ = requests.get(srvProto+octoServer+apiJobMsg+'?apikey='+apiKey)
	if respJ.status_code != 200: # This means something went wrong.
		print('\nError retrieving printer information. Confirm that OctoPrint has an active connection to the printer. Code: {}\n'.format(respJ.status_code))
    		exit(1)
	return(respJ)

    # ----- basic shell commands -----
    def do_files(self, arg):
        'Show sorted list of files'
        self.fileList()

    def do_octoversion(self, arg):
        'Get Octoprint API & Server versions'
        respV = self.getRespVersionInfo()
        print('\nAPI version   : {}'.format(respV.json()["api"]))
 	print('Server version: {}\n'.format(respV.json()["server"]))

    def do_status(self, arg):
        'Get current printer status'
        respS = self.getRespStatusInfo()
	print('\nExtruder temp : {}'.format(respS.json()['temperature']['tool0']['actual']))
	print('Bed temp      : {}'.format(respS.json()['temperature']['bed']['actual']))
	print('Current state : {}'.format(respS.json()['state']['text']))
	print('Operational   : {}'.format(respS.json()['state']['flags']['operational']))
	print('Printing      : {}'.format(respS.json()['state']['flags']['printing']))
	print('Ready         : {}'.format(respS.json()['state']['flags']['ready']))
	print('Error         : {}\n'.format(respS.json()['state']['flags']['error']))
	
    def do_jobinfo(self,arg):
        'Get information on the current job'
	respJ = self.getRespJobInfo()

	 # Get hh:mm:ss from returned string (which is in total seconds remaining)
	if respJ.json()["progress"]["printTimeLeft"] != None:
		seconds = int(respJ.json()["progress"]["printTimeLeft"])
		m, s = divmod(seconds, 60)
		h, m = divmod(m, 60)
		timeRemaining = "%d:%02d:%02d" % (h, m, s)
	else:
		timeRemaining = 0

  	# Get hh:mm:ss from returned string (which is in total seconds elapsed)
	if respJ.json()["progress"]["printTime"] != None:
		seconds = int(respJ.json()["progress"]["printTime"])
		m, s = divmod(seconds, 60)
		h, m = divmod(m, 60)
		timeElapsed = "%d:%02d:%02d" % (h, m, s)
	else:
		timeElapsed = 0

	# get current print job file name
	if respJ.json()["job"]["file"]["name"] != None:
		jobFileName = respJ.json()["job"]["file"]["name"]
	else:
		jobFileName = " --- "
	# get current print job filament length
	if respJ.json()["job"]["filament"] != None:
		jobFilLen = float(respJ.json()["job"]["filament"]["tool0"]["length"])/1000
	else:
		jobFilLen = 0
	
	print('\nPrinting file   : '+jobFileName)
	print('Filament length : %0.2f' % jobFilLen) + "m"
	print('Elapsed time    : '+str(timeElapsed))
	print('Remaining time  : '+str(timeRemaining))
        print

    def do_bye(self,arg):
        'Close the shell and exit'
        print('\nThank you for using the Octoprint shell\n')
        return True

    def do_quit(self,arg):
        'Close the shell and exit'
        print('\nThank you for using the Octoprint shell\n')
        return True

if __name__ == '__main__':
    octoShell().cmdloop()
