using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using AgentPlatform.API.Data;
using AgentPlatform.API.Services;
using AgentPlatform.API.Middleware;
using AgentPlatform.API.Mapping;
using AgentPlatform.API.Models;
using FluentValidation.AspNetCore;
using FluentValidation;
using System.Text;
using Serilog;
using AspNetCoreRateLimit;
using Microsoft.AspNetCore.Http.Features;
using Microsoft.AspNetCore.Server.Kestrel.Core;
using Microsoft.AspNetCore.Server.IIS;

var builder = WebApplication.CreateBuilder(args);

// Add Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .CreateLogger();

builder.Host.UseSerilog();

// Add services to the container.
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// Add Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
#pragma warning disable CS8604 // Possible null reference argument.
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]))
        };
#pragma warning restore CS8604 // Possible null reference argument.
    });

// Add Rate Limiting
builder.Services.AddMemoryCache();
builder.Services.Configure<IpRateLimitOptions>(builder.Configuration.GetSection("IpRateLimiting"));
builder.Services.AddSingleton<IIpPolicyStore, MemoryCacheIpPolicyStore>();
builder.Services.AddSingleton<IRateLimitCounterStore, MemoryCacheRateLimitCounterStore>();
builder.Services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();
builder.Services.AddSingleton<IProcessingStrategy, AsyncKeyLockProcessingStrategy>();

// Add Configuration Options
builder.Services.Configure<AgentManagementConfig>(builder.Configuration.GetSection(AgentManagementConfig.SectionName));

// Configure file upload limits
builder.Services.Configure<FormOptions>(options =>
{
    // Set the multipart body length limit to 100MB
    options.MultipartBodyLengthLimit = 100 * 1024 * 1024; // 100MB
    // Set the value length limit to 100MB for large file uploads
    options.ValueLengthLimit = 100 * 1024 * 1024; // 100MB
    // Set the value count limit (number of form fields)
    options.ValueCountLimit = 1024;
    // Set the key length limit
    options.KeyLengthLimit = 8192;
    // Buffer body reads
    options.BufferBody = true;
    // Set memory threshold for buffering
    options.MemoryBufferThreshold = 1024 * 1024; // 1MB
});

// Configure Kestrel server limits
builder.Services.Configure<KestrelServerOptions>(options =>
{
    // Set the maximum request body size to 100MB
    options.Limits.MaxRequestBodySize = 100 * 1024 * 1024; // 100MB
    // Set request timeout to 10 minutes for large file uploads
    options.Limits.KeepAliveTimeout = TimeSpan.FromMinutes(10);
    // Set max request header size
    options.Limits.MaxRequestHeadersTotalSize = 32768; // 32KB
});

// Configure IIS Integration (if running under IIS)
builder.Services.Configure<IISServerOptions>(options =>
{
    options.MaxRequestBodySize = 100 * 1024 * 1024; // 100MB
});

// Add HttpClient
builder.Services.AddHttpClient<IAgentRuntimeClient, AgentRuntimeClient>(client =>
{
    // Increase timeout to 10 minutes for long-running agent processing and large file uploads
    client.Timeout = TimeSpan.FromMinutes(10);
    // Set max response content buffer size
    client.MaxResponseContentBufferSize = 100 * 1024 * 1024; // 100MB
});

// Add AutoMapper
builder.Services.AddAutoMapper(typeof(MappingProfile));

// Add FluentValidation
builder.Services.AddFluentValidationAutoValidation();
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

// Add custom services
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IChatService, ChatService>();
builder.Services.AddScoped<IAgentService, AgentService>();
builder.Services.AddScoped<IFileService, FileService>();
builder.Services.AddScoped<IJwtService, JwtService>();
builder.Services.AddSingleton<IToolService, ToolService>();

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "Agent Platform API", Version = "v1" });
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });
    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            new string[] {}
        }
    });
});

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseMiddleware<ErrorHandlingMiddleware>();
app.UseIpRateLimiting();
app.UseCors();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

// Ensure database is migrated
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    context.Database.Migrate();
    
    // Seed database with initial data in development environment
    if (app.Environment.IsDevelopment())
    {
        await DatabaseSeeder.SeedAsync(context);
    }
}

app.Run(); 