for %%i in (*.*) do if not "%%i"=="cleanup_ASTOS.bat" if not "%%i"=="input.tops" if not "%%i"=="scenario_intro.html" del /q "%%i"
RMDIR "reports" /S /Q
RMDIR "integ" /S /Q
RMDIR "gismo" /S /Q
RMDIR "geometry/automatic" /S /Q
del "plot\*.gavc~"
del "model\astos\*.xml~"
