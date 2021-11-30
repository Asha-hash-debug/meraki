


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