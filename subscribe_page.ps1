$userToken = "EAARru94qAw0BQ21ZCx9wsma1MZCOmeHy8GWkB5tariF62Rp4LmAt0aDs69CxOZBoA56GpOdTKMLIo6SoEXUi4fTaUalNsFvQDpEZBgZBXXoEiL9CA8LAAFatCvPlVSSsHlsNqecyHjVMHTmkNwCQISPIDPBbGXYy2sYNcVRSgiXoRo32rv0Ot8sZB6lKJqU8DwZAhrGSkLqpKZAng9UZCn33wsn1956aZC4RktjV87PmEZD"

Write-Host "1. Getting Page Access Token..."
$resp = (Invoke-WebRequest -Uri "https://graph.facebook.com/v25.0/1044361315419793?fields=access_token&access_token=$userToken" -UseBasicParsing).Content
Write-Host "Response: $resp"

$json = $resp | ConvertFrom-Json
$pageToken = $json.access_token
Write-Host "Page Token (first 30): $($pageToken.Substring(0,30))..."

Write-Host ""
Write-Host "2. Subscribing Page to App..."
try {
    $sub = Invoke-WebRequest -Method POST -Uri "https://graph.facebook.com/v25.0/1044361315419793/subscribed_apps?subscribed_fields=feed,messages&access_token=$pageToken" -UseBasicParsing
    Write-Host "Result: $($sub.Content)"
} catch {
    $err = $_.Exception.Response
    $reader = New-Object System.IO.StreamReader($err.GetResponseStream())
    Write-Host "Error: $($reader.ReadToEnd())"
}
