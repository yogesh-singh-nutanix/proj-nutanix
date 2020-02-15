"""
This scripts sends REST API request to Gerrit to get the list of modified files
using legacy Gerrit change Id number provided as input.

Copyrights (c) Nutanix Inc. 2020 - Hackathon 7.0 - THOR Project

Author: yogesh.singh@nutanix.com
"""

# Usage -> "python gerrit_tool.py gerrit_changeid_list_files --gerrit_change_id 375468"

from requests.auth import HTTPBasicAuth
import ast
import sys
import argparse
import traceback
import re
import pprint

from rest_client.gerrit_rest_client import GerritRestClient

UNKNOWN_COMPONENT = 'Unknown'

USER = "yogesh.singh"
PASSWORD = "z8HWAzAzhWQRLUkYsD5VjqDEvvxvMzDl4bthMUG3qg"

class GerritAPI():

  def __init__(self, **kwargs):
    self.auth = HTTPBasicAuth(USER, PASSWORD)
    self.gerrit = GerritRestClient()

  def commit_list_files(self, project, branch, changeid, revision=1):
  """This method lists all modified files using project, branch and change id info.

     Args:
       self (object): Gerrit API instance
       project (str): Gerrit Project
       branch (str): Gerrit Branch
       changeid (str): Gerrit legacy change id number
       revision (int): Gerrit Revision

     Returns:
      files (list) : List of modified source files for the commit.
  """
    query = "a/changes/%s~%s~%s/revisions/%s/files" % (project,
                                                       branch,
                                                       changeid,
                                                       revision)

    response = self.gerrit.get(query, auth=self.auth, verify=False).content
    # print response
    response = ast.literal_eval(response.lstrip(")]}'"))
    # print "Response=%s" % response
    files = []
    for file in response:
      if "/COMMIT_MSG" not in file:
        files.append(file)
    return files

  def get_change_info(self, changeid):
    response = self.gerrit.get(
       "a/changes/?q=change:%s" % changeid,
                            auth=self.auth, verify=False).content
    #print "response=%s" % response
    response = ast.literal_eval(response.lstrip(")]}'"))

    project, branch, new_style_changeid = response[0]["project"], response[0]["branch"], response[0]["change_id"]

    return project, branch, new_style_changeid

class BaseCommand(object):
  """Base class for all commands supported by the GerritClient."""

  NAME = None

  def __init__(self, args):
    """Creating parser and subparser objects.
    Args:
      args (dict): Dictionary with required parameters and their values.
    """
    self.args = args
    if self.NAME is None:
      raise Exception("Command NAME is not provided.")

  @classmethod
  def get_command_parser(cls, sub_parsers, parents=None):
    """This method returns a parser object for the current command Command class

    Args:
      sub_parser (object): Start_job subparser.
      parents (object): Common options parser.
    """
    parser = sub_parsers.add_parser(
      cls.NAME, description=cls.__doc__, help=cls.__doc__, parents=parents)
    parser.set_defaults(command_class=cls)
    return parser

  @classmethod
  def add_command_parser(cls, sub_parsers, parents=None):
    """This method adds args to subparser object.

    Args:
      args (dict): Dictionary with required parameters and their values.
    """
    raise NotImplementedError

  @classmethod
  def validate_args(cls, args):
    """This method validates the args based on the type of command_class.

    Args:
      args (dict): Dictionary with required parameters and their values.
    """
    pass

  def run(self):
    """This method runs the job according to the command class."""
    raise NotImplementedError

class GerritChangeIdListFilesCommand(BaseCommand):
  """Get List of modified files using legacy change id from Gerrit."""

  NAME = "gerrit_changeid_list_files"

  @classmethod
  def add_command_parser(cls, sub_parsers, parents=None):
    """This method adds gerrit_changeid_list_files args to subparser object.

    Args:
      sub_parser (object): abort_job subparser.
      parents (object): Common options parser.
    """
    parser = cls.get_command_parser(sub_parsers, parents)
    parser.add_argument(
      '--gerrit_change_id', type=str, required=True,
      help="Gerrit Legacy Numerical Change Id")

  def run(self):
    """This method gets modified files in gerrit commit.

    Raises:
      AssertionError: When gerrit API is unsuccessful.
    """
    revision_default = 1
    gerrit_api = GerritAPI()

    gerrit_project, gerrit_branch, gerrit_changeid = \
      gerrit_api.get_change_info(self.args["gerrit_change_id"])

    result = gerrit_api.commit_list_files(gerrit_project,
                                          gerrit_branch,
                                          gerrit_changeid,
                                          revision = revision_default)

    result = "Files: %s" % (','.join(result))
    print result
    return 0

class GerritTask(object):

  def __init__(self, args):
    """This method creates the parser object and parses the commandline args.

    args (list): List of commandline args
    """
    parser = self.setup_parser()
    self.args = parser.parse_args(args)

  def setup_parser(self):
    """This method sets up parser and subparser objects."""
    parser = argparse.ArgumentParser(description="Gerrit client")
    sub_parsers = parser.add_subparsers()
    common_options_parser = argparse.ArgumentParser(add_help=False)
    common_options_parser.add_argument('-v', '--verbose', action="store_true",
                                       help="Print verbose output")
    common_options_parser.add_argument('-d', '--debug', action="store_true",
                                       help="Debug mode")
    for command_class in BaseCommand.__subclasses__():
      command_class.add_command_parser(sub_parsers,
                                       parents=[common_options_parser])
    return parser

  def run(self):
    """This method runs the Gerrit task depending upon the command class."""
    args = vars(self.args)
    if args.get("verbose"):
      print "Command arguments:\n%s" % pprint.pformat(args)
    command_class = args.pop("command_class")
    command_class.validate_args(args)
    try:
      return command_class(args).run()
    except Exception:
      print traceback.format_exc()
      return 1

class GerritTask(object):

  def __init__(self, args):
    """This method creates the parser object and parses the commandline args.

    args (list): List of commandline args
    """
    parser = self.setup_parser()
    self.args = parser.parse_args(args)

  def setup_parser(self):
    """This method sets up parser and subparser objects."""
    parser = argparse.ArgumentParser(description="Gerrit client")
    sub_parsers = parser.add_subparsers()
    common_options_parser = argparse.ArgumentParser(add_help=False)
    common_options_parser.add_argument('-v', '--verbose', action="store_true",
                                       help="Print verbose output")
    common_options_parser.add_argument('-d', '--debug', action="store_true",
                                       help="Debug mode")
    for command_class in BaseCommand.__subclasses__():
      command_class.add_command_parser(sub_parsers,
                                       parents=[common_options_parser])
    return parser

  def run(self):
    """This method runs the Gerrit task depending upon the command class."""
    args = vars(self.args)
    if args.get("verbose"):
      print "Command arguments:\n%s" % pprint.pformat(args)
    command_class = args.pop("command_class")
    command_class.validate_args(args)
    try:
      return command_class(args).run()
    except Exception:
      print traceback.format_exc()
      return 1

if __name__ == "__main__":
# Usage -> "python gerrit_tool.py gerrit_changeid_list_files --gerrit_change_id 375468"

  client = GerritTask(sys.argv[1:])
  exit(client.run())
