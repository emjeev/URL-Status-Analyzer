#!/usr/bin/python
#
#   This script checks all the  URL status Once in every 15 minutes and write the data to MongoDB.In a day 96 documents would be committed in DB
#   Author : Jeevan Edakkunnath Mana
#   Date : 12-04-2020
#
############################################################################################################################################################
import requests
import time
from time import gmtime, strftime
import validators
import pymongo
import smtplib,ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

frmt_date = strftime("%d/%m/%Y %H:%M:%S", gmtime())
url_dict_ob = []

def main():

    writeUrlStatus()

def isValidURL(url):
    flag=0
    valid=validators.url(url)
    if valid == True:
       flag=1
    return flag

def writeUrlStatus():
    filename = '/root/urls'
    with open(filename, 'r') as input:
         for line in input:
             url = line[:-1]
             valid = isValidURL(url)
             if valid == 1:
                result = getresponse(url)
                url_dict_ob.append(result)
         writeMongo(url_dict_ob)

def getresponse(url):
    start_time = time.time()
    try:
        r = requests.head(url, timeout=5)
        end_time = time.time()
        response_time = end_time - start_time
        response_code = r.status_code
        if r.status_code != 200:
           status = "DOWN"
           stat = 0
           rc = r.status_code
           sendAlert(frmt_date,url,status,rc,response_time)
        else:
           status = "UP"
           stat = 1
           rc = r.status_code
    except requests.exceptions.ConnectionError:
           status = "DOWN"
           stat = 0
           end_time = time.time()
           response_time = end_time - start_time
           rc = "Exception-UNIDENTIFIED"
           sendAlert(frmt_date,url,status,rc,response_time)

    except requests.exceptions.Timeout:
           status = "DOWN"
           end_time = time.time()
           response_time = end_time - start_time
           rc = "Exception-UNIDENTIFIED"
           sendAlert(frmt_date,url,status,rc,response_time)
  #Creating Dictionary Object For Writing Document To DB
    dict_obj = my_dictionary()
    dict_obj.add('date',frmt_date)
    dict_obj.add('url',url)
    dict_obj.add('status',status)
    dict_obj.add('response_code',rc)
    dict_obj.add('response_time',response_time)
    return dict_obj
class my_dictionary(dict):

      # __init__ function
    def __init__(self):
        self = dict()

    # Function to add key:value
    def add(self, key, value):
        self[key] = value

def getDBConnObj():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["urlstatus"]
    mycol = mydb["url_stat_data"]
    return mycol

def writeMongo(list_url_obj):
    mycol = getDBConnObj()
    for record in list_url_obj:
        commit_log = mycol.insert_one(record)
        print("One Document Inserted To DB") +" : "
        print(commit_log)
def sendAlert(date,url,status,rc,rt):
    issue_string = date + " : " + url + " : " + status + " : " + str(rc) + " : " + str(rt)
    #print(issue_string)
    mail_content = "There is an issue in URL Availability Check\n" + issue_string
    gmail_user = "xxxxx@gmail.com"
    gmail_password = "xxxxx"
    receiver_address="xxxx@gmail.com"
    message = MIMEMultipart()
    message['From'] = gmail_user
    message['To'] = receiver_address
    message['Subject'] = 'URL Availability Check Is Failing'
    try:
        message.attach(MIMEText(mail_content, 'plain'))
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(gmail_user, gmail_password) #login with mail_id and password
        text = message.as_string()
        session.sendmail(gmail_user, receiver_address, text)
        session.quit()
        print('Mail Sent')
        #print 'Email sent!'
    except Exception as e:
           print 'Something went wrong...'
           print(e)
# Main app
#
if __name__ == '__main__':
    main()

