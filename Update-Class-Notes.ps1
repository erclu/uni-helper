Set-Location $PSScriptRoot
pipenv run python notes/organizer.py
Write-Host -NoNewline "Press any key to close..."
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyUp")
