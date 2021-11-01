import meraki
import meraki.exceptions
import requests
import csv
import meraki_automation
import time
import meraki.exceptions
import os
import smtplib
import datetime as dt
import random
from twilio.rest import Client
import certifi
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())

# API_KEY = "9b6b5466f2f02d83c992e865518ea3753594f374"

with open("APIKEY.csv") as apikey:
    key = csv.reader(apikey)
    users=[]
    apikeys=[]
    for row in key:
        if (row[0] != "USERS") and (row[1] != "API_KEY"):
            users.append(row[0])
            apikeys.append(row[1])

username = input("Enter dashboard account email:")
index_match = users.index(f"{username}")
API_KEY = apikeys[index_match]
dashboard = meraki.DashboardAPI(api_key=API_KEY,suppress_logging=True)

is_on = True

lab = input("Select Lab Type:\n1.Appliance Lab\n2.Combined Lab\n")

if lab == "1":
    csv_file = "Appliance_Lab.csv"
    columns = ["BRANCHES", "APPLIANCE"]
else:
    csv_file = "Combined_Lab.csv"
    columns = ["BRANCHES", "APPLIANCE","CAMERA","WIRELESS","SWITCH","SYSTEMSMANAGER"]

while is_on:
    Organization_list = dashboard.organizations.getOrganizations()
    print("\n *****WELCOME TO MERAKI DASHBOARD******* \n")
    print("1.List Organizations \n2.List Networks claimed with Network Devices in Organization \n"
          "3.Create Organization \n4.Delete Organization \n5.Create Network \n6.Delete Network \n"
          "7.Create Template \n8.Delete Template \n9.Claim Device in nework \n10.Delete Device from network \n"
          "11.Monitor Serial numbers\n12.Check Device Status \n13.ADD Admin for Organization \n14.DELETE Admin from Organization\n")
    user_choice = input("Enter your Option: \n ")
    print("\n")

    def code_exit():
        should_exit = input("\npress 'yes' for Continuation or press 'no' for quit\n ")
        if should_exit == "no":
            meraki_automation.backtooriginal_CSVfile(csv_file,columns)
            global is_on
            is_on = False
            return is_on

    def list_organizations():
        for i in Organization_list:
            print(f"{i['name']}")
        print("\n")

    def match_organizationname(org_name):
        for i in Organization_list:
            if i["name"] == org_name:
                org_id = i["id"]
                return org_id

    def list_networks(org_name):
        org_id = match_organizationname(org_name)
        network_list = dashboard.organizations.getOrganizationNetworks(organizationId=org_id)

        network_name = []
        for i in network_list:
            network_name.append(i["name"])

        final_output = []
        for i in network_name:
            list = dashboard.networks.getNetworkDevices(networkId=match_networks(i,org_id))
            for j in list:
                final_output.append(f"* {i} Network contain {j['serial']} device")

        print(f"\nListing Networks in {org_name} Organization: \n")

        if final_output != []:
            for i in final_output:
                print(f"{i}")
            print("\n")
        else:
            for i in network_name:
                print(i)

        return network_list

    def match_networks(network_name,org_id):
        network_list = dashboard.organizations.getOrganizationNetworks(organizationId=org_id)
        for i in network_list:
            if i["name"] == network_name:
                network_id = i["id"]
                return network_id


    def create_organization():
        create_new_org = input("Enter Organization Name which needs to be created :\n")
        dashboard.organizations.createOrganization(name=create_new_org)
        print(f"{create_new_org} Organization has created.\n")


    def delete_organization():
        print("Organization List :\n")
        list_organizations()
        delete_org = input("Enter Organization Name which needs to be deleted from above list :\n")
        org_id = match_organizationname(delete_org)

        delete_org_contains_network = dashboard.organizations.getOrganizationNetworks(organizationId=org_id)

        inventory_device = dashboard.organizations.getOrganizationInventoryDevices(organizationId=org_id)

        if inventory_device != []:
            print(f" WARNING: Deletion of {delete_org} Organization not possible.It contains inventory devices \n")

        elif delete_org_contains_network == []:
            dashboard.organizations.deleteOrganization(organizationId=org_id)
            print(f"{delete_org} Organization has deleted \n")

        else:
            print(f"WARNING : Deletion not possible...{delete_org} Organization contain networks \n")


    def create_network():
        print("Organization List :\n")
        list_organizations()
        org_name = input("Enter Organization Name in which network needs to be created:\n")
        org_id = match_organizationname(org_name)
        type_network = input('1.Create Single Network\n2.Create Bulk Networks\n')

        if type_network == "1":
            try:
                network_name = input("Please provide Name for New Network :\n")
                product_type = input("Please provide product type for New Network:\n")
                dashboard.organizations.createOrganizationNetwork(organizationId=org_id, name=network_name,
                                                                  productTypes=[product_type])
                print(f"{network_name} Network has created inside {org_name} Organization\n")
            except:
                print(f"{network_name} Name already taken")

        else:

            first_word = input("Enter Network Starting Name eg BR:")
            starting_point = int(input("Enter starting number of the range:"))
            ending_point = int(input("Enter ending number of the range:"))

            meraki_automation.modify_CSVfile(csv_file,first_word,columns)

            if starting_point > ending_point:
                print("\n WARNING: starting number should be lesser than ending number\n")
            else:
                for i in range(starting_point, ending_point + 1):
                        if lab == "1":
                            try:
                                dashboard.organizations.createOrganizationNetwork(organizationId=org_id,
                                                                                  name=f"{first_word}{i}",
                                                                                  productTypes=["Appliance"])
                                print(f"\n{first_word}{i} Network has created inside {org_name} Organization\n")
                                with open(f'{csv_file}', 'r') as read_obj:
                                    csv_reader = csv.reader(read_obj)

                                    Network_list = []
                                    for row in csv_reader:
                                        # row variable is a list that represents a row in csv
                                        if (row[0] != "BRANCHES") and (row[1] != "APPLIANCE"):
                                            if row[0] == f"{first_word}{i}":
                                                Network_list = row
                                                # print(Network_list)

                                                for num in Network_list[:]:  # iterate over a shallow copy
                                                    if num == f"{first_word}{i}":
                                                        row.remove(num)
                                                # print(Network_list)

                                                time.sleep(60)

                                                try:
                                                    for serial_num in range(0, len(Network_list)):
                                                        # print(Network_list[serial_num])
                                                        dashboard.networks.claimNetworkDevices(
                                                            networkId=match_networks(f"{first_word}{i}", org_id),
                                                            serials=[Network_list[serial_num]])
                                                        print(
                                                            f"{Network_list[serial_num]} device claimed in to {first_word}{i} Network")

                                                except meraki.exceptions.APIError:
                                                    print(
                                                        f"WARNING: Device with serial {Network_list[serial_num]} is already claimed")
                            except:
                                print(f"{first_word}{i} is already present in organization")

                        else:

                            try:
                                dashboard.organizations.createOrganizationNetwork(organizationId=org_id,
                                                                                  name=f"{first_word}{i}",
                                                                                  productTypes=["Appliance", "camera",
                                                                                                "switch", "systemsManager",
                                                                                               "wireless"])
                                print(f"\n{first_word}{i} Network has created inside {org_name} Organization\n")

                            # except meraki.exceptions.APIError:
                            # print('WARNING: Product Type should be Combined')

                                with open(f'{csv_file}', 'r') as read_obj:
                                    csv_reader = csv.reader(read_obj)

                                    Network_list = []
                                    for row in csv_reader:
                                        # row variable is a list that represents a row in csv
                                        if (row[0] != "BRANCHES") and (row[1] != "APPLIANCE") and (row[2] != "CAMERA") and (
                                                row[3] != "WIRELESS") and (row[4] != "SYSTEMSMANAGER"):

                                            if row[0] == f"{first_word}{i}":
                                                Network_list = row
                                                # print(Network_list)

                                                for num in Network_list[:]:  # iterate over a shallow copy
                                                    if num == "NULL" or num == f"{first_word}{i}":
                                                        row.remove(num)
                                                # print(Network_list)

                                                time.sleep(60)

                                                try:
                                                    for serial_num in range(0, len(Network_list)):
                                                        # print(Network_list[serial_num])
                                                        dashboard.networks.claimNetworkDevices(
                                                            networkId=match_networks(f"{first_word}{i}", org_id),
                                                            serials=[Network_list[serial_num]])
                                                        print(
                                                            f"{Network_list[serial_num]} device claimed in to {first_word}{i} Network")

                                                except meraki.exceptions.APIError:
                                                    print(
                                                         f"WARNING: Device with serial {Network_list[serial_num]} is already claimed")
                            except:
                                print(f"{first_word}{i} is already present in organization")


    def delete_network():
        print("Organization List :\n")
        list_organizations()
        org_name = input("Enter Organization Name from which network needs to be deleted:\n")
        org_id = match_organizationname(org_name)
        list_networks(org_name)

        type_network = input(" SElECT deletion option below:\n1.Delete Single Network\n2.Delete a networks from specific Range \n")

        if type_network == "1":
            network_name = input("Provide Network Name which needs to be deleted from above Network List:\n")

            if network_name == "DC1":
                print("WARNING:DC1 network cannot be deleted")
            else:
                dashboard.networks.deleteNetwork(networkId=match_networks(network_name,org_id))
                print(f"{network_name} Network has deleted from  {org_name} Organization")

        else:
            first_word = input("Enter Network Starting Name:")
            starting_point = int(input("Enter starting number of the range:"))
            ending_point = int(input("Enter ending number of the range:"))

            if starting_point > ending_point:
                print("\n WARNING: starting number should be lesser than ending number\n")
            else:
                for i in range(starting_point, ending_point + 1):
                    try:
                        dashboard.networks.deleteNetwork(networkId=match_networks(f"{first_word}{i}",org_id))
                        print(f"{first_word}{i} network deleted from {org_name} Organization")
                    except meraki.exceptions.APIError:
                        print(f' WARNING: {first_word}{i} network is not present')


    def create_template():
        print("Organization List :\n")
        list_organizations()
        organization_name = input("Enter Organization Name in which Template needs to be created:\n")
        template_name = input("Provide Name for New Template:\n")
        dashboard.organizations.createOrganizationConfigTemplate(organizationId=match_organizationname(organization_name),name=template_name)
        print(f"{template_name} Template has created inside {organization_name} Organization\n")

    def delete_template():
        print("Organization List :\n")
        list_organizations()
        organization_name = input("Enter Organization Name in which Template needs to be deleted:\n")

        template_list = dashboard.organizations.getOrganizationConfigTemplates(organizationId=match_organizationname(organization_name))
        print(f"Template List inside {organization_name} Organization :\n")

        for i in template_list:
            print(i["name"])

        template_name = input("\nSelect Template Name from above list:\n")

        for i in template_list:
            if i["name"] == template_name:
                template_id = i["id"]

        dashboard.organizations.deleteOrganizationConfigTemplate(organizationId=match_organizationname(organization_name),configTemplateId=template_id)
        print(f"{template_name} Template has deleted from {organization_name} Organization\n")


    def claim_device():
        print("Organization List :\n")
        list_organizations()
        organization_name = input("Enter Organization Name of Network where device needs to be claimed:\n")
        list_networks(organization_name)

        network_name = input("Select Network from above List :\n")
        serialnumber = input("Provide Serial number of device :\n")
        dashboard.networks.claimNetworkDevices(networkId=match_networks(network_name,match_organizationname(organization_name)), serials=[serialnumber])
        print(f"{serialnumber} serial number device added to {network_name} Network")


    def delete_device():
        headers = {
            'X-Cisco-Meraki-API-Key': API_KEY,
            'Content-Type': 'application/json'
        }

        print("Organization List :\n")
        list_organizations()

        organization_name = input("Enter Organization Name of Network from where device needs to be deleted.")
        network_list = list_networks(organization_name)

        if network_list == []:
            print(f"\nWARNING: There are no networks present in {organization_name} Organization..so there will be no device connected to network")
        else:

            network_name = input("Select Network from above List :\n")

            network_id = match_networks(network_name,match_organizationname(organization_name))
            print(f"\n List of Serial Numbers Present in {network_name} Network :\n")
            device_list = dashboard.networks.getNetworkDevices(networkId=network_id)
            for i in device_list:
                print(f'{i["serial"]} connected to {network_name} Network')

            if device_list == []:
                print(f"\n WARNING: {network_name} Network has no Network Devices to Delete")

            else:
                serialnumber = input("\nProvide Serial number of device from above List:\n")

                url = f"https://api.meraki.com/api/v0/networks/{network_id}/devices/{serialnumber}/remove"

                # Send request and get response
                response = requests.post(
                    url,
                    headers=headers,
                    verify=False
                )

                print(response)
                print(f"{serialnumber} serial number device has deleted from  {network_name} Network")

    def check_serialnumbers(org_name):

        devicelist = (dashboard.organizations.getOrganizationInventoryDevices(organizationId=match_organizationname(org_name)))
        serialnumberlist = []
        for i in devicelist:
            serialnumberlist.append(i["serial"])

        if lab == "1":

            with open(f'{csv_file}', 'r') as read_obj:
                csv_reader = csv.reader(read_obj)
                Networklist_in_csv = []
                for row in csv_reader:
                    if row[0] != "BRANCHES":
                        Networklist_in_csv.append(row[0])

            with open(f'{csv_file}', 'r') as read_obj:
                csv_reader = csv.reader(read_obj)
                Networkdevice = []
                for row in csv_reader:
                    # row variable is a list that represents a row in csv
                    if (row[0] != "BRANCHES") and (row[1] != "APPLIANCE"):
                        Network_list = row


                        for num in Network_list[:]:  # iterate over a shallow copy

                            if num in Networklist_in_csv:
                                row.remove(num)

                        Networkdevice.extend(Network_list)

        else:

            with open(f'{csv_file}', 'r') as read_obj:
                csv_reader = csv.reader(read_obj)
                Networklist_in_csv = []
                for row in csv_reader:
                    if row[0] != "BRANCHES":
                        Networklist_in_csv.append(row[0])

                Networkdevice = []
                for row in csv_reader:
                    # row variable is a list that represents a row in csv
                    if (row[0] != "BRANCHES") and (row[1] != "APPLIANCE") and (row[2] != "CAMERA") and (row[3] != "WIRELESS") and (row[4] != "SYSTEMSMANAGER"):
                            Network_list = row

                            for num in Network_list[:]:  # iterate over a shallow copy

                                if num == "NULL" or num in Networklist_in_csv:
                                    row.remove(num)

                            Networkdevice.extend(Network_list)


        def non_match_elements(list_a, list_b):
            non_match = []
            for i in list_a:
                if i not in list_b:
                    non_match.append(i)
            return non_match

    # print(Networkdevice)
    # print(serialnumberlist)

        non_match = non_match_elements(Networkdevice, serialnumberlist)

        if non_match != []:

            for i in non_match:

                # ***** MAIL PART ***** #
                with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
                    my_email = "pinkytonny@yahoo.com"
                    password = "glvrafsdohlvhugp"
                    # my_email = "lakshmikn7387@gmail.com"
                    # password = "Ashakn@123"

                    connection.starttls()
                    connection.login(user=my_email, password=password)
                    connection.sendmail(
                        from_addr=my_email,
                        to_addrs=my_email,
                        msg=f"Subject:Meraki-Alert\n\n{i} device is no longer present in {org_name} Organization.")
                    connection.close()

                    #***** SMS PART ****** #

                    # account_sid = "AC9f748df40ba483b8785eb8b8d97b518a"
                    # auth_token = "30db80f0067a83a6f5dc3482f2c97dc4"
                    #
                    # client = Client(account_sid, auth_token)
                    #
                    # message = client.messages \
                    #     .create(
                    #     body=f"MERAKI ALERT :\n {i} device is no longer present in {org_name} Organization",
                    #     from_='+18654194936',
                    #     to='+919845305724'
                    # )
                    #
                    # print(message.status)

                    print(f"{i} device is no longer present in {org_name} Organization.")

            global is_check
            is_check = False
            return is_check


        else:
               try:
                for device_linkedto_network in devicelist:
                    if device_linkedto_network["networkId"] == None:
                        if lab == "1":
                            with open(f"{csv_file}", 'r') as read_obj:
                                csv_reader = csv.reader(read_obj)

                                for row in csv_reader:
                                    if row[1] == device_linkedto_network['serial']:
                                        print(
                                            f'\nWARNING:{device_linkedto_network["serial"]} is not connected to {row[0]} Network\n')
                                        time.sleep(15)

                        else:
                           with open(f"{csv_file}", 'r') as read_obj:
                               csv_reader = csv.reader(read_obj)

                               for row in csv_reader:
                                   if row[1]==device_linkedto_network['serial'] or row[2]==device_linkedto_network['serial'] or row[3]==device_linkedto_network['serial'] or row[4]==device_linkedto_network['serial'] or row[5]==device_linkedto_network['serial']:
                                        print(f'\nWARNING:{device_linkedto_network["serial"]} is not connected to {row[0]} Network\n')
                                        time.sleep(15)

               # is_check = False
               # return is_check

               finally:
                   if non_match == []:
                       print("\nAll network devices are present in Organization Inventory section\n")
                       time.sleep(60)

    def match_networkid(networkId):

        device_name = dashboard.networks.getNetwork(networkId=networkId)
        # print(device_name)
        return device_name["name"]

    def device_status(org_name):

        device_list = dashboard.organizations.getOrganizationDevicesStatuses(organizationId=match_organizationname(org_name))

        if not device_list:
            print(f"There are no network devices present in {org_name} Organization")
        else:
            for device in device_list:
                # print(device)
                if device['status']=="offline" or device['status']=="alerting":
                # ***** MAIL PART ***** #
                    with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
                        my_email = "pinkytonny@yahoo.com"
                        password = "glvrafsdohlvhugp"
                        # my_email = "lakshmikn7387@gmail.com"
                        # password = "Ashakn@123"

                        connection.starttls()
                        connection.login(user=my_email, password=password)
                        connection.sendmail(
                            from_addr=my_email,
                            to_addrs=my_email,
                            msg=f"Subject:Meraki-Alert\n\n{device['serial']} present in {match_networkid(device['networkId'])} Network is {device['status']}")
                        connection.close()

                    print(f"{device['serial']} present in {match_networkid(device['networkId'])} Network is {device['status']}")
                else:
                    print(
                        f"{device['serial']} present in {match_networkid(device['networkId'])} Network is {device['status']}")


    if user_choice == "1":
        print("\nOrganizations List :\n")
        list_organizations()
        code_exit()

    elif user_choice == "2":
        org_name = input("Enter Network's Organization Name : \n")
        list_networks(org_name)
        code_exit()

    elif user_choice == "3":
        create_organization()
        code_exit()

    elif user_choice == "4":
        delete_organization()
        code_exit()

    elif user_choice == "5":
        create_network()
        code_exit()

    elif user_choice == "6":
        delete_network()
        code_exit()

    elif user_choice == "7":
        create_template()
        code_exit()

    elif user_choice == "8":
        delete_template()
        code_exit()

    elif user_choice == "9":
        claim_device()
        code_exit()

    elif user_choice == "10":
        delete_device()
        code_exit()

    elif user_choice == "11":
        org_name = input("Enter Organization name for which inventory devices should be monitored:\n")
        is_check = True
        while is_check:
            check_serialnumbers(org_name)
        is_on = False

    elif user_choice == "12":
        org_name = input("Enter Organization name of which device status needs to be checked:\n")
        device_status(org_name)
        code_exit()

    elif user_choice == "13":
        org_name = input("Enter Organization Name for which admin needs to be added:\n")
        admin_name = input("Enter Admin Name:\n")
        admin_email= input("Enter Admin Email:\n")
        OrganizationPrivilege = input("Organization Privilege? eg: full,read-only,enterprise,none:\n")
        networkaccess = input("want to include network privilege ? yes or no: \n")
        if networkaccess == "yes":
            network_name = input("Enter network Name:\n")
            networkPrivilege = input(f"Network privilege ? eg: full,read-only:\n")
            dashboard.organizations.createOrganizationAdmin(organizationId=match_organizationname(org_name),name=admin_name,email=admin_email,orgAccess=OrganizationPrivilege,networks=[{
            "id": match_networks(network_name,match_organizationname(org_name)),
            "access": networkPrivilege
            }])
            print(f"Email has sent to your {admin_email} check and confirm")
            code_exit()
        else:
            dashboard.organizations.createOrganizationAdmin(organizationId=match_organizationname(org_name),
                                                            name=admin_name, email=admin_email,
                                                            orgAccess=OrganizationPrivilege)
            print(f"\n Email has sent to your {admin_email} check and confirm")
            code_exit()

    else:
            # headers = {
            #     'X-Cisco-Meraki-API-Key': API_KEY,
            #     'Content-Type': 'application/json'
            # }
            # response = requests.get(f"https://api.meraki.com/api/v1/organizations/{match_organizationname('bitvuenetworks.com')}/licenses",headers=headers,verify=False)
            # print(response)
            # print(response.status_code)


            # org_name = input("Enter Organization Name:\n")
            # adminaccounts = dashboard.organizations.getOrganizationAdmins(match_organizationname(org_name))
            # print(f"\n Listing Admin accounts inside {org_name} Organization\n")
            # for account in adminaccounts:
            #     print(f"{account['email']}")
            #
            # deleteadminaccount = input("Select admin account from above list which needs to be deleted:\n")
            #
            # for account in adminaccounts:
            #     if account['email'] == deleteadminaccount:
            #         admin_id = account['id']
            #         dashboard.organizations.deleteOrganizationAdmin(organizationId=match_organizationname(org_name),adminId=admin_id)
            #         print(f"\n{deleteadminaccount} Admin account got deleted from {org_name} Organization")
            #         code_exit()
            #     # else:
            #     #     print(f"{deleteadminaccount} admin account is not listed in {org_name} Organization")
            #     #     code_exit()


