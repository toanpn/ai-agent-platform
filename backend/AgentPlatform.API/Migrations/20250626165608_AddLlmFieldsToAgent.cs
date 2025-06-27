using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AgentPlatform.API.Migrations
{
    /// <inheritdoc />
    public partial class AddLlmFieldsToAgent : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "LlmModelName",
                table: "Agents",
                type: "nvarchar(max)",
                nullable: true);

            migrationBuilder.AddColumn<double>(
                name: "LlmTemperature",
                table: "Agents",
                type: "float",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Tools",
                table: "Agents",
                type: "nvarchar(max)",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "LlmModelName",
                table: "Agents");

            migrationBuilder.DropColumn(
                name: "LlmTemperature",
                table: "Agents");

            migrationBuilder.DropColumn(
                name: "Tools",
                table: "Agents");
        }
    }
}
