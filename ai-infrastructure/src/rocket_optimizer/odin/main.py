import os
import subprocess

exe_path = "./.odin/script/odin.exe"


# Function to run odin with an input file and output file
def odin(input_folder, output_folder):
    print("Odin is running...")

    # Ensure the input and output directories exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    input_files = []
    output_files = []

    # Scan the input folder and list files
    with os.scandir(input_folder) as entries:
        for entry in entries:
            if not entry.is_dir():  # Ensure it is not a directory
                input_files.append(entry.path)  # Append the full path

    # Scan the output folder and list files
    with os.scandir(output_folder) as entries:
        for entry in entries:
            if not entry.is_dir():  # Ensure it is not a directory
                output_files.append(entry.path)  # Append the full path

    # Ensure that there are an equal number of input and output files
    if input_files and output_files and len(input_files) == len(output_files):
        for input_file, output_file in zip(input_files, output_files):
            # Construct the command for each file pair
            command = [exe_path, "-if", input_file, "-of", output_file]

            # Execute the command
            process = subprocess.run(command, text=True, capture_output=True)
            print(f"Command: {' '.join(command)}")
            if process.stderr:
                print("Error:", process.stderr)
            print("Output:", process.stdout)
    else:
        print("Mismatch in number of input" +
              "and output files, or no files found.")
