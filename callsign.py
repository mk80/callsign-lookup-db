#!/usr/bin/python3

import requests
import json
import sys
import datetime
import psycopg2

# connect to db
def connectToDatabase():
    dbConnection = None
    host = "localhost"
    port = "5432"
    database = "callsign"
    username = "callsign"
    password = "callsign"
    
    try:
        dbConnection = psycopg2.connect(database=database, 
                                        user=username, 
                                        password=password, 
                                        host=host, 
                                        port=port)
    except:
        sys.stderr.write("callsign.connectToDatabase Error: Could not connect to database")
        dbConnection = None
    return dbConnection

# write to db
def writeRecord(insertStmt):
    error = None
    conn = connectToDatabase()
    if (conn):
        try:
            cur = conn.cursor()
            cur.execute(insertStmt)
            conn.commit()
            cur.close()
            conn.close()
        except psycopg2.Error as e:
            error = e
            sys.stderr.write("callsign.writeRecord Error: %s\n" % e.diag.message_primary)
    return error

# read from db
def readRecord(queryStmt):
    returnVal = None
    conn = connectToDatabase()
    if (conn):
        try:
            cur = conn.cursor()
            returnVal = cur.execute(queryStmt)
            returnVal = cur.fetchall()
            cur.close()
            conn.close()
        except psycopg2.Error as e:
            e = sys.exc_info()[0]
            sys.stderr.write("callsign.readRecord Error: %s\n" % e.diag.message_primary)
    return returnVal

# verify table for callsign
def verifyCallsignTable(callsignQ):
	returnVal = False
	queryStmt = None

	queryStmt = """SELECT name
		FROM callsign
		WHERE name = '%s'
		""" % (callsignQ)
	if (readRecord(queryStmt)):
		returnVal = True
	return returnVal

# create callsign table and columns
def addCallsign(callsignQ):
	returnVal = False
	returnVal = verifyCallsignTable(callsignQ)

	if ( returnVal == False ):
		insertStmt = 


# store contact info into callsign table
def storeContact(name, timestamp, band, comment):

# retrieve callsign info
def retrieveContact(callsignQ):

## print json function
def outputPrint(data):
	for k, v in data.items():
		if isinstance (v, dict):
			print('{0}'.format(k))
			outputPrint(v)
		else:
			print('\t{0} : {1}'.format(k,v))


### main ###

affInput = {'Y','y','Yes','yes','YES'}
negInput = {'N','n','No','no','NO'}

callsign = 'run'

print("\n Enter an FCC callsign to lookup or 0 to exit.\n\n")

## run loop
while (callsign != '0'):
	# query for callsign
	callsign = input("Callsign : ")
	print('\n')

	# move on to exit if callsign == '0'
	if (callsign != '0'):
		# build request url for api to callook.info
		apiGet =  'https://callook.info/' + callsign + '/json'

		# GET to callook.info for callsign info
		r = requests.get(apiGet)

		output = r.json()

		# print result
		outputPrint(output)
		print('\n')

		inputContact = 'q'

		while (inputContact not in affInput and inputContact not in negInput):
			inputContact = input("Would you like to record this contact? ")
			print('\n')

			if (inputContact in affInput):
				callsignQ = output['current']['callsign']
				nameQ = output['name']
				timestampQ = datetime.datetime.now()
				print("Select band: \n")
				print(" 1. HF\n")
				print(" 2. VHF\n")
				print(" 3. UHF\n")
				bandQ = input(": ")
				if ( bandQ == '1'): bandQ = 'HF'
				elif (bandQ == '2'): bandQ = 'VHF'
				else: bandQ = 'UHF'
				print('\n')
				commentQ = input("Comments: ")
			elif (inputContact not in negInput):
				print('Please enter y/n\n')

		if (inputContact in affInput):
			print(callsignQ)
			print(nameQ)
			print(timestampQ)
			print(bandQ)
			print(commentQ)

		# test db connection and write/read
		#writeRecord("CREATE TABLE callsign.test (coltest varchar(20));")
		#writeRecord("INSERT into callsign.test (coltest) values ('It works!');")
		#dbtest = readRecord("SELECT * FROM callsign.test;")
		#print('dbtest = ' + str(dbtest))
		#writeRecord("DROP TABLE callsign.test;")
		
	else:
		# exit message
		print('exit')

exit
