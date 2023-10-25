import pandas as pd
import os
import csv


def summary_from_csv(csv_file, output_folder="default/"):

    if os.path.exists(csv_file):
        input_file_name = os.path.splitext(os.path.basename(csv_file))[0]

        if output_folder != "default/":
            output_folder = os.path.dirname(csv_file)
        if not (os.path.exists(output_folder)):

            os.mkdir(output_folder)

        data = pd.read_csv(csv_file)

        devices_list = data.Hostname.unique()
        # loop through individual devices

        with open(output_folder + "/" + input_file_name + "_summary.csv", "w") as output_file:

            for device in devices_list:
                device_df = data[data['Hostname'] == device]
                device_df = device_df.astype({'Inlet Temperature Value': int,
                                              'Outlet Temperature Value': int,
                                              'Hotspot Temperature Value': int})
                max_inlet_temp = device_df[device_df['Inlet Temperature Value']
                                           == device_df['Inlet Temperature Value'].max()]
                max_outlet_temp = device_df[device_df['Outlet Temperature Value']
                                            == device_df['Outlet Temperature Value'].max()]
                max_hotspot_temp = device_df[device_df['Hotspot Temperature Value']
                                             == device_df['Hotspot Temperature Value'].max()]

                writer = csv.writer(output_file, delimiter=',')
                writer.writerow([device + " maximum inlet temperature"])
                max_inlet_temp.to_csv(output_file, index=False)
                writer.writerow([device + " maximum outlet temperature"])
                max_outlet_temp.to_csv(output_file, index=False)
                writer.writerow([device + " maximum hotspot temperature"])
                max_hotspot_temp.to_csv(output_file, index=False)

        with open(output_folder + "/" + input_file_name + "_Inlet_summary.csv", "w") as output_file:

            for device in devices_list:
                device_df = data[data['Hostname'] == device]
                device_df = device_df.astype({'Inlet Temperature Value': int,
                                              'Outlet Temperature Value': int,
                                              'Hotspot Temperature Value': int})

                max_outlet_temp = device_df[device_df['Inlet Temperature Value']
                                            == device_df['Inlet Temperature Value'].max()]

                writer = csv.writer(output_file, delimiter=',')
                writer.writerow([device + " maximum Inlet temperature"])
                max_outlet_temp.to_csv(output_file, index=False)

        with open(output_folder + "/" + input_file_name + "_outlet_summary.csv", "w") as output_file:

            for device in devices_list:
                device_df = data[data['Hostname'] == device]
                device_df = device_df.astype({'Inlet Temperature Value': int,
                                              'Outlet Temperature Value': int,
                                              'Hotspot Temperature Value': int})

                max_outlet_temp = device_df[device_df['Outlet Temperature Value']
                                            == device_df['Outlet Temperature Value'].max()]

                writer = csv.writer(output_file, delimiter=',')
                writer.writerow([device + " maximum outlet temperature"])
                max_outlet_temp.to_csv(output_file, index=False)

        with open(output_folder + "/" + input_file_name + "_hotpost_summary.csv", "w") as output_file:

            for device in devices_list:
                device_df = data[data['Hostname'] == device]
                device_df = device_df.astype({'Inlet Temperature Value': int,
                                              'Outlet Temperature Value': int,
                                              'Hotspot Temperature Value': int})

                max_outlet_temp = device_df[device_df['Hotspot Temperature Value']
                                            == device_df['Hotspot Temperature Value'].max()]

                writer = csv.writer(output_file, delimiter=',')
                writer.writerow([device + " maximum hotspot temperature"])
                max_outlet_temp.to_csv(output_file, index=False)
    else:
        print("Data csv file does not exist.")


input = input("Enter temperature csv: ")
summary_from_csv(input, "summary_output/")
