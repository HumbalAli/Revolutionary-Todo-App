# Deployment Guide for Todo Application

This guide explains how to deploy the full-stack todo application to production, with the frontend on Vercel and backend on Railway.

## Architecture Overview

The application consists of two main components:
1. **Frontend**: Next.js application (deployed to Vercel)
2. **Backend**: FastAPI application with SQLModel and Neon PostgreSQL (deployed to Railway)

## Prerequisites

Before deployment, you'll need:
- GitHub account
- Vercel account
- Railway account
- Neon PostgreSQL account
- A strong secret key for JWT authentication (at least 32 random characters)

## Deployment Steps

### Step 1: Prepare Your GitHub Repository

1. **Commit your current changes:**
   ```bash
   git add .
   git commit -m "Complete Phase II - Full-stack todo app with authentication"
   ```

2. **Create a new GitHub repository:**
   - Go to https://github.com/
   - Click "New repository"
   - Repository name: `todo-app-fullstack`
   - Description: "Full-stack todo application with Next.js frontend and FastAPI backend"
   - Set to Public
   - Click "Create repository"

3. **Push your code to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/todo-app-fullstack.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Set Up Neon Database

1. **Create Neon account:**
   - Go to https://neon.tech/
   - Sign up with your credentials

2. **Create a new project:**
   - Click "New Project"
   - Choose a project name (e.g., `todo-app-db`)
   - Select your preferred region
   - Click "Create Project"

3. **Get connection string:**
   - In the Neon dashboard, go to your project
   - Click "Connection Details"
   - Copy the connection string (it will look like: `postgresql://username:password@ep-...us-east-1.aws.neon.tech/dbname?sslmode=require`)

### Step 3: Deploy Backend to Railway

1. **Sign up for Railway:**
   - Go to https://railway.app/
   - Sign in with GitHub

2. **Create new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose the `todo-app-fullstack` repository
   - Select the `backend` directory

3. **Configure environment variables:**
   - Click on "Variables" tab
   - Add these variables:
     ```
     DATABASE_URL=your_neon_database_connection_string_from_step_2
     BETTER_AUTH_SECRET=generate_a_strong_random_secret_here
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     DEBUG=False
     ```

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete
   - Note the Railway backend URL (e.g., `https://your-app-name.up.railway.app`)

### Step 4: Deploy Frontend to Vercel

1. **Sign up for Vercel:**
   - Go to https://vercel.com/
   - Sign in with GitHub

2. **Import your project:**
   - Click "New Project"
   - Import the `todo-app-fullstack` repository
   - Select the `frontend` directory

3. **Configure environment variables:**
   - In the "Environment Variables" section, add:
     ```
     NEXT_PUBLIC_API_URL=https://your-railway-backend-url.up.railway.app
     ```
   - Replace `your-railway-backend-url.up.railway.app` with your actual Railway backend URL from Step 3

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete
   - Note the Vercel frontend URL (e.g., `https://your-app-name.vercel.app`)

## Environment Variables Summary

### Backend (Railway):
- `DATABASE_URL`: Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Strong secret key (min 32 chars) - for JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token lifetime in minutes (default: 30)
- `DEBUG`: `False` for production

### Frontend (Vercel):
- `NEXT_PUBLIC_API_URL`: Backend URL (e.g., `https://your-app.up.railway.app`)

## API Communication

Once deployed:
- Frontend makes API calls to the Railway backend URL
- JWT tokens are stored securely in browser storage
- All requests include proper authentication headers
- Error handling manages network failures gracefully

## Database Configuration

### Neon PostgreSQL Setup:
1. Create a new project in Neon
2. Get your connection string
3. Update your application's database URL
4. Enable connection pooling in Neon dashboard if needed
5. Set up proper database user permissions

### Connection Pooling:
The application is configured with proper connection pooling for production:
- Pool size: 10
- Max overflow: 20
- Connection recycling: Every 5 minutes

## Authentication Flow

### User Registration:
1. User submits registration form on frontend
2. Frontend calls `/api/auth/register` on backend
3. Backend creates user in Neon database
4. Backend generates JWT token
5. Frontend stores token in localStorage and user data

### User Login:
1. Existing users are automatically logged in if valid tokens exist
2. Token validation happens via `/api/auth/me` endpoint
3. If token invalid, user is redirected to auth screen

### User Logout:
1. Frontend clears stored tokens and user data
2. User is redirected to authentication screen
3. All sensitive data is removed from browser

## Security Best Practices

### Secrets Management:
- Store `BETTER_AUTH_SECRET` in Railway environment variables
- Never commit secrets to the repository
- Use strong, randomly generated secrets

### HTTPS:
- Both Vercel and Railway provide HTTPS by default
- All API communication uses HTTPS

### Input Validation:
- Backend validates all inputs
- Frontend provides client-side validation
- SQL injection prevention via parameterized queries

## Monitoring and Logging

### Frontend (Vercel):
- Built-in performance monitoring
- Error tracking
- Usage analytics (optional)

### Backend (Railway):
- Real-time logs available in dashboard
- Performance metrics
- Request/response monitoring

## Scaling Considerations

### Database Connection Pooling:
- Proper connection pooling for Neon PostgreSQL
- Monitor connection limits and optimize accordingly

### Caching:
- Consider Redis for session management in high-traffic scenarios
- CDN for static assets (handled by Vercel)

### Load Balancing:
- Vercel handles frontend scaling automatically
- Railway handles backend scaling based on demand

## Troubleshooting

### Common Issues and Solutions:

1. **CORS errors**: Verify that Vercel domain is allowed in backend CORS settings
2. **Database connection timeouts**: Check connection string and pooling settings
3. **Authentication failures**: Ensure tokens are properly configured
4. **API calls failing**: Verify backend URL in frontend environment variables
5. **Slow performance**: Check connection pooling and database indexes

### Debugging Production Issues:
1. Check Railway logs for backend errors
2. Check Vercel logs for frontend errors
3. Verify environment variables are correctly set
4. Test API endpoints directly with tools like curl

## Development vs Production Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| Frontend URL | http://localhost:3000 | https://your-app.vercel.app |
| Backend URL | http://localhost:8003 | https://your-app.up.railway.app |
| Database | Local/Development DB | Production Neon PostgreSQL |
| Authentication | Token-based | Token-based with production secrets |
| Logging | Console logs | Structured logging system |
| Performance | Local machine | Optimized cloud infrastructure |

## Maintenance Tasks

### Regular Maintenance:
1. Monitor database connection usage
2. Review and rotate secrets periodically
3. Update dependencies regularly
4. Monitor application performance

### Backup Strategy:
- Neon provides automatic database backups
- GitHub maintains code version control
- Railway provides deployment history

## Rollback Strategy

### Frontend Rollbacks:
- Vercel provides easy deployment rollback from dashboard
- Multiple deployment previews available

### Backend Rollbacks:
- Railway provides deployment history and rollback options
- Database migrations should be designed to be reversible

This deployment strategy ensures the application works reliably in production while leveraging the benefits of Vercel for frontend hosting and Railway for backend services, with Neon PostgreSQL providing robust database capabilities.