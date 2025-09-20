"""
Parking Management System - Main Application
Complete Flask app with all admin and user routes for AdminDashboard
Database: D:\MAD2\Parking App\instance\parking.db
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import hashlib
from datetime import datetime, timedelta
import logging

# Create Flask app
app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173'])

# Add debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database path - using the specified database
DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'

def get_db_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create parking_lots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            pincode TEXT,
            price REAL NOT NULL,
            total_slots INTEGER NOT NULL DEFAULT 20,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create parking_slots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_number INTEGER NOT NULL,
            lot_id INTEGER NOT NULL,
            is_available INTEGER DEFAULT 1,
            current_user_id INTEGER,
            current_user_name TEXT,
            current_user_email TEXT,
            booking_id TEXT,
            vehicle_number TEXT,
            booking_start_time TIMESTAMP,
            planned_duration_hours REAL,
            current_duration_hours REAL,
            estimated_current_cost REAL,
            FOREIGN KEY (lot_id) REFERENCES parking_lots (id)
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password TEXT NOT NULL,
            address_line1 TEXT,
            city TEXT,
            state TEXT,
            pin_code TEXT,
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            user_name TEXT,
            user_email TEXT,
            lot_id INTEGER NOT NULL,
            lot_name TEXT,
            lot_address TEXT,
            slot_id INTEGER NOT NULL,
            slot_number INTEGER NOT NULL,
            vehicle_number TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            planned_duration_hours REAL,
            actual_duration_hours REAL,
            hourly_rate REAL NOT NULL,
            final_cost REAL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lot_id) REFERENCES parking_lots (id),
            FOREIGN KEY (slot_id) REFERENCES parking_slots (id)
        )
    ''')
    
    # Create admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Initialize database on startup
init_database()

# =============================================================================
# PARKING LOTS ROUTES
# =============================================================================

@app.route('/api/parking-lots', methods=['GET'])
def get_parking_lots():
    """Get all parking lots with availability stats."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM parking_lots ORDER BY name')
        lots = cursor.fetchall()
        
        logger.info(f"Found {len(lots)} parking lots in database")
        
        lots_data = []
        for lot in lots:
            # Get slot statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_slots,
                    SUM(CASE WHEN is_available = 1 THEN 1 ELSE 0 END) as available_slots,
                    SUM(CASE WHEN is_available = 0 THEN 1 ELSE 0 END) as occupied_slots
                FROM parking_slots 
                WHERE lot_id = ?
            ''', (lot['id'],))
            
            slot_stats = cursor.fetchone()
            
            # If no slots exist, create them based on database total_slots
            if not slot_stats or slot_stats['total_slots'] == 0:
                # Create slots for this lot based on database total_slots
                for slot_num in range(1, lot['total_slots'] + 1):
                    cursor.execute('''
                        INSERT INTO parking_slots (slot_number, lot_id, is_available) 
                        VALUES (?, ?, 1)
                    ''', (slot_num, lot['id']))
                conn.commit()
                
                # Recalculate stats
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_slots,
                        SUM(CASE WHEN is_available = 1 THEN 1 ELSE 0 END) as available_slots,
                        SUM(CASE WHEN is_available = 0 THEN 1 ELSE 0 END) as occupied_slots
                    FROM parking_slots 
                    WHERE lot_id = ?
                ''', (lot['id'],))
                slot_stats = cursor.fetchone()
            
            # Map database columns to frontend expected format
            lot_data = {
                'id': lot['id'],
                'name': lot['name'],
                'address': lot['address'],
                'pincode': lot['pincode'],  # Database has 'pincode'
                'price': lot['price_per_hour'],  # Database has 'price_per_hour'
                'slots': slot_stats['total_slots'] if slot_stats else lot['total_slots'],
                'total_slots': slot_stats['total_slots'] if slot_stats else lot['total_slots'],
                'available_slots': slot_stats['available_slots'] if slot_stats else lot['total_slots'],
                'occupied_slots': slot_stats['occupied_slots'] if slot_stats else 0
            }
            lots_data.append(lot_data)
        
        conn.close()
        logger.info(f"Returning {len(lots_data)} parking lots")
        return jsonify(lots_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching parking lots: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/parking-lots', methods=['POST'])
def create_parking_lot():
    """Create a new parking lot."""
    try:
        data = request.get_json()
        logger.info(f"Creating parking lot with data: {data}")
        
        name = data.get('name')
        address = data.get('address')
        pincode = data.get('pincode')
        price = data.get('price')
        total_slots = data.get('total_slots', 20)
        
        if not all([name, address, price]):
            return jsonify({'error': 'Name, address, and price are required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert parking lot using database column names
        cursor.execute('''
            INSERT INTO parking_lots (name, address, pincode, price_per_hour, total_slots)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, address, pincode, float(price), int(total_slots)))
        
        lot_id = cursor.lastrowid
        
        # Create slots for the parking lot
        for slot_num in range(1, int(total_slots) + 1):
            cursor.execute('''
                INSERT INTO parking_slots (slot_number, lot_id, is_available)
                VALUES (?, ?, 1)
            ''', (slot_num, lot_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created parking lot with ID: {lot_id}")
        return jsonify({
            'id': lot_id,
            'name': name,
            'address': address,
            'pincode': pincode,
            'price': float(price),  # Frontend expects 'price'
            'slots': int(total_slots),
            'total_slots': int(total_slots),
            'message': 'Parking lot created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating parking lot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/parking-lots/<int:lot_id>', methods=['PUT'])
def update_parking_lot(lot_id):
    """Update a parking lot."""
    try:
        data = request.get_json()
        logger.info(f"Updating parking lot {lot_id} with data: {data}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if lot exists
        cursor.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,))
        lot = cursor.fetchone()
        
        if not lot:
            conn.close()
            return jsonify({'error': 'Parking lot not found'}), 404
        
        # Update parking lot using correct database column names
        name = data.get('name', lot['name'])
        address = data.get('address', lot['address'])
        pincode = data.get('pincode', lot['pincode'])
        price = data.get('price', lot['price_per_hour'])  # Database column is price_per_hour
        total_slots = data.get('total_slots', lot['total_slots'])
        
        cursor.execute('''
            UPDATE parking_lots 
            SET name = ?, address = ?, pincode = ?, price_per_hour = ?, total_slots = ?
            WHERE id = ?
        ''', (name, address, pincode, float(price), int(total_slots), lot_id))
        
        # Update slots if total_slots changed
        cursor.execute('SELECT COUNT(*) as count FROM parking_slots WHERE lot_id = ?', (lot_id,))
        current_slot_count = cursor.fetchone()['count']
        
        if int(total_slots) != current_slot_count:
            if int(total_slots) > current_slot_count:
                # Add more slots
                for slot_num in range(current_slot_count + 1, int(total_slots) + 1):
                    cursor.execute('''
                        INSERT INTO parking_slots (slot_number, lot_id, is_available)
                        VALUES (?, ?, 1)
                    ''', (slot_num, lot_id))
            else:
                # Remove excess slots (only if they're available)
                cursor.execute('''
                    DELETE FROM parking_slots 
                    WHERE lot_id = ? AND slot_number > ? AND is_available = 1
                ''', (lot_id, int(total_slots)))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Updated parking lot {lot_id}")
        return jsonify({
            'id': lot_id,
            'name': name,
            'address': address,
            'pincode': pincode,
            'price': float(price),  # Frontend expects 'price'
            'slots': int(total_slots),
            'total_slots': int(total_slots),
            'message': 'Parking lot updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating parking lot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/parking-lots/<int:lot_id>', methods=['DELETE'])
def delete_parking_lot(lot_id):
    """Delete a parking lot."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if lot exists
        cursor.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,))
        lot = cursor.fetchone()
        
        if not lot:
            conn.close()
            return jsonify({'error': 'Parking lot not found'}), 404
        
        # Delete related slots first
        cursor.execute('DELETE FROM parking_slots WHERE lot_id = ?', (lot_id,))
        
        # Delete related bookings
        cursor.execute('DELETE FROM bookings WHERE lot_id = ?', (lot_id,))
        
        # Delete parking lot
        cursor.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted parking lot {lot_id}")
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting parking lot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/parking-lots/<int:lot_id>/slots', methods=['GET'])
def get_parking_lot_slots(lot_id):
    """Get all slots for a specific parking lot with user details."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ps.*, 
                   pl.name as lot_name, 
                   pl.address as lot_address, 
                   pl.price_per_hour as hourly_rate,
                   u.full_name as current_user_name,
                   u.email as current_user_email,
                   b.start_time as booking_start_time_actual,
                   b.end_time as booking_end_time_actual,
                   b.planned_duration_hours as booking_planned_duration,
                   b.actual_duration_hours as booking_actual_duration,
                   b.final_cost as booking_final_cost,
                   b.planned_cost as booking_planned_cost,
                   b.status as booking_status
            FROM parking_slots ps
            JOIN parking_lots pl ON ps.lot_id = pl.id
            LEFT JOIN users u ON ps.current_user_id = u.id
            LEFT JOIN bookings b ON ps.booking_id = b.booking_id
            WHERE ps.lot_id = ?
            ORDER BY ps.slot_number
        ''', (lot_id,))
        
        slots = cursor.fetchall()
        conn.close()
        
        slots_data = []
        for slot in slots:
            # Calculate current duration and cost if slot is booked
            current_duration_hours = None
            estimated_current_cost = None
            start_time_formatted = None
            end_time_formatted = None
            
            if not slot['is_available'] and slot['booking_start_time_actual']:
                try:
                    from datetime import datetime
                    
                    # Parse start time
                    start_time_str = slot['booking_start_time_actual']
                    if start_time_str:
                        # Handle different datetime formats
                        if 'T' in start_time_str:
                            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00') if 'Z' in start_time_str else start_time_str)
                        else:
                            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S.%f')
                        
                        start_time_formatted = start_time.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Calculate current duration
                        current_time = datetime.now()
                        duration_delta = current_time - start_time
                        current_duration_hours = duration_delta.total_seconds() / 3600
                        
                        # Calculate estimated current cost
                        estimated_current_cost = current_duration_hours * slot['hourly_rate']
                    
                    # Parse end time if available
                    end_time_str = slot['booking_end_time_actual']
                    if end_time_str:
                        if 'T' in end_time_str:
                            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00') if 'Z' in end_time_str else end_time_str)
                        else:
                            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S.%f')
                        
                        end_time_formatted = end_time.strftime('%Y-%m-%d %H:%M:%S')
                        
                except Exception as e:
                    print(f"[DEBUG] Error calculating time for slot {slot['slot_number']}: {e}")
                    # Fallback to planned values
                    current_duration_hours = slot['booking_planned_duration'] or slot['planned_duration_hours']
                    estimated_current_cost = slot['booking_planned_cost'] or slot['planned_cost']
                    start_time_formatted = slot['booking_start_time'] or slot['booking_start_time_actual']
            
            # Map database columns to expected format
            slot_data = {
                'id': slot['id'],
                'slot_number': slot['slot_number'],
                'lot_id': slot['lot_id'],
                'lot_name': slot['lot_name'],
                'lot_address': slot['lot_address'],
                'is_available': bool(slot['is_available']),
                'current_user_id': slot['current_user_id'],
                'current_user_name': slot['current_user_name'],
                'current_user_email': slot['current_user_email'],
                'booking_id': slot['booking_id'],
                'vehicle_number': slot['vehicle_number'],
                'booking_start_time': start_time_formatted or slot['booking_start_time'],
                'booking_end_time': end_time_formatted,
                'planned_duration_hours': slot['booking_planned_duration'] or slot['planned_duration_hours'],
                'current_duration_hours': round(current_duration_hours, 2) if current_duration_hours else None,
                'estimated_current_cost': round(estimated_current_cost, 2) if estimated_current_cost else (slot['booking_planned_cost'] or slot['planned_cost']),
                'final_cost': slot['booking_final_cost'],
                'booking_status': slot['booking_status'],
                'hourly_rate': slot['hourly_rate']
            }
            slots_data.append(slot_data)
        
        return jsonify(slots_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching slots for lot {lot_id}: {e}")
        return jsonify({'error': str(e)}), 500

# Admin route compatibility
@app.route('/api/admin/parking-lots/<int:lot_id>/slots', methods=['GET'])
def get_admin_parking_lot_slots(lot_id):
    """Admin route for getting parking lot slots."""
    return get_parking_lot_slots(lot_id)

# Removed duplicate delete_parking_lot function - using the one above with proper cascade deletes

# Removed proxy route - using direct implementation above

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email, phone, address_line1, city, state, pin_code, created_at
            FROM users 
            ORDER BY created_at DESC
        ''')
        users = cursor.fetchall()
        
        users_data = []
        for user in users:
            user_data = {
                'id': user['id'],
                'name': user['full_name'],  # Map full_name to name
                'username': user['full_name'],  # Use full_name as username for display
                'email': user['email'],
                'phone': user['phone'],
                'address': user['address_line1'],
                'city': user['city'],
                'state': user['state'],
                'pin_code': user['pin_code'],
                'created_at': user['created_at']
            }
            users_data.append(user_data)
        
        conn.close()
        logger.info(f"Returning {len(users_data)} users")
        return jsonify(users_data), 200
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Release any active bookings first by updating parking_slots
        cursor.execute('''
            UPDATE parking_slots 
            SET is_available = 1, current_user_id = NULL, booking_id = NULL, 
                vehicle_number = NULL, booking_start_time = NULL, 
                planned_duration_hours = NULL, planned_cost = NULL
            WHERE current_user_id = ?
        ''', (user_id,))
        
        # Update bookings status to 'cancelled'
        cursor.execute('''
            UPDATE bookings 
            SET status = 'cancelled'
            WHERE user_id = ? AND status = 'active'
        ''', (user_id,))
        
        # Delete user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted user {user_id}")
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get booking history with pagination and filtering."""
    try:
        print(f"[DEBUG] Getting bookings with args: {request.args}")
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status_filter = request.args.get('status', 'all')
        
        print(f"[DEBUG] Page: {page}, Per page: {per_page}, Filter: {status_filter}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query based on filter using actual database schema
        base_query = '''
            SELECT b.*, u.full_name as user_name, u.email as user_email,
                   pl.name as lot_name, pl.address as lot_address
            FROM bookings b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN parking_lots pl ON b.lot_id = pl.id
        '''
        
        params = []
        if status_filter != 'all':
            if status_filter == 'today':
                base_query += " WHERE DATE(b.start_time) = DATE('now')"
            elif status_filter == 'week':
                base_query += " WHERE DATE(b.start_time) >= DATE('now', '-7 days')"
            elif status_filter == 'month':
                base_query += " WHERE DATE(b.start_time) >= DATE('now', '-30 days')"
            else:
                base_query += " WHERE b.status = ?"
                params.append(status_filter)
        
        print(f"[DEBUG] Base query: {base_query}")
        print(f"[DEBUG] Params: {params}")
        
        # Count total records
        count_query = base_query.replace(
            'SELECT b.*, u.full_name as user_name, u.email as user_email, pl.name as lot_name, pl.address as lot_address', 
            'SELECT COUNT(*)'
        )
        print(f"[DEBUG] Count query: {count_query}")
        
        cursor.execute(count_query, params)
        count_result = cursor.fetchone()
        print(f"[DEBUG] Count result: {count_result}")
        
        total_records = count_result[0] if count_result else 0
        print(f"[DEBUG] Total records: {total_records}")
        
        # Get paginated results
        base_query += " ORDER BY b.start_time DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        print(f"[DEBUG] Final query: {base_query}")
        print(f"[DEBUG] Final params: {params}")
        
        cursor.execute(base_query, params)
        bookings = cursor.fetchall()
        print(f"[DEBUG] Found {len(bookings)} bookings")
        
        bookings_data = []
        for booking in bookings:
            # Handle None values safely
            actual_duration = booking['actual_duration_hours'] or 0
            final_cost = booking['final_cost'] or 0
            
            booking_data = {
                'id': booking['id'],
                'booking_id': booking['booking_id'],
                'user_id': booking['user_id'],
                'user_name': booking['user_name'],
                'user_email': booking['user_email'],
                'lot_id': booking['lot_id'],
                'lot_name': booking['lot_name'],
                'lot_address': booking['lot_address'],
                'slot_number': booking['slot_id'],  # Using slot_id as slot_number
                'vehicle_number': booking['vehicle_number'],
                'start_time': booking['start_time'],
                'end_time': booking['end_time'],
                'planned_duration_hours': booking['planned_duration_hours'] or 0,
                'actual_duration_hours': actual_duration,
                'hourly_rate': final_cost / actual_duration if actual_duration > 0 else 0,
                'final_cost': final_cost,
                'status': booking['status'],
                'created_at': booking['booking_created_at']
            }
            bookings_data.append(booking_data)
        
        conn.close()
        
        total_pages = (total_records + per_page - 1) // per_page
        
        return jsonify({
            'bookings': bookings_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_records,
                'total_pages': total_pages,
                'pages': total_pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching bookings: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings/stats', methods=['GET'])
def bookings_stats():
    """Get booking statistics for admin dashboard."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total bookings count
        cursor.execute("SELECT COUNT(*) FROM bookings")
        total_bookings = cursor.fetchone()[0]
        
        # Get total revenue from final_cost (actual revenue from completed bookings)
        cursor.execute("SELECT SUM(final_cost) FROM bookings WHERE final_cost IS NOT NULL AND status = 'completed'")
        total_revenue = cursor.fetchone()[0] or 0
        
        # Get average booking duration from actual_duration_hours
        cursor.execute("""
            SELECT AVG(actual_duration_hours) as avg_duration
            FROM bookings 
            WHERE actual_duration_hours IS NOT NULL AND actual_duration_hours > 0
        """)
        avg_duration = cursor.fetchone()[0] or 0
        
        # Get bookings by status
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM bookings 
            GROUP BY status
        """)
        status_stats = {}
        for row in cursor.fetchall():
            status_stats[row[0]] = row[1]
        
        # Get additional useful metrics
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'active'")
        active_bookings = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'completed'")
        completed_bookings = cursor.fetchone()[0]
        
        # Get total slots and occupied slots from parking_slots
        cursor.execute("SELECT COUNT(*) FROM parking_slots")
        total_slots = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM parking_slots WHERE is_available = 0")
        occupied_slots = cursor.fetchone()[0]
        
        # Get additional user and lot counts for complete dashboard data
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM parking_lots")
        total_lots = cursor.fetchone()[0]
        
        # Get today's revenue (completed bookings from today)
        cursor.execute("""
            SELECT SUM(final_cost) 
            FROM bookings 
            WHERE final_cost IS NOT NULL 
            AND status = 'completed' 
            AND DATE(completed_at) = DATE('now')
        """)
        today_revenue = cursor.fetchone()[0] or 0
        
        # Get this week's bookings count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM bookings 
            WHERE DATE(booking_created_at) >= DATE('now', '-7 days')
        """)
        this_week_bookings = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"[DEBUG] Booking stats: total={total_bookings}, revenue={total_revenue}, avg_duration={avg_duration}")
        
        return jsonify({
            # Primary KPIs (match AdminDashboard expectations)
            'totalBookings': total_bookings,
            'totalRevenue': round(total_revenue, 2),
            'averageRevenue': round(total_revenue / total_bookings, 2) if total_bookings > 0 else 0,
            'peakTime': '10:00 AM',  # Could be calculated from actual data
            'occupancyRate': round((occupied_slots / total_slots * 100), 2) if total_slots > 0 else 0,
            
            # Secondary KPIs
            'activeBookings': active_bookings,
            'todayRevenue': round(today_revenue, 2),
            'averageDuration': round(avg_duration, 2),
            'totalUsers': total_users,
            'totalLots': total_lots,
            'totalSlots': total_slots,
            'availableSlots': total_slots - occupied_slots,
            'occupiedSlots': occupied_slots,
            'thisWeekBookings': this_week_bookings,
            'mostPopularLot': 'N/A',  # Could be calculated from booking data
            
            # Additional data for compatibility
            'status_distribution': status_stats,
            'completed_bookings': completed_bookings
        })
        
    except Exception as e:
        print(f"[ERROR] Failed to get booking stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve booking statistics'}), 500

# =============================================================================
# USER AUTHENTICATION COMPATIBILITY ROUTES
# =============================================================================

@app.route('/api/auth/user/register', methods=['POST'])
def user_register():
    """User registration with direct database access."""
    try:
        data = request.get_json()
        print(f"[DEBUG] User registration request for: {data.get('email')}")
        
        # Extract and validate data
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('fullName') or data.get('full_name')
        phone = data.get('phone', '')
        address_line1 = data.get('addressLine1') or data.get('address_line1', '')
        city = data.get('city', '')
        state = data.get('state', '')
        pin_code = data.get('pinCode') or data.get('pin_code', '')
        
        if not email or not password or not full_name:
            return jsonify({'message': 'Email, password, and full name are required'}), 400
        
        # Database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'User with this email already exists'}), 409
        
        # Hash password
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)
        
        # Insert new user
        cursor.execute('''
            INSERT INTO users (email, password, full_name, phone, address_line1, city, state, pin_code, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, full_name, phone, address_line1, city, state, pin_code, True, datetime.now().isoformat()))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"[DEBUG] User registered successfully with ID: {user_id}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user_id,
                'email': email,
                'name': full_name
            }
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Registration error: {str(e)}")
        return jsonify({'message': 'Server error. Please try again later.'}), 500
    
    try:
        with app.test_client() as client:
            response = client.post('/api/user/register', 
                                 json=converted_data,
                                 headers=dict(request.headers))
            
            print(f"[DEBUG] Registration response status: {response.status_code}")
            print(f"[DEBUG] Registration response data: {response.get_data(as_text=True)}")
            
            try:
                return response.get_json(), response.status_code
            except:
                return {"error": "Invalid JSON response", "raw": response.get_data(as_text=True)}, response.status_code
    except Exception as e:
        print(f"[ERROR] Registration proxy error: {e}")
        # Fallback: Direct registration
        return direct_user_register()

def direct_user_register():
    """Direct user registration fallback."""
    try:
        from werkzeug.security import generate_password_hash
        import sqlite3
        from datetime import datetime
        
        data = request.get_json()
        print(f"[DEBUG] Direct registration for: {data}")
        
        # Handle both camelCase (frontend) and snake_case (backend) field names
        full_name = data.get('full_name') or data.get('fullName')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone') or ''
        address_line1 = data.get('address_line1') or data.get('addressLine1') or ''
        city = data.get('city') or ''
        state = data.get('state') or ''
        pin_code = data.get('pin_code') or data.get('pinCode') or ''
        
        # Validate required fields
        if not email:
            return jsonify({'message': 'email is required'}), 400
        if not password:
            return jsonify({'message': 'password is required'}), 400
        if not full_name:
            return jsonify({'message': 'full_name is required'}), 400
        
        # Database connection
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'message': 'Email already registered'}), 400
        
        # Hash password and create user
        hashed_password = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (email, password, full_name, phone, address_line1, city, state, pin_code, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            email,
            hashed_password,
            full_name,
            phone,
            address_line1,
            city,
            state,
            pin_code,
            0,  # is_active = 0 for regular users
            datetime.now().isoformat()
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"[DEBUG] Direct registration successful for user ID: {user_id}")
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'email': email
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Direct registration error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/user/login', methods=['POST'])
def user_login():
    """User login with direct database access."""
    try:
        data = request.get_json()
        print(f"[DEBUG] User login request for: {data.get('email')}")
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find user by email
        cursor.execute('SELECT id, full_name, email, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Check password
        stored_password = user['password']
        password_valid = False
        
        # Try werkzeug password check first (for hashed passwords)
        try:
            from werkzeug.security import check_password_hash
            if check_password_hash(stored_password, password):
                password_valid = True
                print(f"[DEBUG] Password verified with hash")
        except Exception as e:
            print(f"[DEBUG] Hash check failed: {e}")
        
        # If not hashed, check plain text (for development)
        if not password_valid and stored_password == password:
            password_valid = True
            print(f"[DEBUG] Password verified as plain text")
        
        if not password_valid:
            conn.close()
            print(f"[DEBUG] Password verification failed for {email}")
            return jsonify({'message': 'Invalid email or password'}), 401
        
        # Generate simple token (in production, use JWT or similar)
        import time
        token = f"user_{user['id']}_{int(time.time())}"
        
        conn.close()
        
        print(f"[DEBUG] Login successful for user {user['id']}")
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['full_name'],
                'email': user['email']
            },
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Login error: {str(e)}")
        return jsonify({'message': 'Server error. Please try again later.'}), 500

