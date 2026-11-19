#!/bin/csh -f
source /Home/eud/dkocevsk/.cshrc

# Define the queue directory
set targetedSearchDirectory  = /Home/eud/dkocevsk/Analysis/TargetedSearch
set queueDirectory = $targetedSearchDirectory/queue
set queueDirectoryNX = $targetedSearchDirectory/queueNX
set logDirectory = $targetedSearchDirectory/logs

# Define a defuault number of files in the queue directory
set count = 0

# Count the number of files in the queue directory
set count=`ls -a $queueDirectory | wc | awk '{print $1}'`

# Don't do anything if the queue directory is empty
if ( "${count}" > 2 ) then

	# Get the filenames in the queue
	set messages = `find $queueDirectory -maxdepth 1 -name '*.msg'`

	# Loop through each file and launch the analysis
	foreach message ($messages)

		# Generate the logfile name
		set message_basename = `basename $message`	
		set logfile = `echo $message_basename | sed 's/.msg/.log/g'`  

		# Execute the script
		echo "/usr/bin/python /Home/eud/dkocevsk/Analysis/TargetedSearch/scripts/ReportParser_v2.py $message >& $logDirectory/$logfile"
		env /usr/bin/python /Home/eud/dkocevsk/Analysis/TargetedSearch/scripts/ReportParser_v2.py $message >& $logDirectory/$logfile

		# Remove the message from the queue
		rm $message
		# mv $message $queueDirectoryNX

	end

endif
