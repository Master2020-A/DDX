# PowerShell - probar login directamente
$body = @{
    email = "admin@ddx.com"
    password = "Admin123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8612/api/auth/login" -Method POST -Body $body -ContentType "application/json"