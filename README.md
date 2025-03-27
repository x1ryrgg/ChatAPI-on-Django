# ChatAPI on Django
Chat API

## Main Features:
- JWT authentication.
- Chat with other users using text messages.
- Creation of group chats, extensive functionality within the chat.
- Support full-text search on users, adding friends.
- Notifications for friend requests.

## Installation:
Clone repos
```bash 
git clone https://github.com/x1ryrgg/ChatAPI-on-Django.git
```

You need to activate the venv environment, 
for this we write in the terminal `python -m venv venv`, and then `venv\Scripts\activate`

If nothing happens after the last command, check the permissions 
to execute scripts `Get-ExecutionPolicy` in powershell

If the value is set to 'Restricted', then change it to 'RemoteSigned' 
using the command `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

When the shell vev is activated we download requirements.txt

Install via pip: `pip install -r requirements.txt`

### Configuration
Most configurations are in `settings.py`, others are in backend configurations.

Many settings and their values are hidden in `.env`.

To run Docker, you need to create a `.env` and specify values for the following variables:
``` .env
DB_NAME = chat
DB_USER = postgres
DB_PASSWORD = 1234
DB_HOST = db
DB_PORT = 5432
SECRET_KEY='key'  use django secret key generator 
DEBUG=True

EMAIL_HOST = the email you use
EMAIL_PORT = 2525
EMAIL_HOST_USER = your email
EMAIL_HOST_PASSWORD = smtp password

POSTGRES_NAME=chat
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Docker-compose up 
Build and run containers as daemon 
`docker-compose up --build -d`

### Create superuser

Run command in terminal:
```bash
python manage.py createsuperuser


