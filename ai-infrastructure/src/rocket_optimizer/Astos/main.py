import subprocess


def Astos():
    # Path to the PowerShell script
    ps1_script_path = "./.astos-batch-script/V20_NOM_long_lat_inc_iter/batchmaster/runBatch.ps1"

    # Command to run the PowerShell script
    command = ["powershell.exe", "-File", ps1_script_path]

    # Run the command and wait for it to complete
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(e.output)
        print("Error:", e.stderr)
        print("Return Code:", e.returncode)
