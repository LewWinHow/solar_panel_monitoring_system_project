# Solar Panel Monitoring System

A Django web application for managing solar panel installations, viewing incoming inspection data, detecting visible panel conditions with YOLO, and reviewing historical records and monthly reports.

## Features

- **User accounts:** Registration, login, logout, password recovery by email verification, profile management, and role-based access for administrators, staff, and regular users.
- **Panel management:** Create and edit panel entries with zone, position, and active status. Search and filter panel information and inspection records.
- **Monitoring:** View the latest status of active panels grouped by zone, including damage and cleanliness summaries.
- **AI inspection:** Run YOLO detection on uploaded images for damage, clean, dusty, and bird-dropping conditions. Annotated results are saved under `media/detect_solar_panel_result/`.
- **Inspection history:** Store panel status snapshots with images and timestamps, then browse and filter historical records.
- **Reports:** View monthly panel and login reports and render them as PDFs.
- **Login protection:** Record login attempts and client details, identify likely bots, count failed attempts, and block blacklisted IP addresses through middleware.

## Main Components

- `login/` — authentication, password recovery, login history, IP blacklist, and login reports
- `user/` — custom user model, registration, profiles, and user administration
- `solar_panel/` — panel inventory, monitoring snapshots, inspection history, and solar panel reports
- `ai_model/detect_solar_panel_model/` — YOLO image detection helper and model weights
- `utils/` — validation, pagination, PDF generation, email delivery, and monthly report helpers
- `templates/` and `static/` — Django pages and styles
- `my_middleware/` — IP blacklist checks for incoming requests
- `media/` — uploaded profiles and generated inspection images
- `db.sqlite3` — local SQLite database

## Test Account

For local testing:

- Username: `test`
- Password: `(Test123)`
## Requirements

The project uses Django 5.2 and SQLite by default. Detection and report features also rely on packages such as Ultralytics, PyTorch, OpenCV, NumPy, Pillow, ReportLab, `getmac`, and `user-agents`. Install package versions compatible with your Python and CUDA setup; the repository does not include a dependency lock file.

The image detector currently contains machine-specific paths for the YOLO weights and media output directory; update these paths for your environment before using image detection.

## Run Locally

From the project directory, create and activate a virtual environment, install Django and the packages required by the features you plan to run, then apply migrations and start the server:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install "Django>=5.2,<5.3" ultralytics opencv-python numpy Pillow reportlab getmac user-agents
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Open `http://127.0.0.1:8000/`. The application uses the SQLite database at `db.sqlite3`; create an administrator account with `python manage.py createsuperuser` if needed. Image detection requires the model file at the path configured in the detector code. GPU use depends on a compatible PyTorch/CUDA installation; image detection currently defaults to CUDA.

## Application Paths

The project is a Django template application. Common paths include:

- `/login/`, `/logout/`, `/register/` — account access
- `/forgot_password/`, `/verify_code/`, `/reset_password/` — password recovery
- `/solar_panel_info/` — panel inventory
- `/solar_panel_monitoring/` — latest monitoring dashboard
- `/solar_panel_record/` — inspection history
- `/solar_panel_report/` and `/login_report/` — monthly reports
- `/receive_solar_panel/` — inspection data receiver used by the application integration

Most management, monitoring, record, and report pages require a signed-in user. Panel and user administration actions are restricted by role in the views.

## Configuration Notes

- The configured media root is the project `media/` directory. Ensure the server process can write to it.
- Configure a valid SMTP account for password recovery and report email features. Email settings are currently stored in `settings.py` and should be moved to environment variables before deployment.
- The repository currently contains development-only Django security settings and machine-specific paths. Set a private `SECRET_KEY`, disable `DEBUG`, configure `ALLOWED_HOSTS` and CSRF trusted origins, and review the server binding before deployment.
- Monthly report generation is implemented in `utils/auto_generate_report.py` as a script; it is not configured as a Django scheduled task.
- The image detector uses the class labels returned by the YOLO model. Confirm the model labels and configured paths match your installation.

## Reports

The application can display and generate PDF files for solar panel and login monthly reports. The helper in `utils/auto_generate_report.py` aggregates the previous period, creates report records, renders PDFs, and emails them. Configure the email account and run it through an appropriate scheduler if automatic monthly delivery is required.

## Security

Do not commit real passwords, SMTP credentials, or production secret keys. The checked-in settings include sensitive-looking configuration values and permissive development settings; rotate any credentials that have been exposed and load secrets from environment variables. Review access controls, CSRF settings, upload validation, and deployment settings before exposing the application publicly.



