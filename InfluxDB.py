# Created by Daniel Nilsson
# Please use my invite-link to help me with my work, we get 500skr each :)
# https://tibber.com/se/invite/8af85f51
# Version 1.1 2020-11-04
# Script to fetch hourly prices from Tibber, create a file to be used to store the data into InfluxDB
# Run "influx -import -path=input.txt -precision=s" to store data from file to your InfluxDB
# You can then add a job to Crontab, so this script is running 2-3 times per day and also the command to import the data to InfluxDB

import json,datetime,requests # import libraries

# Tibber
token = "" # insert your token between ""

# InfluxDB variables
database = "Tibber"
measurement = "El"
field = "Pris"

headers = {
    'Authorization': 'Bearer '+token, # Tibber Token
    'Content-Type': 'application/json',
}

data = '{ "query": "{viewer {homes {currentSubscription {priceInfo {today {total startsAt },tomorrow {total startsAt }}}}}}" }' # asking for today's and tomorrow's hourly prices

response = requests.post('https://api.tibber.com/v1-beta/gql', headers=headers, data=data) # make the query to Tibber
response = response._content # selecting the important data from the response
parsed = json.loads(response) # parse it so we can use it easier
file = open("input.txt", "w") # create a file to store the data
file.writelines(["# DML","\n# CONTEXT-DATABASE: "+database+"\n\n"]) # write some important lines into the file
for data in parsed["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]["today"]: # go through today's hours
  time = data["startsAt"] # store the datetime
  utctime = str(datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z").timestamp())[:-2] # change datetime to epoch(seconds) and without decimals  
  total = str(round(data["total"]*100,2)) # recalc to kronor instead of öre
  file.writelines([measurement," ",field,"=",total," ",utctime,"\n"]) # write price and datetime to file
for data in parsed["data"]["viewer"]["homes"][0]["currentSubscription"]["priceInfo"]["tomorrow"]: # go through tomorrow's hours
  time = data["startsAt"] # store the datetime
  utctime = str(datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z").timestamp())[:-2] # change datetime to epoch(seconds) and without decimals
  total = str(round(data["total"]*100,2)) # recalc to kronor instead of öre
  file.writelines([measurement," ",field,"=",total," ",utctime,"\n"]) # write price and datetime to file
file.close()
