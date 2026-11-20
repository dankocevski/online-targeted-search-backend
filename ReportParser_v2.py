#!/usr1/local/bin python

import sys
import email
import os
import glob
import tarfile
import DatabaseTools
import fileinput
import hashlib
import copy
import datetime


##########################################################################################

def computeMET(date, time, return_integer=True):

    year = int(date.split('-')[0])
    month = int(date.split('-')[1])
    day = int(date.split('-')[2])

    hour = int(time.split(':')[0])
    minutes = int(time.split(':')[1])
    seconds_float = float(time.split(':')[2])

    # year = int(year)
    # month = int(month)
    # day = int(day)
    # hour = int(hour)
    # minutes = int(minutes)
    # seconds_float = float(seconds)

    if seconds_float > 1:
        seconds_int = int(seconds_float)
        fractionalSeconds = seconds_float % seconds_int
    else:
        seconds_int = 0
        fractionalSeconds = seconds_float

    date1 = datetime.datetime(year,month, day, hour , minutes , seconds_int)
    metdate = datetime.datetime(2001, 1, 1,0,0,0)
    difference=date1-metdate
    MET=(difference).days*86400.+(difference).seconds

    if year>2005: MET+=1 # 2005 leap second
    if year>2008: MET+=1 # 2008 leap second
    if (month >= 7 and year == 2012) or (year > 2012): MET+=1 # 2012 leap second
    if (month >= 7 and year == 2015) or (year > 2015): MET+=1 # 2015 leap second
    if year>2016: MET+=1 # 2016 leap second

    MET = MET + fractionalSeconds

    if return_integer == True:
        MET = int(MET)

    return MET


##########################################################################################

