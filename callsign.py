#!/usr/bin/python3

# program to lookup FCC callsigns from https://callook.info
# and also store contact info into database to keep track
# of each contact made with that callsign

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
        cur = conn.cursor()
        try:
            returnVal = cur.execute(queryStmt)
		# except for undefined table
        except psycopg2.Error as err:
            if err:
                returnVal = False
                print("No contact stored with this callsign.\n")
                return False
        returnVal = cur.fetchall()
        cur.close()
        conn.close()
    return returnVal

# verify table for callsign
def verifyCallsignTable(callsignQ):
	returnVal = False
	queryStmt = None
	queryStmt = """SELECT * FROM %s """ % ("callsign." + callsignQ)
	if (readRecord(queryStmt) != False):
		returnVal = True
	return returnVal

# create callsign table and columns
def addCallsign(callsignQ):
	returnVal = False
	tableName = None
	createStmt = None
	# check for table
	returnVal = verifyCallsignTable(callsignQ)
	# create table for callsign if it doesn't exist
	if ( returnVal == False ):
		tableName = "callsign." + callsignQ
		createStmt = """CREATE TABLE %s 
						(colname varchar(50), coltimestamp varchar(30), colband varchar(3), colcomment varchar(255)) """ % (tableName)
		# maybe switch to this below with no 'col' on the names of columns
		#createStmt = "CREATE TABLE " + tableName + " (name varchar(50), timestamp varchar(30), band varchar(3), comment varchar(255));"
		returnVal = writeRecord(createStmt)
	return returnVal


# store contact info into callsign table
def storeContact(callsignQ, nameQ, timestampQ, bandQ, commentQ):
	returnVal = False
	tableName = None
	insertStmt = None
	tableName = "callsign." + callsignQ
	insertStmt = """INSERT into %s (colname, coltimestamp, colband, colcomment)
		VALUES ('%s', '%s', '%s', '%s')
		""" % (tableName, nameQ, timestampQ, bandQ, commentQ)
	returnVal = writeRecord(insertStmt)
	return returnVal

# retrieve callsign info
def retrieveContact(callsignQ):
	returnVal = False
	queryStmt = None
	# check for table
	returnVal = verifyCallsignTable(callsignQ)
	if ( returnVal == True ):
		queryStmt = """SELECT * FROM %s """ % ("callsign." + callsignQ)
		returnVal = readRecord(queryStmt)
		return returnVal
	else:
		return returnVal

# drop table for callsign
def removeContact(callsignQ):
	returnVal = False
	tableName = None
	dropStmt = None
	# check for table
	returnVal = verifyCallsignTable(callsignQ)
	if ( returnVal != False):
		tableName = "callsign." + callsignQ
		dropStmt = """DROP TABLE %s """ % (tableName)
		returnVal = writeRecord(dropStmt)
		return returnVal
	else:
		return returnVal

# print json function
def outputPrint(data):
	for k, v in data.items():
		if isinstance (v, dict):
			print('{0}'.format(k))
			outputPrint(v)
		else:
			print('\t{0} : {1}'.format(k,v))


### main ###

if ( __name__ == "__main__"):

	affInput = {'Y','y','Yes','yes','YES'}
	negInput = {'N','n','No','no','NO'}

	callsign = 'run'
	returnVal = None
	doublecheck = ''

	print("\n Enter an FCC callsign to lookup\n or 'remove' to remove contact from db\n or 0 to exit\n\n")

	## run loop
	while (callsign != '0'):
		# query for callsign
		callsign = input("Callsign : ")
		print('\n')

		# move on to exit if callsign == '0'
		if (callsign != '0' and callsign != 'test' and callsign != 'remove'):
			# build request url for api to callook.info
			apiGet =  'https://callook.info/' + callsign + '/json'

			# GET to callook.info for callsign info
			r = requests.get(apiGet)

			output = r.json()

			# print result
			outputPrint(output)
			print('\n')
			
			callsignQ = output['current']['callsign']
			returnVal = retrieveContact(callsignQ)

			# display previously stored contact info
			if ( returnVal != False ):
				print("Past contact with " + callsignQ + ":\n")
				print("{:30}{:28}{:10}{:100}".format("Name", "Date/Time", "Band", "Comment"))
				for i in range(len(returnVal)):
					print("{:30}{:28}{:10}{:100}".format(returnVal[i][0], returnVal[i][1], returnVal[i][2], returnVal[i][3]))
				print('\n')

			inputContact = 'q'

			# store new contact info
			while (inputContact not in affInput and inputContact not in negInput):
				inputContact = input("Would you like to record this new contact? ")
				print('\n')

				if (inputContact in affInput):
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
					returnVal = None
					returnVal = addCallsign(callsignQ)
					if ( returnVal == True or returnVal == None):
						returnVal = storeContact(callsignQ, nameQ, timestampQ, bandQ, commentQ)
						if ( returnVal == None ):
							print("Contact successfully added!\n")

		# remove contact info from db
		elif (callsign == 'remove'):
			callsign = input("Callsign to remove: ")
			doublecheck = 'q'
			while (doublecheck not in affInput and doublecheck not in negInput):
				doublecheck = input("\nAre you sure you want to remove " + callsign + " and all of it's entries? ")
				print('\n')
				if (doublecheck in affInput):
					returnVal = removeContact(callsign)
					if (returnVal == None):
						print("Contact removed successfully from database!\n")
				elif (doublecheck not in negInput):
					print('Please enter y/n\n')

		# unit test for db interaction
		elif (callsign == 'test'):
			# unit test db connection and write/read
			writeRecord("CREATE TABLE callsign.test (coltest varchar(20));")
			writeRecord("INSERT into callsign.test (coltest) values ('It works!');")
			dbtest = readRecord("SELECT * FROM callsign.test;")
			print('dbtest = ' + str(dbtest))
			contTest = input("Continue: y/n")
			writeRecord("DROP TABLE callsign.test;")

		else:
			# exit message
			print('exit')

exit