#!/usr/bin/python
#
#   This script Prints URL status & Response Times For the Past 24 Hours
#   Author Jeevan Edakkunnath Mana
#   Date 12-04-2020
#
############################################################################################################################################################
import pymongo
from time import gmtime, strftime

file_date = strftime("%d%m%Y", gmtime())
file_name = "urlstatus_report_" + str(file_date) + ".html"
htmlfile="/root/"+file_name

def main():
    readMongo()

def getDBConnObj():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["urlstatus"]
    mycol = mydb["url_stat_data"]
    return mycol

def readMongo():
    mycol = getDBConnObj()
    mydoc = mycol.find().sort([('timestamp', -1)]).limit(96)
    html =  "<html>\n<head></head>\n<body>\n"
    title = "URL Availability And Response Time Analysis"
    html += '\n<h1 align="center">' + title + '</h1>\n'
    html += '<table style="width:85%">\n<tr>\n'
    html += '<th style="text-align:left">Date</th>\n<th style="text-align:left">URL</th>\n<th style="text-align:left">Status</th>\n<th style="text-align:left">Response Code</th>\n<th style="text-align:left">Response Time</th>\n'
    for doc in mydoc:
        html += '<tr>\n'
        html += '<td>' +  doc['date'] + '</td>\n'
        html += '<td>' +  doc['url'] + '</td>\n'
        html += '<td>' +  doc['status'] + '</td>\n'
        html += '<td>' +  str(doc['response_code']) + '</td>\n'
        html += '<td>' +  str(doc['response_time']) + '</td>\n'
        html += '</tr>\n'
    html += '</table>\n'
    with open(htmlfile, 'w') as f:
        f.write(html + "\n</body>\n</html>")
# Main app
#
if __name__ == '__main__':
    main()
