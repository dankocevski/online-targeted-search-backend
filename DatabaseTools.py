#!/usr/bin/env python
import sys		
import traceback
import sqlite3
import os
import subprocess

# Hard code the database location
database_sqlite = '/Users/kocevski/Temp/triggers.db'


##########################################################################################

def update_SQLite(data, table):

	# data['analysis_status'] = 'Processing'

	try:
		# Initilize the database connection
		connection = None
		connection = sqlite3.connect(database)

		# Create the cursor object
		cursor = connection.cursor()

		# Create the insert command in parts
		insertCommand = 'INSERT INTO %s (' % table
		for key in list(data.keys()):
			insertCommand = insertCommand + ('%s, ' % key)

		# Remove the trailing comma
		insertCommand = insertCommand[0:-2]

		# Add the joining string
		insertCommand = insertCommand + ') VALUES ('

		for values in list(data.values()):
			insertCommand = insertCommand + ('\'%s\', ' % values)

		# Remove the trailing comma
		insertCommand = insertCommand[0:-2]

		# Close the command string
		insertCommand = insertCommand + ');'

		# execute the insertCommand
		print(insertCommand)
		cursor.execute(insertCommand)
		connection.commit()

		# Close the database connection
		connection.close()

		print("\nDatabase successfully updated.")

	except Exception as message:
		print(message)
		print(traceback.format_exc())
		print("Database update failed.")
		sys.exit(1)


##########################################################################################

