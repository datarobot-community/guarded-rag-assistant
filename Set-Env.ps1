# Function to load .env file
function Import-EnvFile {
    if (-not (Test-Path '.env')) {
        Write-Host "Error: .env file not found."
        Write-Host "Please create a .env file with VAR_NAME=value pairs."
        return $false
    }
    Get-Content '.env' | ForEach-Object {
        if ($_ -match '^(\w+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim('"'))
        }
    }
    Write-Host "Environment variables from .env have been set."
    return $true
}

# Function to activate the virtual environment if it exists
function Enable-VirtualEnvironment {
    if (Test-Path '.venv\Scripts\Activate.ps1') {
        Write-Host "Activated virtual environment found at .venv\Scripts\Activate.ps1"
        . '.venv\Scripts\Activate.ps1'
    }
}

# Main execution
Enable-VirtualEnvironment
Import-EnvFile