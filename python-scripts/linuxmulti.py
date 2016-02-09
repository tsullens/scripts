#!/usr/bin/python

import sys, getopt, subprocess, os
from multiprocessing import Process, Pool
from subprocess import Popen, PIPE

pwd = ""

def printHelp(err = False):
  if err:
    print err + "\n"
  print "\tUsage: -h | --help -> print help\n\t-t | --threads {num_threads} -> where {num_threads is the upper limit of parallel processes\n\t-s | --sudo -> use sudo to execute each command\n\t-i | --input {inputfile} -> where {inputfile} is list of servers\n\t\"command[;command]\"\n\t Ex. ./linuxmulti.py -t 8 -i srv-list \"uptime;date\""


def run(srv, commands):
  print "HOST: " + srv
#  print commands
#  print "ID: %d" % os.getpid()
  ssh = subprocess.Popen(["sshpass", "-p", pwd, "ssh", "-q", "tyler.sullens@%s" % srv, "%s" % commands], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  result,err = ssh.communicate()
  if result:
    print result
  if err:
    print err
  print ""


def sudo_format(comms):
  newstr = ""
  for comm in comms.split(";"):
    newstr += "echo \'" + pwd + "\' | sudo -S " + comm.strip() + ";"
  return newstr

def main(argv):
  threads = 4
  try:
    opts, args = getopt.getopt(argv,"hsi:t:",["help", "sudo", "input", "threads"])
  except getopt.GetoptError:
    printHelp()
    sys.exit()
  comms = args[0]
  if opts:
    for opt, arg in opts:
      if opt in ("-h", "--help"):
        printHelp()
        sys.exit()
      if opt in ("-t", "--threads"):
        threads = int(arg)
      if opt in ("-s", "--sudo"):
        comms = sudo_format(comms)
        print comms
      if opt in ("-i", "--input"):
        if len(args):
