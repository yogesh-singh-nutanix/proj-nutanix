"""
This scripts performs all operations to prepare dataset and
decision tree machine learning core module functionality

Copyrights (c) Nutanix Inc. 2020 - Hackathon 7.0 - THOR Project

Author: yogesh.singh@nutanix.com
"""

# Usage -> "python ml.py --changeid 374556 --dataset source_test_dataset"

# Predictive test selection data processing

import numpy as np
import matplotlib as plt
import pandas as pd
import subprocess
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
import argparse
import json

DOC_PATH="/Users/yogesh.singh/Documents"
TOOLBOX_SRC="/Users/yogesh.singh/source/toolbox"
SOURCE_HASH_FILE="%s/SourceFiles.csv" % DOC_PATH
TEST_HASH_FILE="%s/TestNames.csv" % DOC_PATH
TOOLBOX_PATH="%s/toolbox/jenkins/bin" % TOOLBOX_SRC
JIRA_STORE="%s/jira_test.csv" % DOC_PATH
ML_DATASET_PATH="%s/ml_dataset.csv" % DOC_PATH
ML_STR_DATASET_PATH="%s/ml_str_dataset.csv" % DOC_PATH

def get_source_hash():
  """This method maps source file string to a integer hash and stores it
     in a dictionary and returns the dictionary.

     Returns:
      shash (dict) : Dictionary containing source file to integer hash mapping.
  """
  sds = pd.read_csv(SOURCE_HASH_FILE)
  shash = {}
  for i in range(0, len(sds["Source File"])):
    shash[sds["Source File"][i]] = sds["HASH"][i]
  return shash

def get_test_hash():
  """This method maps test name string to a integer hash and stores it
     in a dictionary and returns the dictionary.

     Returns:
      thash (dict) : Dictionary containing test to integer hash mapping.
  """
  tds = pd.read_csv(TEST_HASH_FILE)
  thash = {}
  for i in range(0, len(tds["Test Name"])):
    thash[tds["Test Name"][i]] = tds["HASH"][i]
  return thash

def get_modified_files(changeid):
  """This method sends a REST API request to Gerrit with legacy Gerrit
      change Id number to get a list of modified files for the change id.

     Args:
       changeid (int): Gerrit legacy change id number.

     Returns:
      files (list) : List of modified files for the input change id.
  """
  command = "/usr/bin/python %s/gerrit_tool.py gerrit_changeid_list_files --gerrit_change_id " \
            "%s" % (TOOLBOX_PATH, changeid)

  print command
  result = subprocess.check_output(command, shell=True)
  files = None
  m = re.search('Files: (.*)', result)
  if m:
    files = m.group(1)
  return files

def create_dataset(n_map):
  """This method creates dataset for decision tree machine learning algorithm.
     Dataset is stored in a CSV file.

     Args:
       n_map (list): List containing list of test name, no. of modified files,
                     and source file. Each entry of list includes test name
                     which does not need to be run for the specified source
                     file.
  """
  shash = get_source_hash()
  thash = get_test_hash()

  # Read CSV file which contains information obtained from Jira such as
  # BUG NO., Change ID and test name.
  ds = pd.read_csv(JIRA_STORE)

  tests = []
  source_files = []
  mod_files = []
  run = []
  source_names = []
  test_names = []

  for i in range(0, len(ds["Idx"])):
    changeid = ds["CHANGEID"][i]
    if changeid == 0:
      continue
    print ds["BUG"][i], changeid, ds["TestName"][i]

    if ds["TestName"][i] == '0':
      continue

    # Get the files modified for change id from Gerrit
    files = get_modified_files(changeid)

    file_list = files.split(",")
    print "Files modified by change Id %s -->\n %s" % (changeid, file_list)
    num_files = len(file_list)

    for f in file_list:
      source_files.append(shash[f])
      source_names.append(f)
      tests.append(thash[ds["TestName"][i]])
      test_names.append(ds["TestName"][i])
      mod_files.append(num_files)
      run.append(1)

  for map in n_map:
    file = map[2]
    test = map[0]
    num_files = map[1]
    source_files.append(shash[file])
    source_names.append(file)
    tests.append(thash[test])
    test_names.append(test)
    mod_files.append(num_files)
    run.append(0)

  # dictionary of column name and lists (of tests (as integer hash), no. of
  # modified files, source files ((as integer hash) and prediction of test run.
  dict = {'Test Name': tests, 'No. of files': mod_files, 'Source file':
          source_files, "Test Run": run}

  df = pd.DataFrame(dict)

  # saving the dataframe for decision tree machine learning dataset
  df.to_csv(ML_DATASET_PATH)

  # dictionary of column name and lists (of tests (as string), no. of
  # modified files, source files ((as string) and prediction of test run.
  dict = {'Test Name': test_names, 'No. of files': mod_files, 'Source file':
           source_names, "Test Run": run}

  df = pd.DataFrame(dict)

  # saving the dataframe for decision tree machine learning dataset
  df.to_csv(ML_STR_DATASET_PATH)

