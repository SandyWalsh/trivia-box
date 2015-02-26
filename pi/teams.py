import json
import sys


with open('teams.json') as teams_file:
    teams = json.load(teams_file)

if len(sys.argv) < 2:
    for idx, team in enumerate(teams):
        print "%d. %s" % (idx, team)
    print
    print "teams <first team #> <second team #>"
    sys.exit(0)

first, second = int(sys.argv[1]), int(sys.argv[2])

config = {
    "teams": [teams[first], teams[second]]
}

with file("config.json", 'w') as f:
    json.dump(config, f, indent=2)

print json.dumps(config, indent=2)
