# Authentication Module Documentation

## Overview

This authentication module provides a complete user account creation and management system for the CircusCircus Forum project. It follows modern security practices and provides a modular, maintainable structure.

## Features Implemented

### Account Creation Form Requirements ✅
- **AUTH (Authentication)**: Complete authentication system implemented
- **Email**: Unique constraint enforced with validation
- **Username**: Unique constraint enforced with validation
- **Password (PWD)**: 6–40 characters, alphanumeric with @#&%! special characters

### User Model Structure ✅
- **ID**: Primary Key (auto-incrementing)
- **Username**: Unique, validated
- **Email**: Unique, validated with proper email format
- **pwd_hash**: Encrypted password using Werkzeug's security functions
- **Admin**: Boolean field (default is False)
- **Posts**: Relationship to user's posts (maintained from existing model)
- **Comments**: Relationship to user's comments (maintained from existing model)

### Additional Features
- **Account Management**: Active/inactive status, creation date, last seen
- **Security**: Login attempt tracking, rate limiting
- **Admin Functions**: User management, admin privileges
- **Password Management**: Secure password changes, reset functionality
- **User Profile**: Extended profile information support

## Module Structure

```
forum/auth/
├── __init__.py              # Module initialization
├── auth_routes.py           # Authentication routes and endpoints
├── auth_models.py           # Authentication-related database models
├── auth_validators.py       # Input validation logic
└── auth_forms.py           # Flask-WTF form definitions
```

## Installation and Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database Tables**:
   ```bash
   python setup_auth.py
   ```

3. **Run the Application**:
   ```bash
   ./run.sh
   ```

## Usage

### User Registration
- Navigate to `/auth/register`
- Fill out the registration form with:
  - Email (must be unique)
  - Username (3-40 characters, alphanumeric + @#&%!)
  - Password (6-40 characters, alphanumeric + @#&%!)
  - Password confirmation

### User Login
- Navigate to `/auth/login`
- Enter username and password
- Optional "Remember Me" functionality
- Rate limiting protection against brute force attacks

### User Management (Admin)
- View all users at `/auth/users`
- Activate/deactivate user accounts
- Grant/revoke admin privileges
- View user profiles and activity

## API Endpoints

### Authentication Routes
- `GET/POST /auth/register` - User registration
- `GET/POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `GET /auth/profile` - User profile page
- `GET/POST /auth/change-password` - Change password
- `GET /auth/users` - List users
- `GET /auth/user/<id>` - View specific user profile

### Admin Routes
- `POST /auth/admin/users/<id>/toggle-active` - Activate/deactivate user
- `POST /auth/admin/users/<id>/toggle-admin` - Grant/revoke admin privileges

### Legacy Compatibility Routes
- `POST /action_login` - Legacy login endpoint
- `GET /action_logout` - Legacy logout endpoint
- `POST /action_createaccount` - Legacy registration endpoint
- `GET /loginform` - Legacy login form

## Security Features

### Input Validation
- Email format validation with regex
- Username format validation (3-40 chars, specific characters allowed)
- Password strength validation (6-40 chars, specific characters allowed)
- XSS protection through proper form handling

### Authentication Security
- Password hashing using Werkzeug's secure methods
- Login attempt tracking and rate limiting (5 attempts per hour by default)
- Session management with Flask-Login
- CSRF protection through Flask-WTF

### Database Security
- Unique constraints on email and username
- Password hashes stored securely (never plain text)
- Account status tracking (active/inactive)
- Token-based systems for password resets

## Database Models

### User Model (Enhanced)
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # ... additional fields for profile, settings, etc.
```

### AuthToken Model
```python
class AuthToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    token = db.Column(db.String(255), unique=True)
    token_type = db.Column(db.String(50))  # 'password_reset', 'email_verification'
    expires_at = db.Column(db.DateTime)
    is_used = db.Column(db.Boolean, default=False)
```

### LoginAttempt Model
```python
class LoginAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    ip_address = db.Column(db.String(45))
    successful = db.Column(db.Boolean)
    attempted_at = db.Column(db.DateTime)
```

## Validation Rules

### Email Validation
- Must be valid email format (regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
- Must be unique in database
- Required field

### Username Validation
- 3-40 characters in length
- Can contain letters, numbers, and special characters: @#&%!
- Must be unique in database
- Required field

### Password Validation
- 6-40 characters in length
- Can contain letters, numbers, and special characters: @#&%!
- Required field
- Must match confirmation password during registration

## Error Handling

The module provides comprehensive error handling:
- Form validation errors displayed to user
- Database constraint violations handled gracefully
- Rate limiting with appropriate user feedback
- Admin action confirmations and feedback

## Testing

To test the authentication module:

1. **Registration Test**:
   - Try registering with invalid emails
   - Try registering with existing usernames/emails
   - Try weak passwords
   - Verify successful registration

2. **Login Test**:
   - Try invalid credentials
   - Try rate limiting (5+ failed attempts)
   - Verify successful login
   - Test "Remember Me" functionality

3. **Admin Functions**:
   - Create admin user (username: "admin")
   - Test user activation/deactivation
   - Test admin privilege management

## Integration with Existing Code

The module maintains backward compatibility with existing routes:
- Existing `/action_login`, `/action_logout`, `/action_createaccount` endpoints still work
- Existing user model and relationships are preserved
- Templates can be gradually migrated to use new auth routes

## Future Enhancements

Possible future additions:
- Email verification system
- Password reset via email
- Two-factor authentication
- OAuth integration (Google, GitHub, etc.)
- User profile picture uploads
- Enhanced user settings management

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure Flask-WTF and WTForms are installed
2. **Database Errors**: Run `setup_auth.py` to create required tables
3. **Template Errors**: Ensure templates are in the correct directory structure
4. **Blueprint Registration**: Verify auth_bp is registered in `__init__.py`

### Debug Mode

To enable debug mode, set `FLASK_DEBUG=1` in your environment or config file.
