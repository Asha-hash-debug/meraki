import pandas

def modify_CSVfile(csv_file,first_word,columns):
    data = pandas.read_csv(f"{csv_file}")
    # print(data)

    if csv_file == "Appliance_Lab.csv":
        BranchList = data["BRANCHES"].tolist()
        print(BranchList)

        serialnumbers = data["APPLIANCE"].tolist()
        # print(serialnumbers)

        Device_Names = data["APPLIANCE_NAME"].tolist()


        for i in range(0, len(BranchList)):
            BranchList[i] = f"{first_word}{i + 1}"
        print(BranchList)

        updated_csv = pandas.DataFrame(list(zip(BranchList, serialnumbers,Device_Names)), columns=columns)

        updated_csv.to_csv(f"{csv_file}", index=False)

    else:

        BranchList = data["BRANCHES"].tolist()
        # print(BranchList)

        serialnumbers = data["APPLIANCE"].tolist()
        # print(serialnumbers)

        cameras = data["CAMERA"].tolist()
        # print(cameras)

        wireless = data["WIRELESS"].tolist()
        # print(wireless)

        switch = data["SWITCH"].tolist()
        # print(switch)

        systemsmanager = data["SYSTEMSMANAGER"].tolist()
        # print(systemsmanager)

        for i in range(0, len(BranchList)):
            BranchList[i] = f"{first_word}{i + 1}"
        #print(BranchList)

        updated_csv = pandas.DataFrame(list(zip(BranchList, serialnumbers,cameras,wireless,switch,systemsmanager)), columns=columns)

        updated_csv.to_csv(f"{csv_file}", index=False)


def backtooriginal_CSVfile(csv_file,columns):
    data = pandas.read_csv(f"{csv_file}")
    # print(data)

    if csv_file == "Appliance_Lab.csv":
        BranchList = data["BRANCHES"].tolist()
        # print(BranchList)

        serialnumbers = data["APPLIANCE"].tolist()
        # print(serialnumbers)

        for i in range(0, len(BranchList)):
            BranchList[i] = f"Network{i + 1}"
        # print(BranchList)

        updated_csv = pandas.DataFrame(list(zip(BranchList, serialnumbers)), columns=columns)

        updated_csv.to_csv(f"{csv_file}", index=False)

    else:
        BranchList = data["BRANCHES"].tolist()
        # print(BranchList)

        serialnumbers = data["APPLIANCE"].tolist()
        # print(serialnumbers)

        cameras = data["CAMERA"].tolist()
        # print(cameras)

        wireless = data["WIRELESS"].tolist()
        # print(wireless)

        switch = data["SWITCH"].tolist()
        # print(switch)

        systemsmanager = data["SYSTEMSMANAGER"].tolist()
        # print(systemsmanager)

        for i in range(0, len(BranchList)):
            BranchList[i] = f"Network{i + 1}"
        # print(BranchList)

        updated_csv = pandas.DataFrame(list(zip(BranchList, serialnumbers, cameras, wireless, switch, systemsmanager)),
                                       columns=columns)

        updated_csv.to_csv(f"{csv_file}", index=False)

