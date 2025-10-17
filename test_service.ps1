# Test cases for Python Execution Service

$baseUrl = "http://localhost:8080"

function Invoke-TestCase {
    param (
        [string]$name,
        [string]$script
    )
    Write-Host "`n=== Testing: $name ===" -ForegroundColor Cyan
    Write-Host "Script:`n$script" -ForegroundColor Gray
    
    $body = @{
        script = $script
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/execute" -Method Post -Body $body -ContentType "application/json"
        Write-Host "Response:" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 10
    }
    catch {
        Write-Host "Error Response:" -ForegroundColor Red
        $_.Exception.Response.GetResponseStream().Position = 0
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    }
}

# Test 1: Missing main() function
$script1 = @"
def some_function():
    return {"data": "test"}
"@
Invoke-TestCase -name "Missing main() function" -script $script1

# Test 2: Non-JSON return value
$script2 = @"
def main():
    return set([1, 2, 3])
"@
Invoke-TestCase -name "Non-JSON return value" -script $script2

# Test 3: Dangerous import attempt
$script3 = @"
import os
def main():
    return {"files": os.listdir("/")}
"@
Invoke-TestCase -name "Dangerous import attempt" -script $script3

# Test 4: Resource limit test
$script4 = @"
def main():
    large_list = list(range(100000000))
    return {"data": large_list}
"@
Invoke-TestCase -name "Resource limit test" -script $script4

# Test 5: Basic calculation
$script5 = @"
def main():
    x = 10
    y = 20
    return {"sum": x + y, "product": x * y}
"@
Invoke-TestCase -name "Basic calculation" -script $script5

# Test 6: Pandas DataFrame operations
$script6 = @"
def main():
    import pandas as pd
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    return {
        "mean_A": float(df['A'].mean()),
        "sum_B": float(df['B'].sum())
    }
"@
Invoke-TestCase -name "Pandas DataFrame operations" -script $script6

# Test 7: NumPy computations
$script7 = @"
def main():
    import numpy as np
    arr = np.array([1, 2, 3, 4, 5])
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr))
    }
"@
Invoke-TestCase -name "NumPy computations" -script $script7

# Test health endpoint
Write-Host "`n=== Testing: Health Endpoint ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "Response:" -ForegroundColor Green
    $response | ConvertTo-Json
}
catch {
    Write-Host "Error Response:" -ForegroundColor Red
    $_.Exception.Response.GetResponseStream().Position = 0
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $reader.ReadToEnd()
}