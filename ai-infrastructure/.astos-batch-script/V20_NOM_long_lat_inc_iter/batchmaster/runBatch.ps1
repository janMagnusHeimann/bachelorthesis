###################################################################
# Custom ASTOS batch script
#  This script allows the user to generate a batch of trajectories
#  with ASTOS.
###################################################################

# Include scripts
. '.\.astos-batch-script\V20_NOM_long_lat_inc_iter\batchmaster\printAstosHomotopyXml.ps1'
#Import-Module ./printAstosHomotopyXml.ps1

function main() {
    Write-Output ("[INFO] $(Get-Date) Executing custom ASTOS batch mode.")         # Show in console

    # Get the current directory
    [String]$currentDir = (Get-Location).Path;
    Write-Output ("[INFO] $(Get-Date) Current directory is: $currentDir")          # Print current directory

    # Define ASTOS location 
    [String]$path_astos = "C:\Program Files\Astos Solutions\ASTOS 9.10\"

    # Define input and output file locations relative to current directory
    [String]$path_infiles = "$currentDir\.astos-batch-script\V20_NOM_long_lat_inc_iter\batchmaster\inFiles\";
    [String]$path_outfiles = "$currentDir\.astos-batch-script\V20_NOM_long_lat_inc_iter\batchmaster\outFiles";

    ## Initialize folder structure and iteration
    $numInFiles = (Get-ChildItem $path_infiles | Measure-Object).Count;            # Get list of input homotopy files
    Write-Output ("[INFO] $(Get-Date) Found " + $numInFiles + " homotopy files.")  # Write list of input homotopy files in console

    # Get the list of homotopy files and find the one with the highest number
    $homotopyFiles = Get-ChildItem -Path $path_infiles -Filter "homotopy_*.xml"
    $maxIndexFile = $homotopyFiles | Sort-Object { [int]($_.BaseName -replace 'homotopy_', '') } | Select-Object -Last 1

    # Check if a homotopy file was found
    if ($maxIndexFile -ne $null) {
        Write-Output ("[INFO] $(Get-Date) Running ASTOS optimization " + $maxIndexFile + ".")

        $fileIndex = [int]($maxIndexFile.BaseName -replace 'homotopy_', '')

        # Get the file with '0_' as the prefix from the path_outfiles folder
        [String]$fileZero = Get-ChildItem "$path_outfiles\0_*" -Directory | Select-Object -First 1

        # Extract the scenario name from the file name
        if ($fileZero -ne $null) {
            [String]$name_scenario = $fileZero -replace '^.*\\0_',''
            Write-Output ("[INFO] $(Get-Date) Scenario file found: $name_scenario.")
        } else {
            Write-Output ("[ERROR] $(Get-Date) No scenario file starting with '0_' found in $path_outfiles.")
            exit 1
        }

        # Generate the full file names
        [String]$file_scenario_old = "$path_outfiles\" + ($fileIndex - 1) +"_$name_scenario";
        [String]$file_scenario = "$path_outfiles\$fileIndex"+"_$name_scenario";        # Pointing to the initial gtp
        [String]$arg_scenario = "-scenario:$file_scenario";                            #
        [String]$file_homotopy = "$file_scenario\batch\homotopy.xml";                  # Pointing to the homotopy of the initial .gtp
        [String]$file_summary = "$path_scenario$name_scenario\result_summary.dat";     # Pointing to results => .dat
        [String]$path_exports = "$file_scenario\exports\"
        [String]$path_reports = "$file_scenario\reports\"

        # Make a copy of the last available gtp in outFiles
        Copy-Item -Path $file_scenario_old -Destination $file_scenario -Recurse

        # Get the maximum index from files in the $path_outfiles folder
        [Int]$maxFileIndex = Get-ChildItem "$path_outfiles\*_*.gtp" |
            ForEach-Object { $_.Name -replace '_.*', '' } |
            Sort-Object { [int]$_ } |
            Select-Object -Last 1

        # Compare the maximum index with the file index from $maxIndexFile
        if ($maxFileIndex -ne $fileIndex) {
            Write-Output ("[ERROR] $(Get-Date) The maximum index in $path_outfiles ($maxFileIndex) does not match the file index from $maxIndexFile ($fileIndex).")
            exit 1
        } else {
            Write-Output ("[INFO] $(Get-Date) Maximum index in $path_outfiles matches the file index from $maxIndexFile.")
        }

        # Remove exports of initial gtp file in batchmaster
        if (Test-Path $path_exports) {
            Remove-Item $path_exports -Recurse -Force;
        }
        New-Item -Path $path_exports -ItemType Directory | Out-Null;

        # Remove reports of initial gtp file in batchmaster
        if (Test-Path $path_reports) {
            Remove-Item $path_reports -Recurse -Force;
        }
        New-Item -Path $path_reports -ItemType Directory | Out-Null;

        # Remove summary of initial gtp file in batchmaster
        if (Test-Path $file_summary) {
            Remove-Item $file_summary -Force;
        }

        # Go to ASTOS directory but remember the current one
        $oldPath = Get-Location;
        Set-Location $path_astos;

        # Make homotopy file available for astos: copy the homotopy file to initial gtp
        Copy-Item -Path $maxIndexFile.FullName -Destination $file_homotopy

        # Iterate over the highest indexed input file
        Write-Output ("[INFO] $(Get-Date) Running ASTOS optimization " + $fileIndex + ".")
        printAstosHomotopyXml $file_homotopy                   # Show homotopy file parameters in console
        .\start.bat $arg_scenario -optimize | Out-Null         # Optimize
        Write-Output ("[INFO] $(Get-Date) Optimization finished. Generating output files.")
        .\start.bat $arg_scenario -exports | Out-Null          # Create export
        .\start.bat $arg_scenario -reports | Out-Null          # Create report

        # Reduce output size
        Set-Location $file_scenario
        .\cleanup_ASTOS.bat | Out-Null

        # Restore previous path
        Set-Location $oldPath
        Write-Output ("[INFO] $(Get-Date) Optimization done. End of program.")
    } else {
        Write-Output ("[ERROR] $(Get-Date) No homotopy files found in the directory.")
        # Restore previous path
        Set-Location $oldPath
        exit 1
    }
}

# Execute main function
$oldPath = Get-Location;
main;
Set-Location $oldPath;