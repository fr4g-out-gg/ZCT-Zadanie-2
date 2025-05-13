$host.UI.RawUI.ForegroundColor = "Blue"

Write-Output  "Zastavenie aplikacie..."
docker-compose down
$host.UI.RawUI.ForegroundColor = "Blue"
Write-Output  "Aplikacia bola uspesne zastavena."

$host.UI.RawUI.ForegroundColor = "White"
