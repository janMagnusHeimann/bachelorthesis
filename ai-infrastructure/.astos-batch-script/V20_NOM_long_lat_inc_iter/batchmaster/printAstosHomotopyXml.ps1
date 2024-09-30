

function printAstosHomotopyXml($filename)
{
    # Get the user specified XML file content
    $xml = New-Object XML
    [xml]$doc = Get-Content $filename;

    $xmlVarCnt = $doc.Variables.Variable.Count;

    $result = New-Object -TypeName PSObject
    $result | Add-Member -MemberType Noteproperty -Name "Batch Variable" -Value "Value"

    #echo("[INFO] $(Get-Date) > # Parameter `t`t`t Value")
    # Loop over all variables that are in the XML file
    for ($i=0; $i -lt $xmlVarCnt; $i++)
    {
        $varName = $doc.Variables.Variable.Item($i).name;
        $varVal = $doc.Variables.Variable.Item($i).InnerText;

        #echo("[INFO] $(Get-Date) > $i $varName`t`t$varVal")

        $result | Add-Member -MemberType Noteproperty -Name $varName -Value $varVal
    }

    # Print formatted output
    $result | Format-List
}
