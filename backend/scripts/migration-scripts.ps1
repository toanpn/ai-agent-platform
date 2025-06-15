# Entity Framework Migration Scripts for Agent Platform

# Add a new migration
function Add-Migration {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name
    )
    Write-Host "Adding migration: $Name" -ForegroundColor Green
    dotnet ef migrations add $Name
}

# Update database with latest migration
function Update-Database {
    Write-Host "Updating database with latest migrations..." -ForegroundColor Green
    dotnet ef database update
}

# Remove last migration
function Remove-LastMigration {
    Write-Host "Removing last migration..." -ForegroundColor Yellow
    dotnet ef migrations remove
}

# Generate SQL script for migrations
function Generate-SqlScript {
    param(
        [string]$OutputFile = "migrations.sql"
    )
    Write-Host "Generating SQL script: $OutputFile" -ForegroundColor Green
    dotnet ef migrations script --output $OutputFile
}

# Drop database (USE WITH CAUTION!)
function Drop-Database {
    Write-Host "WARNING: This will drop the entire database!" -ForegroundColor Red
    $confirmation = Read-Host "Are you sure you want to continue? (type 'yes' to confirm)"
    if ($confirmation -eq 'yes') {
        dotnet ef database drop --force
        Write-Host "Database dropped successfully." -ForegroundColor Red
    } else {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
    }
}

# Show migration history
function Show-Migrations {
    Write-Host "Showing migration history..." -ForegroundColor Green
    dotnet ef migrations list
}

# Show available commands
function Show-Help {
    Write-Host "Available Migration Commands:" -ForegroundColor Cyan
    Write-Host "  Add-Migration <name>        - Add a new migration"
    Write-Host "  Update-Database            - Apply pending migrations"
    Write-Host "  Remove-LastMigration       - Remove the last migration"
    Write-Host "  Generate-SqlScript [file]  - Generate SQL script"
    Write-Host "  Drop-Database              - Drop entire database"
    Write-Host "  Show-Migrations            - Show migration history"
    Write-Host "  Show-Help                  - Show this help"
}

Write-Host "Agent Platform Migration Scripts Loaded!" -ForegroundColor Green
Write-Host "Type 'Show-Help' to see available commands." -ForegroundColor Cyan 