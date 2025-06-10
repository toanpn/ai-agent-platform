# AI Agent Platform

This repository contains a chatbot UI platform built with Next.js and Supabase for authentication and data storage.

## Project Structure

- `chatbot-ui/`: Frontend application built with Next.js
- `supabase/`: Supabase configuration files
- `backend/`: Backend services

## Setup Instructions

### Prerequisites

- Node.js (v18 or later recommended)
- npm or yarn
- Docker (for local Supabase)
- Supabase CLI

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-agent-platform.git
cd ai-agent-platform
```

#### 2. Set Up Supabase Locally

Install the Supabase CLI:

**MacOS/Linux**
```bash
brew install supabase/tap/supabase
```

**Windows**
```bash
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase
```

Start Supabase:
```bash
supabase start
```

#### 3. Configure Environment Variables

```bash
cd chatbot-ui
cp .env.local.example .env.local
```

Get the required values by running:
```bash
supabase status
```

Fill in the values in your `.env.local` file:
- Use `API URL` from `supabase status` for `NEXT_PUBLIC_SUPABASE_URL`
- Use `anon key` for `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Use `service_role_key` for appropriate variables

#### 4. Configure SQL Setup

In the migration file `supabase/migrations/20240108234540_setup.sql`, update:
- `project_url` (line 53): Should be `http://supabase_kong_chatbotui:8000` by default
- `service_role_key` (line 54): Use the value from `supabase status`

#### 5. Install Dependencies and Run

```bash
cd chatbot-ui
npm install
npm run chat
```

Your local instance should now be running at [http://localhost:3000](http://localhost:3000).

### Production Deployment

#### 1. Create a Supabase Project

Go to [Supabase](https://supabase.com/) and create a new project.

#### 2. Configure Authentication

In the Supabase dashboard:
- Go to Authentication → Providers
- Enable Email provider
- Configure other settings as needed

#### 3. Connect to Hosted Database

Get your project values from the Supabase dashboard:
- Project URL
- Project ID
- Anon key
- Service role key

Link your project:
```bash
supabase login
supabase link --project-ref <project-id>
```

Apply migrations:
```bash
supabase db push
```

#### 4. Deploy Frontend

The chatbot-ui is a Next.js application that can be deployed to platforms like Vercel:

```bash
cd chatbot-ui
npm run build
```

Follow the deployment instructions for your chosen hosting platform (Vercel, Netlify, etc.).

## Features

- Modern chat interface
- Integration with various AI models
- User authentication
- Conversation history storage
- Customizable UI

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.