def ml_core(input_data):
  """This method makes the input data for machine learning core module
     which implements decision tree algorithm.

     Args:
       input_data (list): List containing source files, number of modified files
                          and test name.
     Returns:
      pred (int) : 1 if test needs to be run for the input data,
                   0 if test does not need to be run for the input data.
  """
  ds = pd.read_csv(ML_DATASET_PATH)

  x = ds.iloc[:, 1:-1].values
  y = ds.iloc[:, 4].values

  X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0,
                                                      random_state = 0)

  # sc = StandardScaler()
  # X_train = sc.fit_transform(X_train)
  # X_test = sc.transform(X_test)

  classifier = DecisionTreeClassifier(criterion = "entropy", random_state = 0)
  classifier.fit(X_train, y_train)

  y_pred = classifier.predict(input_data)

  return y_pred[0]

def get_mapped_tests(files):
  """This method returns the set of tests mapped to modified files passed as
     input.

     Args:
       files (list): List of modified files.

     Returns:
      tests (list) : List of tests mapped to source files.
  """
  command = "/usr/bin/python test_selector.py " \
            "--modified_files " \
            "%s" % files
  print command
  result = subprocess.check_output(command, shell=True)
  tests = []
  m = re.search('TCs: \[\'(.+?)\'\]', result)
  if m:
    # tests = ' '.join(m.group(1).split(','))
    tests = m.group(1).split(',')
  return tests

def prepare_inputs(files, tests):
  """This method prepares a mapping of source and test name for passing it as
     input to machine learning core module.

     Args:
       files (list): List of modified files.
       tests (list): List of tests

     Returns:
      inputs (list) : List of tests mapped to source files.
  """
  files = files.split(",")
  mod_files = len(files)
  inputs = []
  for file in files:
    for test in tests:
      inputs.append([test.strip(), mod_files, file])

  return inputs

def get_run_tests(inputs):
  """This method prepares a mapping of source and test name for passing it as
     input to machine learning core module.

     Args:
       files (list): List of modified files.
       tests (list): List of tests

     Returns:
      inputs (list) : List of tests mapped to source files.
  """
  shash = get_source_hash()
  thash = get_test_hash()
  run_tests = []
  skipped_tests = []
  for input in inputs:
    data = []
    #print "Input: %s" % input
    src_file = input[2]
    test = input[0]
    print "Verifying if test %s needs to be run for source file %s" % (
            test, src_file)
    data.append([shash[src_file], input[1], thash[test]])
    pred = ml_core(data)
    if pred == 0:
      print "Test %s does not need to be run for source file %s" % (
             test, src_file)
      skipped_tests.append(test)
    else:
      print "Test %s needs to be run for source file %s" % (
            test, src_file)
      run_tests.append(test)
  print "Skipped Tests -->\n %s" % skipped_tests
  return run_tests

if __name__ == "__main__":
  # Usage -> "python ml.py --changeid 374556 --dataset source_test_dataset"

  parser = argparse.ArgumentParser()
  parser.add_argument("--changeid", help="Gerrit Change Id", type=str,
                      required=True)
  parser.add_argument("--dataset", help="Dataset path of tests which does not"
                                        " need to be run on source "
                                        "files",

                      required=True)
  args = vars(parser.parse_args())

  # Dataset of tests and source specifying tests which does not need to be run
  # on source files.
  with open(args["dataset"]) as f:
    map = json.load(f)
    n_map = json.loads(map["n_map"])

  changeid = args["changeid"]
  print "Get Code churn for change id %s" % changeid
  files = get_modified_files(changeid)
  print "Files modified by changeid %s --> %s" % (changeid, files)
  tests = get_mapped_tests(files)
  print "Tests mapped before predictive test selection -->\n %s" % tests
  print "Preparing Input data for machine learning"
  inputs = prepare_inputs(files, tests)
  create_dataset(n_map)
  run_tests = get_run_tests(inputs)
  print "Tests to run using Predictive Model -->\n %s" % run_tests
