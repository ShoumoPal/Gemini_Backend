# Gemini Backend

A complete FastAPI backend implementation that clones Gemini's functionality with authentication, subscriptions, and AI-powered chat capabilities.

## Features

- 🔐 **Authentication System**
  - Mobile number + password authentication
  - OTP-based password reset
  - JWT token-based authorization
  - Refresh token mechanism

- 💬 **Chat System**
  - Create and manage chatrooms
  - Send messages with AI responses
  - Message history and pagination
  - Real-time Gemini AI integration

- 💳 **Subscription Management**
  - Basic and Pro tiers
  - Stripe integration for payments
  - Usage limits and tracking
  - Webhook handling

- 🚀 **Performance Features**
  - Redis caching
  - Background task processing with Celery
  - Rate limiting
  - Database optimization

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Celery** - Background task processing
- **Stripe** - Payment processing
- **Google Gemini API** - AI responses
- **JWT** - Authentication tokens
- **Docker** - Containerization

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd gemini_backend
   cp .env.example .env
   ```

2. **Configure environment variables** in `.env`:
   ```
   DATABASE_URL=postgresql://user:pass@localhost/gemini_db
   REDIS_URL=redis://localhost:6379
   GEMINI_API_KEY=your_gemini_api_key
   STRIPE_SECRET_KEY=sk_test_...
   JWT_SECRET_KEY=your_jwt_secret_key
   ```

3. **Run with Docker**:
   ```bash
   docker-compose up --build
   ```

4. **Install dependencies locally** (optional):
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/send-otp` - Send OTP for password reset
- `POST /auth/verify-otp` - Verify OTP
- `POST /auth/reset-password` - Reset password
- `POST /auth/refresh-token` - Refresh JWT token

### User Management
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update user profile
- `GET /users/usage-stats` - Get usage statistics

### Chatrooms
- `POST /chatrooms/` - Create chatroom
- `GET /chatrooms/` - List user chatrooms
- `GET /chatrooms/{id}` - Get specific chatroom
- `PUT /chatrooms/{id}` - Update chatroom
- `DELETE /chatrooms/{id}` - Delete chatroom
- `POST /chatrooms/{id}/messages` - Send message
- `GET /chatrooms/{id}/messages` - Get messages

### Subscriptions
- `GET /subscriptions/` - Get current subscription
- `POST /subscriptions/create-checkout-session` - Create Stripe checkout
- `POST /subscriptions/cancel` - Cancel subscription
- `POST /subscriptions/webhook` - Stripe webhook handler

## Project Structure

```
gemini_backend/
├── app/
│   ├── api/           # API routes
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   ├── middleware/    # Custom middleware
│   ├── tasks/         # Celery tasks
│   └── utils/         # Helper functions
├── alembic/          # Database migrations
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Usage Limits

- **Basic Tier**: 5 messages per day
- **Pro Tier**: Unlimited messages
- **Rate Limiting**: 5 login attempts per 5 minutes, 3 OTP requests per 5 minutes

## Development

1. **Database migrations**:
   ```bash
   alembic revision --autogenerate -m "Description"
   alembic upgrade head
   ```

2. **Run Celery worker**:
   ```bash
   celery -A app.tasks.gemini_tasks worker --loglevel=info
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

## Production Deployment

1. Configure environment variables properly
2. Set up SSL certificates
3. Configure CORS origins
4. Set up monitoring and logging
5. Configure database backups
6. Set up proper Stripe webhook endpoints

## Security Features

- Password hashing with bcrypt
- JWT token expiration
- Rate limiting on sensitive endpoints
- Input validation and sanitization
- CORS configuration
- Secure webhook verification

# Note
---
Still in progress
