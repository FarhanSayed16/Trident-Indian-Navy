# Database Setup Script for TRIDENT Project (PowerShell)
# This script helps set up the database for local PostgreSQL installation on Windows

Write-Host "TRIDENT Database Setup Script" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is installed
try {
    $psqlVersion = psql --version 2>&1
    Write-Host "PostgreSQL found: $psqlVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: PostgreSQL (psql) is not installed." -ForegroundColor Red
    Write-Host "Please install PostgreSQL first." -ForegroundColor Yellow
    Write-Host "See docs/setup/POSTGRESQL_SETUP_GUIDE.md for instructions." -ForegroundColor Yellow
    exit 1
}

# Database configuration
$DB_NAME = "trident_db"
$DB_USER = "trident_user"
$DB_PASSWORD = "trident_password"

Write-Host "Creating database and user..." -ForegroundColor Yellow
Write-Host "Database: $DB_NAME"
Write-Host "User: $DB_USER"
Write-Host ""

# Prompt for postgres password
$postgresPassword = Read-Host "Enter PostgreSQL 'postgres' user password" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword)
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Set PGPASSWORD environment variable
$env:PGPASSWORD = $plainPassword

try {
    # Create database
    Write-Host "Creating database..." -ForegroundColor Yellow
    psql -U postgres -c "CREATE DATABASE $DB_NAME;" 2>&1 | Out-Null
    Write-Host "Database created (or already exists)" -ForegroundColor Green
} catch {
    Write-Host "Note: Database may already exist" -ForegroundColor Yellow
}

try {
    # Create user
    Write-Host "Creating user..." -ForegroundColor Yellow
    psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>&1 | Out-Null
    Write-Host "User created (or already exists)" -ForegroundColor Green
} catch {
    Write-Host "Note: User may already exist" -ForegroundColor Yellow
}

# Grant privileges
Write-Host "Granting privileges..." -ForegroundColor Yellow
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
psql -U postgres -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

Write-Host ""
Write-Host "Database setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update .env file with database credentials"
Write-Host "2. Run migrations: cd backend; alembic upgrade head"
Write-Host ""

# Clear password from memory
$env:PGPASSWORD = ""

