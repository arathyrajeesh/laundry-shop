# Laundry Shop Management System

A comprehensive Django-based laundry shop management system with user authentication, shop management, order tracking, and payment integration.

## Features

- **User Management**: Customer registration and authentication
- **Shop Management**: Multi-shop support with branch management
- **Order Management**: Complete order lifecycle from placement to delivery
- **Payment Integration**: Razorpay payment gateway
- **Admin Dashboard**: Comprehensive analytics and management tools
- **Email Notifications**: Automated email notifications for orders and updates
- **Location Services**: GPS-based location detection for better service

## Installation

### Prerequisites

- Python 3.8+
- Git
- A GitHub account

### Setup Instructions

1. **Clone the repository** (skip if you already have the code):
   ```bash
   git clone https://github.com/your-username/laundry-shop.git
   cd laundry-shop
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r laundry_shop/requirements.txt
   ```

4. **Environment Configuration**:
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit the .env file with your actual credentials
   nano .env  # or use any text editor
   ```

   Fill in your actual values in the `.env` file:
   ```env
   SECRET_KEY=your-actual-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com

   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-gmail-app-password

   RAZORPAY_KEY_ID=your-razorpay-key-id
   RAZORPAY_KEY_SECRET=your-razorpay-key-secret
   ```

5. **Database Setup**:
   ```bash
   cd laundry_shop
   python manage.py migrate
   ```

6. **Create Superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000` in your browser.

## Security Setup for GitHub

### Important: Never commit secrets!

1. **Create `.env` file**: Copy `.env.example` to `.env` and fill with real values
2. **Check `.gitignore`**: Ensure sensitive files are excluded from Git
3. **Generate new SECRET_KEY**: Use Django's secret key generator for production

### Getting Gmail App Password

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → App passwords
4. Generate a new app password for "Mail"
5. Use this 16-character password in your `.env` file

### Getting Razorpay Keys

1. Sign up at [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Go to Settings → API Keys
3. Copy your Key ID and Key Secret
4. Add them to your `.env` file

## Deployment

### For Production Deployment:

1. Set `DEBUG=False` in your `.env` file
2. Update `ALLOWED_HOSTS` with your domain
3. Use a production database (PostgreSQL recommended)
4. Set up proper static files serving
5. Configure HTTPS

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `your-secret-key` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated domains | `example.com,www.example.com` |
| `EMAIL_HOST_USER` | Gmail address | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Gmail app password | `16-char-password` |
| `RAZORPAY_KEY_ID` | Razorpay Key ID | `rzp_test_xxx` |
| `RAZORPAY_KEY_SECRET` | Razorpay Secret | `your-secret` |

## Project Structure

```
laundry-shop/
├── laundry_shop/          # Main Django project
│   ├── laundry_shop/      # Project settings
│   ├── shop/             # Main app
│   ├── media/            # User uploaded files
│   └── static/           # Static files
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── requirements.txt     # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@your-laundry-app.com or create an issue in this repository.

---

**⚠️ Security Note**: Always keep your `.env` file private and never commit it to version control. The `.gitignore` file is configured to automatically exclude sensitive files.