# StockSphere - Multi-Account Trading Platform

A full-stack trading platform that supports multiple broker accounts (Zerodha & 5paisa) with automated login, account management, and user authentication.

## 🚀 Features

- **Multi-Broker Support**: Manage Zerodha and 5paisa accounts
- **Automated Login**: Background authentication for broker accounts using TOTP
- **User Management**: Secure JWT-based authentication
- **Account Validation**: Test broker credentials before saving
- **Real-time Updates**: Background tasks for session management
- **Secure Storage**: Encrypted credential storage in PostgreSQL

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.9 or higher) - [Download](https://www.python.org/)
- **PostgreSQL** (v13 or higher) - [Download](https://www.postgresql.org/)
- **Git** - [Download](https://git-scm.com/)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/StockSphere.git
cd StockSphere
```

### 2. Database Setup

Create a PostgreSQL database:

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE trading_db;

# Exit PostgreSQL
\q
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_auth.txt

# Create .env file
# Copy the example below and update with your values
```

**Create `backend/.env` file:**

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/trading_db
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=false
SECRET_KEY=your-secret-key-here-generate-a-random-string
PROJECT_NAME="StockSphere Trading Backend"
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Generate a secure SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Run database migrations:**

```bash
# Initialize alembic (if not already done)
alembic upgrade head
```

### 4. Frontend Setup

```bash
# Navigate to frontend (root directory)
cd ..

# Install dependencies
npm install
```

## 🚀 Running the Application

### Start Backend Server

```bash
# From backend directory
cd backend

# Activate virtual environment (if not already activated)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Run the server
python run.py
```

Backend will run on: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start Frontend Server

```bash
# From root directory (in a new terminal)
npm run dev
```

Frontend will run on: `http://localhost:5173` (or `http://localhost:3000` depending on your setup)

## 📱 Usage

### 1. Create an Account

1. Navigate to `http://localhost:5173`
2. Click on **Sign Up**
3. Fill in your details and create an account
4. Login with your credentials

### 2. Add a Trading Account

1. Go to **Settings** → **Trading Accounts**
2. Click **Add Account**
3. Select your broker (Zerodha or 5paisa)
4. Fill in your broker credentials:
   - **Zerodha**: Client ID, Password, TOTP Secret, API Key, API Secret
   - **5paisa**: Client Code, MPIN, TOTP Secret, User ID, Login Password, User Key, App Source
5. Click **Validate** to test credentials
6. Click **Save** to add the account

### 3. Account Validation

- After saving, the system will automatically attempt to log in to your broker account in the background
- The account status will update from "Invalid" to "Valid" once authentication succeeds
- Refresh the page to see the updated status

## 🔑 Getting Broker Credentials

### Zerodha (Kite Connect)

1. Go to [Kite Connect](https://kite.trade/)
2. Create an app to get API Key and API Secret
3. Enable TOTP in your Zerodha account settings
4. Get your TOTP secret key

### 5paisa

1. Login to your 5paisa account
2. Go to API settings to get User Key and App Source
3. Enable TOTP in security settings
4. Note your Client Code, MPIN, and User ID

## 🗂️ Project Structure

```
StockSphere/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core configuration
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── alembic/          # Database migrations
│   ├── requirements.txt  # Python dependencies
│   └── run.py           # Application entry point
├── src/
│   ├── Components/       # React components
│   ├── Pages/           # Page components
│   ├── Services/        # API services
│   └── store/           # State management
└── README.md
```

## 🔒 Security Notes

- **Never commit `.env` files** to version control
- **Keep your SECRET_KEY secure** and random
- **Broker credentials are encrypted** before storage
- **Use HTTPS** in production
- **Regularly rotate** your API keys

## 🐛 Troubleshooting

### Backend won't start

- Check if PostgreSQL is running
- Verify database credentials in `.env`
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Frontend won't connect to backend

- Verify backend is running on `http://localhost:8000`
- Check CORS settings in `backend/.env`
- Clear browser cache and reload

### Account validation fails

- Verify broker credentials are correct
- Check if TOTP secret is valid
- Ensure broker API access is enabled
- Wait 30 seconds and try again (TOTP codes expire)

### Database migration errors

```bash
# Reset migrations (WARNING: This will delete all data)
alembic downgrade base
alembic upgrade head
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- Zerodha Kite Connect API
- 5paisa API
- FastAPI framework
- React ecosystem
