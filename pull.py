import os
import json
from pprint import pprint
from testrail import *

client = APIClient('https://testrail.stage.mozaws.net')

try:
  client.user = os.environ['TESTRAIL_USERNAME']
  client.password = os.environ['TESTRAIL_PASSWORD']
except KeyError:
  print("You must set your TESTRAIL_USERNAME and TESTRAIL_PASSWORD environment variables.")
  exit()

filter_key = "custom_one_and_done"

print("Fetching project data from testrail...")

projects = client.send_get('get_projects')

one_and_done_cases = {}
one_and_done_cases["projects"] = {}

for project in projects:

  project_id = project["id"]
  if project["suite_mode"] is 1: #single-suite project
    cases = client.send_get('get_cases/%s' % project_id)
    cases_to_add = {case["id"]: case for case in cases if case[filter_key] is True}

    if len(cases_to_add) > 0:
      one_and_done_cases["projects"][project_id] = {}
      one_and_done_cases["projects"][project_id]["project_name"] = project["name"]
      one_and_done_cases["projects"][project_id]["cases"] = cases_to_add

  elif project["suite_mode"] is 3: # multi-suite project
    suites = client.send_get('get_suites/%s' % project_id)
    for suite in suites:
      suite_id = suite["id"]
      cases = client.send_get('get_cases/%s&suite_id=%s' % (project_id, suite_id))
      cases_to_add = {case["id"]: case for case in cases if case[filter_key] is True}

      if len(cases_to_add) > 0:
        if project_id not in one_and_done_cases:
          one_and_done_cases["projects"][project_id] = {}
          one_and_done_cases["projects"][project_id]["project_name"] = project["name"]
          one_and_done_cases["projects"][project_id]["suites"] = {}
        if suite_id not in one_and_done_cases["projects"][project_id]["suites"]:
          one_and_done_cases["projects"][project_id]["suites"][suite_id] = {}
          one_and_done_cases["projects"][project_id]["suites"]["suite_name"] = suite["name"]
        one_and_done_cases["projects"][project_id]["suites"][suite_id]["cases"] = cases_to_add

with open('cases.json', 'w') as outfile:
  json.dump(one_and_done_cases, outfile, indent=4, sort_keys=True, separators=(',', ':'))