def delete(table, trigger_id=None, comment=None, verbose=False):

	if verbose == True:
		print("\nUpdating database...")

	try:

		if trigger_id is not None:

			# Create the delete command:
			deleteCommand = 'DELETE FROM %s WHERE trigger_id = \'%s\';' % (table, trigger_id)

		elif comment is not None:

			# Create the delete command:
			deleteCommand = 'DELETE FROM %s WHERE comment like \'%s%%\';' % (table, comment)

		else:
			print("Please specify a trigger_id or comment.")
			print("Database update failed.")
			return

		if verbose == True:
			print("")
			print(deleteCommand)

		# execute the insertCommand
		remoteCommand = ['mysql', '-h', 'asddb.gsfc.nasa.gov', '-u', 'dkocevsk', '-pdkSQLworks4me', '-D', 'FAVA', '-e', '%s' % deleteCommand]

		if verbose == True:
			print("")
			print(remoteCommand)

		# Python 2
		process = subprocess.Popen(remoteCommand, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
		output, error = process.communicate()

		# # Python 3
		# result = subprocess.check_output(['mysql', '-h', 'asddb.gsfc.nasa.gov', '-u', 'dkocevsk', '-p\'dkSQLworks4me\'', '-D', 'FAVA', '-e', '%s' % insertCommand])

		if len(error) != 0:
			print("\nDatabase update failed:")
			print(error)
			sys.exit(1)
		else:
			if verbose == True:
				print("Done.")
	
	except Exception as message:
		print(message)
		print(traceback.format_exc())
		print("Database update failed.")
		sys.exit(1)

##########################################################################################

def update(data, table, verbose=False):

	if verbose == True:
		print("\nUpdating database...")

	try:

		# Create the insert command in parts
		insertCommand = 'REPLACE INTO %s (' % table
		for key in list(data.keys()):
			insertCommand = insertCommand + ('%s, ' % key)

		# Remove the trailing comma
		insertCommand = insertCommand[0:-2]

		# Add the joining string
		insertCommand = insertCommand + ') VALUES ('

		for values in list(data.values()):
			insertCommand = insertCommand + ('\'%s\', ' % values)

		# Remove the trailing comma
		insertCommand = insertCommand[0:-2]

		# Close the command string
		insertCommand = insertCommand + ');'

		if verbose == True:
			print("")
			print(insertCommand)

		# execute the insertCommand
		remoteCommand = ['mysql', '-h', 'asddb.gsfc.nasa.gov', '-u', 'dkocevsk', '-pdkSQLworks4me', '-D', 'FAVA', '-e', '%s' % insertCommand]

		if verbose == True:
			print("")
			print(remoteCommand)

		# Python 2
		process = subprocess.Popen(remoteCommand, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
		output, error = process.communicate()

		# # Python 3
		# result = subprocess.check_output(['mysql', '-h', 'asddb.gsfc.nasa.gov', '-u', 'dkocevsk', '-p\'dkSQLworks4me\'', '-D', 'FAVA', '-e', '%s' % insertCommand])

		if len(error) != 0:
			print("\nDatabase update failed:")
			print(error)
			sys.exit(1)
		else:
			if verbose == True:
				print("Done.")
	
	except Exception as message:
		print(message)
		print(traceback.format_exc())
		print("Database update failed.")
		sys.exit(1)

##########################################################################################

# def updateTrigger_SQLite(data):

	# data['analysis_status'] = 'Complete'

	# try:
	# 	# Initilize the database connection
	# 	connection = None
	# 	connection = sqlite3.connect(database)

	# 	# Create the cursor object
	# 	cursor = connection.cursor()

	# 	# Create the insert command by iterating through an array of key, value pairs
	# 	updateCommand = 'UPDATE Triggers SET '
	# 	for key in data.keys():

	# 		print key, data[key]

	# 		updateCommand = updateCommand + ('%s = \'%s\', ' % (key, data[key]))

	# 	# Remove the trailing comma
	# 	updateCommand = updateCommand[0:-2]

	# 	# Add the where clause
	# 	updateCommand = updateCommand + (" WHERE trigger_id = \'%s\';" % data['trigger_id']);

	# 	# execute the insertCommand
	# 	print updateCommand
	# 	cursor.execute(updateCommand)
	# 	connection.commit()

	# 	# Close the database connection
	# 	connection.close()

	# 	print "\nDatabase successfully updated."

	# except Exception, message:
	# 	print message
	# 	print traceback.format_exc()
	# 	print "Database update failed"


##########################################################################################

# def updateTrigger_mySQL(data):

	# data['analysis_status'] = 'Complete'

	# try:
	# 	# Initilize the database connection
	# 	connection = None
	# 	connection = sqlite3.connect(database)

	# 	# Create the cursor object
	# 	cursor = connection.cursor()

	# 	# Create the insert command by iterating through an array of key, value pairs
	# 	updateCommand = 'UPDATE Triggers SET '
	# 	for key in data.keys():

	# 		print key, data[key]

	# 		updateCommand = updateCommand + ('%s = \'%s\', ' % (key, data[key]))

	# 	# Remove the trailing comma
	# 	updateCommand = updateCommand[0:-2]

	# 	# Add the where clause
	# 	updateCommand = updateCommand + (" WHERE trigger_id = \'%s\';" % data['trigger_id']);

	# 	# execute the insertCommand
	# 	remoteCommand = ['mysql', '-h', 'asddb.gsfc.nasa.gov', '-u', 'dkocevsk', '-pdkSQLworks4me', '-D', 'FAVA', '-e', '%s' % updateCommand]

	# 	# Python 2
	# 	process = subprocess.Popen(remoteCommand, stderr=subprocess.PIPE, stdout=subprocess.PIPE )
	# 	output, error = process.communicate()

	# 	# # Python 3
	# 	# result = subprocess.check_output(['mysql', '-h', 'asddb.gsfc.nasa.gov', '-u', 'dkocevsk', '-p\'dkSQLworks4me\'', '-D', 'FAVA', '-e', '%s' % insertCommand])

	# 	if len(error) != 0:
	# 		print "\nDatabase update failed:"
	# 		print error
	# 	else:
	# 		print "\nDatabase successfully updated."
	# 		print output

	# except Exception, message:
	# 	print message
	# 	print traceback.format_exc()
	# 	print "Database update failed."


##########################################################################################


def updateAnalysisStatus_sqlite(tigger_id, percentage):

	try:
		# Initilize the database connection
		connection = None
		connection = sqlite3.connect(database)

		# Create the cursor object
		cursor = connection.cursor()

		# Create the insert command by iterating through an array of key, value pairs
		updateCommand = 'UPDATE Triggers SET analysis_status = \'%s\' WHERE trigger_id = \'%s\'' % (percentage, data['trigger_id'])

		# execute the insertCommand
		print("\n%s\n" % updateCommand)
		cursor.execute(updateCommand)
		connection.commit()

		# Close the database connection
		connection.close()

	except Exception as message:
		print(message)
		print(traceback.format_exc())
		print("Database update failed")
		sys.exit(1)

##########################################################################################

