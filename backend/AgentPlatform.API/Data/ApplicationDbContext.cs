using Microsoft.EntityFrameworkCore;
using AgentPlatform.API.Models;

namespace AgentPlatform.API.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<User> Users { get; set; }
        public DbSet<Agent> Agents { get; set; }
        public DbSet<ChatMessage> ChatMessages { get; set; }
        public DbSet<ChatSession> ChatSessions { get; set; }
        public DbSet<AgentFile> AgentFiles { get; set; }
        public DbSet<AgentFunction> AgentFunctions { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            // User entity configuration
            modelBuilder.Entity<User>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.HasIndex(e => e.Email).IsUnique();
                entity.Property(e => e.Email).IsRequired().HasMaxLength(255);
                entity.Property(e => e.PasswordHash).IsRequired();
                entity.Property(e => e.FirstName).HasMaxLength(100);
                entity.Property(e => e.LastName).HasMaxLength(100);
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETDATE()");
            });

            // Agent entity configuration
            modelBuilder.Entity<Agent>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
                entity.Property(e => e.Department).IsRequired().HasMaxLength(100);
                entity.Property(e => e.Instructions).HasColumnType("nvarchar(max)");
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETDATE()");
                entity.HasOne(e => e.CreatedBy).WithMany().HasForeignKey(e => e.CreatedById)
                    .OnDelete(DeleteBehavior.Restrict);
                entity.HasMany(e => e.Files).WithOne(f => f.Agent).HasForeignKey(f => f.AgentId);
                entity.HasMany(e => e.Functions).WithOne(f => f.Agent).HasForeignKey(f => f.AgentId);
            });

            // ChatSession entity configuration
            modelBuilder.Entity<ChatSession>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETDATE()");
                entity.HasOne(e => e.User).WithMany().HasForeignKey(e => e.UserId);
                entity.HasMany(e => e.Messages).WithOne(m => m.ChatSession).HasForeignKey(m => m.ChatSessionId);
            });

            // ChatMessage entity configuration
            modelBuilder.Entity<ChatMessage>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Content).IsRequired().HasColumnType("nvarchar(max)");
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETDATE()");
                entity.Property(e => e.Role).IsRequired().HasMaxLength(50);
                entity.HasOne(e => e.ChatSession).WithMany(s => s.Messages).HasForeignKey(e => e.ChatSessionId);
            });

            // AgentFile entity configuration
            modelBuilder.Entity<AgentFile>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.FileName).IsRequired().HasMaxLength(500);
                entity.Property(e => e.FilePath).IsRequired().HasMaxLength(1000);
                entity.Property(e => e.ContentType).HasMaxLength(100);
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETDATE()");
                entity.HasOne(e => e.Agent).WithMany(a => a.Files).HasForeignKey(e => e.AgentId);
                entity.HasOne(e => e.UploadedBy).WithMany().HasForeignKey(e => e.UploadedById)
                    .OnDelete(DeleteBehavior.Restrict);
            });

            // AgentFunction entity configuration
            modelBuilder.Entity<AgentFunction>(entity =>
            {
                entity.HasKey(e => e.Id);
                entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
                entity.Property(e => e.Description).HasColumnType("nvarchar(max)");
                entity.Property(e => e.Schema).HasColumnType("nvarchar(max)");
                entity.Property(e => e.EndpointUrl).HasMaxLength(500);
                entity.Property(e => e.CreatedAt).HasDefaultValueSql("GETDATE()");
                entity.HasOne(e => e.Agent).WithMany(a => a.Functions).HasForeignKey(e => e.AgentId);
            });
        }
    }
} 