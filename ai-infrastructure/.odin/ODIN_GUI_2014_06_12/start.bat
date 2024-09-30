@echo off
rem Launch Odin
rem
rem Copyright (c) 2005 by Astos Solutions GmbH
rem $Revision: 53 $, $Date: 2014-03-03 13:19:44 +0100 (Mon, 03 Mar 2014) $


set ODIN_HOME=%~dps0

set JAVA_DIR=%ODIN_HOME%jre\bin\
set ODIN_GUI_DIR=%ODIN_HOME%
set ODIN_LIB=%ODIN_HOME%lib\
set CLASSES=%ODIN_LIB%\ODIN_GUI.jar;
       
rem change to executable folder, otherwise odin gui cannot find odin optimizer
cd %ODIN_HOME%\bin

@start %JAVA_DIR%javaw -XX:+UseParallelGC -Xmx1024m -classpath %CLASSES% de.as.odin.gui.Odin %1 %2

if ERRORLEVEL 1 goto error_occured
goto end_end

:error_occured
echo =======================================================
echo Error %ERRORLEVEL% occured!
echo ODIN_HOME setting is '%ODIN_HOME%'

echo =======================================================
echo Used Java version is:
echo JAVA_DIR setting is '%JAVA_DIR%'
echo on
%JAVA_DIR%java -version
@echo off
echo =======================================================
echo Test, if there is also a default Java version installed:
echo on
java -version
@echo off
echo =======================================================
echo Send this information to service@astos.de

pause

:end_end
endlocal

