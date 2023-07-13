import requests
import json
import sys
import pyodbc
import argparse
import io
import logging
import math
import os
import uuid
#from csv import DictWriter
#from datetime import datetime, timedelta
#from FuelSDK import ET_Client, ET_DataExtension_Row, ET_DataExtension, ET_DataExtension_Column
from suds.sudsobject import asdict
from pathlib import Path
from getpass import getpass

global whserver, whdatabase, whusername, whpassword, whtrustedconnection
global authenticationurl, clientid, clientsecret, granttype
global urlquerystringpayload, urlquerystringheaders, authresponse
global emailtriggersenturl, emailtriggersendmethodurl, soapendpoint, baseapiurl, jsonpayload
global requestid, recipientsendid, accesstoken, tokentype, expiresin, scope
global subscriberkey, submissionid, executiontype
global executiontype , idxexecutiontype
global whDefaults, status, messages, messageerrors

whDefaults={'whServer':'edw-db-dev'}
whDefaults['whDatabase']  = 'Webhook'
whDefaults['whUserName']  = 'EMERALD_API'
whDefaults['whPassword']  = 'xxxxxxxx'
whDefaults['whTrustedConnection']  = 'Yes'

def PaperformWhitepaperEmail(*args):
    try:
        authenticationurl = ''
        clientid = ''
        clientsecret = ''
        granttype = ''
        urlquerystringpayload = ''
        urlquerystringheaders = ''
        authresponse = ''
        emailtriggersenturl = ''
        emailtriggersendmethodurl = ''
        soapendpoint = ''
        baseapiurl = ''
        jsonpayload = ''
        requestid = ''
        recipientsendid = ''
        accesstoken = ''
        tokentype = ''
        expiresin = ''
        scope = ''
        subscriberkey = ''
        submissionid = ''
        executiontype = ''
        messages = ''
        messageerrors = ''
    
        args = args[0]
        # Collect command line arguments and assign
        
        # Database Arguments
        if "-whServer" in args:
            whserver = args[args.index("-whServer") + 1]
        else:
            whserver= whDefaults["whServer"]
            
        if "-whDatabase" in args:
            whdatabase = args[args.index("-whDatabase") + 1]
        else:
            whdatabase = whDefaults["whDatabase"]        
    
        if "-whUserName" in args:
            whusername = args[args.index("-whUserName") + 1]
        else: 
            whusername = whDefaults["whUserName"]
    
        if "-whPassword" in args:
            whpassword = args[args.index("-whPassword") + 1]
        else:
            whpassword = whDefaults["whPassword"]
            
        if "-whTrustedConnection" in args:
            whtrustedconnection = args[args.index("-whTrustedConnection") + 1]
        else:
            whtrustedconnection = whDefaults["whTrustedConnection"]
            
        #Database Connection Opening and Initiating Cursor
        conn_string = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=" + whserver + ";DATABASE=" + whdatabase + ";Trusted_Connection=" + whtrustedconnection + ";"
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()            

        #API Arguments    
        if "-AuthenticationUrl" in args:
            authenticationurl = args[args.index("-AuthenticationUrl") + 1]
        else:
            raise Exception("Authentication URL was not provided")
    
        if "-ClientId" in args:
            clientid = args[args.index("-ClientId") + 1]
        else:
            raise Exception("Client Id was not provided")
            
        if "-ClientSecret" in args:
            clientsecret = args[args.index("-ClientSecret") + 1]
        else:
            raise Exception("Client Secret was not provided")
    
        if "-GrantType" in args:
            granttype = args[args.index("-GrantType") + 1]
        else:
            raise Exception("Grant Type was not provided")
            
        if "-EmailTriggerUrl" in args:
            emailtriggersendmethodurl = args[args.index("-EmailTriggerUrl") + 1]
        else:
            raise Exception("Email Trigger Send Method URL was not provided")
    
        if "-SubscriberKey" in args:
            subscriberkey = args[args.index("-SubscriberKey") + 1]
        else:
            raise Exception("Subscriber Key was not provided")
    
        if subscriberkey == "":
            raise Exception("Subscriber Key has blank value")
        
        print("Subcriber Key : " + str(subscriberkey));
        selectsql = "EXEC dbo.usp_GetMCIntegrationDetails @SubscriberKey = ?"
        cursor.execute(selectsql, subscriberkey)
        records = cursor.fetchall()
        print("Total Rows Fetched :", str(len(records)))
        
        for row in records:
            submissionid = str(row[0])
            subscriberkey = str(row[1])
            email = str(row[2])
            brand = str(row[3])
            pubdoctitle = str(row[4])
            pubdocurl = str(row[5])
            productcode = str(row[6])
            
        print("Submission Id : ", str(row[0]))
        print("Subscriber Key : ", str(row[1]))
        print("Email : ", str(row[2]))
        print("Product Code : ", str(row[6]))
        print("Brand Name : ", str(row[3]))
        print("Published Document Title : ", str(row[4]))
        print("Published Document URL : ", str(row[5]))        
        print("\n")
        jsonpayload="{\r\n   \"To\":{\r\n      \"Address\":\"" + str(row[2])  + "\",\r\n      \"SubscriberKey\":\"" + str(row[1])  + "\",\r\n      \"ContactAttributes\":{\r\n         \"SubscriberAttributes\":{\r\n            \"brand\":\"" + str(row[3]) + "\",\r\n            \"pubTitle\":\"" + str(row[4]) + "\",\r\n            \"pubURL\":\"" + str(row[5]) + "\"\r\n            }\r\n        }\r\n    },\r\n    \"Options\": {\r\n        \"RequestType\": \"SYNC\"\r\n    }\r\n}"
        print("JSON Payload : ", str(jsonpayload))

        if (productcode == "None" or productcode == "") :
           raise Exception("Product Code not passed from Paperform Webhook Application Form URL")
        
        if (pubdoctitle == "None" or pubdoctitle == "") :
           raise Exception("Missing / Invalid Product Master Code : " + str(productcode))

        if (brand == "None" or brand == "")  :
           raise Exception("Missing Brand Name")

        if (pubdocurl == "None" or pubdocurl == "") :
           raise Exception("Missing URL")
            
        try:
                print('>>> Authentication Process for Access Token Begin')
                
                urlquerystringpayload='client_id=' + clientid + '&client_secret=' + clientsecret + '&grant_type=' + granttype + '&content_type=application%2Fx-www-form-urlencoded'
                urlquerystringheaders = {'Content-Type': 'application/x-www-form-urlencoded'}
                authresponse = requests.request("POST", authenticationurl, headers=urlquerystringheaders, data=urlquerystringpayload)
                if "200" in str(authresponse):
                    print('>>> Authentication Response : ', str(authresponse))
                else:
                    raise Exception("No Authentication Response")
                authresponse.raise_for_status()

                accesstoken = json.loads(authresponse.text)["access_token"]
                tokentype = json.loads(authresponse.text)["token_type"]
                expiresin = json.loads(authresponse.text)["expires_in"]
                scope = json.loads(authresponse.text)["scope"]
                soapendpoint = json.loads(authresponse.text)["soap_instance_url"]
                baseapiurl = json.loads(authresponse.text)["rest_instance_url"]

                print('Access Token : ' + str(accesstoken))
                print('Token Type: ' + str(tokentype))
                print('Expires In : ' + str(expiresin))
                print('Scope : ' + str(scope))
                print('SOAP End Point URL : ' + str(soapendpoint))
                print('REST API URL : ' + str(baseapiurl))

                print('>>> Authentcation Process for Access Token End')
                
                print(">>> Email Trigger sending Process Begin for Subcriber Key :" , str(subscriberkey))

                authorization = "Bearer " + str(accesstoken)

                emailtriggersenturl = baseapiurl + emailtriggersendmethodurl

                jsonheaders = {'Authorization': authorization , 'Content-Type': 'application/json'}
                emailtriggersentresponse = requests.request("POST", emailtriggersenturl, headers=jsonheaders, data=jsonpayload)
                emailtriggersentresponse.raise_for_status()

                print('Email Trigger Response :' + str(emailtriggersentresponse.text))
                requestid = json.loads(emailtriggersentresponse.text)["requestId"]
                print('Request Id : ' + str(requestid))
                
                if 'recipientSendId' not in json.loads(emailtriggersentresponse.text)["responses"][0]:
                    raise ValueError("No recipientSendId key in Email Trigger Response")
                else:
                    recipientsendid = json.loads(emailtriggersentresponse.text)["responses"][0]["recipientSendId"]
                    print('Recipient Send Id : ' + str(recipientsendid))
                
                if 'hasErrors' not in json.loads(emailtriggersentresponse.text)["responses"][0]:
                    raise ValueError("No hasErrors key in Email Trigger Response")
                else:
                    haserrors = json.loads(emailtriggersentresponse.text)["responses"][0]["hasErrors"]  
                    print('Has Errors : ' + str(haserrors))

                if (str(haserrors) == 'False'):
                    if 'messages' not in json.loads(emailtriggersentresponse.text)["responses"][0]:
                        raise ValueError("No messages key in Email Trigger Response")
                    else:
                        messages = json.loads(emailtriggersentresponse.text)["responses"][0]["messages"][0]               
                        print('Success Message : ' + str(messages))
                else:   
                    if 'messageErrors' not in json.loads(emailtriggersentresponse.text)["responses"][0]:
                        raise ValueError("No messageErrors key in Email Trigger Response")
                    else:
                        messageerrors = json.loads(emailtriggersentresponse.text)["responses"][0]["messageErrors"][0]               
                        print('Failure Message : ' + str(messageerrors))
                
                if (str(haserrors) == 'False'):
                    insertsql = "EXEC dbo.usp_CreateMCIntegrationLog @Action = ?, @SubmissionId = ?, @SubscriberKey = ?, @JsonPayLoad = ?, @AccessToken = ?, @TokenType = ?, @AuthenticationUrl = ?, @SoapInstanceUrl = ?, @RestInstanceUrl = ?, @TriggerSendMethodFullUrl = ?, @RequestId = ?, @RecipientId = ?, @HasErrors = ?, @Status = ?, @MCErrorMessage = ?"
                    cursor.execute(insertsql, 'Email', str(submissionid), str(subscriberkey), str(jsonpayload), str(accesstoken), str(tokentype), str(authenticationurl), str(soapendpoint), str(baseapiurl), str(emailtriggersenturl), str(requestid), str(recipientsendid), '0','Successful', 'Email Trigger Sent Successfully')
                else:
                    insertsql = "EXEC dbo.usp_CreateMCIntegrationLog @Action = ?, @SubmissionId = ?, @SubscriberKey = ?, @JsonPayLoad = ?, @AccessToken = ?, @TokenType = ?, @AuthenticationUrl = ?, @SoapInstanceUrl = ?, @RestInstanceUrl = ?, @TriggerSendMethodFullUrl = ?, @RequestId = ?, @RecipientId = ?, @HasErrors = ?, @Status = ?, @MCErrorMessage = ?"
                    cursor.execute(insertsql, 'Email', str(submissionid), str(subscriberkey), str(jsonpayload), str(accesstoken), str(tokentype), str(authenticationurl), str(soapendpoint), str(baseapiurl), str(emailtriggersenturl), str(requestid), str(recipientsendid), '1','Failed', (str(messages) + str(messageerrors)))
                
                print(">>> Email Trigger sending Process End for Subcriber Key :" , str(subscriberkey))
                conn.commit()
                if (str(haserrors) == 'False'):
                    return 0
                else:
                    return 1
        except pyodbc.Error as ex1:
                    print("Error Message (ex1):", str(ex1))
                    raise ex1
                    return 1     
        except pyodbc.DatabaseError as ex2:
                    print("Database Error Message (ex2):",str(ex2))
                    cursor.rollback()
                    raise ex2
                    return 1
    except Exception as e:
        print("Error Message (e):",str(e))

        insertsql = "EXEC dbo.usp_CreateMCIntegrationLog @Action = ?, @SubmissionId = ?, @SubscriberKey = ?, @JsonPayLoad = ?, @AccessToken = ?, @TokenType = ?, @AuthenticationUrl = ?, @SoapInstanceUrl = ?, @RestInstanceUrl = ?, @TriggerSendMethodFullUrl = ?, @RequestId = ?, @RecipientId = ?, @HasErrors = ?, @Status = ?, @MCErrorMessage = ?"
        cursor.execute(insertsql, 'Email', str(submissionid), str(subscriberkey), str(jsonpayload), str(accesstoken), str(tokentype), str(authenticationurl), str(soapendpoint), str(baseapiurl), str(emailtriggersenturl), str(requestid), str(recipientsendid), '1','Failed', str(e))

        if (conn):
            conn.commit()  

        return 1
    except ValueError as e:
        print("Error Message (e):",str(e))

        insertsql = "EXEC dbo.usp_CreateMCIntegrationLog @Action = ?, @SubmissionId = ?, @SubscriberKey = ?, @JsonPayLoad = ?, @AccessToken = ?, @TokenType = ?, @AuthenticationUrl = ?, @SoapInstanceUrl = ?, @RestInstanceUrl = ?, @TriggerSendMethodFullUrl = ?, @RequestId = ?, @RecipientId = ?, @HasErrors = ?, @Status = ?, @MCErrorMessage = ?"
        cursor.execute(insertsql, 'Email', str(submissionid), str(subscriberkey), str(jsonpayload), str(accesstoken), str(tokentype), str(authenticationurl), str(soapendpoint), str(baseapiurl), str(emailtriggersenturl), str(requestid), str(recipientsendid), '1','Failed', str(e))

        if (conn):
            conn.commit()  

        return 1
    finally:
        if (cursor):
                cursor.close()
                
        if (cursor):        
            del cursor
        
        if (conn):
                conn.close()                    

def main(*args):
    for i, arg in enumerate(sys.argv):
        if (arg == "-ExecutionType"):
            idxexecutiontype = i 

    for i, arg in enumerate(sys.argv):       
           if (i == (idxexecutiontype + 1)):
             executiontype = arg

    if (executiontype == "PaperformWhitepaperEmail"):   
        status = PaperformWhitepaperEmail(sys.argv)
        print("Return/Execution Status : ", str(status))
        return status
        
          
if (__name__ == "__main__"):
      status = main(sys.argv)
      if (status == 1):
        sys.exit(1)
      else:
        sys.exit(0)
    

