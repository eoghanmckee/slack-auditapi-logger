# Slack Audit API Logger

Slack provides an API for capturing events in an Enterprise Grid organization.

This tool queries the Slack Audit API with your organizations associated Bearer Token, retrieving logs for User Logins, User Logouts, and Created Users. To explore all the logs available from the Slack Audit API visit the [Slack Audit API Documentation Page](https://api.slack.com/docs/audit-logs-api).  

The tool will initially create entries in `times.log`for the `LOGTYPES` located in config.json. The initial timestamp for these logs goes back to 01/01/2000 @ 12:00am (UTC) (946684800) in order to retrieve all the logs. To avoid redundency, and massive useless API requests, the tool will then only pull new logs with the earlist date being the last time it saw activity from a given action. 

Once up and running, if you would like to add new actions to be logged, simply add the action to config.json. The tool will see that there is no entry for this action in times.log and create one with the earliest being 01/01/2000 @ 12:00am (UTC) (946684800) in order to pull all past logs related to that action.

Slack Audit API allows for 9,999 results per API request. If you're a larger Org you may reach that limit on the inital backfill of log requests. In this case you'll need to incorporate [Pagination](https://api.slack.com/docs/pagination#cursors)

For querying the standard [Slack Web API](https://api.slack.com/web), [@maus](https://github.com/maus-/slack-auditor) originally created a very similar tool.

Finally, `guest_invite_added` and `app_resources_added` returns a 400 error. Until this is resolved by slack, they will be ommitted from this.

## Requirements

1. Your organization must have the Enterprise Grid plan rolled out. Audit logs are not available on any other plans (Free, Standard, or Plus plans).
2. A `Bearer` token is required for authentication. To retrieve this token, follow the instruction on setting up an [app on the Enterprise Grid](https://api.slack.com/docs/audit-logs-api#install).
Having said that, it's extremely unlikely you'll succeed in retrieving the `Bearer` token from the instructions above, I would highly recommend just going straight to Slack API Support, devsupport@slack.com. 

## Deployment

### Docker

1. docker build -t slacklogger:latest .
2. docker run slacklogger:latest

### From Source

1. Install dependencies `pip install -r scripts/requirements.txt`
2. Update directories in `src/slackauditlogger.py` and `src/config/config.json`
3. Add `Bearer` token to `src/config/config.json`
4. Run Logstash, alternatively, from just running the script from the CL: `$ python slackauditlogger.py getlatestlogs`
