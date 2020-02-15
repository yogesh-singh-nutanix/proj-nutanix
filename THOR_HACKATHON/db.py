"""
This scripts updates and reads source and test file mapping from persistent
storage.

Copyrights (c) Nutanix Inc. 2020 - Hackathon 7.0 - THOR Project

Author: yogesh.singh@nutanix.com
"""

# Usage -> "python db.py --test_map_store map_store_source_test"

import json
import os
import argparse

mapping_store = "map_store"

def update_db(testMap):
  """This method dumps a source and test file mapping in a persistent storage.
    Args:
      testMap (Dict): Dictionary of source and test

  """
  dirPath = os.path.dirname(os.path.realpath(__file__))
  global mapping_store
  mapping_store = os.path.join(dirPath, mapping_store)
  with open(mapping_store, "w+") as sh:
    json.dump(testMap, sh)

def read_db():
  """This method reads the source and test map from a persistent storage.

    Returns:
      testMap (Dict): Dictionary of source and test

  """
  with open(mapping_store) as sh:
    testMap = json.load(sh)
    return testMap

if __name__ == "__main__":
  # Usage -> "python db.py --test_map_store map_store_source_test"

  parser = argparse.ArgumentParser()
  parser.add_argument("--test_map_store", help="Mapping of Source and test "
                                               "store", type=str,
                      required=True)
  args = vars(parser.parse_args())
  changeid = args["test_map_store"]

  with open(args["test_map_store"]) as f:
    test_map = json.load(f)
    test_map_db = test_map["test_map_db"]

  update_db(test_map_db)
  read_db()

