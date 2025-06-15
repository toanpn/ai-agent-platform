# Entity Framework Migration Commands for SQL Server

## Initial Setup

After switching from PostgreSQL to SQL Server, you'll need to create new migrations for SQL Server.

### 1. Remove Old Migrations (if any exist)

```bash
# Remove existing migrations folder
rm -rf Migrations/

# Or if you have specific migrations to remove
dotnet ef migrations remove
```

### 2. Add Initial Migration

```bash
# Create initial migration for SQL Server
dotnet ef migrations add InitialCreate

# Review the generated migration files in Migrations/ folder
```

### 3. Update Database

```bash
# Apply migrations to create database schema
dotnet ef database update

# Or specify connection string explicitly
dotnet ef database update --connection "Server=localhost,1433;Database=agentplatform;User Id=sa;Password=YourStrong@Passw0rd;TrustServerCertificate=true;MultipleActiveResultSets=true"
```

## Useful Commands

### Check Migration Status
```bash
# List all migrations
dotnet ef migrations list

# Check which migrations have been applied
dotnet ef migrations has-pending-model-changes
```

### Database Management
```bash
# Drop database (be careful!)
dotnet ef database drop

# Update to specific migration
dotnet ef database update <MigrationName>

# Generate SQL script for migration
dotnet ef migrations script

# Generate SQL script for specific migration range
dotnet ef migrations script <FromMigration> <ToMigration>
```

### Troubleshooting

If you encounter issues:

1. **Ensure SQL Server is running:**
   ```bash
   docker-compose up sqlserver -d
   ```

2. **Test connection:**
   ```bash
   # Test connection using sqlcmd (if available)
   sqlcmd -S localhost,1433 -U sa -P "YourStrong@Passw0rd"
   ```

3. **Check Entity Framework Tools:**
   ```bash
   # Install/update EF tools
   dotnet tool install --global dotnet-ef
   dotnet tool update --global dotnet-ef
   ```

4. **Verify connection string:**
   - Check appsettings.json has correct SQL Server connection string
   - Ensure password meets SQL Server complexity requirements
   - Verify server name and port (localhost,1433)

## Notes

- SQL Server requires strong passwords (8+ chars, mixed case, numbers, symbols)
- Default SQL Server port is 1433
- Use `TrustServerCertificate=true` for local development
- `MultipleActiveResultSets=true` allows multiple active result sets 