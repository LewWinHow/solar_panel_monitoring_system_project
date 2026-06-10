# Solar Panel Monitoring System

## Overview
This is a Django-based web application for monitoring solar panels. The system provides features for user management, solar panel tracking, AI-powered damage detection, and comprehensive reporting capabilities.

## Features
- **User Management**: Registration, authentication, and role-based access control
- **Solar Panel Monitoring**: Real-time monitoring of solar panel status
- **AI Detection**: Image and video-based solar panel damage detection using YOLO model
- **Reporting**: Automated monthly reports for login activities and solar panel status
- **Security**: IP blacklisting, bot detection, and brute force protection
- **Email Integration**: Password reset via email verification

## Technology Stack
- **Backend**: Django 5.2.1
- **Database**: SQLite (default), MySQL support available
- **Frontend**: HTML/CSS/JavaScript with Django templates
- **AI Model**: YOLO-based solar panel detection model
- **PDF Generation**: ReportLab for PDF report generation
- **Email**: SMTP integration for password reset functionality

## Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd solar_panel_monitoring_system_project
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django
   pip install reportlab
   pip install getmac
   pip install user-agents
   pip install Pillow
   # Add other required packages as needed
   ```

4. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

## Supervisor Login Credentials

For administrative access, you can use the following supervisor account:

- **Username**: `lewwinhow`
- **Password**: `(XiaoHao6070)`

⚠️ **Security Note**: Please change these default credentials after first login in production environments.

## Project Structure

```
solar_panel_monitoring_system_project/
├── ai_model/                 # AI detection models
│   └── detect_solar_panel_model/
├── login/                    # Authentication module
├── solar_panel/              # Solar panel management
├── user/                     # User management
├── utils/                    # Utility functions
├── my_middleware/            # Custom middleware
├── templates/                # HTML templates
├── static/                   # Static files (CSS, JS)
├── media/                    # Uploaded files and detection results
├── solar_panel_monitoring_system_project/  # Main project settings
├── manage.py                 # Django management script
└── db.sqlite3                # SQLite database
```

## Key Modules

### 1. Authentication System (`login/`)
- User login/logout functionality
- Password reset with email verification
- Login attempt tracking and IP blacklisting
- Bot detection and prevention

### 2. User Management (`user/`)
- User registration and profile management
- Role-based permissions (superuser, staff, regular user)
- User list with filtering and pagination

### 3. Solar Panel Management (`solar_panel/`)
- Solar panel information management
- Real-time monitoring dashboard
- Damage and cleanliness detection
- Historical records and reporting

### 4. AI Detection (`ai_model/`)
- Image-based solar panel defect detection
- Video processing for continuous monitoring
- Results storage and visualization

## API Endpoints

### Authentication
- `POST /login/` - User login
- `GET /logout/` - User logout
- `POST /forgot_password/` - Request password reset
- `POST /verification_code/` - Verify reset code
- `POST /reset_password/` - Reset password

### Solar Panel
- `GET /solar_panel_info/` - View solar panel information
- `POST /add_solar_panel/` - Add new solar panel
- `POST /edit_solar_panel/<id>/` - Edit solar panel details
- `GET /delete_solar_panel/<id>/` - Delete solar panel
- `GET /monitoring/` - Real-time monitoring dashboard

### Reports
- `GET /login_report/` - View login reports
- `GET /solar_panel_report/` - View solar panel reports
- `GET /login_report_pdf/<id>/` - Download login report as PDF
- `GET /solar_panel_report_pdf/<id>/` - Download solar panel report as PDF

## Configuration

### Email Settings
The system uses Gmail SMTP for email functionality. Update the following in `settings.py`:
```python
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_app_password"
```

### Database Configuration
By default, the system uses SQLite. To use MySQL, uncomment the MySQL configuration in `settings.py` and update the connection parameters.

### Allowed Hosts
Update `ALLOWED_HOSTS` in `settings.py` for production deployment:
```python
ALLOWED_HOSTS = ["your-domain.com", "localhost", "127.0.0.1"]
```

## Security Features

- **IP Blacklisting**: Automatic blocking of suspicious IP addresses
- **Brute Force Protection**: Account lockout after multiple failed login attempts
- **Bot Detection**: Identification and blocking of automated bots
- **CSRF Protection**: Built-in Django CSRF protection
- **Session Management**: Secure session handling with configurable timeout

## Reporting System

The system automatically generates monthly reports for:
- Login activities (successful/failed attempts, blacklisted IPs)
- Solar panel status (damage, cleanliness, maintenance needs)

Reports can be viewed online or downloaded as PDF files.

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## Deployment

For production deployment, consider:
1. Using a production-ready WSGI server (e.g., Gunicorn, uWSGI)
2. Setting up a reverse proxy (e.g., Nginx)
3. Using a production database (e.g., PostgreSQL, MySQL)
4. Enabling HTTPS
5. Setting `DEBUG = False` in settings.py
6. Configuring proper logging

## Troubleshooting

### Common Issues

1. **Database errors**: Ensure database migrations are up to date
2. **Static files not loading**: Run `collectstatic` command
3. **Email not sending**: Check SMTP configuration and app passwords
4. **AI model errors**: Verify model files exist in the correct directory

### Logs
Check Django logs for detailed error information:
```bash
python manage.py runserver --verbosity 2
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the system administrator or create an issue in the repository.

---

**Note**: This system is designed for educational and monitoring purposes. Always ensure compliance with local regulations when deploying surveillance systems.