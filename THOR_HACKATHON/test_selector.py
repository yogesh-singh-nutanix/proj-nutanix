"""
This scripts performs mapping of source files to test.
This script uses database of source files and tests which is created before
test selection using machine learning algorithm.

Copyrights (c) Nutanix Inc. 2020 - Hackathon 7.0 - THOR Project

Author: yogesh.singh@nutanix.com
"""

# Usage -> "python test_selector.py --modified_files minerva/py/minerva/utils/minerva_task_util.py"

import os
import subprocess, shlex
import re
import argparse
import random
import string
import db

CWD = os.getcwd()

class Process(object):
  """ Executes a given command in a shell

  Examples:
    cmd = "ls -l /tmp"
    process = Process(cmd)
    process.run()
    print process.rc, process.stdout, process.stderr
  """

  def __init__(self, cmd):
    """ Initiator
    Args:
      cmd (str): A command to be run in a shell
    Returns:
      Nothing
    """
    self._cmd = Process._str_to_tokens(cmd)
    self._process, self._stdout, self._stderr = None, None, None
    self._rc = 0

  @staticmethod
  def _str_to_tokens(cmd):
    """Split a line into a list of words
    Args:
      cmd (str, list): A string representing a command to be executed. (Preferred input)
                       or a list of words in a command string
    Raises:
      ValueError: When cmd is an empty string
      TypeError: If cmd is not a string or not a list of words in cmd  
    """
    if len(cmd) == 0:
      raise ValueError('Command is an empty string')
    if isinstance(cmd, list):
      return cmd
    if isinstance(cmd, str):
      return shlex.split(cmd)
    else:
      raise TypeError('cmd {0} is {1}. Should have been list or string'.format(
        cmd, type(cmd)))
     
  def run(self, blocking=True):
    """ Runs a command by default in a blocking mode
    Args:
      blocking (bool): Default value: True; run a command in a blocking mode
    """
    print self._cmd
    self._process = subprocess.Popen(self._cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)    
    if blocking:
      self.wait()

  def wait(self):
    """ Wait for a command's execution to complete.
        Populates return code(rc), stdout, stderr
    """
    self._process.wait()
    self._rc = self._process.returncode
    self._stdout, self._stderr = self._process.communicate()

  @property
  def rc(self):
    """ Getter for return code of command execution
    """
    return self._rc

  @property
  def stdout(self):
    """ Getter for stdout of command execution
    """
    if self._stdout is None or len(self._stdout) == 0:
      return None
    return self._stdout.split('\n') 

  @property
  def stderr(self):
    """ Getter for stderr of command execution
    """
    if self._stderr is None or len(self._stderr) == 0:
      return None
    return self._stderr.split('\n') 


class TestSelector(object):

  def __init__(self):
    """ Constructor """
    #self.cc_db = CC_DB
    #self.update_db()
    self.cc_db = db.read_db() 
    self._tcs, self._no_tcs = None, None

  @property  
  def tcs(self):
    """ List of test-cases to be run """
    return self._tcs

  @property
  def no_tcs(self):
    """ List of src file which do not have any TC mapped to it """
    return self._no_tcs

  def update_db(self):
    db.update_db(CC_DB) 

  def _query(self, src_file):
    """ Queries database
      This implementation is based upon a simple dictionary where each code-file
      is mapped to single TC. Going forwards it will '1 -> Many' relationship

      Args:
        src_file (str): relative path of test-case
      Returns:
        If found:
         list of path of test-case required in .lst
        else:
          Empty list
    """
    tcs_for_src_file = []
    try:
      test_case = self.cc_db[src_file]
    except KeyError:
      print "Warning: No test-case is mapped to src_file: %s" % src_file 
    else:
      tcs_for_src_file.append(test_case)
   
    print "tcs_for_sec_file %s" % set(tcs_for_src_file) 
    return list(set(tcs_for_src_file))

  def load(self, src_files):
    """ Returns a list of TCs
      Args:
        src_files (list): relative file paths
      Returns:
        a list of test-cases
    """
    tcs, no_tcs = [], []
    for src_file in src_files[0].split(","):
      _tcs = self._query(src_file)

      if not _tcs:
        no_tcs.append(src_file)
      else:
        tcs.extend(_tcs)

    self._tcs, self._no_tcs = list(set(tcs)), no_tcs

def parse_cmd_line():
  parser = argparse.ArgumentParser(description="Test Selector")
  parser.add_argument('--modified_files', type=str, required=True,
                             nargs='+', help="List of modified files") 
  return parser.parse_args()

def main():
  """ main()
  """

  args = vars(parse_cmd_line())
  test_selector = TestSelector()
  test_selector.load(args["modified_files"])
  ts =[]
  for tests in test_selector.tcs:
    ts.append(tests.encode("ascii", "ignore"))
  print 'TCs: {0}'.format(ts)

if __name__ == '__main__':
  main()

# Usage -> "python test_selector.py --modified_files minerva/py/minerva/utils/minerva_task_util.py"
