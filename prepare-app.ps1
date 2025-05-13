$host.UI.RawUI.ForegroundColor = "Blue"
Write-Output  "Aplikacia  sa pripravuje..."

docker-compose build

$host.UI.RawUI.ForegroundColor = "Blue"
Write-Output "Aplikacia bola uspesne pripravena."

$host.UI.RawUI.ForegroundColor = "White"
