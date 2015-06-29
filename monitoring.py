import common
import settings
import subprocess

def start(directory):
    nodes = settings.getnodes('clients', 'osds', 'mons', 'rgws')
    collectl_dir = '%s/collectl' % directory
    perf_dir = '%s/perf' % directory
    blktrace_dir = '%s/blktrace' % directory

    # collectl
    common.pdsh(nodes, 'mkdir -p -m0755 -- %s' % collectl_dir)
    common.pdsh(nodes, 'collectl -s+mYZ -i 1:10 -F0 -f %s' % collectl_dir)

    # perf
    common.pdsh(nodes, 'mkdir -p -m0755 -- %s' % perf_dir)
    common.pdsh(nodes, 'cd %s;sudo perf record -g -f -a -F 100 -o perf.data' % perf_dir)

    # blktrace
    common.pdsh(settings.getnodes('osds'), 'mkdir -p -m0755 -- %s' % blktrace_dir)
    for device in 'bcdefghijklm':
        common.pdsh(settings.getnodes('osds'), 'cd %s;sudo blktrace -o sd%s1 -d /dev/sd%s1' % (blktrace_dir, device, device))



def stop(directory=None):
    nodes = settings.getnodes('clients', 'osds', 'mons', 'rgws')

    common.pdsh(nodes, 'pkill -SIGINT -f collectl').communicate()
    common.pdsh(nodes, 'sudo pkill -SIGINT -f perf').communicate()
    common.pdsh(settings.getnodes('osds'), 'sudo pkill -SIGINT -f blktrace').communicate()
    if directory:
        sc = settings.cluster
        common.pdsh(nodes, 'cd %s/perf;sudo chown %s.%s perf.data' % (directory, sc.get('user'), sc.get('user')))
        make_movies(directory)

def make_movies(directory):
    sc = settings.cluster
    seekwatcher = '/usr/bin/seekwatcher'
    blktrace_dir = '%s/blktrace' % directory

    for device in 'bcdefghijklm':
        common.pdsh(settings.getnodes('osds'), 'cd %s;%s -t sd%s1 -o sd%s1.mpg --movie' % (blktrace_dir,seekwatcher,device,device)).communicate()

