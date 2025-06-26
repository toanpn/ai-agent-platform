using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AgentPlatform.API.Migrations
{
    /// <inheritdoc />
    public partial class AddToolConfigsToAgent : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "ToolConfigs",
                table: "Agents",
                type: "nvarchar(max)",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "ToolConfigs",
                table: "Agents");
        }
    }
}
