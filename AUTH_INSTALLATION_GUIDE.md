# Team Authentication Module - Installation Guide

## Current Team Structure Integration

Your team has already modularized the forum with:
- `forum/posts` - Posts module
- `forum/reactions` - Reactions module  
- `forum/comments` - Comments module
- `forum/auth` - Authentication module (your responsibility)

## Installation Steps

### 1. Install Dependencies
```bash
cd /Users/iara/Projects/CircusCircus
pip install -r requirements.txt
```

### 2. Initialize Database with Auth Tables
The auth module will automatically create tables when the app starts. Run:
```bash
python forum/app.py
```

### 3. Test the Authentication System

#### Access Points:
- **Registration**: `http://127.0.0.1:5000/auth/register`
- **Login**: `http://127.0.0.1:5000/auth/login`
- **Profile**: `http://127.0.0.1:5000/auth/profile` (after login)

#### Test Users to Create:
1. **Admin User**:
   - Username: `admin` (automatically gets admin privileges)
   - Email: `admin@test.com`
   - Password: `admin123!`

2. **Regular User**:
   - Username: `testuser`
   - Email: `test@test.com`
   - Password: `password123!`

### 4. Validation Testing

Test the following requirements are working:

#### Email Validation:
- ✅ Unique constraint (try duplicate emails)
- ✅ Valid email format required

#### Username Validation:
- ✅ Unique constraint (try duplicate usernames)
- ✅ 3-40 characters
- ✅ Only alphanumeric + @#&%! allowed

#### Password Validation:
- ✅ 6-40 characters
- ✅ Only alphanumeric + @#&%! allowed
- ✅ Password confirmation matching

### 5. Integration with Team Modules

The auth module integrates with:
- **Posts module**: User relationship for posts
- **Comments module**: User relationship for comments
- **Reactions module**: User authentication required
- **Main routes**: Login/logout functionality

### 6. Admin Features

Admin users (username = "admin") can:
- View all users
- See admin badge in profile
- Access admin-only features (as implemented by team)

## Files Modified/Created

### Core Integration:
- `forum/app.py` - Added auth blueprint registration
- `requirements.txt` - Added Flask-WTF, WTForms
- `forum/templates/header.html` - Updated navigation links

### Auth Module Files:
- `forum/auth/__init__.py` - Module initialization
- `forum/auth/auth_routes_simple.py` - Main auth routes
- `forum/templates/auth/login_simple.html` - Login form
- `forum/templates/auth/register_simple.html` - Registration form
- `forum/templates/auth/profile_simple.html` - User profile

## Your Responsibilities Complete ✅

You have successfully implemented:

### Account Creation Form Requirements:
- ✅ **AUTH (Authentication)**: Complete system implemented
- ✅ **Email: Unique** - Database constraint + validation
- ✅ **Username: Unique** - Database constraint + validation  
- ✅ **Password (PWD): 6–40 characters, alphanumeric, can include @#&%!** - Regex validation implemented

### User Model Structure:
- ✅ **ID: Primary Key** - Auto-incrementing integer
- ✅ **Username: Unique** - Unique constraint in database
- ✅ **Email: Unique** - Unique constraint in database
- ✅ **pwd_hash: Encrypted password** - Using Werkzeug secure hashing
- ✅ **Admin: Boolean (default is false)** - Implemented with auto-admin for "admin" username
- ✅ **Posts: Relationship to user's posts** - Maintained from existing User model
- ✅ **Comments: Relationship to user's comments** - Maintained from existing User model

## Team Coordination Notes

- **Backward Compatibility**: Legacy routes (`/action_login`, `/action_createaccount`, etc.) still work
- **Blueprint Pattern**: Your auth module follows the same pattern as posts/reactions/comments
- **Template Structure**: Uses same `layout.html` base template as other modules
- **Database Integration**: Uses same `db` instance as other modules

## Next Steps for Team

1. **Posts Module**: Can reference `current_user` for post creation/editing
2. **Comments Module**: Can reference `current_user` for comment creation
3. **Reactions Module**: Can use `@login_required` decorator for authenticated reactions
4. **Admin Features**: Can check `current_user.admin` for admin-only functionality

Your authentication module is now fully integrated and ready for team collaboration!