def direct_user_login():
    """Direct user login fallback."""
    try:
        from werkzeug.security import check_password_hash
        import sqlite3
        from datetime import datetime
        
        data = request.get_json()
        print(f"[DEBUG] Direct login for: {data.get('email')}")
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Database connection
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check user credentials
        cursor.execute('SELECT * FROM users WHERE email = ? AND is_active = 0', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            print(f"[DEBUG] Direct login successful for: {email}")
            user_data = {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'phone': user['phone'] or '',
                'address_line1': user['address_line1'] or '',
                'city': user['city'] or '',
                'state': user['state'] or '',
                'pin_code': user['pin_code'] or ''
            }
            
            token = f"user_{user['id']}_{datetime.now().timestamp()}"
            print(f"[DEBUG] Generated token: {token}")
            print(f"[DEBUG] User data: {user_data}")
            
            return jsonify({
                'message': 'Login successful',
                'access_token': token,
                'user': user_data
            }), 200
        
        return jsonify({'message': 'Invalid credentials'}), 401
        
    except Exception as e:
        print(f"[ERROR] Direct login error: {e}")
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/profile', methods=['GET', 'PUT'])
def user_profile():
    """Direct user profile endpoint with token-based authentication."""
    print(f"[DEBUG] Profile {request.method} request")
    print(f"[DEBUG] Headers: {dict(request.headers)}")
    
    # Extract user ID from token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Authorization token required'}), 401
    
    token = auth_header.replace('Bearer ', '')
    print(f"[DEBUG] Token: {token}")
    
    # Extract user ID from token (format: user_{id}_{timestamp})
    try:
        if token.startswith('user_'):
            parts = token.split('_')
            if len(parts) >= 2:
                user_id = int(parts[1])
                print(f"[DEBUG] Extracted user ID: {user_id}")
            else:
                return jsonify({'message': 'Invalid token format'}), 401
        else:
            return jsonify({'message': 'Invalid token'}), 401
    except (ValueError, IndexError):
        return jsonify({'message': 'Invalid token format'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'GET':
            # Get user profile
            cursor.execute('SELECT id, email, full_name, phone, address_line1, city, state, pin_code, created_at FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                profile_data = {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user['full_name'],  # Frontend expects full_name
                    'name': user['full_name'],        # Also provide name as fallback
                    'phone': user['phone'],
                    'address_line1': user['address_line1'],  # Frontend expects address_line1
                    'address': user['address_line1'],        # Also provide address as fallback
                    'city': user['city'],
                    'state': user['state'],
                    'pin_code': user['pin_code'],     # Frontend expects pin_code
                    'pinCode': user['pin_code'],      # Also provide pinCode as fallback
                    'created_at': user['created_at'],
                    'createdAt': user['created_at']
                }
                
                return jsonify({
                    'profile': profile_data,
                    'type': 'user'
                }), 200
            else:
                return jsonify({'message': 'User not found'}), 404
                
        elif request.method == 'PUT':
            # Update user profile
            data = request.get_json()
            print(f"[DEBUG] PUT data received: {data}")
            
            # Update user data - match frontend field names
            cursor.execute('''
                UPDATE users SET 
                    email = ?, full_name = ?, phone = ?, address_line1 = ?, 
                    city = ?, state = ?, pin_code = ?
                WHERE id = ?
            ''', (
                data.get('email'),
                data.get('full_name'),
                data.get('phone'),
                data.get('address_line1'),
                data.get('city'),
                data.get('state'),
                data.get('pin_code'),
                user_id
            ))
            
            conn.commit()
            
            # Get updated user data to return
            cursor.execute('SELECT id, email, full_name, phone, address_line1, city, state, pin_code, created_at FROM users WHERE id = ?', (user_id,))
            updated_user = cursor.fetchone()
            conn.close()
            
            if updated_user:
                profile_data = {
                    'id': updated_user['id'],
                    'email': updated_user['email'],
                    'full_name': updated_user['full_name'],
                    'name': updated_user['full_name'],
                    'phone': updated_user['phone'],
                    'address_line1': updated_user['address_line1'],
                    'address': updated_user['address_line1'],
                    'city': updated_user['city'],
                    'state': updated_user['state'],
                    'pin_code': updated_user['pin_code'],
                    'pinCode': updated_user['pin_code'],
                    'created_at': updated_user['created_at'],
                    'createdAt': updated_user['created_at']
                }
                
                return jsonify({
                    'message': 'Profile updated successfully',
                    'profile': profile_data
                }), 200
            else:
                return jsonify({'message': 'Profile updated successfully'}), 200
            
    except Exception as e:
        print(f"[ERROR] Profile error: {str(e)}")
        return jsonify({'message': 'Server error. Please try again later.'}), 500

# Removed unused direct_user_profile function - now using direct implementation in user_profile route

@app.route('/api/my-bookings', methods=['GET'])
def user_bookings():
    """Direct user bookings endpoint."""
    print(f"[DEBUG] User bookings request")
    print(f"[DEBUG] Headers: {dict(request.headers)}")
    
    # Extract user ID from token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        print(f"[DEBUG] Missing or invalid Authorization header: {auth_header}")
        return jsonify({'message': 'Authorization token required'}), 401
    
    token = auth_header.replace('Bearer ', '')
    print(f"[DEBUG] Token: {token}")
    
    # Extract user ID from token (format: user_{id}_{timestamp})
    try:
        if token.startswith('user_'):
            parts = token.split('_')
            if len(parts) >= 2:
                user_id = int(parts[1])
                print(f"[DEBUG] Extracted user ID from token: {user_id}")
            else:
                print(f"[DEBUG] Invalid token format - not enough parts: {parts}")
                return jsonify({'message': 'Invalid token format'}), 401
        else:
            print(f"[DEBUG] Token doesn't start with 'user_': {token}")
            return jsonify({'message': 'Invalid token'}), 401
    except (ValueError, IndexError) as e:
        print(f"[DEBUG] Token parsing error: {e}")
        return jsonify({'message': 'Invalid token format'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's bookings with parking lot details
        cursor.execute('''
            SELECT b.*, 
                   pl.name as lot_name, 
                   pl.address as lot_address,
                   pl.price_per_hour as hourly_rate,
                   ps.slot_number
            FROM bookings b
            JOIN parking_lots pl ON b.lot_id = pl.id
            JOIN parking_slots ps ON b.slot_id = ps.id
            WHERE b.user_id = ?
            ORDER BY b.booking_created_at DESC
        ''', (user_id,))
        
        bookings = cursor.fetchall()
        conn.close()
        
        bookings_data = []
        for booking in bookings:
            booking_data = {
                'id': booking['id'],
                'booking_id': booking['booking_id'],
                'lot_id': booking['lot_id'],
                'lot_name': booking['lot_name'],
                'lot_address': booking['lot_address'],
                'slot_id': booking['slot_id'],
                'slot_number': booking['slot_number'],
                'vehicle_number': booking['vehicle_number'],
                'payment_method': booking['payment_method'],
                'start_time': booking['start_time'],
                'end_time': booking['end_time'],
                'planned_duration_hours': booking['planned_duration_hours'],
                'actual_duration_hours': booking['actual_duration_hours'],
                'planned_cost': booking['planned_cost'],
                'final_cost': booking['final_cost'],
                'status': booking['status'],
                'created_at': booking['booking_created_at'],
                'completed_at': booking['completed_at'],
                'hourly_rate': booking['hourly_rate']
            }
            bookings_data.append(booking_data)
        
        print(f"[DEBUG] Returning {len(bookings_data)} bookings for user {user_id}")
        return jsonify(bookings_data), 200
        
    except Exception as e:
        print(f"[ERROR] Bookings error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Failed to fetch bookings: {str(e)}'}), 500

@app.route('/api/book-slot', methods=['POST'])
def book_slot():
    """Direct slot booking implementation.""" 
    print(f"[DEBUG] Book slot request received")
    print(f"[DEBUG] Request data: {request.get_json()}")
    print(f"[DEBUG] Headers: {dict(request.headers)}")
    
    # Extract user ID from token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        print(f"[DEBUG] Missing or invalid Authorization header: {auth_header}")
        return jsonify({'message': 'Authorization token required'}), 401
    
    token = auth_header.replace('Bearer ', '')
    print(f"[DEBUG] Token: {token}")
    
    # Extract user ID from token (format: user_{id}_{timestamp})
    try:
        if token.startswith('user_'):
            parts = token.split('_')
            if len(parts) >= 2:
                user_id = int(parts[1])
                print(f"[DEBUG] Extracted user ID from token: {user_id}")
            else:
                print(f"[DEBUG] Invalid token format - not enough parts: {parts}")
                return jsonify({'message': 'Invalid token format'}), 401
        else:
            print(f"[DEBUG] Token doesn't start with 'user_': {token}")
            return jsonify({'message': 'Invalid token'}), 401
    except (ValueError, IndexError) as e:
        print(f"[DEBUG] Token parsing error: {e}")
        return jsonify({'message': 'Invalid token format'}), 401
    
    # Get booking data
    booking_data = request.get_json() or {}
    lot_id = booking_data.get('lot_id')
    slot_id = booking_data.get('slot_id')
    vehicle_number = booking_data.get('vehicle_number')
    planned_duration = booking_data.get('duration', 2)  # Default 2 hours
    start_time = booking_data.get('start_time')  # Get start_time from frontend
    end_time = booking_data.get('end_time')      # Get end_time from frontend
    
    print(f"[DEBUG] Booking data received: lot_id={lot_id}, slot_id={slot_id}, start_time={start_time}, end_time={end_time}")
    
    if not all([lot_id, slot_id, vehicle_number]):
        return jsonify({'message': 'Missing required fields: lot_id, slot_id, vehicle_number'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify user exists
        cursor.execute('SELECT id, full_name, email FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'message': 'Invalid user'}), 401
        
        # Find the specific slot
        cursor.execute('''
            SELECT ps.*, pl.price_per_hour 
            FROM parking_slots ps 
            JOIN parking_lots pl ON ps.lot_id = pl.id 
            WHERE ps.id = ?
        ''', (slot_id,))
        slot = cursor.fetchone()
        
        if not slot:
            conn.close()
            return jsonify({'message': 'Slot not found'}), 404
        
        if not slot['is_available']:
            conn.close()
            return jsonify({'message': 'Slot is already booked'}), 409
        
        # Generate booking ID
        import random
        import string
        booking_id = 'BK-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Calculate costs
        hourly_rate = slot['price_per_hour']
        slot_number = slot['slot_number']  # Extract slot_number from slot data
        planned_cost = planned_duration * hourly_rate
        
        print(f"[DEBUG] Slot data: {slot}")
        print(f"[DEBUG] Extracted slot_number: {slot_number}")
        
        # Use provided start_time and end_time, or defaults
        from datetime import datetime, timedelta
        if not start_time:
            start_time = datetime.now().isoformat()
        else:
            # Ensure proper datetime format for SQLite
            try:
                # Parse the datetime string from frontend
                if 'T' in start_time and len(start_time) == 16:  # Format: 2025-08-01T22:02
                    start_time += ':00'  # Add seconds: 2025-08-01T22:02:00
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00') if 'Z' in start_time else start_time)
                start_time = start_dt.isoformat()
            except Exception as dt_error:
                print(f"[ERROR] Start time parsing error: {dt_error}")
                start_time = datetime.now().isoformat()
        
        if not end_time:
            # Default to start_time + planned_duration hours
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00') if 'Z' in start_time else start_time)
            end_dt = start_dt + timedelta(hours=planned_duration)
            end_time = end_dt.isoformat()
        else:
            # Ensure proper datetime format for SQLite
            try:
                # Parse the datetime string from frontend
                if 'T' in end_time and len(end_time) == 16:  # Format: 2025-08-01T22:02
                    end_time += ':00'  # Add seconds: 2025-08-01T22:02:00
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00') if 'Z' in end_time else end_time)
                end_time = end_dt.isoformat()
            except Exception as dt_error:
                print(f"[ERROR] End time parsing error: {dt_error}")
                # Fallback: calculate from start_time + planned_duration
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00') if 'Z' in start_time else start_time)
                end_dt = start_dt + timedelta(hours=planned_duration)
                end_time = end_dt.isoformat()
        
        print(f"[DEBUG] Using start_time={start_time}, end_time={end_time}, planned_cost={planned_cost}")
        print(f"[DEBUG] Insert values: user_id={user_id}, lot_id={lot_id}, slot_id={slot['id']}, booking_id={booking_id}")
        print(f"[DEBUG] Vehicle: {vehicle_number}, Duration: {planned_duration}, Status: active")
        
        # Create booking record with all required fields
        cursor.execute('''
            INSERT INTO bookings (
                user_id, lot_id, slot_id, booking_id, vehicle_number, 
                payment_method, start_time, end_time, planned_duration_hours, 
                actual_duration_hours, planned_cost, final_cost, status, 
                booking_created_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, lot_id, slot['id'], booking_id, vehicle_number, 
              'pay_counter', start_time, end_time, planned_duration, 
              0.0, planned_cost, 0.0, 'active', 
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        # Update slot availability
        cursor.execute('''
            UPDATE parking_slots SET 
                is_available = 0, 
                current_user_id = ?,
                booking_id = ?,
                vehicle_number = ?,
                booking_start_time = datetime('now'),
                planned_duration_hours = ?,
                planned_cost = ?
            WHERE id = ?
        ''', (user_id, booking_id, vehicle_number, planned_duration, planned_cost, slot['id']))
        
        conn.commit()
        conn.close()
        
        print(f"[DEBUG] Slot booked successfully: {booking_id}")
        print(f"[DEBUG] About to return response with slot_number: {slot_number}")
        
        return jsonify({
            'message': 'Slot booked successfully',
            'booking': {
                'booking_id': booking_id,
                'slot_number': slot_number,
                'lot_id': lot_id,
                'user_id': user_id,
                'vehicle_number': vehicle_number,
                'planned_duration': planned_duration,
                'planned_cost': planned_cost,
                'hourly_rate': hourly_rate
            }
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Booking error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Booking failed: {str(e)}'}), 500

@app.route('/api/release-slot', methods=['POST'])
def release_slot():
    """Direct slot release implementation."""
    print(f"[DEBUG] Release slot request received")
    print(f"[DEBUG] Request data: {request.get_json()}")
    print(f"[DEBUG] Headers: {dict(request.headers)}")
    
    # Extract user ID from token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Authorization token required'}), 401
    
    token = auth_header.replace('Bearer ', '')
    try:
        if token.startswith('user_'):
            parts = token.split('_')
            if len(parts) >= 2:
                user_id = int(parts[1])
                print(f"[DEBUG] Release request from user ID: {user_id}")
            else:
                return jsonify({'message': 'Invalid token format'}), 401
        else:
            return jsonify({'message': 'Invalid token'}), 401
    except (ValueError, IndexError):
        return jsonify({'message': 'Invalid token format'}), 401
    
    # Get request data
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    slot_id = data.get('slot_id')  # Fallback for frontend compatibility
    
    # Support both booking_id and slot_id for compatibility
    if not booking_id and not slot_id:
        return jsonify({'message': 'Either booking_id or slot_id is required'}), 400
    
    print(f"[DEBUG] Release data: booking_id={booking_id}, slot_id={slot_id}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find the booking - support both booking_id and slot_id
        if booking_id:
            cursor.execute('''
                SELECT b.*, ps.id as slot_id, ps.slot_number, pl.price_per_hour
                FROM bookings b
                JOIN parking_slots ps ON b.slot_id = ps.id
                JOIN parking_lots pl ON b.lot_id = pl.id
                WHERE b.booking_id = ? AND b.user_id = ? AND b.status = 'active'
            ''', (booking_id, user_id))
        else:
            # Find by slot_id - get the most recent active booking for this slot
            cursor.execute('''
                SELECT b.*, ps.id as slot_id, ps.slot_number, pl.price_per_hour
                FROM bookings b
                JOIN parking_slots ps ON b.slot_id = ps.id
                JOIN parking_lots pl ON b.lot_id = pl.id
                WHERE b.slot_id = ? AND b.user_id = ? AND b.status = 'active'
                ORDER BY b.id DESC LIMIT 1
            ''', (slot_id, user_id))
        
        booking = cursor.fetchone()
        
        if not booking:
            conn.close()
            if booking_id:
                return jsonify({'message': f'Active booking not found for booking_id: {booking_id}'}), 404
            else:
                return jsonify({'message': f'Active booking not found for slot_id: {slot_id}'}), 404
        
        print(f"[DEBUG] Found booking: {dict(booking)}")
        
        # Extract slot_number for use in response
        slot_number = booking['slot_number']
        print(f"[DEBUG] Extracted slot_number: {slot_number}")
        
        # Calculate final cost
        from datetime import datetime
        start_time = datetime.fromisoformat(booking['start_time'].replace('Z', '+00:00') if 'Z' in booking['start_time'] else booking['start_time'])
        end_time = datetime.now()
        actual_duration = (end_time - start_time).total_seconds() / 3600
        final_cost = actual_duration * booking['price_per_hour']
        
        # Update booking record
        cursor.execute('''
            UPDATE bookings SET 
                end_time = ?,
                actual_duration_hours = ?,
                final_cost = ?,
                status = 'completed',
                completed_at = ?
            WHERE id = ?
        ''', (end_time.isoformat(), actual_duration, final_cost, end_time.isoformat(), booking['id']))
        
        # Release the slot
        cursor.execute('''
            UPDATE parking_slots SET 
                is_available = 1,
                current_user_id = NULL,
                booking_id = NULL,
                vehicle_number = NULL,
                booking_start_time = NULL,
                planned_duration_hours = NULL,
                planned_cost = NULL
            WHERE id = ?
        ''', (booking['slot_id'],))
        
        conn.commit()
        conn.close()
        
        print(f"[DEBUG] Slot {slot_number} released successfully")
        
        # Format start_time for frontend consistency
        formatted_start_time = booking['start_time']
        if 'T' in formatted_start_time and len(formatted_start_time) > 16:
            # Keep full datetime format: 2025-08-01T22:16:00
            formatted_start_time = formatted_start_time[:19]  # Remove microseconds if present
        
        print(f"[DEBUG] Returning start_time: {formatted_start_time}")
        
        return jsonify({
            'message': 'Slot released successfully',
            'booking_id': booking['booking_id'],
            'slot_number': slot_number,
            'slot_id': booking['slot_id'],  # Include slot_id for frontend compatibility
            'final_cost': round(final_cost, 2),
            'actual_duration': round(actual_duration, 2),
            'start_time': formatted_start_time,
            'startTime': formatted_start_time,  # Alternative key for frontend
            'end_time': end_time.isoformat(),
            'endTime': end_time.isoformat(),    # Alternative key for frontend
            'vehicle_number': booking['vehicle_number'],
            'lot_name': booking['lot_name'] if 'lot_name' in booking.keys() else '',
            'planned_duration_hours': booking['planned_duration_hours'],
            'planned_cost': booking['planned_cost']
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Release slot error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Failed to release slot: {str(e)}'}), 500

# =============================================================================
# DEBUG ROUTES FOR TESTING
# =============================================================================

@app.route('/api/debug/users', methods=['GET'])
def debug_users():
    """Debug route to test user listing without auth."""
    with app.test_client() as client:
        response = client.get('/api/admin/users')
        return response.get_json(), response.status_code

@app.route('/api/debug/delete-user/<int:user_id>', methods=['POST'])
def debug_delete_user(user_id):
    """Debug route to test user deletion without auth requirements."""
    with app.test_client() as client:
        response = client.delete(f'/api/admin/users/{user_id}')
        return response.get_json(), response.status_code

@app.route('/api/debug/update-lot/<int:lot_id>', methods=['POST'])
def debug_update_lot(lot_id):
    """Debug route to test lot update without auth requirements."""
    data = request.get_json()
    print(f"[DEBUG] Update lot request: {data}")
    with app.test_client() as client:
        response = client.put(f'/api/admin/parking-lots/{lot_id}', json=data)
        return response.get_json(), response.status_code

@app.route('/api/debug/profile/<int:user_id>', methods=['GET'])
def debug_user_profile(user_id):
    """Debug route to test user profile without auth requirements."""
    print(f"[DEBUG] Getting profile for user ID: {user_id}")
    
    try:
        import sqlite3
        
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ? AND is_active = 0', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            profile_data = {
                'id': user['id'],
                'email': user['email'],
                'full_name': user['full_name'],
                'phone': user['phone'] or '',
                'address_line1': user['address_line1'] or '',
                'city': user['city'] or '',
                'state': user['state'] or '',
                'pin_code': user['pin_code'] or ''
            }
            
            return jsonify({
                'profile': profile_data,
                'type': 'user'
            }), 200
        else:
            return jsonify({'message': 'User not found'}), 404
            
    except Exception as e:
        print(f"[ERROR] Debug profile error: {e}")
        return jsonify({'message': f'Profile fetch failed: {str(e)}'}), 500

@app.route('/api/debug/test-login', methods=['POST'])
def debug_test_login():
    """Debug route to test login without frontend."""
    data = request.get_json()
    email = data.get('email', 'test@example.com')
    password = data.get('password', 'password123')
    
    print(f"[DEBUG] Test login for: {email}")
    
    try:
        with app.test_client() as client:
            response = client.post('/api/auth/user/login', 
                                 json={'email': email, 'password': password})
            return response.get_json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/parking-lots', methods=['GET'])
def debug_parking_lots():
    """Debug route to test parking lots endpoint."""
    print(f"[DEBUG] Testing parking lots endpoint")
    
    try:
        with app.test_client() as client:
            response = client.get('/api/admin/parking-lots')
            print(f"[DEBUG] Admin parking lots response status: {response.status_code}")
            print(f"[DEBUG] Admin parking lots response: {response.get_data(as_text=True)}")
            
            try:
                data = response.get_json()
                print(f"[DEBUG] Parsed JSON: {data}")
                return data, response.status_code
            except Exception as e:
                print(f"[DEBUG] JSON parsing error: {e}")
                return {"error": "Invalid JSON", "raw": response.get_data(as_text=True)}, response.status_code
                
    except Exception as e:
        print(f"[ERROR] Debug parking lots error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/add-sample-lots', methods=['POST'])
def debug_add_sample_lots():
    """Debug route to add sample parking lots."""
    print(f"[DEBUG] Adding sample parking lots")
    
    try:
        import sqlite3
        from datetime import datetime
        
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if parking lots already exist
        cursor.execute("SELECT COUNT(*) FROM parking_lots")
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"Database already has {existing_count} parking lots")
            conn.close()
            return jsonify({
                'message': f'Database already has {existing_count} parking lots',
                'existing_count': existing_count
            }), 200
        
        sample_lots = [
            {
                'name': 'Central Mall Parking',
                'address': '123 Main Street, Downtown',
                'pincode': '110001',
                'price_per_hour': 50.0,
                'total_slots': 20
            },
            {
                'name': 'City Hospital Parking',
                'address': '456 Healthcare Avenue',
                'pincode': '110002', 
                'price_per_hour': 30.0,
                'total_slots': 15
            },
            {
                'name': 'Metro Station Park & Ride',
                'address': '789 Transit Road',
                'pincode': '110003',
                'price_per_hour': 25.0,
                'total_slots': 30
            }
        ]
        
        created_lots = []
        for lot_data in sample_lots:
            print(f"Creating parking lot: {lot_data['name']}")
            
            # Insert parking lot
            cursor.execute('''
                INSERT INTO parking_lots (name, address, pincode, price_per_hour, total_slots, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                lot_data['name'],
                lot_data['address'],
                lot_data['pincode'],
                lot_data['price_per_hour'],
                lot_data['total_slots'],
                datetime.now().isoformat()
            ))
            
            lot_id = cursor.lastrowid
            
            # Create parking slots for the lot
            for slot_num in range(1, lot_data['total_slots'] + 1):
                cursor.execute('''
                    INSERT INTO parking_slots (lot_id, slot_number, is_available, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (lot_id, slot_num, 1, datetime.now().isoformat()))
            
            created_lots.append({
                'id': lot_id,
                'name': lot_data['name'],
                'total_slots': lot_data['total_slots']
            })
            
            print(f"  Created {lot_data['total_slots']} slots for lot ID {lot_id}")
        
        conn.commit()
        conn.close()
        
        print(f"Successfully created {len(sample_lots)} sample parking lots!")
        
        return jsonify({
            'message': f'Successfully created {len(sample_lots)} sample parking lots',
            'created_lots': created_lots
        }), 201
        
    except Exception as e:
        print(f"[ERROR] Error adding sample lots: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/check-db', methods=['GET'])
def debug_check_db():
    """Debug route to check database status."""
    try:
        import sqlite3
        import os
        
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        
        if not os.path.exists(DB_PATH):
            return jsonify({'error': f'Database file does not exist at {DB_PATH}'}), 404
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check parking_lots table
        cursor.execute("SELECT COUNT(*) FROM parking_lots")
        lots_count = cursor.fetchone()[0]
        
        # Check parking_slots table
        cursor.execute("SELECT COUNT(*) FROM parking_slots")
        slots_count = cursor.fetchone()[0]
        
        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute("SELECT id, name, address, total_slots FROM parking_lots LIMIT 3")
        sample_lots = [dict(row) for row in cursor.fetchall()]
        
        # Get sample users (handle potential column name variations)
        try:
            cursor.execute("SELECT id, email, full_name FROM users LIMIT 3")
            sample_users = [dict(row) for row in cursor.fetchall()]
        except Exception as user_error:
            print(f"[DEBUG] Error getting users: {user_error}")
            try:
                cursor.execute("SELECT id, email, name FROM users LIMIT 3")
                sample_users = [dict(row) for row in cursor.fetchall()]
            except:
                sample_users = []
        
        conn.close()
        
        return jsonify({
            'database_exists': True,
            'database_path': DB_PATH,
            'parking_lots_count': lots_count,
            'parking_slots_count': slots_count,
            'users_count': users_count,
            'sample_lots': sample_lots,
            'sample_users': sample_users
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/db-schema', methods=['GET'])
def debug_db_schema():
    """Debug route to check database schema."""
    try:
        import sqlite3
        
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_info = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            schema_info[table] = [{'name': col[1], 'type': col[2], 'not_null': col[3], 'pk': col[5]} for col in columns]
        
        conn.close()
        
        return jsonify({
            'tables': tables,
            'schema': schema_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/create-test-user', methods=['GET'])
def debug_create_test_user():
    """Debug route to create a test user."""
    try:
        import sqlite3
        import hashlib
        from datetime import datetime
        
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if test user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", ('test@example.com',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({
                'message': 'Test user already exists',
                'user_id': existing_user['id'],
                'email': 'test@example.com'
            }), 200
        
        # Create test user
        password_hash = hashlib.md5('test123'.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (full_name, email, phone, password, address_line1, city, state, pin_code, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Test User',
            'test@example.com',
            '1234567890',
            password_hash,
            '123 Test Street',
            'Test City',
            'Test State',
            '123456',
            datetime.now().isoformat()
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Test user created successfully',
            'user_id': user_id,
            'email': 'test@example.com',
            'password': 'test123'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/setup-test-user', methods=['GET'])
def debug_setup_test_user():
    """Create a test user and provide login instructions."""
    try:
        import sqlite3
        import hashlib
        from datetime import datetime
        
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # First, check if users table exists and what its structure is
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
        table_info = cursor.fetchone()
        
        if not table_info:
            # Create users table if it doesn't exist
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    password TEXT NOT NULL,
                    address_line1 TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code TEXT,
                    is_active INTEGER DEFAULT 0,
                    created_at TEXT
                )
            ''')
            print("Created users table")
        
        # Check if test user exists
        cursor.execute("SELECT id, email FROM users WHERE email = ?", ('test@example.com',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user['id']
            message = f"Test user already exists with ID {user_id}"
        else:
            # Create test user
            password_hash = hashlib.md5('test123'.encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO users (full_name, email, phone, password, address_line1, city, state, pin_code, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Test User',
                'test@example.com',
                '1234567890',
                password_hash,
                '123 Test Street',
                'Test City',
                'Test State',
                '123456',
                0,  # is_active = 0 means active user
                datetime.now().isoformat()
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            message = f"Test user created successfully with ID {user_id}"
        
        # Generate a test token for immediate use
        import time
        test_token = f"user_{user_id}_{int(time.time())}"
        
        conn.close()
        
        return jsonify({
            'message': message,
            'user_id': user_id,
            'test_credentials': {
                'email': 'test@example.com',
                'password': 'test123'
            },
            'test_token': test_token,
            'instructions': {
                '1': 'Use the test credentials to log in through the frontend',
                '2': 'Or use the test_token directly by setting localStorage.setItem("token", "' + test_token + '")',
                '3': 'Then refresh the user dashboard'
            }
        }), 201
        
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/debug/test-auth-flow', methods=['GET'])
def debug_test_auth_flow():
    """Test the complete authentication flow."""
    try:
        import sqlite3
        import hashlib
        from datetime import datetime
        
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_table_exists = cursor.fetchone() is not None
        
        if not users_table_exists:
            return jsonify({
                'error': 'Users table does not exist',
                'solution': 'Database schema is incomplete'
            }), 404
        
        # 2. Check if we have any users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        
        if user_count == 0:
            # Create a test user
            password_hash = hashlib.md5('test123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (full_name, email, phone, password, address_line1, city, state, pin_code, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Test User',
                'test@example.com',
                '1234567890',
                password_hash,
                '123 Test Street',
                'Test City',
                'Test State',
                '123456',
                0,
                datetime.now().isoformat()
            ))
            conn.commit()
            user_count = 1
        
        # 3. Get a test user
        cursor.execute("SELECT id, email, full_name FROM users LIMIT 1")
        test_user = cursor.fetchone()
        
        if not test_user:
            return jsonify({'error': 'No users found even after creation'}), 404
        
        # 4. Generate test token
        import time
        test_token = f"user_{test_user['id']}_{int(time.time())}"
        
        # 5. Test the profile endpoint directly
        with app.test_client() as client:
            profile_response = client.get('/api/auth/profile', 
                                        headers={'Authorization': f'Bearer {test_token}'})
            profile_status = profile_response.status_code
            profile_data = profile_response.get_data(as_text=True)
        
        # 6. Test parking lots endpoint
        with app.test_client() as client:
            lots_response = client.get('/api/parking-lots')
            lots_status = lots_response.status_code
            lots_data = lots_response.get_data(as_text=True)
        
        conn.close()
        
        return jsonify({
            'users_table_exists': users_table_exists,
            'user_count': user_count,
            'test_user': {
                'id': test_user['id'],
                'email': test_user['email'],
                'full_name': test_user['full_name']
            },
            'test_token': test_token,
            'profile_test': {
                'status': profile_status,
                'response': profile_data[:500] + '...' if len(profile_data) > 500 else profile_data
            },
            'parking_lots_test': {
                'status': lots_status,
                'response': lots_data[:500] + '...' if len(lots_data) > 500 else lots_data
            },
            'instructions': {
                'step1': f'Set token: localStorage.setItem("token", "{test_token}")',
                'step2': 'Go to UserDashboard and check browser console for debug messages',
                'step3': 'The profile and parking lots should now load'
            }
        }), 200
        
    except Exception as e:
        import traceback
@app.route('/api/debug/show-users', methods=['GET'])
def debug_show_users():
    """Show all users in the database with their details."""
    try:
        import sqlite3
        
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, full_name, password FROM users")
        users = cursor.fetchall()
        
        users_list = []
        for user in users:
            users_list.append({
                'id': user['id'],
                'email': user['email'], 
                'full_name': user['full_name'],
                'password_hash': user['password'][:20] + '...' if len(user['password']) > 20 else user['password']
            })
        
        conn.close()
        
        return jsonify({
            'total_users': len(users_list),
            'users': users_list,
            'note': 'Try logging in with one of these emails. If you know the original password, use that. Otherwise, I can reset a password for testing.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/reset-password', methods=['POST'])
def debug_reset_password():
    """Reset a user's password to a known value for testing."""
    try:
        import sqlite3
        import hashlib
        
        data = request.get_json()
        email = data.get('email')
        new_password = data.get('password', 'test123')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        DB_PATH = r'D:\MAD2\Parking App\instance\parking.db'
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': f'No user found with email: {email}'}), 404
        
        # Reset password using MD5 (matching the test user creation)
        password_hash = hashlib.md5(new_password.encode()).hexdigest()
        
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (password_hash, email))
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'Password reset successfully for {email}',
            'new_password': new_password,
            'email': email
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/frontend-test', methods=['GET'])
def debug_frontend_test():
    """Debug route to provide frontend testing info."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Frontend Debug Test</title>
        <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    </head>
    <body>
        <h1>Frontend Debug Test</h1>
        <div id="output"></div>
        
        <button onclick="testAPI()">Test Parking Lots API</button>
        <button onclick="checkToken()">Check Token</button>
        <button onclick="testLogin()">Test Login</button>
        
        <script>
            const output = document.getElementById('output');
            
            function log(message) {{
                output.innerHTML += '<div>' + new Date().toLocaleTimeString() + ': ' + message + '</div>';
            }}
            
            async function testAPI() {{
                try {{
                    log('Testing parking lots API...');
                    const response = await axios.get('/api/parking-lots');
                    log('API Response: ' + JSON.stringify(response.data, null, 2));
                }} catch (error) {{
                    log('API Error: ' + error.message);
                }}
            }}
            
            function checkToken() {{
                const token = localStorage.getItem('token');
                log('Token: ' + (token || 'No token found'));
            }}
            
            async function testLogin() {{
                try {{
                    log('Testing user login...');
                    const response = await axios.post('/api/auth/user/login', {{
                        email: 'test@example.com',
                        password: 'test123'
                    }});
                    log('Login Response: ' + JSON.stringify(response.data, null, 2));
                    if (response.data.token) {{
                        localStorage.setItem('token', response.data.token);
                        log('Token saved to localStorage');
                    }}
                }} catch (error) {{
                    log('Login Error: ' + error.message);
                    if (error.response) {{
                        log('Error Response: ' + JSON.stringify(error.response.data, null, 2));
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    """

# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@app.route('/')
def index():
    """Basic health check endpoint."""
    return {'message': 'Parking Management System API is running', 'status': 'healthy'}

@app.route('/health')
def health():
    """Health check endpoint."""
    return {'status': 'healthy', 'message': 'API is operational'}

@app.route('/api/debug/check-slots', methods=['GET'])
def check_slots():
    """Check and create parking slots if they don't exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if parking slots exist for lot_id = 1
        cursor.execute('SELECT COUNT(*) as count FROM parking_slots WHERE lot_id = 1')
        slot_count = cursor.fetchone()['count']
        
        if slot_count == 0:
            # Create slots for lot_id = 1 (20 slots as per the lot data)
            for slot_num in range(1, 21):
                cursor.execute('''
                    INSERT INTO parking_slots (slot_number, lot_id, is_available) 
                    VALUES (?, ?, 1)
                ''', (slot_num, 1))
            
            conn.commit()
            cursor.execute('SELECT COUNT(*) as count FROM parking_slots WHERE lot_id = 1')
            new_count = cursor.fetchone()['count']
            
            conn.close()
            return jsonify({
                'message': f'Created {new_count} parking slots for lot 1',
                'created_slots': new_count
            })
        else:
            # Get slot details
            cursor.execute('SELECT * FROM parking_slots WHERE lot_id = 1 ORDER BY slot_number')
            slots = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return jsonify({
                'message': f'Found {slot_count} existing slots for lot 1',
                'slots': slots
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# CSV EXPORT FUNCTIONALITY
# =============================================================================

import csv
import io
import threading
import time
from datetime import datetime

# Store export job status
export_jobs = {}

@app.route('/api/export/parking-history', methods=['POST'])
def export_parking_history():
    """Export user's parking history as CSV - Async Job"""
    print(f"[DEBUG] CSV Export request received")
    
    # Extract user ID from token
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Authorization token required'}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        if token.startswith('user_'):
            parts = token.split('_')
            if len(parts) >= 2:
                user_id = int(parts[1])
            else:
                return jsonify({'message': 'Invalid token format'}), 401
        else:
            return jsonify({'message': 'Invalid token'}), 401
    except (ValueError, IndexError):
        return jsonify({'message': 'Invalid token format'}), 401
    
    # Get export parameters
    export_data = request.get_json() or {}
    date_from = export_data.get('date_from')  # Format: YYYY-MM-DD
    date_to = export_data.get('date_to')      # Format: YYYY-MM-DD
    status_filter = export_data.get('status', 'all')  # all, active, completed
    
    # Generate unique job ID
    job_id = f"export_{user_id}_{int(time.time())}"
    
    # Initialize job status
    export_jobs[job_id] = {
        'status': 'started',
        'progress': 0,
        'message': 'Starting export...',
        'user_id': user_id,
        'created_at': datetime.now().isoformat(),
        'download_url': None,
        'file_name': None
    }
    
    # Start background job
    thread = threading.Thread(
        target=process_csv_export, 
        args=(job_id, user_id, date_from, date_to, status_filter)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'job_id': job_id,
        'message': 'Export job started successfully',
        'status': 'started'
    }), 202

def process_csv_export(job_id, user_id, date_from, date_to, status_filter):
    """Background process to generate CSV export"""
    try:
        print(f"[DEBUG] Starting CSV export job {job_id} for user {user_id}")
        
        # Update job status
        export_jobs[job_id]['status'] = 'processing'
        export_jobs[job_id]['progress'] = 10
        export_jobs[job_id]['message'] = 'Fetching booking data...'
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        base_query = '''
            SELECT 
                b.id as booking_record_id,
                b.booking_id,
                b.user_id,
                u.full_name as user_name,
                u.email as user_email,
                u.phone as user_phone,
                pl.id as lot_id,
                pl.name as lot_name,
                pl.address as lot_address,
                pl.pincode as lot_pincode,
                ps.id as slot_id,
                ps.slot_number as spot_id,
                b.vehicle_number,
                b.payment_method,
                b.start_time,
                b.end_time,
                b.planned_duration_hours,
                b.actual_duration_hours,
                b.planned_cost,
                b.final_cost,
                b.status,
                b.booking_created_at as booking_timestamp,
                b.completed_at,
                pl.price as hourly_rate,
                CASE 
                    WHEN b.status = 'completed' THEN 'Parking completed successfully'
                    WHEN b.status = 'active' THEN 'Currently parked'
                    ELSE 'Unknown status'
                END as remarks
            FROM bookings b
            LEFT JOIN users u ON b.user_id = u.id
            LEFT JOIN parking_lots pl ON b.lot_id = pl.id
            LEFT JOIN parking_slots ps ON b.slot_id = ps.id
            WHERE b.user_id = ?
        '''
        
        params = [user_id]
        
        # Add date filters
        if date_from:
            base_query += " AND DATE(b.start_time) >= ?"
            params.append(date_from)
        
        if date_to:
            base_query += " AND DATE(b.start_time) <= ?"
            params.append(date_to)
        
        # Add status filter
        if status_filter != 'all':
            base_query += " AND b.status = ?"
            params.append(status_filter)
        
        base_query += " ORDER BY b.start_time DESC"
        
        print(f"[DEBUG] Executing query: {base_query}")
        print(f"[DEBUG] Query params: {params}")
        
        export_jobs[job_id]['progress'] = 30
        export_jobs[job_id]['message'] = 'Processing booking records...'
        
        cursor.execute(base_query, params)
        bookings = cursor.fetchall()
        
        print(f"[DEBUG] Found {len(bookings)} booking records")
        
        export_jobs[job_id]['progress'] = 50
        export_jobs[job_id]['message'] = f'Found {len(bookings)} records. Generating CSV...'
        
        # Generate CSV content
        csv_content = generate_csv_content(bookings)
        
        export_jobs[job_id]['progress'] = 80
        export_jobs[job_id]['message'] = 'Saving CSV file...'
        
        # Save CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"parking_history_user_{user_id}_{timestamp}.csv"
        file_path = f"exports/{file_name}"
        
        # Create exports directory if it doesn't exist
        import os
        os.makedirs('exports', exist_ok=True)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write(csv_content)
        
        # Complete job
        export_jobs[job_id]['status'] = 'completed'
        export_jobs[job_id]['progress'] = 100
        export_jobs[job_id]['message'] = f'Export completed successfully. {len(bookings)} records exported.'
        export_jobs[job_id]['download_url'] = f'/api/download/{file_name}'
        export_jobs[job_id]['file_name'] = file_name
        export_jobs[job_id]['record_count'] = len(bookings)
        export_jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
        conn.close()
        print(f"[DEBUG] CSV export job {job_id} completed successfully")
        
    except Exception as e:
        print(f"[ERROR] CSV export job {job_id} failed: {str(e)}")
        export_jobs[job_id]['status'] = 'failed'
        export_jobs[job_id]['progress'] = 0
        export_jobs[job_id]['message'] = f'Export failed: {str(e)}'
        export_jobs[job_id]['error'] = str(e)

def generate_csv_content(bookings):
    """Generate CSV content from booking data"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV Headers
    headers = [
        'Booking Record ID',
        'Booking ID',
        'User Name',
        'User Email', 
        'User Phone',
        'Parking Lot ID',
        'Parking Lot Name',
        'Lot Address',
        'Lot Pincode',
        'Slot ID',
        'Spot ID (Slot Number)',
        'Vehicle Number',
        'Payment Method',
        'Start Time',
        'End Time',
        'Planned Duration (Hours)',
        'Actual Duration (Hours)',
        'Planned Cost (₹)',
        'Final Cost (₹)',
        'Hourly Rate (₹)',
        'Status',
        'Booking Timestamp',
        'Completion Timestamp',
        'Remarks'
    ]
    
    writer.writerow(headers)
    
    # Data rows
    for booking in bookings:
        row = [
            booking['booking_record_id'] or '',
            booking['booking_id'] or '',
            booking['user_name'] or '',
            booking['user_email'] or '',
            booking['user_phone'] or '',
            booking['lot_id'] or '',
            booking['lot_name'] or '',
            booking['lot_address'] or '',
            booking['lot_pincode'] or '',
            booking['slot_id'] or '',
            booking['spot_id'] or '',
            booking['vehicle_number'] or '',
            booking['payment_method'] or '',
            booking['start_time'] or '',
            booking['end_time'] or '',
            booking['planned_duration_hours'] or '',
            booking['actual_duration_hours'] or '',
            booking['planned_cost'] or '',
            booking['final_cost'] or '',
            booking['hourly_rate'] or '',
            booking['status'] or '',
            booking['booking_timestamp'] or '',
            booking['completed_at'] or '',
            booking['remarks'] or ''
        ]
        writer.writerow(row)
    
    return output.getvalue()

@app.route('/api/export/status/<job_id>', methods=['GET'])
def get_export_status(job_id):
    """Get export job status"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Authorization token required'}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        if token.startswith('user_'):
            parts = token.split('_')
            if len(parts) >= 2:
                user_id = int(parts[1])
            else:
                return jsonify({'message': 'Invalid token format'}), 401
        else:
            return jsonify({'message': 'Invalid token'}), 401
    except (ValueError, IndexError):
        return jsonify({'message': 'Invalid token format'}), 401
    
    if job_id not in export_jobs:
        return jsonify({'message': 'Job not found'}), 404
    
    job = export_jobs[job_id]
    
    # Verify job belongs to user
    if job['user_id'] != user_id:
        return jsonify({'message': 'Unauthorized access to job'}), 403
    
    return jsonify(job), 200

@app.route('/api/download/<file_name>', methods=['GET'])
def download_csv(file_name):
    """Download CSV file"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Authorization token required'}), 401
    
    try:
        from flask import send_file
        file_path = f"exports/{file_name}"
        
        if not os.path.exists(file_path):
            return jsonify({'message': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_name,
            mimetype='text/csv'
        )
    except Exception as e:
        return jsonify({'message': f'Download failed: {str(e)}'}), 500

@app.route('/api/export/jobs', methods=['GET'])
def get_user_export_jobs():
    """Get user's export jobs history"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Authorization token required'}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        if token.startswith('user_'):
            parts = token.split('_')
            if len(parts) >= 2:
                user_id = int(parts[1])
            else:
                return jsonify({'message': 'Invalid token format'}), 401
        else:
            return jsonify({'message': 'Invalid token'}), 401
    except (ValueError, IndexError):
        return jsonify({'message': 'Invalid token format'}), 401
    
    # Filter jobs for this user
    user_jobs = {
        job_id: job for job_id, job in export_jobs.items() 
        if job.get('user_id') == user_id
    }
    
    return jsonify(user_jobs), 200

if __name__ == '__main__':
    print("Starting Parking Management System...")
    print("Admin API endpoints available at: http://localhost:5001/api/admin/")
    print("User API endpoints available at: http://localhost:5001/api/user/")
    print("Database location: D:\\MAD2\\Parking App\\instance\\parking.db")
    app.run(debug=True, port=5001, host='0.0.0.0')
