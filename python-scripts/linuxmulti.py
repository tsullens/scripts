#!/usr/bin/python

import sys, getopt, subprocess, os
from multiprocessing import Process, Pool
from subprocess import Popen, PIPE

def printHelp(err = False):
  if err:
    print err + "\n"
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

def main(argv):
  threads = 4
  try:
    opts, args = getopt.getopt(argv,"hi:t:",["help", "input", "threads"])
  except getopt.GetoptError:
    printHelp()
    sys.exit()
  if opts: 
    for opt, arg in opts:
      if opt in ("-h", "--help"):
        printHelp()
        sys.exit()
      if opt in ("-t", "--threads"):
        threads = int(arg)
      if opt in ("-i", "--input"):
        if len(args):
          try:
            f = open(arg, 'r')
          except:
            printHelp("File read error")
            sys.exit()
          srvs = []
          try:
            pool = Pool(processes=threads)
            results = [pool.apply_async(run, args=(srv,  args[0])).get(30) for srv in f]
          except:
            print"Failure: thread block, exiting\n"
            sys.exit()
        else:
          printHelp("No command list found")
      else: 
        printHelp()
  else:
    printHelp()

if __name__ == "__main__":
  main(sys.argv[1:])
