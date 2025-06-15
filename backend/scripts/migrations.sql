IF OBJECT_ID(N'[__EFMigrationsHistory]') IS NULL
BEGIN
    CREATE TABLE [__EFMigrationsHistory] (
        [MigrationId] nvarchar(150) NOT NULL,
        [ProductVersion] nvarchar(32) NOT NULL,
        CONSTRAINT [PK___EFMigrationsHistory] PRIMARY KEY ([MigrationId])
    );
END;
GO

BEGIN TRANSACTION;
GO

CREATE TABLE [Users] (
    [Id] int NOT NULL IDENTITY,
    [Email] nvarchar(255) NOT NULL,
    [PasswordHash] nvarchar(max) NOT NULL,
    [FirstName] nvarchar(100) NULL,
    [LastName] nvarchar(100) NULL,
    [Department] nvarchar(max) NULL,
    [IsActive] bit NOT NULL,
    [CreatedAt] datetime2 NOT NULL DEFAULT (GETDATE()),
    [UpdatedAt] datetime2 NULL,
    CONSTRAINT [PK_Users] PRIMARY KEY ([Id])
);
GO

CREATE TABLE [Agents] (
    [Id] int NOT NULL IDENTITY,
    [Name] nvarchar(200) NOT NULL,
    [Department] nvarchar(100) NOT NULL,
    [Description] nvarchar(max) NULL,
    [Instructions] nvarchar(max) NULL,
    [IsActive] bit NOT NULL,
    [IsMainRouter] bit NOT NULL,
    [CreatedById] int NOT NULL,
    [CreatedAt] datetime2 NOT NULL DEFAULT (GETDATE()),
    [UpdatedAt] datetime2 NULL,
    CONSTRAINT [PK_Agents] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_Agents_Users_CreatedById] FOREIGN KEY ([CreatedById]) REFERENCES [Users] ([Id]) ON DELETE NO ACTION
);
GO

CREATE TABLE [ChatSessions] (
    [Id] int NOT NULL IDENTITY,
    [UserId] int NOT NULL,
    [Title] nvarchar(max) NULL,
    [IsActive] bit NOT NULL,
    [CreatedAt] datetime2 NOT NULL DEFAULT (GETDATE()),
    [UpdatedAt] datetime2 NULL,
    CONSTRAINT [PK_ChatSessions] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_ChatSessions_Users_UserId] FOREIGN KEY ([UserId]) REFERENCES [Users] ([Id]) ON DELETE CASCADE
);
GO

CREATE TABLE [AgentFiles] (
    [Id] int NOT NULL IDENTITY,
    [AgentId] int NOT NULL,
    [FileName] nvarchar(500) NOT NULL,
    [FilePath] nvarchar(1000) NOT NULL,
    [ContentType] nvarchar(100) NULL,
    [FileSize] bigint NOT NULL,
    [IsIndexed] bit NOT NULL,
    [UploadedById] int NOT NULL,
    [CreatedAt] datetime2 NOT NULL DEFAULT (GETDATE()),
    CONSTRAINT [PK_AgentFiles] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_AgentFiles_Agents_AgentId] FOREIGN KEY ([AgentId]) REFERENCES [Agents] ([Id]) ON DELETE CASCADE,
    CONSTRAINT [FK_AgentFiles_Users_UploadedById] FOREIGN KEY ([UploadedById]) REFERENCES [Users] ([Id]) ON DELETE NO ACTION
);
GO

CREATE TABLE [AgentFunctions] (
    [Id] int NOT NULL IDENTITY,
    [AgentId] int NOT NULL,
    [Name] nvarchar(200) NOT NULL,
    [Description] nvarchar(max) NULL,
    [Schema] nvarchar(max) NULL,
    [EndpointUrl] nvarchar(500) NULL,
    [HttpMethod] nvarchar(max) NULL,
    [Headers] nvarchar(max) NULL,
    [IsActive] bit NOT NULL,
    [CreatedAt] datetime2 NOT NULL DEFAULT (GETDATE()),
    [UpdatedAt] datetime2 NULL,
    CONSTRAINT [PK_AgentFunctions] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_AgentFunctions_Agents_AgentId] FOREIGN KEY ([AgentId]) REFERENCES [Agents] ([Id]) ON DELETE CASCADE
);
GO

CREATE TABLE [ChatMessages] (
    [Id] int NOT NULL IDENTITY,
    [ChatSessionId] int NOT NULL,
    [Content] nvarchar(max) NOT NULL,
    [Role] nvarchar(50) NOT NULL,
    [AgentName] nvarchar(max) NULL,
    [Metadata] nvarchar(max) NULL,
    [CreatedAt] datetime2 NOT NULL DEFAULT (GETDATE()),
    CONSTRAINT [PK_ChatMessages] PRIMARY KEY ([Id]),
    CONSTRAINT [FK_ChatMessages_ChatSessions_ChatSessionId] FOREIGN KEY ([ChatSessionId]) REFERENCES [ChatSessions] ([Id]) ON DELETE CASCADE
);
GO

CREATE INDEX [IX_AgentFiles_AgentId] ON [AgentFiles] ([AgentId]);
GO

CREATE INDEX [IX_AgentFiles_UploadedById] ON [AgentFiles] ([UploadedById]);
GO

CREATE INDEX [IX_AgentFunctions_AgentId] ON [AgentFunctions] ([AgentId]);
GO

CREATE INDEX [IX_Agents_CreatedById] ON [Agents] ([CreatedById]);
GO

CREATE INDEX [IX_ChatMessages_ChatSessionId] ON [ChatMessages] ([ChatSessionId]);
GO

CREATE INDEX [IX_ChatSessions_UserId] ON [ChatSessions] ([UserId]);
GO

CREATE UNIQUE INDEX [IX_Users_Email] ON [Users] ([Email]);
GO

INSERT INTO [__EFMigrationsHistory] ([MigrationId], [ProductVersion])
VALUES (N'20250615064520_InitialCreate', N'8.0.0');
GO

COMMIT;
GO

