#!/usr/bin/python
import sys, getopt, subprocess, os
from multiprocessing import Process, Pool
from subprocess import Popen, PIPE
from itertools import repeat

def printHelp():
  print """Usage:
           -h | --help -> print help
           -t | --threads {num_threads} -> where {num_threads is the upper limit of parallel processes
           -i | --input {inputfile} -> where {inputfile} is list of servers
           \"command[;command]\""""


def run(srv, commands):
  print "HOST: %s" % srv
  print commands
  print "ID: %d" % os.getpid()
  ssh = subprocess.Popen(["ssh", "-q", srv, "%s" % commands], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  result,err = ssh.communicate()
  if result:
    print result
  if err:
    print err
  print ""
#  with ssh.stdin:
#    for cmd in commands[0].split(';'):
#      ssh.stdin.write(cmd.trim())
#      ssh.stdin.flush()
#  result = ssh.stdout.readlines()
 #  if result == []:
 #   error = ssh.stderr.readlines()
 #   print >>sys.stderr, "error: %s" % error
 # else:
 #   print "done"
  #ssh.kill()

def main(argv):
  threads = 4
  try:
    opts, args = getopt.getopt(argv,"hi:t:",["help", "input", "threads"])
  except getopt.GetoptError:
    printHelp()
    sys.exit()
  for opt, arg in opts:
    if opt in ("-t", "--threads"):
      threads = arg
    if opt in ("-h", "--help"):
      printHelp()
      sys.exit()
    elif opt in ("-i", "--input"):
      f = open(arg, 'r')
      srvs = []
      pool = Pool(processes=threads)
      results= [pool.apply(run, args=(srv,  args[0])) for srv in f]
      #for srv in f:
      #  p = Process(target=run, args=(srv.strip(), args[0]))
      #  p.start()
      #  p.join()
    else: 
      printHelp()
#      srvs.append(line)
#   pool = Pool(4)
#   pool.map(run, zip(srvs, repeat(args[2]))

if __name__ == "__main__":
  main(sys.argv[1:])

