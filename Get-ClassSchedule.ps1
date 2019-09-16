Set-Location $PSScriptRoot
pipenv run python schedule/importer.py -dvu
Write-Host -NoNewline "Press any key to close..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyUp")