def write_to_disk(filename, data):

    print("\nSaving file:\n%s" % filename)
    file = open(filename, 'wb')
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
    print(("\nParsing filtered events file:\n%s" % filteredEvents))
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

    print("From: %s" % sender)
    print("Date: %s" % date)
    print("subject: %s" % subject)


    # Extract the message body
    body = message.get_payload(decode=False)

    # Extract the message contents
    message_text = body[0].get_payload()

    print("")
    print(message_text)

    # Split the message apart into seperate lines
    lines = message_text.split("\n")

    # Parse the status messages
    if '[GBM pipeline alerts]' in subject:

        #### Commenting out job status updates for now ####

        # results = {}

        # # Parse the email line by line
        # for line in lines:

        #     # Get the event name
        #     if 'name = ' in line:
        #         event_id = line.split()[2]
        #         results['event_id'] = event_id

        #     # Get the job ID
        #     if 'id = ' in line:
        #         job_id = line.split()[2]
        #         results['hash'] = job_id

        #     # Get the job status
        #     if 'status = ' in line:
        #         status = line.split()[2]

        #     # Get the trigger date and time
        #     if 'event time = ' in line:
        #         date = line.split()[3]
        #         time = line.split()[4]
        #         results['trigger_date'] = date
        #         results['trigger_time'] = time 

        #         # Get the associated MET
        #         trigger_met = computeMET(date, time, return_integer=False)
        #         trigger_id = computeMET(date, time, return_integer=True)
        #         results['trigger_met'] = trigger_met
        #         results['trigger_id'] = trigger_id

        #     # Get the sample name
        #     if 'publish = ' in line:
        #         sample = line.split()[2]
        #         results['sample'] = sample

        #     # Get the time of the message
        #     if 'Time job status modified: ' in line:
        #         date = '/'.join(line.split()[4].split('-')[1:])
        #         time = line.split()[5]
        #         time_modified =  date + ' ' + time


        # # Set the job id and status in the comment field
        # results['comment'] = "Job %s - %s - %s" % (job_id, status, time_modified)

        # # Set the targeted search version
        # results['targeted_search_version'] = 'v2'

        # print(results)

        # # Update the database

        # if 'SUCCESS' in status:
        #     print("\nDeleting trigger from database...")
        #     # DatabaseTools.delete(results['trigger_id'], 'Triggers_v2', verbose=True)
        #     DatabaseTools.delete('Triggers_v2', comment="Job %s" % job_id, verbose=True)
        # else:

        #     print("\nUpdating trigger database...")
        #     DatabaseTools.update(results, 'Triggers_v2', verbose=False)

        # print("Done.\n")


        return 

    # Parse the results messages
    else:


        # Creating a dictionary to store the search results
        results = {}

        # Create a dictionary that will store the result for the detected event
        event = {}

        # Create a list that will contain all of the event dictionaries
        events = []

        # Setting default values
        results['event_id'] = ''
        results['trigger_id'] = ''
        results['trigger_met'] = ''
        results['trigger_gps'] = ''
        results['trigger_date'] = ''
        results['trigger_time'] = ''
        results['skymap'] = ''
        results['area_90'] = ''
        results['coverage'] = ''
        results['trigger_detector'] = ''
        results['trigger_distance'] = ''
        results['trigger_distance_std'] = ''
        results['trigger_pipeline'] = ''
        results['geocenter_ra'] = ''
        results['geocenter_dec'] = ''
        results['earth_radius'] = ''
        results['timescale1_soft'] = ''
        results['timescale1_norm'] = ''
        results['timescale1_hard'] = ''
        results['timescale2_soft'] = ''
        results['timescale2_norm'] = ''
        results['timescale2_hard'] = ''
        results['timescale3_soft'] = ''
        results['timescale3_norm'] = ''
        results['timescale3_hard'] = ''
        results['comment'] = ''
        results['hash'] = ''
        results['sample'] = ''
        results['inSAA'] = ''
        results['joint_event'] = ''

        # Set the targeted search version
        results['targeted_search_version'] = 'v2'

        # Set the default event number
        event_number = 0

        # Set the default state on the upper limit collection
        collect_upperlimits = False

        # Check if the spacecraft was in the SAA at T0
        if 'Occurred During SAA Transit' in subject:
            inSAA = True
            results['inSAA'] = 'True'
            print("\nSpacecraft in SAA at time of trigger")
        else:
            inSAA = False  
            results['inSAA'] = 'False'

        if 'Joint Event' in subject:
            joint_event = True
            results['joint_event'] = 'True'
            print("\nPossible Joint Event!\n")

        print("Parsing message body...")

        # Parse the email line by line
        for line in lines:

            # Get the custom event ID
            if 'Event ID:' in line:
                event_id = line.split()[2]
                results['event_id'] = event_id

            # Get the trigger met
            if 'Search MET:' in line:
                trigger_met = line.split()[2]
                results['trigger_id'] = str(int(float(trigger_met)))
                results['trigger_met'] = trigger_met

            # Get the trigger gps time
            if 'Search GPS:' in line:
                results['trigger_gps'] = line.split()[2]

            # Get the trigger date and time
            if 'Search UTC:' in line:
                datetime = line.split()[2].split()[0]
                results['trigger_date'] = datetime.split('T')[0]
                results['trigger_time'] = datetime.split('T')[1]              


            # Get the candidate information
            if 'Candidate ' in line:

                if event_number != 0:

                    # Add a copy of the event dictionary to the list of events
                    events.append(copy.copy(event))

                    # Reset the event dictionary
                    event = {}

                event_number = event_number + 1

                event['event_number'] = str(event_number)

            if 'Offset:' in line:
                event['event_offset'] = line.split()[1] 
                event['event_met'] = str(float(trigger_met) + float(event['event_offset']))

            if 'Duration:' in line:
                event['duration'] = line.split()[1] 

            if 'Spectrum:' in line:
                event['spectrum'] = line.split()[1] 

            if 'LogLR:' in line:
                event['loglr'] = line.split()[1] 

            if 'CoincLR:' in line:
                event['coinclr'] = line.split()[1] 

            if 'FAR:' in line:
                event['far'] = line.split()[1] 

            if 'Pspatial' in line:
                event['pspatial'] = line.split()[1]


            # Get the skymap information
            if 'Input skymap:' in line:
                results['skymap'] = line.split()[2] 

            if '90% Area:' in line:
                results['area_90'] = line.split()[2] 

            if '% Observed:' in line:
                results['coverage'] = line.split()[2] 

            if 'Detectors:' in line:
                try:
                    results['trigger_detector'] = line.split()[1] 
                except:
                    pass

            if 'Distance:' in line:
                results['trigger_distance'] = line.split()[1] 
                results['trigger_distance_std'] = line.split()[3] 

            if 'Creator:' in line:
                results['trigger_pipeline'] = line.split()[1] 


            # Get the occultation information
            if 'Geocenter' in line:
                results['geocenter_ra'] = line.split()[3].replace(',','')
                results['geocenter_dec'] = line.split()[4]

            if 'Earth radius' in line:
                results['earth_radius'] = line.split()[2]


            # Get the upper limit information
            if '--------------------------------------' in line:

                # Start collecting the upper limit results
                collect_upperlimits = True

            if '0.128 s' in line and collect_upperlimits is True:
                results['timescale1_soft'] = line.split()[2]
                results['timescale1_norm'] = line.split()[3]
                results['timescale1_hard'] = line.split()[4]

            if '1.024 s' in line and collect_upperlimits is True:
                results['timescale2_soft'] = line.split()[2]
                results['timescale2_norm'] = line.split()[3]
                results['timescale2_hard'] = line.split()[4]

            if '8.192 s' in line and collect_upperlimits is True:
                results['timescale3_soft'] = line.split()[2]
                results['timescale3_norm'] = line.split()[3]
                results['timescale3_hard'] = line.split()[4]

                # Stop collecting the upper limit results
                collect_upperlimits = False


            # Get any user supplied comments
            if 'Comment:' in line:
                comment = " ".join(line.split()[1:])
                results['comment'] = comment                        

            # Get the hash value
            if 'https://' in line:
                hash_id = line.split('&')[-1].split('=')[1]
                results['hash'] = hash_id

            # Get the analysis sample 
            if 'sample' in line and 'fermi.gsfc.nasa.gov' in line:
                sample = line.split('&')[1].split('=')[1]
                sample = sample.replace('3D','')
                results['sample'] = sample


        # Add the last candidate event to the list of events
        if event_number != 0:
            events.append(copy.copy(event))

        print("Done.")

        print("\nResults:")
        print(results)

        print("\nEvents:")
        print(events)


        # Update the database
        print("\nUpdating trigger database...")
        DatabaseTools.update(results, 'Triggers_v2')
        print("Done.")


        # Add the found events
        print("\nUpdating event database...")
        for event in events:

            # Add the sample and hash_id
            event['sample'] = sample
            event['hash'] = hash_id

            print("Adding event %s" % event['event_number'])

            # Add the event to the database
            DatabaseTools.update(event, 'Events_v2', verbose=False)

        print("Done.")


        # Set the directory that will be used to stage the tar file and plot extraction
        staging_directory = '/Home/eud/dkocevsk/Analysis/TargetedSearch/attachements'

        # Create a unique path name for the results. This allows the directory paths to still be human readable (and sortable), but still unique
        uniquePath = str(int(float(trigger_met))) + '_' + hash_id

        # Generate the directory name to store the results
        results_directory = os.path.join('/htdocs/glast/ssc/data/access/gbm/targeted_search/results/', sample)
        results_directory = os.path.join(results_directory, uniquePath)

        # Create the results directory if it doesn't already exist
        if not os.path.exists(results_directory):
            print("\nCreating directory:")
            print(results_directory)
            os.makedirs(results_directory)
            pass

        # Manage the file attachments
        attachments = body[1:]

        print("\nFound %s attachments" % len(attachments))


        # Loop through each of the file attachments
        for attachment in attachments:

            filename = attachment.get_filename()
            print(filename)

            # Extract the position plot
            if '_FermiPosition.png' in filename:
                position_plot_filename = filename
                position_plot = attachment.get_payload()[1]
            else:
                position_plot = None

            # Extract the tarball
            if '_plots.tar.gz' in filename:
                tarball = attachment
            else:
                tarball = None


        # Generate the full tarfile path 
        tarball_filename = os.path.join(results_directory, tarball.get_filename())

        # Write the filtered output and tarfile to disk
        write_to_disk(tarball_filename, tarball.get_payload(decode=True))

        # Extract all of the files from the tar file
        print("\nExtracting tar file contents...")
        # print tarball_filename
        tarball_handle = tarfile.open(tarball_filename)
        tarball_handle.extractall(path=results_directory)
        tarball_handle.close()
        print("Done.")

        # Delete the tarfile
        print("\nCleaning up...")
        os.remove(tarball_filename)
        print("Done.")

        # Change the permissions of the extracted files
        print("\nChanging file permissions...")
        os.chmod(results_directory, 0o755)
        files = glob.glob(results_directory + '/*')
        for file in files:
            os.chmod(file, 0o755) 
        print("Done.")

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



