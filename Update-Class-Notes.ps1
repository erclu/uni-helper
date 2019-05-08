cd D:\_Programming\uni-helper
pipenv run python notes/organizer.py
Write-Host -NoNewline "Press any key to close..."
$x = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyUp")
