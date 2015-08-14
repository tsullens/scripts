#!/usr/bin/python
import sys, os

def print_help():
  print """Usage: diff_check arg1 arg2 """

def print_array(arr):
  for k, v in arr.iteritems():
    print k,v

# Create dictionary from filesystem path
def compile_fs(rt_dir):
  dict_fs = {}
  for rt,dirs,fls in os.walk(rt_dir):
    for f in fls:
      fd =os.open(os.path.join(rt,f), os.O_RDONLY)
      dict_fs[os.path.join(rt,f)] = int(os.fstat(fd).st_mtime)
      os.close(fd)
  return dict_fs

# Create dictionary from db file
def compile_db(db_file):
  dict_db = {}
  with open(db_file, 'r') as f:
    for line in f:
      x=line.split(';')
      dict_db[x[0].strip()]=int(x[1].strip())
    f.close()
  return dict_db

# Compare will compare the contents of arr2 AGAINST arr1
# Compare will loop through arr2, comparing each key-value pair against 
# arr1. If the key exists in both arrays, the instance in arr1 is deleted.
# If the corresponding key values are different between the arrays, we note it.
# If the key doesn't exist in arr1, we note that the file is new.
# If there are any keys remaining in arr1, we not that these have been deleted.
# If the arrays are not equal, return 1

def compare(arr1, arr2):
  change = False
  for k,v in arr2.iteritems():
    if arr1.has_key(k):
      if v != arr1[k]:
        print "Modifed: " + k + "\t" + str(arr1[k]) + " " + str(v)
        change = True
      del arr1[k]
    else:
      print "New: " + k
      change = True
  if len(arr1) > 0:
    change = True
    for k in arr1.keys():
      print "Deleted/Not Found: " + k
  return change
    

def main(args):
  if len(args) != 2:
    print_help()
    sys.exit()
  if os.path.isfile(args[1]):
    print "Reading from existing db " + args[1]
  else:
    fo = open(args[1], 'w+')
    fo.close()
