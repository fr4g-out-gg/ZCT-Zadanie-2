  # Nastavenie modrej farby pre text
  $host.UI.RawUI.ForegroundColor = "Blue"
  Write-Output "Spustanie aplikacie..."

  docker-compose up -d

  # Nastavenie modrej farby pre bežný text a žltej pre link
  $host.UI.RawUI.ForegroundColor = "Blue"
  Write-Output "Aplikacia je spustena na "
  $host.UI.RawUI.ForegroundColor = "Yellow"
  Write-Output "http://localhost:5000"

  # Reset farby na predvolenú
  $host.UI.RawUI.ForegroundColor = "White"
