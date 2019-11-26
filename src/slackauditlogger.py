import requests
import json
import sys
import os
import time
import dateutil
import tzlocal
from datetime import datetime
from dateutil.parser import *

class SlackAuditLogger(object):

    def __init__(self):

        with open(os.getenv(
            'CONFIG_PATH', '/usr/share/logstash/src/config/config.json')) as config_data:
            self.config = json.load(config_data)

        self.timeslog_path = '{}/times.log'.format(self.config['SINCEDB_PATH'])
        self.timeslog_sincedb = self._check_sincedbs(self.timeslog_path)

    def _check_sincedbs(self, SINCEDB_PATH):

        if os.path.isfile(SINCEDB_PATH):

            log_types = self.config["LOGTYPES"]
            config_logtypes = []
            timeslog_types = []

            for logtype in log_types:
                config_logtypes.append(logtype)

            with open(self.timeslog_path) as json_file:
                data = json.load(json_file)
                for key in data['logs']:
                    for k in key:
                        timeslog_types.append(k)

            uniq_list = []

            for log in config_logtypes:
                if log not in timeslog_types:
                    uniq_list.append(log)
                else:
                    continue

            #Loop through the new log list and add an entry to times.log
            for u in uniq_list:
                with open(self.timeslog_path) as f:
                    obj = json.load(f)
                    obj["logs"][0][u] = 946684800
                with open(self.timeslog_path, 'w+') as g:
                    g.write(json.dumps(obj))

            return
        else:
            since_db = open(self.timeslog_path, 'w')
            since_db.write(json.dumps({"logs": [{}]}))
            since_db.close()

            log_types = self.config["LOGTYPES"]
            for log_type in log_types:
                with open(self.timeslog_path) as f:
                    times_log = json.load(f)
                    times_log["logs"][0][log_type] = 946684800
                    with open(self.timeslog_path, 'w+') as g:
                        g.write(json.dumps(times_log))
            return

    def _unix_to_pretty_utc(self, date):

        utc_time = datetime.utcfromtimestamp(date)
        return utc_time.strftime("%Y-%m-%d %H:%M:%S")

    #Get logs for a given action, with earlist date being the last time a log was captured for a given action.
    def getlogs(self):

        log_types = self.config["LOGTYPES"]
        headers = self.config["HEADERS"]

        results = []
        for log_type in log_types:

            with open(self.timeslog_path) as json_file:
                data = json.load(json_file)
                oldest = data['logs'][0][log_type]

            url = "https://api.slack.com/audit/v1/logs?oldest={}".format(oldest)
            querystring = {"Accept":"application/json","action":log_type,"limit":"9999"}

            r = requests.request("GET", url, headers=headers, params=querystring)
            jsonresponse = r.json()
            results.append(jsonresponse)

        return results

    #Get the latest logs and update times.log with the most recent timestamp for a given action
    def get_latest_logs(self):

        logs = self.getlogs()
        results = []

        for json_inner_array in logs:
            times = []

            for json_data in json_inner_array['entries']:

                action = json_data['action']

                times.append(json_data['date_create'])
                times.sort()
                largest = times[-1]

                with open(self.timeslog_path) as json_file:
                    data = json.load(json_file)

                last_log_time = data['logs'][0][action]
                data['logs'][0][action] = largest

                if datetime.utcfromtimestamp(float(json_data['date_create'])) > datetime.utcfromtimestamp(float(last_log_time)):
                    json_data['date_create'] = self._unix_to_pretty_utc(float(json_data['date_create']))
                    results.append(json_data)

            with open(self.timeslog_path, 'w') as f:
                f.write(json.dumps(data))

        results = json.dumps(results)
        return results

if __name__ == "__main__":
    auditlogger = SlackAuditLogger()

    if sys.argv[1] == 'getlogs':
      print(auditlogger.getlogs())

    if sys.argv[1] == 'getlatestlogs':
      print(auditlogger.get_latest_logs())