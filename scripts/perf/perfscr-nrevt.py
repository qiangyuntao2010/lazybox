# perf script event handlers, generated by perf script -g python
# Licensed under the terms of the GNU GPL License version 2

# The common_* event handler fields are the most useful fields common to
# all events.  They don't necessarily correspond to the 'common_*' fields
# in the format files.  Those fields not available as handler params can
# be retrieved using Python functions of the form common_*(context).
# See the perf-trace-python Documentation for the list of available functions.

import os
import sys

sys.path.append(os.environ['PERF_EXEC_PATH'] + \
	'/scripts/python/Perf-Trace-Util/lib/Perf/Trace')

from perf_trace_context import *
from Core import *


def trace_begin():
	print "in trace_begin"

def pr_evcnts_in_time():
    title = "time"
    evnames = sorted(ev_per_time.keys())
    for n in evnames:
        title += ", %s" % n
    print title

    secs = sorted(ev_per_time[n])
    for s in secs:
        line = "%10s" % s
        for n in evnames:
            count = 0
            if s in ev_per_time[n]:
                count = ev_per_time[n][s]
            line += ",%10s" % count
        print line

def trace_end():
    pr_evcnts_in_time()
    return
    for ev in sorted(ev_per_time.keys()):
        print "event ", ev, "\n"
        evcnts = ev_per_time[ev]
        for t in sorted(evcnts.keys()):
            print t, ": ", evcnts[t]
        print "\n\n"
    print "in trace_end"
    for ev in nr_events.keys():
        print "event ", ev, ": ", nr_events[ev]

nr_events = {}
ev_per_time = autodict()

def process_event(pd):
    name = pd["ev_name"]
    count = pd["sample"]["period"]
    try:
        nr_events[name] += count
    except KeyError:
        nr_events[name] = count

    # sampled time in second
    t = pd["sample"]["time"] / (1000*1000*1000)
    try:
        ev_per_time[name][t] += count
    except TypeError:
        ev_per_time[name][t] = count

def trace_unhandled(event_name, context, event_fields_dict):
		print ' '.join(['%s=%s'%(k,str(v))for k,v in sorted(event_fields_dict.items())])

def print_header(event_name, cpu, secs, nsecs, pid, comm):
	print "%-20s %5u %05u.%09u %8u %-20s " % \
	(event_name, cpu, secs, nsecs, pid, comm),
