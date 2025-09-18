# AOI Monitoring System

A professional Django-based backend system for Area of Interest (AOI) monitoring with satellite imagery analysis, payment processing, and real-time notifications.

## Features

- **AOI Management**: Draw, manage, and monitor areas of interest
- **Cart System**: Add AOIs to cart with different monitoring plans
- **Payment Integration**: Stripe and Paystack payment processing
- **Satellite Monitoring**: AI-powered encroachment detection
- **Real-time Notifications**: WebSocket notifications and SMS alerts
- **Order Management**: Complete order processing workflow

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL with PostGIS
- **Task Queue**: Celery with Redis
- **Payments**: Stripe, Paystack
- **WebSockets**: Django Channels
- **Containerization**: Docker & Docker Compose

## Quick Start

1. **Clone and setup:**

```bash
git clone <repository>
cd backend
cp .env.example .env  # Configure your environment variables
```

2. **Start with Docker:**

```bash
docker-compose up -d
```

3. **Run setup script:**

```bash
docker-compose exec web ./scripts/setup.sh
```

4. **Access the API:**

- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

################### API Endpoints #########################################

### Authentication

- `POST /api/auth/users/` - Register
- `POST /api/auth/jwt/create/` - Login

### AOI Management

- `GET /api/aois/` - List AOIs
- `POST /api/aois/` - Create AOI (auto-adds to cart)
- `GET /api/aois/in_cart/` - Get cart AOIs

### Cart & Orders

- `GET /api/cart/` - Get user cart
- `POST /api/cart/add_item/` - Add AOI to cart
- `POST /api/orders/` - Create order from cart
- `GET /api/orders/` - List orders

### Payments

- `POST /api/payments/` - Initialize payment
- `GET /api/payments/pricing/` - Get pricing info

### Notifications

- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/mark_read/` - Mark as read

## Environment Variables

Key variables to configure in `.env`:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgis://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
STRIPE_SECRET_KEY=sk_test_...
PAYSTACK_SECRET_KEY=sk_test_...
TWILIO_AUTH_TOKEN=your-twilio-token
```

## Architecture

- **Models**: AOI, Cart, Order, Payment, Notification, MonitoringJob
- **Services**: Payment processing, cart management, order processing
- **Tasks**: Celery tasks for monitoring and satellite image processing
- **WebSockets**: Real-time notifications via Django Channels

## Development

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run Celery worker
celery -A backend worker --loglevel=info

# Run Celery beat scheduler
celery -A backend beat --loglevel=info
