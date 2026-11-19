#!/usr/bin/env python

import sys
import email
import os
import glob
import tarfile
import DatabaseTools
import fileinput
import hashlib

##########################################################################################

def write_to_disk(filename, data):

    print "\nSaving file:\n%s" % filename
    file = open(filename, 'w')
    file.write(data)
    file.close()

    return


###########################################################################################

def extractEvents(filteredEvents, trigger_met, sample, hash_id, trigger_id=None, llr_min=1):

    # Create a dictionary that will house all of the search results for a single event
    event = {}

    # Create an array that will house all of the event dictionaries
    events = []

    # Set a default event counter to 1
    event_number = 0

    # Parse the filtered output fule
    print("\nParsing filtered events file:\n%s" % filteredEvents)
    for line in fileinput.input([filteredEvents]):

        # Get the output keys and assign empty lists to later store values
        if 'tcent' in line:

            # Replace plus sign with a string
            line = line.replace('+', '_plus')
            line = line.replace('dec', 'decl') 

            # Get the result keys for later use
            keys = line.split()
            for key in keys:
                event[key] = ''

        # Get the output values and store them in the associated key
        if 'tcent' not in line:
            if len(line.split()) == 23:
                lineContents = line.split()
                for key, value in zip(keys, lineContents):
                    event[key] = value

                # Determine 
                if float(event['logLR']) > llr_min or float(event['coincLR']) > llr_min:
                    event['trigger_met'] = trigger_met
                    event_number = event_number + 1
                    event['event_number'] = 'Event' + str(event_number)
                    event['sample'] = sample
                    event['hash'] = hash_id

                    # Use the trigger MET as the default id if no id is supplied
                    if trigger_id is None:
                        event['trigger_id'] = str(int(float(trigger_met)))
                    else:
                        event['trigger_id'] = trigger_id

                    # Store a copy of the event dictionary
                    events.append(event.copy()) 

    return events


##########################################################################################

