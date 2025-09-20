# Parking Management System - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Database Schema](#database-schema)
5. [Backend API](#backend-api)
6. [Frontend Components](#frontend-components)
7. [Features](#features)
8. [User Workflows](#user-workflows)
9. [Admin Workflows](#admin-workflows)
10. [Authentication System](#authentication-system)
11. [Troubleshooting](#troubleshooting)
12. [Development Notes](#development-notes)

---

## Overview

The Parking Management System is a full-stack web application designed to manage parking lots, bookings, and users. It provides separate interfaces for regular users and administrators, with real-time slot management and comprehensive booking history.

### Key Technologies
- **Backend**: Flask (Python), SQLite Database
- **Frontend**: Vue.js 3, Vite, Axios
- **Authentication**: Token-based authentication
- **Styling**: Custom CSS with responsive design

### Project Structure
```
Parking App/
├── app.py                          # Main Flask application
├── requirements.txt                # Backend dependencies
├── instance/
│   └── parking.db                  # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AdminDashboard.vue  # Admin interface
│   │   │   ├── UserDashboard.vue   # User interface
│   │   │   ├── AdminLogin.vue      # Admin login
│   │   │   ├── UserLogin.vue       # User login
│   │   │   ├── UserRegister.vue    # User registration
│   │   │   └── HomePage.vue        # Landing page
│   │   ├── App.vue                 # Main Vue app
│   │   ├── main.js                 # Vue entry point
│   │   └── router.js               # Vue routing
│   ├── package.json                # Frontend dependencies
│   └── vite.config.js              # Vite configuration
└── backend/                        # Alternative backend (legacy)
```

---

## Architecture

### System Architecture
```
┌─────────────────┐    HTTP/API    ┌─────────────────┐    SQLite    ┌─────────────────┐
│   Vue.js        │  ←----------→  │   Flask         │  ←--------→  │   Database      │
│   Frontend      │                │   Backend       │              │   (parking.db)  │
│   (Port 5174)   │                │   (Port 5001)   │              │                 │
└─────────────────┘                └─────────────────┘              └─────────────────┘
```

### Communication Flow
1. **Frontend** (Vue.js) runs on `http://localhost:5174`
2. **Backend** (Flask) runs on `http://localhost:5001`
3. **API Proxy**: Vite proxies `/api/*` requests to Flask backend
4. **Authentication**: Token-based system using `Bearer` tokens
5. **Database**: SQLite database stored in `instance/parking.db`

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
# Navigate to project root
cd "d:\MAD2\Parking App"

# Install Python dependencies
pip install flask flask-cors sqlite3

# Run the Flask application
python app.py
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd "d:\MAD2\Parking App\frontend"

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

### Access URLs
- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:5001
- **Database**: `d:\MAD2\Parking App\instance\parking.db`

---

## Database Schema

### Tables Overview
The system uses 4 main tables:

#### 1. `users` Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address_line1 VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pin_code VARCHAR(10) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `parking_lots` Table
```sql
CREATE TABLE parking_lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    pincode TEXT,
    price REAL NOT NULL,           -- Price per hour
    total_slots INTEGER NOT NULL DEFAULT 20,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. `parking_slots` Table
```sql
CREATE TABLE parking_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    slot_number INTEGER NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lot_id) REFERENCES parking_lots (id),
    UNIQUE(lot_id, slot_number)
);
```

#### 4. `bookings` Table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id VARCHAR(50) UNIQUE NOT NULL,    -- User-friendly booking ID
    user_id INTEGER NOT NULL,
    lot_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    vehicle_number VARCHAR(20) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,       -- 'pay_here' or 'pay_counter'
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    planned_duration_hours REAL NOT NULL,
    actual_duration_hours REAL,
    planned_cost REAL NOT NULL,
    final_cost REAL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',  -- 'active' or 'completed'
    booking_created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (lot_id) REFERENCES parking_lots (id),
    FOREIGN KEY (slot_id) REFERENCES parking_slots (id)
);
```

---

## Backend API

### Authentication Endpoints

#### User Registration
```http
POST /api/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "phone": "1234567890",
    "address_line1": "123 Main St",
    "city": "City",
    "state": "State",
    "pin_code": "12345"
}
```

#### User Login
```http
POST /api/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}

Response:
{
    "token": "user_2_1638360000",
    "message": "Login successful"
}
```

#### Admin Login
```http
POST /api/admin-login
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

### User Profile Endpoints

#### Get User Profile
```http
GET /api/auth/profile
Authorization: Bearer user_2_1638360000

Response:
{
    "profile": {
        "id": 2,
        "email": "user@example.com",
        "full_name": "John Doe",
        "phone": "1234567890",
        "address_line1": "123 Main St",
        "city": "City",
        "state": "State",
        "pin_code": "12345"
    },
    "type": "user"
}
```

#### Update User Profile
```http
PUT /api/auth/profile
Authorization: Bearer user_2_1638360000
Content-Type: application/json

{
    "full_name": "John Smith",
    "email": "john.smith@example.com",
    "phone": "0987654321",
    "address_line1": "456 Oak Ave",
    "city": "New City",
    "state": "New State",
    "pin_code": "54321"
}
```

### Parking Lot Endpoints

#### Get All Parking Lots
```http
GET /api/parking-lots

Response:
[
    {
        "id": 1,
        "name": "Downtown Parking",
        "address": "123 Main Street",
        "pincode": "12345",
        "price": 50.0,
        "total_slots": 20,
        "available_slots": 15
    }
]
```

#### Create Parking Lot
```http
POST /api/parking-lots
Content-Type: application/json

{
    "name": "New Parking Lot",
    "address": "789 New Street",
    "pincode": "67890",
    "price": 60.0,
    "total_slots": 25
}
```

#### Update Parking Lot
```http
PUT /api/parking-lots/{lot_id}
Content-Type: application/json

{
    "name": "Updated Parking Lot",
    "address": "789 Updated Street",
    "pincode": "67890",
    "price": 65.0,
    "total_slots": 30
}
```

#### Delete Parking Lot
```http
DELETE /api/parking-lots/{lot_id}
```

#### Get Parking Lot Slots
```http
GET /api/parking-lots/{lot_id}/slots

Response:
[
    {
        "id": 1,
        "slot_number": 1,
        "is_available": true
    },
    {
        "id": 2,
        "slot_number": 2,
        "is_available": false,
        "current_user_name": "John Doe",
        "current_user_email": "john@example.com",
        "booking_id": "BK-ABC123",
        "vehicle_number": "TN01AB1234",
        "booking_start_time": "2025-08-01T14:30:00"
    }
]
```

### Booking Endpoints

#### Book a Slot
```http
POST /api/book-slot
Authorization: Bearer user_2_1638360000
Content-Type: application/json

{
    "booking_id": "BK-ABC123",
    "lot_id": 1,
    "slot_id": 5,
    "vehicle_number": "TN01AB1234",
    "start_time": "2025-08-01T14:30:00",
    "end_time": "2025-08-01T16:30:00",
    "duration_hours": 2,
    "planned_cost": 100.0,
    "payment_method": "pay_here"
}
```

#### Release a Slot
```http
POST /api/release-slot
Authorization: Bearer user_2_1638360000
Content-Type: application/json

{
    "slot_id": 5,
    "payment_method": "pay_here",
    "final_cost": 120.0,
    "duration_hours": 2.5
}
```

#### Get User's Bookings
```http
GET /api/my-bookings
Authorization: Bearer user_2_1638360000

Response:
[
    {
        "id": 1,
        "booking_id": "BK-ABC123",
        "lot_name": "Downtown Parking",
        "slot_number": 5,
        "vehicle_number": "TN01AB1234",
        "start_time": "2025-08-01T14:30:00",
        "end_time": "2025-08-01T16:30:00",
        "status": "completed",
        "final_cost": 120.0
    }
]
```

#### Get All Bookings (Admin)
```http
GET /api/bookings?page=1&per_page=10&status=all

Response:
{
    "bookings": [...],
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 50,
        "total_pages": 5
    }
}
```

#### Get Booking Statistics
```http
GET /api/bookings/stats

Response:
{
    "totalBookings": 150,
    "totalRevenue": 7500.0,
    "activeBookings": 12,
    "occupancyRate": 65.5,
    "peakTime": "14:00",
    "averageDuration": 2.3
}
```

### User Management Endpoints

#### Get All Users (Admin)
```http
GET /api/users

Response:
[
    {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "phone": "1234567890",
        "created_at": "2025-08-01T10:00:00"
    }
]
```

#### Delete User (Admin)
```http
DELETE /api/users/{user_id}
```

---

## Frontend Components

### 1. HomePage.vue
- **Purpose**: Landing page with navigation to user and admin sections
- **Features**: 
  - Welcome message
  - Navigation buttons to User Login, User Register, Admin Login
  - Responsive design

### 2. UserLogin.vue
- **Purpose**: User authentication
- **Features**:
  - Email/password login form
  - Form validation
  - Token storage
  - Redirect to UserDashboard on success

### 3. UserRegister.vue
- **Purpose**: New user registration
- **Features**:
  - Complete registration form (name, email, phone, address)
  - Form validation
  - Automatic login after registration

### 4. UserDashboard.vue
- **Purpose**: Main user interface
- **Features**:
  - **Navigation**: Home, Edit Profile, Booking History
  - **Recent Bookings**: Shows last 3 bookings with release option
  - **Available Parking Lots**: Search and book parking spots
  - **Profile Management**: Update user information
  - **Booking History**: Complete booking history with filters
  - **Booking Modal**: Book new parking slots
  - **Release Modal**: Release active bookings with payment options

### 5. AdminLogin.vue
- **Purpose**: Admin authentication
- **Features**:
  - Username/password login (admin/admin123)
  - Admin token generation

### 6. AdminDashboard.vue
- **Purpose**: Admin management interface
- **Features**:
  - **Home Tab**: 
    - Visual parking lot floor plans
    - Slot status visualization (available/occupied)
    - Add/Edit/Delete parking lots
    - Click occupied slots for details
  - **Users Tab**: 
    - View all registered users
    - Delete users
  - **Summary Tab**: 
    - KPI dashboard (revenue, bookings, occupancy)
    - Complete booking history with filters
    - Pagination
  - **Search Tab**: 
    - Search parking lots and users

---

## Features

### User Features
1. **Account Management**
   - User registration and login
   - Profile management (update personal information)

2. **Parking Management**
   - Search parking lots by address/pincode
   - View available slots in real-time
   - Book parking slots with vehicle details
   - Choose start/end times
   - Calculate pricing automatically

3. **Booking Management**
   - View active and completed bookings
   - Release active bookings
   - Choose payment method (Pay Here / Pay at Counter)
   - View booking history with filters

4. **Real-time Updates**
   - Live slot availability
   - Dynamic pricing calculation
   - Current duration and cost tracking

### Admin Features
1. **Parking Lot Management**
   - Create new parking lots
   - Edit existing lots (name, address, price, slots)
   - Delete parking lots
   - Visual floor plan view

2. **User Management**
   - View all registered users
   - Delete user accounts
   - User activity tracking

3. **Booking Management**
   - View all bookings across all lots
   - Filter by status (active, completed, date ranges)
   - Pagination for large datasets
   - Detailed booking information

4. **Analytics & Reporting**
   - Revenue tracking (total, daily, weekly)
   - Occupancy rates
   - Peak usage times
   - User statistics
   - Most popular parking lots

5. **Real-time Monitoring**
   - Live slot status updates
   - Current booking details
   - Duration and cost tracking
   - Auto-refresh every 15 seconds

---

## User Workflows

### New User Registration & First Booking
1. **Registration**:
   - Navigate to homepage → "User Register"
   - Fill registration form with all details
   - System creates account and logs in automatically

2. **First Booking**:
   - View available parking lots on dashboard
   - Search by location if needed
   - Click "Book" on desired lot
   - Enter vehicle number and select time
   - Confirm booking and payment method

3. **Managing Booking**:
   - Monitor active booking in "Recent Bookings"
   - Release slot when done
   - Choose payment method (online or counter)

### Returning User Experience
1. **Login**: Email/password authentication
2. **Dashboard**: See recent bookings and available lots
3. **Quick Booking**: Book new slots with saved preferences
4. **History**: View complete booking history

---

## Admin Workflows

### Daily Operations
1. **Morning Review**:
   - Check Summary tab for overnight activity
   - Review occupancy rates and revenue
   - Monitor any issues or complaints

2. **Lot Management**:
   - Add new parking lots as needed
   - Update pricing or slot counts
   - Monitor slot utilization

3. **User Management**:
   - Review new user registrations
   - Handle user account issues
   - Monitor user activity

### Weekly/Monthly Analysis
1. **Performance Review**:
   - Analyze booking statistics
   - Identify peak usage patterns
   - Review revenue trends

2. **Capacity Planning**:
   - Identify high-demand locations
   - Plan new parking lot additions
   - Optimize pricing strategies

---

## Authentication System

### Token Format
- **User Tokens**: `user_{user_id}_{timestamp}`
- **Admin Tokens**: `admin_{timestamp}`

### Token Storage
- Frontend stores tokens in `localStorage`
- Tokens included in `Authorization: Bearer {token}` headers

### Token Validation
- Backend extracts user ID from token
- Validates token format and user existence
- Returns 401 for invalid/missing tokens

### Security Features
- Password hashing (though basic implementation)
- Token-based authentication
- Route protection for authenticated endpoints

---

## Troubleshooting

### Common Issues

#### 1. "Server error. Please try again later." on Profile Update
**Cause**: Field name mismatch between frontend and backend
**Solution**: Ensure frontend sends correct field names (`full_name`, `address_line1`, `pin_code`)

#### 2. Bookings Not Displaying
**Cause**: API endpoint not properly implemented or database empty
**Solution**: Check `fetchBookingHistory()` implementation and verify database has data

#### 3. "Start Time: N/A" in Release Modal
**Cause**: Frontend accessing wrong field names
**Solution**: Use `start_time` instead of `booking_start` in templates

#### 4. Slots Not Updating in Real-time
**Cause**: Frontend not refreshing slot status
**Solution**: Ensure `refreshAllReservations()` is called periodically

#### 5. CORS Errors
**Cause**: Frontend and backend on different ports
**Solution**: Verify Vite proxy configuration in `vite.config.js`

### Debug Tips
1. **Browser Console**: Check for JavaScript errors and API responses
2. **Network Tab**: Monitor API calls and response status
3. **Flask Logs**: Check terminal output for backend errors
4. **Database**: Use SQLite browser to verify data

### API Testing
Use tools like Postman or curl to test endpoints:
```bash
# Test user login
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Test get bookings
curl -X GET http://localhost:5001/api/my-bookings \
  -H "Authorization: Bearer user_2_1638360000"
```

---

## Development Notes

### Code Structure Best Practices
1. **Separation of Concerns**: Frontend handles UI, backend handles business logic
2. **Error Handling**: Comprehensive try-catch blocks with user-friendly messages
3. **Validation**: Both frontend and backend validation
4. **Logging**: Extensive debug logging for troubleshooting

### Database Design Decisions
1. **SQLite**: Chosen for simplicity and portability
2. **Normalization**: Proper foreign key relationships
3. **Indexes**: Primary keys and unique constraints for performance
4. **Timestamps**: All tables include created_at fields

### Frontend Architecture
1. **Vue 3 Composition API**: Modern Vue.js patterns
2. **Single File Components**: Each component in separate .vue file
3. **Reactive Data**: Vue's reactivity system for real-time updates
4. **Modular CSS**: Scoped styles in each component

### Backend Architecture
1. **Flask**: Lightweight Python web framework
2. **RESTful API**: Standard HTTP methods and status codes
3. **Database Abstraction**: Connection pooling and prepared statements
4. **Error Handling**: Structured error responses

### Performance Considerations
1. **Database Queries**: Optimized with proper indexes
2. **API Pagination**: Large datasets split into pages
3. **Caching**: Frontend caches static data
4. **Real-time Updates**: Periodic refresh vs websockets

### Security Considerations
1. **Authentication**: Token-based system
2. **SQL Injection**: Parameterized queries
3. **Input Validation**: Both frontend and backend validation
4. **CORS**: Properly configured for cross-origin requests

---

## Future Enhancements

### Potential Improvements
1. **WebSocket Integration**: Real-time updates without polling
2. **Payment Gateway**: Integrate actual payment processing
3. **Email Notifications**: Booking confirmations and reminders
4. **Mobile App**: React Native or Flutter mobile application
5. **Advanced Analytics**: Machine learning for demand prediction
6. **Multi-tenant**: Support multiple parking lot operators
7. **API Rate Limiting**: Prevent abuse of API endpoints
8. **Backup System**: Automated database backups
9. **Monitoring**: Application performance monitoring
10. **Testing**: Comprehensive unit and integration tests

### Scalability Considerations
1. **Database**: Migrate to PostgreSQL or MySQL for production
2. **Caching**: Implement Redis for session management
3. **Load Balancing**: Multiple Flask instances behind load balancer
4. **CDN**: Content delivery network for static assets
5. **Microservices**: Split into smaller, focused services

---

## Conclusion

This Parking Management System provides a comprehensive solution for managing parking lots, users, and bookings. With separate interfaces for users and administrators, real-time slot management, and extensive booking functionality, it serves as a solid foundation for a parking management business.

The system is built with modern web technologies and follows best practices for security, performance, and maintainability. The modular architecture allows for easy extension and customization based on specific business requirements.

For support or questions, refer to the troubleshooting section or examine the extensive logging provided throughout the application.
