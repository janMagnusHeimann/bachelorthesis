import csv
from dataclasses import is_dataclass, fields
from rocket_optimizer.DynamicDatabase import AstosOutput, DatabaseOutput, Results


# Function to save dictionary to CSV
def save_dict_to_csv(filename, data_dict):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Writing headers (dictionary keys)
        writer.writerow(data_dict.keys())
        # Writing rows (dictionary values)
        # *data_dict.values() unpacks the lists in the dictionary and zip() combines them into rows
        rows = zip(*data_dict.values())
        writer.writerows(rows)


# Function to save dataclass instance to CSV
def save_dataclass_to_csv(filename, dataclass_type):
    if not is_dataclass(dataclass_type):
        raise ValueError("Provided type is not a dataclass")

    data_dict = {field.name: getattr(dataclass_type, field.name, None) for field in fields(dataclass_type)}

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Writing headers
        writer.writerow(data_dict.keys())
        # Writing data
        writer.writerow(data_dict.values())


def create_csv(fold):

    # Save the dataclasses directly to CSV files
    save_dict_to_csv(fold + '/results_dict.csv', Results._data)  # TODO # does not work
    save_dataclass_to_csv(fold + '/astos_output.csv', AstosOutput)
    save_dataclass_to_csv(fold + '/database_output.csv', DatabaseOutput)
