$usrin = $args[0];


$path_scenario              = $usrin;
$path_mission_constraints   = ($path_scenario + "/models/astos/Mission_Constraints.xml");
$path_model_data            = ($path_scenario + "/models/astos/Model_Data.xml");
$path_homotopy              = ($path_scenario + "/batch/Model_Data.xml");

# Generate the homotopy file
[xml]$doc = Get-Content $path_homotopy;

$e = $doc.CreateElement("Variable")
$e.SetAttribute("name","mass_payload")
$e.SetAttribute("type","Floating Point Variable")
$e.InnerText = "0";

$doc.Variables.AppendChild($e)
$doc.save($doc)

# Link the mission constraints
[xml]$doc = Get-Content $path_mission_constraints;

$numConstraints = $doc.Mission_Constraints.Constraint.Count;

for ($i = 0; $i -lt $numConstraints; $i++) {
    if ($doc.Mission_Constraints.Constraint.Item($i) -eq "Stage3_Mass_Fuel_Initial")
    {
        $doc.Mission_Constraints.Constraint.Item($i).Vehicle_Mass.Reference
    }


}

$doc.Mission_Constraints.Constraint.Stage3_Mass_Fuel_Initial = 

$doc.save($doc)

# Link the model data
[xml]$doc = Get-Content $path_model_data;