def parse(filename=None):

    # Read standard in
    if filename == None:
        raw_message = sys.stdin.read()
    else:
        with open(filename, 'r') as myfile:
            raw_message=myfile.read()

    # Parse the email string
    message = email.message_from_string(raw_message)

    # Extract message contents
    sender = message['from']
    subject = message['subject'].replace('\n','')
    date = message['date']

    print "From: %s" % sender
    print "Date: %s" % date
    print "subject: %s" % subject

    # Check if the spacecraft was in the SAA at T0
    if 'Occurred During SAA Transit' in subject:
        inSAA = True
        print "\nSpacecraft in SAA at time of trigger"
    else:
        inSAA = False

    # Extract the message body
    body = message.get_payload(decode=False)

    # Extract the message contents
    message_text = body[0].get_payload()

    print ""
    print message_text

    # Only extract the message attachments if the spacecraft wasn't in the SAA at T0
    if inSAA is False:

        # Extract the attachements
        attachments = body[1:]

        print "Found %s attachments:" % len(attachments)
        for attachment in attachments:
            print attachment.get_filename()

            if 'filtered_output.txt' in attachment.get_filename():
                filtered_output = attachment
            if '_plots.tar.gz' in attachment.get_filename():
                tarfileData = attachment


        if 'filtered_output' not in locals():
            filtered_output = None
        if 'tarfileData' not in locals():
            tarfileData = None
        if 'position_plot' not in locals():
            position_plot = None

    if inSAA is True:

        # Extract the attachements
        attachments = body[1:]

        print "Found %s attachments:" % len(attachments)

        attachment = attachments[0]

        print attachment.get_payload()[1].get_filename()

        if '_FermiPosition.png' in attachment.get_payload()[1].get_filename():
            position_plot_filename = attachment.get_payload()[1].get_filename()
            position_plot = attachment.get_payload()[1]
        else:
            position_plot = None

    # Split the message apart into seperate lines
    lines = message_text.split("\n")

    # Creating a dictionary to store the results
    results = {}

    # Setting default values
    results['analysis_status'] = 'Complete'
    results['nside'] = ''
    results['area_50'] = ''
    results['area_90'] = ''
    results['time_elapsed'] = ''
    results['number_of_windows'] = ''
    results['coverage'] = ''
    results['trigger_detector'] = ''
    results['trigger_distance'] = ''
    results['trigger_distance_std'] = ''
    results['trigger_pipeline'] = ''
    results['graceDB_id'] = ''
    results['sample'] = ''

    if inSAA is True:
        results['comment'] = "GBM in SAA"
    else:
        results['comment'] = ''

    print "\nParsing message body..."

    for line in lines:

        # Get the trigger met
        if 'GW MET:' in line:
            trigger_met = line.split('\t')[1]
            results['trigger_id'] = str(int(float(trigger_met)))
            results['trigger_met'] = trigger_met

        # Get the trigger gps time
        if 'GW GPS:' in line:
            results['trigger_gps'] = line.split('\t')[1]

        # Get the trigger date and time
        if 'GW UTC:' in line:
            try:
                results['trigger_date'] = line.split('\t')[1].split()[0]
                results['trigger_time'] = line.split('\t')[1].split()[1]
            except:
                datetime = line.split('\t')[1].split()[0]
                results['trigger_date'] = datetime.split('T')[0]
                results['trigger_time'] = datetime.split('T')[1]              

        # Get the analysis sample 
        if 'sample' in line:
            sample = line.split('&')[1].split('=')[1]
            sample = sample.replace('3D','')
            results['sample'] = sample

        if 'GraceBD ID' in line:
            graceDB_id = line.split()[-1]
            results['graceDB_id'] = graceDB_id

        if 'LIGO Detectors Online:' in line:
            trigger_detector = line.split()[-1]
            trigger_detector = trigger_detector.replace(',', ', ')
            results['trigger_detector'] = trigger_detector

        if 'LIGO Distance Mean:' in line:
            trigger_distance = line.split()[-1]  
            results['trigger_distance'] = trigger_distance

        if 'LIGO Distance Std:' in line:
            trigger_distance_std = line.split()[-1]
            results['trigger_distance_std'] = trigger_distance_std

        if 'LIGO Skymap Area:' in line:
            area_90 = line.split()[-1]  
            results['area_90'] = area_90

        if 'LIGO Skymap Observed:' in line:
            coverage = line.split()[-1]  
            results['coverage'] = coverage

        if 'LIGO Skymap Origin:' in line:
            trigger_pipeline = line.split()[-1]
            results['trigger_pipeline'] = trigger_pipeline

        if 'FAR:' in line:
            far = line.split()[1]  
            far_90cl = line.split()[-1]  

        if 'FAP:' in line:
            fap = line.split()[1]  

        if 'Comment:' in line:
            comment = " ".join(line.split()[1:])
            results['comment'] = comment                        

        if 'https://' in line:
            hash_id = line.split('&')[-1].split('=')[1]
            results['hash'] = hash_id

    # Put together a string to generate a unique hash. This allows multiple runs of the same triggerID to be stored
    # string_to_hash = results['trigger_id'] + '_' + results['sample'] + '_' + results['comment']

    # # Create the 16 bit MD5 hash
    # m = hashlib.md5()
    # m.update(string_to_hash)
    # hash_id = m.hexdigest()[:16]

    # Add the unique hash to the dictionary so the webpage knows where to find the results
    # results['hash'] = hash_id

    print "Done."

    # Update the database
    print "\nUpdating trigger database..."
    DatabaseTools.update_mySQL(results, 'Triggers')
    print "Done."

    # Set the directory that will be used to stage the tar file and plot extraction
    staging_directory = '/Home/eud/dkocevsk/Analysis/TargetedSearch/attachements'

    # Get the met from the subject line
    met = subject.split()[4].replace(':','')

    # Create a unique path name for the results. This allows the directory paths to still be human readable (and sortable), but still unique
    uniquePath = met + '_' + hash_id

    # Generate the directory name to store the results
    results_directory = os.path.join('/htdocs/glast/ssc/data/access/gbm/targeted_search/results/', sample)
    results_directory = os.path.join(results_directory, uniquePath)

    # Create the results directory if it doesn't already exist
    if not os.path.exists(results_directory):
        print "\nCreating directory:"
        print results_directory
        os.makedirs(results_directory)
        pass

    # Manage the file attachments
    if inSAA == False:

        # Generate the filenames for the filtered output and tarfile
        filtered_output_filename = os.path.join(results_directory, filtered_output.get_filename())
        tarfile_filename = os.path.join(results_directory, tarfileData.get_filename())

        # Write the filtered output and tarfile to disk
        write_to_disk(filtered_output_filename, filtered_output.get_payload(decode=True))
        write_to_disk(tarfile_filename, tarfileData.get_payload(decode=True))

        # Extract all of the files from the tar file
        print "\nExtracting tar file:"
        print tarfile_filename
        tarfile_handle = tarfile.open(tarfile_filename)
        tarfile_handle.extractall(path=results_directory)
        tarfile_handle.close()
        print "Done."

        # Change the permissions of the extracted files
        print "\nChanging file permissions..."
        os.chmod(results_directory, 0o755)
        files = glob.glob(results_directory + '/*')
        for file in files:
            os.chmod(file, 0o755) 
        print "Done."

        # Read the filtered output file
        events = extractEvents(filtered_output_filename, trigger_met, sample, hash_id)

        # Add the FAP and FAR results to the first event
        events[0]['far'] = far
        events[0]['far_90cl'] = far_90cl
        events[0]['fap'] = fap

        # Define a maximum number of events that we want to store per trigger
        maxEvents = 4

        # Determine how many detections were found (if any)
        detection_logLR = 0
        detection_coincLR = 0

        for event in events:
            if float(event['logLR']) > 10.0:
                detection_logLR = detection_logLR + 1
            if float(event['coincLR']) > 10.0:
                detection_coincLR = detection_coincLR + 1

        numberOfDetections = max(detection_logLR, detection_coincLR)
        print("\nFound %s events with logLR > 10." % numberOfDetections) 

        # Loop through each event and create the associated plots
        index = 0
        for event in events:

            if index == (maxEvents):
                print("Max events reached. Skipping remaining events.")
                break

            # Update the database, but only if it's a detection
            # if event['logLR'] > 10.0 or event['coincLR'] > 10.0:
            #     print "\nAdding %s..." % event['event_number']
            #     DatabaseTools.update_mySQL(event, 'Events', verbose=False)
            #     print "Done."

            # Add up to 4 events regardless of the logLR
            print "\nAdding %s..." % event['event_number']
            DatabaseTools.update_mySQL(event, 'Events', verbose=False)
            print "Done."

            index = index + 1

        # Delete the tarfile
        print "\nCleaning up..."
        os.remove(tarfile_filename)
        print "Done.\n"

    if inSAA is True:

        # Generate the filenames for the spacecraft position plot
        if position_plot is not None:
            position_plot_filename = os.path.join(results_directory, position_plot_filename)

            # Write the position plot to disk
            write_to_disk(position_plot_filename, position_plot.get_payload(decode=True))

            # Change the permissions of the extracted files
            print "\nChanging file permissions..."
            os.chmod(results_directory, 0o755)
            files = glob.glob(results_directory + '/*')
            for file in files:
                os.chmod(file, 0o755) 
            print "Done."


    return


##########################################################################################

if __name__=='__main__':

    # Check to see if any arguments were passed
    if(len(sys.argv) > 1):

        # Extract the first arugument
        filename = sys.argv[1]
                        
        parse(filename=filename)

    else:

        parse()



