"""
This scripts uses JIRA REST API to get
BUG No. Change Id and test name information from product bugs.

Copyrights (c) Nutanix Inc. 2020 - Hackathon 7.0 - THOR Project

Author: rahul.gupta@nutanix.com
"""

# Usage -> "python jira_info.py"

import jira.client
import re
import sys
import requests
import json
from jira.client import JIRA

url='https://jita.eng.nutanix.com/api/v2/testcases?raw_query={"name":"%s","git.branch":"master"}'

jira_options={'server': 'https://jira.nutanix.com'}
# AD password of the user is masked.
jira=JIRA(options=jira_options,basic_auth=('yogesh.singh','*****'))
block_size=100
block_num=0
jql='project=Engineering AND affectedVersion="AFS 3.7" AND type=Bug and labels = regression_run and status = Resolved  and resolution = Fixed'

def get_avg_test_duration(testpath):
  resp = requests.get(url % testpath).text
  if "avg_run_duration" not in resp:
    return 0
  else:
    val = json.loads(resp)
    return val["data"][0]["avg_run_duration"]


with open('data.csv', mode='a') as f:
  while True:
    start_idx = block_num*block_size
    issues = jira.search_issues(jql, start_idx, block_size)
    if len(issues) == 0:
      #print("no more issues:", issues)
      break
    block_num += 1
    iter_index = 1
    #print ("iter: total issues", str(iter_index), issues)
    for issue in issues:
      issue_entry=''
      issues_in_project=jira.issue(issue.key)
      gerrit_id_list=[]
      for comment in issues_in_project.raw['fields']['comment']['comments']:
        if ("===git tracker=== : Ticket Resolved" in comment["body"]) and ("JIRA Version (branch equiv): master" not in comment["body"]):
          gerritid = re.search("Code Review URL: https://gerrit.eng.nutanix.com/(.*)$", comment["body"])
          if gerritid:
            gerrit_id_list.append(gerritid.group(1))
      if gerrit_id_list==[]:
        gerrit_id_list.append('0')
      if issues_in_project.fields.customfield_18060:
        val_tcname = []
        for tcname in issues_in_project.fields.customfield_18060:
          val_tcname.append(tcname)
        print   str(iter_index) + ',' + issue.key + ',' + val_tcname[-1] + ',' + gerrit_id_list[-1] + ',' + str(get_avg_test_duration(val_tcname[-1]))
        f.write(str(iter_index) + ',' + issue.key + ',' + val_tcname[-1] + ',' + gerrit_id_list[-1] + ',' + str(get_avg_test_duration(val_tcname[-1])) + '\n')
      else:
        des=(jira.issue(issue.key)).fields.description.encode('utf-8')
        idata = []
        for line in re.split(r'\n|\|', des):
        #for line in des.split('\n'):
          if ("http://" in line) and ("logs" in line) and ("nutest_test.log" in line):
            #print line
            sline = '' 
            aline =line.split("/")
            for elem  in aline[5:]:
              if not ((aline[4][0:7] in elem) or ("nutest_test.log" in elem)):
                sline = sline + '.' + elem
            sline = sline.lstrip('.')
            idata.append(sline)
        if idata == []:
          print   str(iter_index) + ',' + issue.key + ',0 ,' + gerrit_id_list[-1] + ',' + str(get_avg_test_duration(''))
          f.write(str(iter_index) + ',' + issue.key + ',0 ,' + gerrit_id_list[-1] + ',' + str(get_avg_test_duration(''))+ '\n')
        else:
          print   str(iter_index) + ',' + issue.key + ',' + idata[-1] + ',' + gerrit_id_list[-1] + ',' + str(get_avg_test_duration(idata[-1]))
          f.write(str(iter_index) + ',' + issue.key + ',' + idata[-1] + ',' + gerrit_id_list[-1] + ',' + str(get_avg_test_duration(idata[-1]))+ '\n')
      iter_index += 1
