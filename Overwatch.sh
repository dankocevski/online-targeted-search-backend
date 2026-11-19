#!/bin/bash

source /Home/eud/dkocevsk/.bashrc

targetedSearchDirectory="/Home/eud/dkocevsk/Analysis/TargetedSearch"
queueDirectory="$targetedSearchDirectory/queue"
logDirectory="$targetedSearchDirectory/logs"
python="/Home/eud/dkocevsk/bin/miniconda3/bin/python"
parser="$targetedSearchDirectory/scripts_py3/ReportParser_v2.py"

# Loop over .msg files, including hidden ones. An empty queue yields no iterations.
shopt -s nullglob dotglob

for message in "$queueDirectory"/*.msg; do
    [[ -f "$message" ]] || continue

    # Extract the base name of the message file and construct the corresponding log file path
    message_basename=${message##*/}
    logfile="$logDirectory/${message_basename%.msg}.log"

    printf 'Processing %s (log: %s)\n' "$message" "$logfile"

    # Run the parser and handle its exit status
    if "$python" "$parser" "$message" > "$logfile" 2>&1; then
        rm -- "$message" || exit $?
    else
        status=$?
        printf 'Parser exited with status %d. Leaving %s in the queue. See %s\n' \
            "$status" "$message" "$logfile" >&2
        exit "$status"
    fi
done
