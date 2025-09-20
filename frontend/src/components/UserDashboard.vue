<template>
  <div class="dashboard-container">
    <!-- Navigation Bar -->
    <nav class="navbar">
      <div class="nav-content">
        <!-- Logo and Welcome -->
        <div class="nav-left">
          <div class="logo">
            <span class="logo-icon">🅿️</span>
            <span class="logo-text">ParkEase</span>
          </div>
          <span class="welcome-text">Welcome, {{ userFullName }}</span>
        </div>
        
        <!-- Navigation Items -->
        <div class="nav-right">
          <button 
            :class="['nav-btn', { active: activeSection === 'dashboard' }]" 
            @click="activeSection = 'dashboard'"
          >
            Home
          </button>
          <button 
            :class="['nav-btn', { active: activeSection === 'profile' }]" 
            @click="activeSection = 'profile'"
          >
            Edit Profile
          </button>
          <button 
            :class="['nav-btn', { active: activeSection === 'history' }]" 
            @click="activeSection = 'history'"
          >
            Booking History
          </button>
          <button 
            :class="['nav-btn', { active: activeSection === 'export' }]" 
            @click="activeSection = 'export'"
          >
            Export Data
          </button>
          <button class="nav-btn logout-btn" @click="logout">Logout</button>
          
          <!-- Search Bar -->
          <div class="search-container">
            <input 
              v-model="searchQuery" 
              type="text" 
              class="search-input" 
              placeholder="Search by address or pincode..."
              @input="filterLots"
            />
            <span class="search-icon">🔍</span>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Dashboard Section -->
      <div v-if="activeSection === 'dashboard'">
        <!-- Recent Parking History -->
        <section class="history-section">
          <div class="section-header">
            <h3>Recent Parking History</h3>
          </div>
          <div class="table-container">
            <table class="history-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Location</th>
                  <th>Vehicle Number</th>
                  <th>Timestamp</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="recentBookings.length === 0">
                  <td colspan="5" style="text-align: center; color: #718096; padding: 32px;">
                    No recent bookings found. Start by booking a parking spot!
                  </td>
                </tr>
                <tr v-for="booking in recentBookings" :key="booking.id">
                  <td>{{ booking.id }}</td>
                  <td>{{ booking.lot_name || 'Unknown Location' }}</td>
                  <td>{{ booking.vehicle_number || 'N/A' }}</td>
                  <td>{{ formatDateTime(booking.start_time || booking.booking_start || booking.created_at) }}</td>
                  <td>
                    <button 
                      v-if="booking.is_active || booking.status === 'active'" 
                      class="action-btn release-btn"
                      @click="showReleaseModal(booking)"
                    >
                      Release
                    </button>
                    <span v-else class="status-badge parked-out">Parked Out</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Available Parking Lots -->
        <section class="lots-section">
          <div class="section-header">
            <h3>Available Parking Lots</h3>
          </div>
          <div class="table-container">
            <table class="lots-table">
              <thead>
                <tr>
                  <th>Lot Address</th>
                  <th>Availability</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filteredLots.length === 0">
                  <td colspan="3" style="text-align: center; color: #718096; padding: 32px;">
                    {{ searchQuery ? 'No parking lots match your search.' : 'No parking lots available. Please contact admin to add parking lots.' }}
                  </td>
                </tr>
                <tr v-for="lot in filteredLots" :key="lot.id">
                  <td>{{ lot.address || lot.name }}, PIN: {{ lot.pincode || lot.pin_code }}</td>
                  <td>{{ lot.available_slots || 0 }} slots available</td>
                  <td>
                    <button 
                      class="action-btn book-btn"
                      @click="showBookingModal(lot)"
                      :disabled="(lot.available_slots || 0) === 0"
                    >
                      Book
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>

      <!-- Profile Section -->
      <div v-if="activeSection === 'profile'" class="profile-section">
        <div class="section-header">
          <h3>Edit Profile</h3>
        </div>
        <div class="profile-form">
          <div class="form-row">
            <div class="form-group">
              <label>Full Name <span class="required">*</span></label>
              <input 
                v-model="userProfile.full_name" 
                type="text" 
                class="form-input"
                :placeholder="userProfile.full_name || 'Enter your full name'"
                required
              >
            </div>
            <div class="form-group">
              <label>Email <span class="required">*</span></label>
              <input 
                v-model="userProfile.email" 
                type="email" 
                class="form-input"
                :placeholder="userProfile.email || 'Enter your email'"
                required
              >
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Phone</label>
              <input 
                v-model="userProfile.phone" 
                type="tel" 
                class="form-input"
                :placeholder="userProfile.phone || 'Phone number'"
              >
            </div>
            <div class="form-group">
              <label>Address Line 1</label>
              <input 
                v-model="userProfile.address_line1" 
                type="text" 
                class="form-input"
                :placeholder="userProfile.address_line1 || 'Enter your address'"
              >
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>City</label>
              <input 
                v-model="userProfile.city" 
                type="text" 
                class="form-input"
                :placeholder="userProfile.city || 'Enter your city'"
              >
            </div>
            <div class="form-group">
              <label>State</label>
              <input 
                v-model="userProfile.state" 
                type="text" 
                class="form-input"
                :placeholder="userProfile.state || 'Enter your state'"
              >
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>PIN Code</label>
              <input 
                v-model="userProfile.pin_code" 
                type="text" 
                class="form-input"
                :placeholder="userProfile.pin_code || 'Enter your PIN code'"
                pattern="[0-9]{6}"
                maxlength="6"
              >
            </div>
          </div>
          
          <div class="form-actions">
            <button class="submit-btn" @click="updateProfile" :disabled="!isProfileValid">
              Update Profile
            </button>
            <button class="reset-btn" @click="resetProfile" type="button">
              Reset Changes
            </button>
          </div>
        </div>
      </div>

      <!-- Full Booking History -->
      <div v-if="activeSection === 'history'" class="full-history-section">
        <div class="section-header">
          <h3>Complete Booking History</h3>
        </div>
        <div class="table-container">
          <table class="history-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Location</th>
                <th>Vehicle Number</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Duration</th>
                <th>Cost</th>
                <th>Payment</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="allBookings.length === 0">
                <td colspan="9" style="text-align: center; color: #718096; padding: 32px;">
                  No booking history found.
                </td>
              </tr>
              <tr v-for="booking in allBookings" :key="booking.id">
                <td>{{ booking.id }}</td>
                <td>{{ booking.lot_name || 'Unknown Location' }}</td>
                <td>{{ booking.vehicle_number || 'N/A' }}</td>
                <td>{{ formatDateTime(booking.start_time || booking.booking_start || booking.created_at) }}</td>
                <td>{{ booking.end_time ? formatDateTime(booking.end_time) : (booking.booking_end ? formatDateTime(booking.booking_end) : 'Active') }}</td>
                <td>{{ calculateDuration(booking) }}</td>
                <td>₹{{ booking.final_cost || booking.planned_cost || 0 }}</td>
                <td>
                  <span v-if="booking.payment_method" :class="['payment-badge', booking.payment_method === 'pay_here' ? 'paid-online' : 'paid-counter']">
                    {{ booking.payment_method === 'pay_here' ? 'Paid Online' : 'Paid at Counter' }}
                  </span>
                  <span v-else class="payment-badge pending">Pending</span>
                </td>
                <td>
                  <span :class="['status-badge', (booking.is_active || booking.status === 'active') ? 'active' : 'completed']">
                    {{ (booking.is_active || booking.status === 'active') ? 'Active' : 'Completed' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Export Data Section -->
    <div v-if="activeSection === 'export'" class="export-section">
      <div class="section-header">
        <h3>Export Parking History</h3>
      </div>
      
      <!-- Export Form -->
      <div class="export-form">
        <div class="export-options">
          <div class="form-row">
            <div class="form-group">
              <label>From Date:</label>
              <input 
                v-model="exportForm.dateFrom" 
                type="date" 
                class="form-input"
                :max="exportForm.dateTo || new Date().toISOString().split('T')[0]"
              >
            </div>
            <div class="form-group">
              <label>To Date:</label>
              <input 
                v-model="exportForm.dateTo" 
                type="date" 
                class="form-input"
                :min="exportForm.dateFrom"
                :max="new Date().toISOString().split('T')[0]"
              >
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Status Filter:</label>
              <select v-model="exportForm.statusFilter" class="form-input">
                <option value="all">All Bookings</option>
                <option value="active">Active Only</option>
                <option value="completed">Completed Only</option>
              </select>
            </div>
            <div class="form-group">
              <label>Export Format:</label>
              <select v-model="exportForm.format" class="form-input">
                <option value="csv">CSV (Comma Separated Values)</option>
              </select>
            </div>
          </div>
          
          <div class="export-preview">
            <h4>Export Details:</h4>
            <div class="preview-info">
              <p><strong>Period:</strong> 
                {{ exportForm.dateFrom || 'All time' }} 
                {{ exportForm.dateFrom && exportForm.dateTo ? ' to ' + exportForm.dateTo : (exportForm.dateTo ? ' to ' + exportForm.dateTo : '') }}
              </p>
              <p><strong>Status:</strong> {{ exportForm.statusFilter === 'all' ? 'All bookings' : exportForm.statusFilter + ' bookings' }}</p>
              <p><strong>Format:</strong> {{ exportForm.format.toUpperCase() }} file</p>
              <p><strong>Estimated Records:</strong> {{ estimatedRecords }} bookings</p>
            </div>
          </div>
          
          <div class="export-actions">
            <button 
              @click="startExport" 
              :disabled="isExporting"
              class="export-btn"
            >
              <span v-if="!isExporting">📥 Start Export</span>
              <span v-else>⏳ Processing...</span>
            </button>
            <button @click="resetExportForm" class="reset-btn">Reset Form</button>
          </div>
        </div>
      </div>
      
      <!-- Export Jobs Status -->
      <div class="export-jobs" v-if="exportJobs.length > 0">
        <div class="section-header">
          <h4>Export Jobs History</h4>
          <button @click="refreshExportJobs" class="refresh-btn">🔄 Refresh</button>
        </div>
        
        <div class="jobs-list">
          <div v-for="job in exportJobs" :key="job.id" class="job-card" :class="job.status">
            <div class="job-header">
              <span class="job-id">Job #{{ job.id.split('_').pop() }}</span>
              <span class="job-status" :class="job.status">{{ job.status.toUpperCase() }}</span>
            </div>
            
            <div class="job-details">
              <p><strong>Created:</strong> {{ formatDateTime(job.created_at) }}</p>
              <p><strong>Status:</strong> {{ job.message }}</p>
              <p v-if="job.record_count"><strong>Records:</strong> {{ job.record_count }} bookings</p>
              
              <!-- Progress Bar -->
              <div v-if="job.status === 'processing' || job.status === 'started'" class="progress-container">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: job.progress + '%' }"></div>
                </div>
                <span class="progress-text">{{ job.progress }}%</span>
              </div>
              
              <!-- Download Button -->
              <div v-if="job.status === 'completed' && job.download_url" class="job-actions">
                <button @click="downloadFile(job)" class="download-btn">
                  📄 Download {{ job.file_name }}
                </button>
                <span class="file-info">
                  Completed: {{ formatDateTime(job.completed_at) }}
                </span>
              </div>
              
              <!-- Error Message -->
              <div v-if="job.status === 'failed'" class="error-message">
                <p><strong>Error:</strong> {{ job.error || 'Export failed' }}</p>
                <button @click="retryExport(job)" class="retry-btn">🔄 Retry</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Export Information -->
      <div class="export-info">
        <div class="info-card">
          <h4>📋 CSV Export Includes:</h4>
          <ul>
            <li><strong>Booking Details:</strong> Booking ID, timestamps, duration</li>
            <li><strong>Location Info:</strong> Parking lot name, address, slot details</li>
            <li><strong>Vehicle Info:</strong> Vehicle number, payment method</li>
            <li><strong>Cost Details:</strong> Planned cost, final cost, hourly rates</li>
            <li><strong>Status & Remarks:</strong> Booking status and additional notes</li>
          </ul>
        </div>
        
        <div class="info-card">
          <h4>⚡ Export Process:</h4>
          <ol>
            <li>Configure your export options above</li>
            <li>Click "Start Export" to begin processing</li>
            <li>Monitor progress in the jobs list</li>
            <li>Download your CSV file when ready</li>
            <li>Files are available for 24 hours</li>
          </ol>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div v-if="showBookModal" class="modal-overlay" @click="closeBookingModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4>Book Parking Spot</h4>
          <button class="close-btn" @click="closeBookingModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="booking-details">
            <div class="detail-row">
              <label>Booking ID:</label>
              <span>{{ generateBookingId() }}</span>
            </div>
            <div class="detail-row">
              <label>Vehicle Number:</label>
              <input v-model="bookingForm.vehicleNumber" type="text" class="modal-input" placeholder="Enter vehicle number">
            </div>
            <div class="detail-row">
              <label>Start Time:</label>
              <input v-model="bookingForm.startTime" type="datetime-local" class="modal-input">
            </div>
            <div class="detail-row">
              <label>End Time:</label>
              <input v-model="bookingForm.endTime" type="datetime-local" class="modal-input">
            </div>
            <div class="detail-row">
              <label>Expected Total Price:</label>
              <span class="price">
                {{ bookingForm.startTime && bookingForm.endTime ? `₹${calculatePrice()}` : 'Please select start and end time' }}
              </span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="book-confirm-btn" @click="confirmBooking" :disabled="!isBookingValid">
            Book
          </button>
        </div>
      </div>
    </div>

    <!-- Release Modal -->
    <div v-if="isReleaseModalOpen" class="modal-overlay" @click="closeReleaseModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h4>Release Parking Spot</h4>
          <button class="close-btn" @click="closeReleaseModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="release-details">
            <div class="detail-row">
              <label>Booking ID:</label>
              <span>{{ releaseBooking.booking_id || releaseBooking.id }}</span>
            </div>
            <div class="detail-row">
              <label>Vehicle Number:</label>
              <span>{{ releaseBooking.vehicle_number }}</span>
            </div>
            <div class="detail-row">
              <label>Start Time:</label>
              <span>{{ formatDateTime(releaseBooking.start_time || releaseBooking.booking_start) }}</span>
            </div>
            <div class="detail-row">
              <label>Release Time:</label>
              <span>{{ formatDateTime(new Date()) }}</span>
            </div>
            <div class="detail-row">
              <label>Total Duration:</label>
              <span>{{ calculateCurrentDuration() }} hours</span>
            </div>
            <div class="detail-row">
              <label>Total Amount:</label>
              <span class="price">₹{{ calculateFinalPrice() }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer payment-options">
          <button class="payment-btn pay-here-btn" @click="confirmRelease('pay_here')">
            Pay Here - ₹{{ calculateFinalPrice() }}
          </button>
          <button class="payment-btn pay-counter-btn" @click="confirmRelease('pay_counter')">
            Pay at Counter
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message.text" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      // Navigation
      activeSection: 'dashboard',
      
      // User data
      userProfile: {
        full_name: '',
        email: '',
        phone: '',
        address_line1: '',
        city: '',
        state: '',
        pin_code: ''
      },
      originalProfile: {}, // Store original profile for reset functionality
      
      // Parking data
      allLots: [],
      filteredLots: [],
      searchQuery: '',
      recentBookings: [],
      allBookings: [],
      
      // Modals
      showBookModal: false,
      isReleaseModalOpen: false,
      selectedLot: null,
      releaseBooking: null,
      
      // Booking form
      bookingForm: {
        vehicleNumber: '',
        startTime: '',
        endTime: ''
      },
      
      // UI state
      message: {
        text: '',
        type: ''
      },
      
      // Export functionality
      exportForm: {
        dateFrom: '',
        dateTo: '',
        statusFilter: 'all',
        format: 'csv'
      },
      isExporting: false,
      exportJobs: [],
      currentExportJobId: null,
      exportJobCheckInterval: null
    };
  },
  
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token');
    },
    
    userFullName() {
      console.log('Computing userFullName...');
      console.log('Current userProfile:', this.userProfile);
      
      const fullName = this.userProfile?.full_name || '';
      console.log('Extracted full name:', fullName);
      
      if (fullName) {
        // Extract first name (first word before any space)
        const firstName = fullName.split(' ')[0];
        console.log('First name extracted:', firstName);
        return firstName;
      }
      
      console.log('No name found, returning "User"');
      return 'User';
    },
    
    isBookingValid() {
      return this.bookingForm.vehicleNumber && 
             this.bookingForm.startTime && 
             this.bookingForm.endTime &&
             new Date(this.bookingForm.endTime) > new Date(this.bookingForm.startTime);
    },
    
    isProfileValid() {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return this.userProfile.full_name && 
             this.userProfile.full_name.trim().length > 0 &&
             this.userProfile.email && 
             emailRegex.test(this.userProfile.email);
    },
    
    estimatedRecords() {
      // Estimate records based on current bookings and filters
      let count = this.allBookings.length;
      
      if (this.exportForm.statusFilter !== 'all') {
        count = this.allBookings.filter(booking => 
          booking.status === this.exportForm.statusFilter
        ).length;
      }
      
      if (this.exportForm.dateFrom || this.exportForm.dateTo) {
        // This is a rough estimate since we don't filter by date in memory
        count = Math.floor(count * 0.8); // Assume 80% fall within date range
      }
      
      return count;
    }
  },
  
  async mounted() {
    if (!this.isLoggedIn) {
      this.$router.push('/user/login');
      return;
    }
    
    await this.loadUserProfile();
    await this.loadParkingLots();
    await this.loadBookingHistory();
    await this.loadExportJobs(); // Load existing export jobs
    this.setDefaultTimes();
  },
  
  beforeDestroy() {
    // Clean up polling interval
    this.stopJobStatusPolling();
  },
  
  methods: {
    // =============================================================================
    // DATA LOADING METHODS
    // =============================================================================
    
    async loadUserProfile() {
      try {
        console.log('[DEBUG] Starting to load user profile...');
        const token = localStorage.getItem('token');
        console.log('[DEBUG] Token from localStorage:', token ? `${token.substr(0, 20)}...` : 'null');
        
        const response = await axios.get('/api/auth/profile', {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        console.log('[DEBUG] Profile response received:');
        console.log('  - Status:', response.status);
        console.log('  - Raw profile response:', response.data);
        
        // Backend returns profile data wrapped in a 'profile' object
        // Response structure: { profile: {...}, type: 'user' }
        if (response.data.profile) {
          console.log('[DEBUG] Using profile data from response.data.profile');
          this.userProfile = {
            full_name: response.data.profile.full_name || response.data.profile.name || '',
            email: response.data.profile.email || '',
            phone: response.data.profile.phone || '',
            address_line1: response.data.profile.address_line1 || '',
            city: response.data.profile.city || '',
            state: response.data.profile.state || '',
            pin_code: response.data.profile.pin_code || ''
          };
        } else {
          console.log('[DEBUG] Using fallback profile data structure');
          // Fallback in case backend structure changes
          this.userProfile = {
            full_name: response.data.full_name || response.data.name || '',
            email: response.data.email || '',
            phone: response.data.phone || '',
            address_line1: response.data.address_line1 || '',
            city: response.data.city || '',
            state: response.data.state || '',
            pin_code: response.data.pin_code || ''
          };
        }
        
        console.log('[DEBUG] Final userProfile object:', this.userProfile);
        console.log('[DEBUG] userProfile.full_name:', this.userProfile.full_name);
        console.log('[DEBUG] userProfile.email:', this.userProfile.email);
        
        // Store original profile for reset functionality
        this.originalProfile = { ...this.userProfile };
        
        // Force reactivity update
        this.$forceUpdate();
        
        console.log('[SUCCESS] User profile loaded successfully');
      } catch (error) {
        console.error('[ERROR] Error loading user profile:', error);
        console.error('  - Error message:', error.message);
        console.error('  - Error response:', error.response);
        if (error.response) {
          console.error('  - Response status:', error.response.status);
          console.error('  - Response data:', error.response.data);
        }
        this.showMessage('Failed to load user profile', 'error');
      }
    },
    
    async loadParkingLots() {
      try {
        console.log('[DEBUG] Starting to load parking lots...');
        console.log('[DEBUG] Making request to /api/parking-lots');
        
        const response = await axios.get('/api/parking-lots');
        console.log('[DEBUG] Response received:');
        console.log('  - Status:', response.status);
        console.log('  - Data type:', typeof response.data);
        console.log('  - Data is array:', Array.isArray(response.data));
        console.log('  - Data length:', response.data?.length);
        console.log('  - Raw parking lots data:', response.data);
        
        if (!Array.isArray(response.data)) {
          console.error('[ERROR] Response data is not an array:', response.data);
          this.showMessage('Invalid parking lots data format', 'error');
          return;
        }
        
        this.allLots = response.data.map((lot, index) => {
          console.log(`[DEBUG] Processing lot ${index + 1}:`, lot);
          
          // Use available_slots from API response, or calculate from slots array if available
          const availableSlots = lot.available_slots !== undefined ? 
            lot.available_slots :
            (lot.slots ? 
              lot.slots.filter(slot => slot.is_available).length : 
              lot.total_slots); // Default to total if no slots data
          
          const processedLot = {
            ...lot,
            available_slots: availableSlots
          };
          
          console.log(`[DEBUG] Processed lot ${index + 1}:`, processedLot);
          return processedLot;
        });
        
        this.filteredLots = [...this.allLots];
        console.log('[DEBUG] Final results:');
        console.log('  - allLots length:', this.allLots.length);
        console.log('  - filteredLots length:', this.filteredLots.length);
        console.log('  - Processed parking lots:', this.allLots);
        console.log('  - Filtered lots for display:', this.filteredLots);
        
        if (this.allLots.length === 0) {
          console.warn('[WARNING] No parking lots loaded');
        } else {
          console.log(`[SUCCESS] Successfully loaded ${this.allLots.length} parking lots`);
        }
        
      } catch (error) {
        console.error('[ERROR] Error loading parking lots:', error);
        console.error('  - Error message:', error.message);
        console.error('  - Error response:', error.response);
        if (error.response) {
          console.error('  - Response status:', error.response.status);
          console.error('  - Response data:', error.response.data);
        }
        this.showMessage('Failed to load parking lots', 'error');
      }
    },
    
    async loadBookingHistory() {
      try {
        const response = await axios.get('/api/my-bookings', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        console.log('Raw booking data:', response.data);
        
        this.allBookings = response.data;
        this.recentBookings = this.allBookings.slice(0, 3);
        console.log('Processed bookings:', this.allBookings);
        console.log('Recent bookings:', this.recentBookings);
        
        // Debug: Check which bookings should show release button
        this.recentBookings.forEach((booking, index) => {
          console.log(`Booking ${index}:`, {
            id: booking.id,
            is_active: booking.is_active,
            status: booking.status,
            shouldShowRelease: booking.is_active || booking.status === 'active'
          });
        });
      } catch (error) {
        console.error('Error loading booking history:', error);
        this.showMessage('Failed to load booking history', 'error');
        
        // Set empty arrays as fallback
        this.allBookings = [];
        this.recentBookings = [];
      }
    },
    
    // =============================================================================
    // SEARCH AND FILTER METHODS
    // =============================================================================
    
    filterLots() {
      if (!this.searchQuery.trim()) {
        this.filteredLots = [...this.allLots];
        return;
      }
      
      const query = this.searchQuery.toLowerCase();
      this.filteredLots = this.allLots.filter(lot => {
        const address = (lot.address || '').toLowerCase();
        const name = (lot.name || '').toLowerCase();
        const pincode = (lot.pincode || lot.pin_code || '').toString().toLowerCase();
        
        return address.includes(query) || 
               pincode.includes(query) || 
               name.includes(query);
      });
    },
    
    // =============================================================================
    // BOOKING METHODS
    // =============================================================================
    
    showBookingModal(lot) {
      this.selectedLot = lot;
      this.showBookModal = true;
      this.setDefaultTimes();
    },
    
    closeBookingModal() {
      this.showBookModal = false;
      this.selectedLot = null;
      this.resetBookingForm();
    },
    
    setDefaultTimes() {
      // Get current time and add 2 hours
      const now = new Date();
      const later = new Date(now.getTime() + 2 * 60 * 60 * 1000); // 2 hours later
      
      this.bookingForm.startTime = this.formatDateTimeLocal(now);
      this.bookingForm.endTime = this.formatDateTimeLocal(later);
    },
    
    resetBookingForm() {
      this.bookingForm = {
        vehicleNumber: '',
        startTime: '',
        endTime: ''
      };
    },
    
    generateBookingId() {
      return 'PK' + Date.now().toString().slice(-8);
    },
    
    calculatePrice() {
      if (!this.bookingForm.startTime || !this.bookingForm.endTime || !this.selectedLot) {
        return 0;
      }
      
      const start = new Date(this.bookingForm.startTime);
      const end = new Date(this.bookingForm.endTime);
      
      // Check if end time is after start time
      if (end <= start) {
        return 0;
      }
      
      const hours = Math.ceil((end - start) / (1000 * 60 * 60));
      const pricePerHour = this.selectedLot.price_per_hour || 50;
      
      return Math.max(0, hours * pricePerHour);
    },
    
    calculateDurationHours() {
      if (!this.bookingForm.startTime || !this.bookingForm.endTime) {
        return 1; // Default 1 hour
      }
      
      const start = new Date(this.bookingForm.startTime);
      const end = new Date(this.bookingForm.endTime);
      
      if (end <= start) {
        return 1; // Minimum 1 hour
      }
      
      const hours = Math.ceil((end - start) / (1000 * 60 * 60));
      return Math.max(1, hours); // Minimum 1 hour
    },
    
    async confirmBooking() {
      try {
        // Find an available slot in the selected lot
        let availableSlotId = null;
        
        // Check if the lot has slots data and find first available slot
        if (this.selectedLot.slots && this.selectedLot.slots.length > 0) {
          const availableSlot = this.selectedLot.slots.find(slot => slot.is_available);
          if (availableSlot) {
            availableSlotId = availableSlot.id;
          }
        }
        
        // If no slot found in cached data, try to get fresh slot data
        if (!availableSlotId) {
          try {
            const slotResponse = await axios.get(`/api/parking-lots/${this.selectedLot.id}/slots`);
            const availableSlot = slotResponse.data.find(slot => slot.is_available);
            if (availableSlot) {
              availableSlotId = availableSlot.id;
            }
          } catch (slotError) {
            console.error('Error fetching slots:', slotError);
          }
        }
        
        // If still no slot available, show error
        if (!availableSlotId) {
          this.showMessage('No available slots in this parking lot', 'error');
          return;
        }
        
        const bookingData = {
          booking_id: this.generateBookingId(), // Send the generated booking ID
          lot_id: this.selectedLot.id,
          slot_id: availableSlotId, // Use the found available slot
          vehicle_number: this.bookingForm.vehicleNumber,
          start_time: this.bookingForm.startTime,
          end_time: this.bookingForm.endTime,
          duration_hours: this.calculateDurationHours(),
          planned_cost: this.calculatePrice(),
          payment_method: 'pay_here' // Default payment method
        };
        
        console.log('Booking data:', bookingData);
        
        const response = await axios.post('/api/book-slot', bookingData, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        this.showMessage('Parking spot booked successfully!', 'success');
        this.closeBookingModal();
        await this.loadBookingHistory();
        await this.loadParkingLots();
        
      } catch (error) {
        console.error('Error booking parking:', error);
        this.showMessage(error.response?.data?.message || 'Failed to book parking', 'error');
      }
    },
    
    // =============================================================================
    // RELEASE METHODS
    // =============================================================================
    
    showReleaseModal(booking) {
      console.log('showReleaseModal called with booking:', booking);
      console.log('Booking structure:');
      console.log('  - id:', booking.id);
      console.log('  - booking_id:', booking.booking_id);
      console.log('  - slot_id:', booking.slot_id);
      console.log('  - lot_id:', booking.lot_id);
      console.log('  - is_active:', booking.is_active);
      console.log('  - status:', booking.status);
      console.log('  - vehicle_number:', booking.vehicle_number);
      console.log('  - start_time:', booking.start_time);
      console.log('  - booking_start:', booking.booking_start);
      console.log('  - created_at:', booking.created_at);
      
      this.releaseBooking = booking;
      this.isReleaseModalOpen = true;
    },
    
    closeReleaseModal() {
      this.isReleaseModalOpen = false;
      this.releaseBooking = null;
    },
    
    calculateCurrentDuration() {
      if (!this.releaseBooking) return 0;
      
      // Get start time from multiple possible sources - backend sends 'start_time' field
      let startTimeString = this.releaseBooking.start_time || 
                           this.releaseBooking.booking_start || 
                           this.releaseBooking.created_at;
      
      if (!startTimeString) {
        console.error('No start time found in booking:', this.releaseBooking);
        return 1; // Default to 1 hour
      }
      
      // Parse the start time - backend sends IST times in ISO format
      const start = new Date(startTimeString);
      // Get current time in IST for proper comparison
      const now = new Date();
      
      console.log('Duration calculation:');
      console.log('Raw start time string:', startTimeString);
      console.log('Parsed start time:', start);
      console.log('Current time:', now);
      console.log('Time difference (ms):', now - start);
      console.log('Time difference (minutes):', (now - start) / (1000 * 60));
      
      // Validate the parsed date
      if (isNaN(start.getTime())) {
        console.error('Invalid start time:', startTimeString);
        return 1; // Default to 1 hour
      }
      
      // Calculate duration in hours
      // Both times are now in the same timezone context (browser local)
      // The backend IST time is automatically converted by JavaScript Date parsing
      const totalMinutes = (now - start) / (1000 * 60);
      const hours = Math.ceil(totalMinutes / 60);
      
      console.log('Total minutes:', totalMinutes);
      console.log('Calculated hours (ceiled):', hours);
      
      // Ensure minimum 1 hour, maximum reasonable duration (24 hours)
      const finalHours = Math.max(1, Math.min(Math.abs(hours), 24));
      
      console.log('Final duration hours:', finalHours);
      return finalHours;
    },
    
    calculateFinalPrice() {
      if (!this.releaseBooking) return 0;
      
      const duration = this.calculateCurrentDuration();
      
      // Get price per hour from multiple possible sources
      let pricePerHour = 50; // Default fallback
      
      if (this.releaseBooking.price_per_hour) {
        pricePerHour = this.releaseBooking.price_per_hour;
      } else if (this.releaseBooking.hourly_rate) {
        pricePerHour = this.releaseBooking.hourly_rate;
      } else {
        // Try to get price from the selected lot if available
        const lotId = this.releaseBooking.lot_id;
        const lot = this.allLots.find(l => l.id === lotId);
        if (lot && lot.price_per_hour) {
          pricePerHour = lot.price_per_hour;
        }
      }
      
      console.log('Price calculation:');
      console.log('Duration:', duration, 'hours');
      console.log('Price per hour:', pricePerHour);
      console.log('Total:', duration * pricePerHour);
      
      return duration * pricePerHour;
    },
    
    async confirmRelease(paymentMethod = 'pay_here') {
      try {
        // Debug logging to understand the booking structure
        console.log('=== RELEASE BOOKING DEBUG ===');
        console.log('Full releaseBooking object:', this.releaseBooking);
        console.log('releaseBooking.slot_id:', this.releaseBooking.slot_id);
        console.log('releaseBooking.id:', this.releaseBooking.id);
        console.log('releaseBooking.booking_start:', this.releaseBooking.booking_start);
        console.log('releaseBooking.price_per_hour:', this.releaseBooking.price_per_hour);
        console.log('releaseBooking.hourly_rate:', this.releaseBooking.hourly_rate);
        console.log('Calculated duration:', this.calculateCurrentDuration());
        console.log('Calculated final price:', this.calculateFinalPrice());
        console.log('===========================');
        
        // Ensure we have a valid slot_id
        const slotId = this.releaseBooking.slot_id;
        if (!slotId) {
          console.error('No slot_id found in booking:', this.releaseBooking);
          this.showMessage('Error: Unable to find slot information for this booking', 'error');
          return;
        }
        
        const finalCost = this.calculateFinalPrice();
        const duration = this.calculateCurrentDuration();
        
        const releaseData = {
          slot_id: slotId,
          payment_method: paymentMethod, // 'pay_here' or 'pay_counter'
          final_cost: finalCost,
          duration_hours: duration
        };
        
        console.log('Release data being sent to API:', releaseData);
        
        const response = await axios.post('/api/release-slot', releaseData, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        console.log('Release API response:', response.data);
        
        if (paymentMethod === 'pay_here') {
          this.showMessage(`Payment successful! Parking released. Total cost: ₹${finalCost}`, 'success');
        } else {
          this.showMessage(`Parking released successfully! Please pay ₹${finalCost} at the counter.`, 'success');
        }
        
        this.closeReleaseModal();
        await this.loadBookingHistory();
        await this.loadParkingLots();
        
      } catch (error) {
        console.error('Error releasing parking:', error);
        console.error('Error response:', error.response?.data);
        this.showMessage(error.response?.data?.message || 'Failed to release parking', 'error');
      }
    },
    
    // =============================================================================
    // PROFILE METHODS
    // =============================================================================
    
    async updateProfile() {
      try {
        // Validate required fields
        if (!this.userProfile.full_name || !this.userProfile.email) {
          this.showMessage('Full name and email are required', 'error');
          return;
        }

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(this.userProfile.email)) {
          this.showMessage('Please enter a valid email address', 'error');
          return;
        }

        // Show loading state
        const originalText = 'Update Profile';
        const updateBtn = document.querySelector('.submit-btn');
        if (updateBtn) {
          updateBtn.textContent = 'Updating...';
          updateBtn.disabled = true;
        }

        const response = await axios.put('/api/auth/profile', this.userProfile, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });

        this.showMessage('Profile updated successfully!', 'success');
        
        // Update local profile data with response
        if (response.data.profile) {
          this.userProfile = {
            full_name: response.data.profile.full_name || '',
            email: response.data.profile.email || '',
            phone: response.data.profile.phone || '',
            address_line1: response.data.profile.address_line1 || '',
            city: response.data.profile.city || '',
            state: response.data.profile.state || '',
            pin_code: response.data.profile.pin_code || ''
          };
        }

        // Reset button state
        if (updateBtn) {
          updateBtn.textContent = originalText;
          updateBtn.disabled = false;
        }

      } catch (error) {
        console.error('Error updating profile:', error);
        
        // Reset button state
        const updateBtn = document.querySelector('.submit-btn');
        if (updateBtn) {
          updateBtn.textContent = 'Update Profile';
          updateBtn.disabled = false;
        }

        const errorMessage = error.response?.data?.message || 'Failed to update profile';
        this.showMessage(errorMessage, 'error');
      }
    },
    
    resetProfile() {
      // Reset profile to original values
      this.userProfile = { ...this.originalProfile };
      this.showMessage('Profile changes reset', 'success');
    },
    
    // =============================================================================
    // UTILITY METHODS
    // =============================================================================
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      });
    },
    
    formatDateTimeLocal(date) {
      // Format date for datetime-local input (always uses local browser timezone)
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    },
    
    calculateDuration(booking) {
      // Handle different column name formats from backend - backend sends 'start_time'
      const startTime = booking.start_time || booking.booking_start;
      const endTime = booking.end_time || booking.booking_end || booking.completed_at;
      
      if (!startTime) return 'N/A';
      
      const start = new Date(startTime);
      const end = endTime ? new Date(endTime) : new Date();
      
      // Calculate duration directly - JavaScript Date automatically handles timezone conversion
      // Backend sends IST times, JavaScript converts them to browser local time for calculation
      const timeDiff = end - start;
      const hours = Math.ceil(timeDiff / (1000 * 60 * 60));
      
      // Ensure positive duration and minimum 1 hour
      const finalHours = Math.max(1, Math.abs(hours));
      
      return `${finalHours}h`;
    },
    
    showMessage(text, type) {
      this.message = { text, type };
      setTimeout(() => {
        this.message = { text: '', type: '' };
      }, 5000);
    },
    
    // =============================================================================
    // EXPORT FUNCTIONALITY
    // =============================================================================
    
    async startExport() {
      if (this.isExporting) return;
      
      this.isExporting = true;
      
      try {
        const exportData = {
          date_from: this.exportForm.dateFrom || null,
          date_to: this.exportForm.dateTo || null,
          status: this.exportForm.statusFilter,
          format: this.exportForm.format
        };
        
        console.log('Starting export with data:', exportData);
        
        const response = await axios.post('/api/export/parking-history', exportData, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        if (response.status === 202) {
          this.currentExportJobId = response.data.job_id;
          this.showMessage('Export job started successfully! You will be notified when it\'s ready.', 'success');
          
          // Start polling for job status
          this.startJobStatusPolling();
          
          // Refresh export jobs list
          await this.loadExportJobs();
        }
        
      } catch (error) {
        console.error('Error starting export:', error);
        this.showMessage(`Export failed: ${error.response?.data?.message || error.message}`, 'error');
      } finally {
        this.isExporting = false;
      }
    },
    
    startJobStatusPolling() {
      if (this.exportJobCheckInterval) {
        clearInterval(this.exportJobCheckInterval);
      }
      
      this.exportJobCheckInterval = setInterval(async () => {
        if (this.currentExportJobId) {
          await this.checkJobStatus(this.currentExportJobId);
        }
      }, 3000); // Check every 3 seconds
    },
    
    async checkJobStatus(jobId) {
      try {
        const response = await axios.get(`/api/export/status/${jobId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        const job = response.data;
        
        // Update job in the list
        const jobIndex = this.exportJobs.findIndex(j => j.id === jobId);
        if (jobIndex !== -1) {
          this.$set(this.exportJobs, jobIndex, { ...job, id: jobId });
        } else {
          this.exportJobs.unshift({ ...job, id: jobId });
        }
        
        // Check if job is complete
        if (job.status === 'completed') {
          this.showMessage(`Export completed! ${job.record_count} records exported. Download is ready.`, 'success');
          this.stopJobStatusPolling();
        } else if (job.status === 'failed') {
          this.showMessage(`Export failed: ${job.message}`, 'error');
          this.stopJobStatusPolling();
        }
        
      } catch (error) {
        console.error('Error checking job status:', error);
      }
    },
    
    stopJobStatusPolling() {
      if (this.exportJobCheckInterval) {
        clearInterval(this.exportJobCheckInterval);
        this.exportJobCheckInterval = null;
      }
      this.currentExportJobId = null;
    },
    
    async loadExportJobs() {
      try {
        const response = await axios.get('/api/export/jobs', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        
        // Convert object to array and sort by creation time
        this.exportJobs = Object.entries(response.data)
          .map(([id, job]) => ({ ...job, id }))
          .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
          
        console.log('Loaded export jobs:', this.exportJobs);
        
      } catch (error) {
        console.error('Error loading export jobs:', error);
      }
    },
    
    async refreshExportJobs() {
      await this.loadExportJobs();
      this.showMessage('Export jobs refreshed', 'success');
    },
    
    async downloadFile(job) {
      try {
        const response = await axios.get(job.download_url, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          responseType: 'blob'
        });
        
        // Create download link
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = job.file_name;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        this.showMessage(`Downloaded ${job.file_name} successfully!`, 'success');
        
      } catch (error) {
        console.error('Error downloading file:', error);
        this.showMessage(`Download failed: ${error.response?.data?.message || error.message}`, 'error');
      }
    },
    
    async retryExport(job) {
      // Restart the export with the same parameters
      // Extract parameters from job (if available) or use current form
      await this.startExport();
    },
    
    resetExportForm() {
      this.exportForm = {
        dateFrom: '',
        dateTo: '',
        statusFilter: 'all',
        format: 'csv'
      };
      this.showMessage('Export form reset', 'success');
    },
    
    logout() {
      // Clear export polling when logging out
      this.stopJobStatusPolling();
      localStorage.removeItem('token');
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
/* =============================================================================
   DASHBOARD CONTAINER & LAYOUT
============================================================================= */

.dashboard-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* =============================================================================
   NAVIGATION BAR
============================================================================= */

.navbar {
  background: rgba(173, 216, 230, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 0;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: #2d3748;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
}

.welcome-text {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  margin-left: 16px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.nav-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: transparent;
  color: #2d3748;
  font-size: 14px;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.nav-btn.active {
  background: #667eea;
  color: white;
}

.logout-btn {
  background: #e53e3e !important;
  color: white !important;
}

.logout-btn:hover {
  background: #c53030 !important;
}

.search-container {
  position: relative;
  margin-left: 16px;
}

.search-input {
  padding: 10px 40px 10px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 25px;
  font-size: 14px;
  width: 280px;
  background: rgba(255, 255, 255, 0.9);
  color: #2d3748;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #718096;
  font-size: 16px;
}

/* =============================================================================
   MAIN CONTENT
============================================================================= */

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* =============================================================================
   SECTIONS
============================================================================= */

.history-section,
.lots-section,
.profile-section,
.full-history-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.section-header {
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 16px;
  margin-bottom: 24px;
}

.section-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 24px;
  font-weight: 700;
}

/* =============================================================================
   TABLES
============================================================================= */

.table-container {
  overflow-x: auto;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.history-table,
.lots-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.history-table th,
.lots-table th,
.history-table td,
.lots-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.history-table th,
.lots-table th {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.history-table td,
.lots-table td {
  color: #4a5568;
  font-size: 14px;
}

.history-table tbody tr:hover,
.lots-table tbody tr:hover {
  background: #f7fafc;
  transform: scale(1.002);
  transition: all 0.2s ease;
}

/* =============================================================================
   ACTION BUTTONS & STATUS BADGES
============================================================================= */

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.book-btn {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
}

.book-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(72, 187, 120, 0.4);
}

.book-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.release-btn {
  background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
  color: white;
}

.release-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(237, 137, 54, 0.4);
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.parked-out {
  background: #e2e8f0;
  color: #4a5568;
}

.status-badge.active {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.completed {
  background: #bee3f8;
  color: #2a4365;
}

.payment-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.payment-badge.paid-online {
  background: #c6f6d5;
  color: #22543d;
}

.payment-badge.paid-counter {
  background: #fef5e7;
  color: #744210;
}

.payment-badge.pending {
  background: #fed7d7;
  color: #742a2a;
}

/* =============================================================================
   PROFILE FORM
============================================================================= */

.profile-form {
  max-width: 800px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.form-row:last-child {
  grid-template-columns: 1fr;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 8px;
  font-size: 14px;
}

.form-group label .required {
  color: #e53e3e;
  margin-left: 4px;
}

.form-input {
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: #f7fafc;
  color: #2d3748;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  color: #1a202c;
}

.form-input:invalid {
  border-color: #e53e3e;
}

.form-actions {
  display: flex;
  gap: 16px;
  margin-top: 24px;
}

.submit-btn {
  padding: 14px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: none;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.reset-btn {
  padding: 14px 32px;
  background: transparent;
  color: #4a5568;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: none;
}

.reset-btn:hover {
  background: #f7fafc;
  border-color: #cbd5e0;
  transform: translateY(-1px);
}

/* =============================================================================
   MODALS
============================================================================= */

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h4 {
  margin: 0;
  color: #2d3748;
  font-size: 20px;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #718096;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f7fafc;
  color: #2d3748;
}

.modal-body {
  padding: 24px;
}

.booking-details,
.release-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row label {
  font-weight: 600;
  color: #4a5568;
  font-size: 14px;
}

.detail-row span {
  color: #2d3748;
  font-weight: 500;
}

.detail-row .price {
  color: #38a169;
  font-weight: 700;
  font-size: 16px;
}

.modal-input {
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  max-width: 200px;
  transition: all 0.3s ease;
  color: #2d3748 !important;
  background: white !important;
}

.modal-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  color: #1a202c !important;
  background: white !important;
}

.modal-footer {
  padding: 24px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: center;
}

.payment-options {
  flex-direction: column;
  gap: 12px;
}

.payment-btn {
  padding: 14px 32px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
  text-align: center;
}

.pay-here-btn {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
}

.pay-here-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(72, 187, 120, 0.4);
}

.pay-counter-btn {
  background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
  color: white;
}

.pay-counter-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(237, 137, 54, 0.4);
}

.book-confirm-btn,
.release-confirm-btn {
  padding: 14px 32px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 140px;
}

.book-confirm-btn {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
}

.book-confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(72, 187, 120, 0.4);
}

.book-confirm-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.release-confirm-btn {
  background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
  color: white;
}

.release-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(237, 137, 54, 0.4);
}

/* =============================================================================
   MESSAGES
============================================================================= */

.message {
  position: fixed;
  top: 100px;
  right: 24px;
  padding: 16px 24px;
  border-radius: 8px;
  font-weight: 600;
  z-index: 3000;
  max-width: 400px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.message.success {
  background: #c6f6d5;
  color: #22543d;
  border-left: 4px solid #38a169;
}

.message.error {
  background: #fed7d7;
  color: #742a2a;
  border-left: 4px solid #e53e3e;
}

/* =============================================================================
   RESPONSIVE DESIGN
============================================================================= */

@media (max-width: 768px) {
  .nav-content {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .nav-left {
    justify-content: space-between;
  }
  
  .nav-right {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100%;
    max-width: 280px;
  }
  
  .main-content {
    padding: 20px 16px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .modal-content {
    width: 95%;
    margin: 16px;
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .modal-input {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .nav-btn {
    padding: 8px 12px;
    font-size: 12px;
  }
  
  .welcome-text {
    font-size: 16px;
    margin-left: 0;
  }
  
  .history-table th,
  .lots-table th,
  .history-table td,
  .lots-table td {
    padding: 12px 8px;
    font-size: 12px;
  }
  
  .section-header h3 {
    font-size: 20px;
  }
  
  .payment-btn {
    min-width: 150px;
    font-size: 14px;
  }
  
  .table-container {
    font-size: 12px;
  }
  
  .history-table th,
  .lots-table th,
  .history-table td,
  .lots-table td {
    padding: 8px;
  }
}

/* =============================================================================
   EXPORT SECTION STYLES
============================================================================= */

.export-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.export-form {
  margin-bottom: 32px;
}

.export-options {
  background: #f8fafc;
  border-radius: 12px;
  padding: 24px;
  border: 2px solid #e2e8f0;
}

.export-preview {
  background: #ebf8ff;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  border-left: 4px solid #3182ce;
}

.export-preview h4 {
  margin: 0 0 12px 0;
  color: #2d3748;
  font-size: 16px;
  font-weight: 600;
}

.preview-info {
  font-size: 14px;
}

.preview-info p {
  margin: 6px 0;
  color: #4a5568;
}

.export-actions {
  display: flex;
  gap: 16px;
  margin-top: 20px;
}

.export-btn {
  padding: 14px 32px;
  background: linear-gradient(135deg, #3182ce 0%, #2c5aa0 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.export-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(49, 130, 206, 0.4);
}

.export-btn:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.refresh-btn {
  background: #38a169;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background: #2f855a;
  transform: translateY(-1px);
}

/* Export Jobs Styles */
.export-jobs {
  margin-bottom: 32px;
}

.export-jobs .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.export-jobs .section-header h4 {
  margin: 0;
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
}

.jobs-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.job-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #e2e8f0;
  transition: all 0.3s ease;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.job-card.completed {
  border-left-color: #38a169;
  background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
}

.job-card.processing,
.job-card.started {
  border-left-color: #3182ce;
  background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
}

.job-card.failed {
  border-left-color: #e53e3e;
  background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.job-id {
  font-weight: 600;
  color: #2d3748;
  font-size: 16px;
}

.job-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.job-status.completed {
  background: #c6f6d5;
  color: #22543d;
}

.job-status.processing,
.job-status.started {
  background: #bee3f8;
  color: #2a4365;
}

.job-status.failed {
  background: #fed7d7;
  color: #742a2a;
}

.job-details {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.5;
}

.job-details p {
  margin: 8px 0;
}

.progress-container {
  margin: 12px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3182ce, #63b3ed);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-weight: 600;
  color: #3182ce;
  font-size: 12px;
  min-width: 40px;
}

.job-actions {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.download-btn {
  background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-start;
}

.download-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(56, 161, 105, 0.4);
}

.file-info {
  font-size: 12px;
  color: #718096;
  font-style: italic;
}

.error-message {
  background: #fed7d7;
  border: 1px solid #fc8181;
  border-radius: 8px;
  padding: 12px;
  margin-top: 12px;
}

.error-message p {
  margin: 0 0 8px 0;
  color: #742a2a;
}

.retry-btn {
  background: #ed8936;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background: #dd6b20;
  transform: translateY(-1px);
}

/* Export Information Cards */
.export-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 32px;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-top: 4px solid #667eea;
}

.info-card h4 {
  margin: 0 0 16px 0;
  color: #2d3748;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-card ul,
.info-card ol {
  margin: 0;
  padding-left: 20px;
  color: #4a5568;
  line-height: 1.6;
}

.info-card li {
  margin-bottom: 8px;
}

.info-card li strong {
  color: #2d3748;
  font-weight: 600;
}

/* Responsive Design for Export Section */
@media (max-width: 768px) {
  .export-info {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .export-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .export-btn {
    justify-content: center;
  }
  
  .job-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .progress-container {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .progress-text {
    align-self: center;
  }
}

@media (max-width: 480px) {
  .export-section {
    padding: 16px;
  }
  
  .export-options {
    padding: 16px;
  }
  
  .job-card {
    padding: 16px;
  }
  
  .info-card {
    padding: 16px;
  }
  
  .download-btn {
    align-self: stretch;
    text-align: center;
  }
}
</style>
