def list_networks(org_name):
    org_id = match_organizationname(org_name)
    network_list = dashboard.organizations.getOrganizationNetworks(organizationId=org_id)

    network_name = []
    for i in network_list:
        network_name.append(i["name"])

    final_output = []
    for i in network_name:
        list = dashboard.networks.getNetworkDevices(networkId=match_networks(i, org_id))
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


def match_networks(network_name, org_id):
    network_list = dashboard.organizations.getOrganizationNetworks(organizationId=org_id)
    for i in network_list:
        if i["name"] == network_name:
            network_id = i["id"]
            return network_id