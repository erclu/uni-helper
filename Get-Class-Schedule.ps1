cd $PSScriptRoot
pipenv run python schedule/importer.py -dvu
Write-Host -NoNewline "Press any key to close..."
$x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyUp")
