# pylint: disable=line-too-long

import sys
import time
import requests
import csv

# vRNI is using a self-signed certificate, so ignore any warnings.
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class Subnet_Create():
    """Main class which holds the DS and functions required for Script Operations"""

    def __init__(self):
        """
        **** Customer needs to set up the below properties before running the script  for first time ****
        self.host : vRNI IP Address
        self.username : username of local account
        self.password : password of local account
        """
        self.verbose = False
        self.delay = 0
        self.host = "10.79.197.111"
        self.username = 'admin@local'
        self.password = 'admin'
        self.token = 'qo5d7yeXf85XTfT22ZunRg=='
        self.token_age = 0


    def create_Authtoken(self):
        """
        Creates an Auth Code which would be used for  API transactions.
        """

        try:
            response = requests.post("https://{}/api/ni/auth/token".format(self.host),
                                     json={'username': self.username, 'password': self.password,
                                           'domain': {'domain_type': 'LOCAL'}}, verify=False)

            print("\n")
            response_json = response.json()
            if response.status_code != 200 or response_json.get('code'):
                print("Error logging into API")
                print(response_json)
                sys.exit(1)
            self.token = response_json.get('token')
            self.token_age = response_json.get('expiry')
        except requests.exceptions.ConnectionError:
            print("Error connecting to {}, connection refused".format(self.host))
            sys.exit(1)



    def token_check(self):
        """
        Checks if the current token in "self.token"  is still valid. Else create a new one
        which would replace the old one.
        """

        i = self.token_age - time.time() * 1000
        if i <= 200:
            print("Creating New token.\n")
            self.create_Authtoken()
            print("###########################################")
            print(" Active token is :",self.token)
            print("Current Token is active for :",(self.token_age - time.time() * 1000)/60000,"minutes")
            print("###########################################")



    def add_subnet(self,entry_list):
        print("************************* SUBNET CREATION **************************")
        token = "NetworkInsight"+" "+ self.token

        req = requests.post("https://{}/api/ni/settings/subnet-mappings".format(self.host),
                            headers={'Authorization': token, 'Content-Type': 'application/json'},
                            json={'cidr': entry_list[0],"vlan_id": entry_list[1]}, verify=False)
        print(entry_list[0],"subnet was added with status", req.status_code)

    def del_subnet(self):
        print("************************* SUBNET DELETION **************************")
        token = "NetworkInsight" + " " + self.token

        req = requests.get("https://{}/api/ni/settings/subnet-mappings".format(self.host),
                            headers={'Authorization': token, 'Content-Type': 'application/json'}, verify=False)
        #print(req.json().get('results'), req.status_code)
        for i in req.json().get('results'):
            #print(i['entity_id'])
            req = requests.delete("https://{}/api/ni/settings/subnet-mappings/{}".format(self.host,i['entity_id']),
                                headers={'Authorization': token, 'Content-Type': 'application/json'},
                                 verify=False)
            print("Subnet",i['cidr'], "got deleted with status", req.status_code)
            print("***********************************")



    def main(self):
        """Starting point for the Script """
        self.host = input("Input the Ip address of vRNI.\n")
        self.username = input("Input the local username to used.\n")
        self.password = input("Input the password to be used..\n")


        targettype = input("Select 2 for Subnet Creation and Select 1 Subnet Deletion.\n")


        if targettype == '1':
            targettype1 = input("You are going to delete all the subnet config in Network Insight. Confirm with input YES ( case sessitive ) \n")
            if targettype1 == 'YES':
                self.token_check()
                self.del_subnet()

        else:
            print("This script adds  Subnet Info to Network Insight from a csv file. Make sure to place the csv file and the script in the same directory.")
            with open('subnet.csv', mode='r') as file:
                # reading the CSV file
                csvFile = csv.reader(file)

                # displaying the contents of the CSV file and also getting the subnet configured in Network Insight
                for lines in csvFile:
                    if (lines[0] == 'subnet'):
                        continue
                    self.token_check()
                    #print(lines)
                    self.add_subnet(lines)


if __name__ == "__main__":
    try:
        Subnet_Create().main()
    except KeyboardInterrupt:
        pass