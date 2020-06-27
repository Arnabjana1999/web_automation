'''
Working script for automating user registration and login through Python requests and BeautifulSoup Library
url='http://www.poolprop.com/default.aspx'

Created by: Arnab Jana
Date: June 26, 2020
'''

import re
import json
import datetime

import requests
from bs4 import BeautifulSoup

# hardcoded JSON files for user registration and login respectively
register_json_file='register.json'
login_json_file='login.json'

# Due to default response being available in Thai, this dictionary maintains mapping between byte-encoded message and its corresponding english equivalent 
message={
    "*\u0e2d\u0e35\u0e40\u0e21\u0e25\u0e4c \u0e2b\u0e23\u0e37\u0e2d \u0e23\u0e2b\u0e31\u0e2a\u0e1c\u0e48\u0e32\u0e19 \u0e1c\u0e34\u0e14": "Incorrect username or password",
    "\u0e21\u0e35\u0e2d\u0e35\u0e40\u0e21\u0e25\u0e4c\u0e19\u0e35\u0e49\u0e43\u0e19\u0e23\u0e30\u0e1a\u0e1a\u0e41\u0e25\u0e49\u0e27 \u0e01\u0e23\u0e38\u0e13\u0e32\u0e43\u0e0a\u0e49\u0e2d\u0e35\u0e40\u0e21\u0e25\u0e4c\u0e2d\u0e37\u0e48\u0e19\u0e04\u0e48\u0e30": "Email already used",
}


def register_user():
    # Reading the contents from JSON-file
    with open(register_json_file,'r') as reg_file:
        reg_file_cont=json.load(reg_file)

    # creating the form-data for POST request
    reg_data={
            "ctl00$tbsignupname": reg_file_cont['name_th']+' '+reg_file_cont['surname_th'],
            "ctl00$tbsignuptele": reg_file_cont['tel'],
            "ctl00$tbsignupemail": reg_file_cont['user'],
            "ctl00$tbsignuppass": reg_file_cont['pass'],
            "ctl00$tbsignuppass2": reg_file_cont['pass'],
            "ctl00$cbagreesignup": "on",
            "ctl00$btnsignupdetailside": "Sign up",
            "ctl00$ddlcerrency": "BAHT",
            "ctl00$ddlsetlangfoot": "en-US"
    }

    url='http://www.poolprop.com/default.aspx'

    # timestamp before making POST request
    time_start=datetime.datetime.utcnow()  

    # Creating a requests session
    with requests.Session() as sess:
        # fetching the contents of the url via GET request
        page = sess.get(url)
        
        # scrapping using BeautifulSoup to obtain values of __VIEWSTATE and ASP.NET related hidden variables
        soup = BeautifulSoup(page.content, features="html.parser")
        reg_data["__VIEWSTATE"] = soup.select_one("#__VIEWSTATE")["value"]
        reg_data["__VIEWSTATEGENERATOR"] = soup.select_one("#__VIEWSTATEGENERATOR")["value"]
        reg_data["__EVENTVALIDATION"] = soup.select_one("#__EVENTVALIDATION")["value"]
        
        # POST request to submit the Sign-Up form
        response=sess.post(url,data=reg_data)

        # timestamp after making the POST request
        time_end=datetime.datetime.utcnow()  
        
        # Find alerts in the response html. Alerts indicate success (or particular kind of error) as a result of form submission 
        alerts= re.findall(r"(?<=alert\(\').+(?=\')", response.text)
        
        # success stores boolean status of the request
        success=True
        if(response.status_code!=200):
            success=False

        # detail variable stores the message corresponding to the status of the POST request
        if reg_data['ctl00$tbsignupname'] in alerts[0]:
            detail=reg_data['ctl00$tbsignupname']+" successfully registered"
        else:
            success=False 
            detail=message[alerts[0]]

        # required output info
        output={
                "websitename": url,
                "success": success,
                "start_time": str(time_start),
                "end_time": str(time_end),
                "usage_time": str(time_end - time_start),
                "detail": detail,
        }   

        # pretty-printing the json output
        print(json.dumps(output, indent=4, sort_keys=False))


def test_login():
    # Reading the contents from JSON-file
    with open(login_json_file,'r') as login_file:
        login_file_cont=json.load(login_file)

    # creating the form-data for POST request
    login_data={
            "ctl00$tbuserlogin": login_file_cont['user'],
            "ctl00$tbpasslogin": login_file_cont['pass'],
            "ctl00$btnlogin": "Log in",
            "ctl00$ddlcerrency": "BAHT",
            "ctl00$ddlsetlangfoot": "en-US"
    }

    url='http://www.poolprop.com/default.aspx'

    # timestamp before making POST request
    time_start=datetime.datetime.utcnow()  

    # Creating a requests session
    with requests.Session() as sess:
        # fetching the contents of the url via GET request
        page = sess.get(url)
        
        # scrapping using BeautifulSoup to obtain values of __VIEWSTATE and ASP.NET related hidden variables
        soup = BeautifulSoup(page.content, features="html.parser")
        login_data["__VIEWSTATE"] = soup.select_one("#__VIEWSTATE")["value"]
        login_data["__VIEWSTATEGENERATOR"] = soup.select_one("#__VIEWSTATEGENERATOR")["value"]
        login_data["__EVENTVALIDATION"] = soup.select_one("#__EVENTVALIDATION")["value"]
        
        # POST request to submit the Log-In form
        response=sess.post(url,data=login_data)

        # timestamp after making the POST request
        time_end=datetime.datetime.utcnow()  

        # extracting the name of the user after Log-In using BeautifulSoup
        soup = BeautifulSoup(response.content, features="html.parser")
        name= soup.find("span", {"id": "lbmember"}).find_all(text=True)

        # Find alerts in the response html. Alerts indicate success (or particular kind of error) as a result of form submission 
        alerts= re.findall(r"(?<=alert\(\').+(?=\')", response.text)

        # success stores boolean status of the request
        success=True
        if(response.status_code!=200 or len(name)==0):
            success=False

        # detail variable stores the message corresponding to the status of the POST request
        if len(alerts)==0:
            detail=name[0]+" succesfully logged in"
        else:
            success=False
            detail=message[alerts[0]]
        
        # required output info
        output={
                "websitename": url,
                "success": success,
                "start_time": str(time_start),
                "end_time": str(time_end),
                "usage_time": str(time_end - time_start),
                "detail": detail,
        }   

        # pretty-printing the json output
        print(json.dumps(output, indent=4, sort_keys=False))

    
def main():
    user_choice=int(input("Enter 1 for register_user and 2 for test_login: \n"))

    # Calling the appropriate function
    if user_choice==1:
        register_user()
    elif user_choice==2:
        test_login()
    else:
        print('Enter 1 for register_user and 2 for test_login')

if __name__ == '__main__':
    main()
