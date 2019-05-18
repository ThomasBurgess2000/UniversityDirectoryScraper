#Import Modules
import os
import requests
import configparser
from urllib.request import urlopen
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import re

#MAIN
#Login to page

session = requests.Session()


def login(url, username=None, password=None):
    if not username:
        username = input('Please input your NetID: ')
    if not password:
        password = input('Please input your password: ')
    response = session.get(url, cookies=session.cookies)
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        lt = soup.find('input', {'name': 'lt'})['value']
        execution = soup.find('input', {'name': 'execution'})['value']
        payload = {
            'username': username,
            'password': password,
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit',
            'submit': 'Log In'
        }
        response = session.post(url, data=payload, cookies=session.cookies)
        return response
    except TypeError:
        # Already registered
        return response


def cas_login(url, username, password):
    response = login(url, username, password)
    soup = BeautifulSoup(response.text, 'html.parser')
    while soup.find_all(class_="errors"):
        print(soup.find(id='msg').string, end="\n\n")
        response = login(url)
        soup = BeautifulSoup(response.text, 'html.parser')
    print('NetID Log In Successful\n')
    return response


NetID = "USERNAME"
Password = "PASSWORD"
cas_login('https://login.biola.edu/cas/login', NetID, Password)


#Iterate through x-1 pages
i=1
t=0
listOfNames=[]
listOfEmails=[]
while i < 387:
#Make a list (listOfNames) of all the names on the page
  
    iStr=str(i)
    url=('https://www.biola.edu/directory/search?_type=person&login=true&page='+iStr)
    result=session.get(url,cookies=session.cookies)
    HTMLsoup=BeautifulSoup(result.text)
    nameList2=HTMLsoup.findAll(class_="title")
    for name in nameList2:
        printable=name.get_text()
        listOfNames.append(printable)
        #print(printable)

#Download images and set the filename to the corresponding first and last name (personName)
    
    downloadList=HTMLsoup.findAll(class_="result_image")

    for download in downloadList:
        personName=listOfNames[t]
        strT=str(t)
        fileName=strT+" "+personName+".png"
        downloadURL=download.find("img")["src"]
        if downloadURL[-10:]=="medium.jpg":
            downloadURL=downloadURL[:-10]
            downloadURL=downloadURL+"large.jpg"
        fullFileName=os.path.join("/home/pi/Desktop/DirectoryData/DirectoryPics", fileName)
        urlretrieve("https:"+downloadURL,fullFileName)
        print ("Downloaded "+fileName)
        t=t+1
    i=i+1
    
#Writes all names to file

namesFile=os.path.join("/home/pi/Desktop/DirectoryData/DirectoryNames", "names.txt")
f=open(namesFile,'a')
for name in listOfNames:
    f.write(name)
    f.write('\n')
    print ((name)+" added to list")
f.close()

print ("\nPhotos downloaded: " + str(t))
print ("Names in list: " +str(len(listOfNames)))
print ("Emails in list: "+str(len(listOfEmails)))

print ("Program Complete")
