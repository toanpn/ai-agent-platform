-- Initial database setup for Agent Platform

-- This script runs automatically when the PostgreSQL container starts
-- It creates any necessary extensions and initial data

-- Enable UUID extension if needed in the future
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Sample data will be inserted by the Entity Framework migrations
-- This script is primarily for any database-level configurations

-- Create indexes for better performance
DO $$
BEGIN
    -- Check if tables exist before creating indexes
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'Users') THEN
        CREATE INDEX IF NOT EXISTS idx_users_email ON "Users"("Email");
        CREATE INDEX IF NOT EXISTS idx_users_active ON "Users"("IsActive");
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'Agents') THEN
        CREATE INDEX IF NOT EXISTS idx_agents_department ON "Agents"("Department");
        CREATE INDEX IF NOT EXISTS idx_agents_active ON "Agents"("IsActive");
        CREATE INDEX IF NOT EXISTS idx_agents_created_by ON "Agents"("CreatedById");
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ChatSessions') THEN
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON "ChatSessions"("UserId");
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_created ON "ChatSessions"("CreatedAt");
    END IF;

    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ChatMessages') THEN
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON "ChatMessages"("ChatSessionId");
        CREATE INDEX IF NOT EXISTS idx_chat_messages_created ON "ChatMessages"("CreatedAt");
    END IF;
END $$; 