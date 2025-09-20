<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-container">
      <!-- Top Header with Title -->
      <header class="dashboard-header">
        <h1 class="dashboard-title">Admin Dashboard</h1>
      </header>

      <!-- Navigation Bar -->
      <nav class="nav-bar">
        <button @click="navigateTo('home')" class="nav-btn" :class="{ active: currentTab === 'home' }">Home</button>
        <button @click="navigateTo('users')" class="nav-btn" :class="{ active: currentTab === 'users' }">Users</button>
        <button @click="navigateTo('summary')" class="nav-btn" :class="{ active: currentTab === 'summary' }">Summary</button>
        <button @click="navigateTo('search')" class="nav-btn" :class="{ active: currentTab === 'search' }">Search</button>
        <button @click="logout" class="nav-btn logout-btn">Logout</button>
      </nav>

      <main class="dashboard-main">
        <!-- Home Tab Content -->
        <div v-if="currentTab === 'home'">
          <!-- Parking Lots Display Section -->
          <section class="section">
            <div class="section-header">
              <h2 class="section-title">Parking Lots Floor Plan</h2>
              <button @click="showAddLotForm = true" class="btn btn-primary add-lot-btn">+ Add Parking Lot</button>
            </div>

            <!-- Modal -->
            <div v-if="showAddLotForm" class="modal">
              <div class="modal-content">
                <h3>Add Parking Lot</h3>
                <form @submit.prevent="addParkingLot">
                  <div class="form-row">
                    <div class="form-group">
                      <label for="lotName">Name</label>
                      <input v-model="newLot.name" id="lotName" type="text" required />
                    </div>
                    <div class="form-group">
                      <label for="lotPincode">PINCODE</label>
                      <input v-model="newLot.pincode" id="lotPincode" type="text" required />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label for="lotAddress">Address</label>
                      <input v-model="newLot.address" id="lotAddress" type="text" required />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label for="lotPrice">Price per Slot</label>
                      <input v-model="newLot.price" id="lotPrice" type="number" required />
                    </div>
                    <div class="form-group">
                      <label for="lotSlots">Number of Slots</label>
                      <input v-model="newLot.slots" id="lotSlots" type="number" required />
                    </div>
                  </div>
                  <button type="submit" class="btn btn-success">Add</button>
                  <button type="button" @click="showAddLotForm = false" class="btn btn-secondary">Cancel</button>
                </form>
              </div>
            </div>

            <!-- Edit Lot Modal -->
            <div v-if="showEditLotForm && editingLot" class="modal">
              <div class="modal-content">
                <h3>Edit Parking Lot</h3>
                <form @submit.prevent="updateParkingLot">
                  <div class="form-row">
                    <div class="form-group">
                      <label for="editLotName">Name</label>
                      <input v-model="editingLot.name" id="editLotName" type="text" required />
                    </div>
                    <div class="form-group">
                      <label for="editLotPincode">PINCODE</label>
                      <input v-model="editingLot.pincode" id="editLotPincode" type="text" required />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label for="editLotAddress">Address</label>
                      <input v-model="editingLot.address" id="editLotAddress" type="text" required />
                    </div>
                  </div>
                  <div class="form-row">
                    <div class="form-group">
                      <label for="editLotPrice">Price per Slot</label>
                      <input v-model="editingLot.price" id="editLotPrice" type="number" step="0.01" required />
                    </div>
                    <div class="form-group">
                      <label for="editLotSlots">Total Slots</label>
                      <input v-model="editingLot.total_slots" id="editLotSlots" type="number" required />
                    </div>
                  </div>
                  <button type="submit" class="btn btn-success">Update</button>
                  <button type="button" @click="cancelEdit" class="btn btn-secondary">Cancel</button>
                </form>
              </div>
            </div>

            <!-- Slot Details Modal -->
            <div v-if="showSlotDetailsModal && selectedSlotDetails" class="modal">
              <div class="modal-content slot-details-modal">
                <div class="modal-header">
                  <h3>Slot Details</h3>
                  <button @click="closeSlotDetailsModal" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                  <div class="slot-detail-grid">
                    <div class="detail-row">
                      <label>Parking Lot:</label>
                      <span>{{ selectedSlotDetails.lot_name }}</span>
                    </div>
                    <div class="detail-row">
                      <label>Address:</label>
                      <span>{{ selectedSlotDetails.lot_address }}</span>
                    </div>
                    <div class="detail-row">
                      <label>Slot Number:</label>
                      <span>#{{ selectedSlotDetails.slot_number }}</span>
                    </div>
                    <div class="detail-row">
                      <label>User Name:</label>
                      <span>{{ selectedSlotDetails.current_user_name }}</span>
                    </div>
                    <div class="detail-row">
                      <label>User Email:</label>
                      <span>{{ selectedSlotDetails.current_user_email }}</span>
                    </div>
                    <div class="detail-row">
                      <label>Booking ID:</label>
                      <span>{{ selectedSlotDetails.booking_id }}</span>
                    </div>
                    <div class="detail-row">
                      <label>Vehicle Number:</label>
                      <span>{{ selectedSlotDetails.vehicle_number }}</span>
                    </div>
                    <div class="detail-row">
                      <label>Start Time:</label>
                      <span>{{ selectedSlotDetails.booking_start_time ? formatDateTime(selectedSlotDetails.booking_start_time) : 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                      <label>Duration:</label>
                      <span>{{ selectedSlotDetails.current_duration_hours ? (Math.round(selectedSlotDetails.current_duration_hours * 10) / 10) + ' hours' : 'N/A' }}</span>
                    </div>
                    <div class="detail-row">
                      <label>Hourly Rate:</label>
                      <span>₹{{ selectedSlotDetails.hourly_rate || 0 }}/hour</span>
                    </div>
                    <div class="detail-row">
                      <label>Current Cost:</label>
                      <span class="cost-highlight">₹{{ selectedSlotDetails.estimated_current_cost ? Math.round(selectedSlotDetails.estimated_current_cost) : 0 }}</span>
                    </div>
                  </div>
                </div>
                <div class="modal-footer">
                  <button @click="closeSlotDetailsModal" class="btn btn-secondary">Close</button>
                </div>
              </div>
            </div>

            <div v-if="parkingLots.length" class="lots-floor-container">
              <div v-for="lot in parkingLots" :key="lot.id" class="parking-floor-tile">
                <!-- Lot Header -->
                <div class="lot-header">
                  <h3 class="lot-title">{{ lot.name }}</h3>
                  <p class="lot-address">{{ lot.address }}, PIN: {{ lot.pincode || lot.pin_code }}</p>
                  <div class="lot-info">
                    <span class="lot-price">₹{{ lot.price }}/hour</span>
                    <span class="lot-capacity">
                      {{ getOccupiedCount(lot) }}/{{ getTotalSlots(lot) }} slots
                    </span>
                  </div>
                </div>
                
                <!-- Parking Floor Grid -->
                <div class="parking-floor">
                  <div class="floor-grid-wrapper">
                    <div class="floor-grid" :ref="`grid-${lot.id}`">
                      <!-- Show parking slots as simple rectangles -->
                      <div 
                        v-for="n in getTotalSlots(lot)" 
                        :key="`slot-${lot.id}-${n}`" 
                        class="parking-slot"
                        :class="{ 
                          'available': !isSlotOccupied(lot, n), 
                          'occupied': isSlotOccupied(lot, n),
                          'clickable': isSlotOccupied(lot, n)
                        }"
                        :title="`Slot ${n} - ${!isSlotOccupied(lot, n) ? 'Available' : 'Occupied'} - ₹${lot.price}`"
                        @click="handleSlotClick(lot, n)"
                      >
                        {{ n }}
                      </div>
                    </div>
                    
                    <!-- Vertical Scroll Controls for lots with more than 20 slots -->
                    <div v-if="getTotalSlots(lot) > 20" class="scroll-controls">
                      <button @click="scrollSlots(lot.id, 'up')" class="scroll-btn scroll-up">↑</button>
                      <div class="scroll-info">
                        <span>{{ getVisibleSlotRange(lot.id) }} of {{ getTotalSlots(lot) }} slots</span>
                      </div>
                      <button @click="scrollSlots(lot.id, 'down')" class="scroll-btn scroll-down">↓</button>
                    </div>
                  </div>
                  
                  <!-- Status Legend - Bottom Left -->
                  <div class="slot-legend">
                    <div class="legend-item">
                      <div class="legend-slot available">A</div>
                      <span>Available</span>
                    </div>
                    <div class="legend-item">
                      <div class="legend-slot occupied">O</div>
                      <span>Occupied</span>
                    </div>
                  </div>
                </div>
                
                <!-- Lot Controls -->
                <div class="lot-controls">
                  <button @click="editLot(lot.id)" class="btn btn-info btn-sm">Edit</button>
                  <button @click="deleteLot(lot.id)" class="btn btn-danger btn-sm">Delete</button>
                </div>
              </div>
            </div>
            <p v-else class="no-lots-message">No parking lots available. Create your first parking lot!</p>
          </section>
        </div>

        <!-- Users Tab Content -->
        <div v-if="currentTab === 'users'">
          <section class="section">
            <h2 class="section-title">Registered Users</h2>
            <div v-if="users.length" class="users-grid">
              <div v-for="user in users" :key="user.id" class="user-card">
                <div class="user-info">
                  <h4>{{ user.username || user.name }}</h4>
                  <p><strong>Email:</strong> {{ user.email }}</p>
                  <p v-if="user.phone"><strong>Phone:</strong> {{ user.phone }}</p>
                  <p v-if="user.created_at"><strong>Registered:</strong> {{ formatDate(user.created_at) }}</p>
                </div>
                <div class="user-actions">
                  <button @click="deleteUser(user.id)" class="btn btn-danger btn-sm">Delete</button>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <p>No users registered yet.</p>
            </div>
          </section>
        </div>

        <!-- Summary Tab Content -->
        <div v-if="currentTab === 'summary'">
          <section class="section">
            <h2 class="section-title">Dashboard Summary</h2>
            
            <!-- All KPI Cards in Dynamic Grid -->
            <div class="summary-cards-container">
              <!-- Primary KPI Cards -->
              <div class="summary-card primary">
                <h3>Total Bookings</h3>
                <p class="summary-value">{{ summaryData.totalBookings || 0 }}</p>
                <span class="summary-subtitle">Completed</span>
              </div>
              <div class="summary-card primary">
                <h3>Total Revenue</h3>
                <p class="summary-value">₹{{ summaryData.totalRevenue || 0 }}</p>
                <span class="summary-subtitle">All time</span>
              </div>
              <div class="summary-card primary">
                <h3>Peak Booking Time</h3>
                <p class="summary-value">{{ summaryData.peakTime || '10:00 AM' }}</p>
                <span class="summary-subtitle">Most popular hour</span>
              </div>
              <div class="summary-card primary">
                <h3>Occupancy Rate</h3>
                <p class="summary-value">{{ summaryData.occupancyRate || 0 }}%</p>
                <span class="summary-subtitle">Current usage</span>
              </div>
              
              <!-- Secondary KPI Cards -->
              <div class="summary-card secondary">
                <h4>Active Bookings</h4>
                <p class="summary-value-small">{{ summaryData.activeBookings || 0 }}</p>
              </div>
              <div class="summary-card secondary">
                <h4>Today's Revenue</h4>
                <p class="summary-value-small">₹{{ summaryData.todayRevenue || 0 }}</p>
              </div>
              <div class="summary-card secondary">
                <h4>Average Duration</h4>
                <p class="summary-value-small">{{ (summaryData.averageDuration || 0).toFixed(1) }}h</p>
              </div>
              <div class="summary-card secondary">
                <h4>Registered Users</h4>
                <p class="summary-value-small">{{ summaryData.totalUsers || 0 }}</p>
              </div>
              <div class="summary-card secondary">
                <h4>Available Slots</h4>
                <p class="summary-value-small">{{ summaryData.availableSlots || 0 }}/{{ summaryData.totalSlots || 0 }}</p>
              </div>
              <div class="summary-card secondary">
                <h4>This Week</h4>
                <p class="summary-value-small">{{ summaryData.thisWeekBookings || 0 }} bookings</p>
              </div>
            </div>

            <!-- Most Popular Parking Lot -->
            <div class="summary-highlight" v-if="summaryData.mostPopularLot && summaryData.mostPopularLot !== 'N/A'">
              <h3>🏆 Most Popular Parking Lot</h3>
              <p class="highlight-value">{{ summaryData.mostPopularLot }}</p>
            </div>

            <!-- Booking History Section -->
            <div class="booking-history-section">
              <div class="section-header">
                <h3 class="section-title">📋 Booking History</h3>
                <div class="history-controls">
                  <select v-model="historyFilter" @change="filterBookingHistory" class="filter-select">
                    <option value="all">All Bookings</option>
                    <option value="today">Today</option>
                    <option value="week">This Week</option>
                    <option value="month">This Month</option>
                  </select>
                  <button @click="refreshBookingHistory" class="btn btn-secondary btn-sm">
                    🔄 Refresh
                  </button>
                </div>
              </div>

              <div v-if="loadingHistory" class="loading-spinner">
                <p>Loading booking history...</p>
              </div>

              <div v-else-if="filteredBookingHistory.length === 0" class="no-bookings">
                <p>No bookings found for the selected period.</p>
              </div>

              <div v-else class="booking-history-table">
                <table class="history-table">
                  <thead>
                    <tr>
                      <th>Booking ID</th>
                      <th>User</th>
                      <th>Parking Lot</th>
                      <th>Slot</th>
                      <th>Vehicle</th>
                      <th>Start Time</th>
                      <th>End Time</th>
                      <th>Duration</th>
                      <th>Cost</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="booking in filteredBookingHistory" :key="booking.id" class="history-row">
                      <td class="booking-id">{{ booking.booking_id || `#${booking.id}` }}</td>
                      <td class="user-info">
                        <div class="user-name">{{ booking.user_name }}</div>
                        <div class="user-email">{{ booking.user_email }}</div>
                      </td>
                      <td class="lot-info">
                        <div class="lot-name">{{ booking.lot_name }}</div>
                        <div class="lot-address">{{ booking.lot_address }}</div>
                      </td>
                      <td class="slot-number">#{{ booking.slot_number }}</td>
                      <td class="vehicle">{{ booking.vehicle_number || 'N/A' }}</td>
                      <td class="time">{{ formatDateTime(booking.start_time) }}</td>
                      <td class="time">{{ formatDateTime(booking.end_time) }}</td>
                      <td class="duration">{{ booking.actual_duration_hours?.toFixed(1) }}h</td>
                      <td class="cost">₹{{ booking.final_cost?.toFixed(2) }}</td>
                      <td class="status">
                        <span class="status-badge" :class="booking.status">
                          {{ booking.status.charAt(0).toUpperCase() + booking.status.slice(1) }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Pagination -->
              <div v-if="totalBookingPages > 1" class="pagination">
                <button 
                  @click="changeBookingPage(currentBookingPage - 1)" 
                  :disabled="currentBookingPage === 1"
                  class="btn btn-secondary btn-sm">
                  Previous
                </button>
                <span class="page-info">
                  Page {{ currentBookingPage }} of {{ totalBookingPages }}
                </span>
                <button 
                  @click="changeBookingPage(currentBookingPage + 1)" 
                  :disabled="currentBookingPage === totalBookingPages"
                  class="btn btn-secondary btn-sm">
                  Next
                </button>
              </div>
            </div>
          </section>
        </div>

        <!-- Search Tab Content -->
        <div v-if="currentTab === 'search'">
          <section class="section">
            <h2 class="section-title">Search</h2>
            <div class="search-container">
              <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="Search by parking lot address, pin code, or user name..." 
                class="search-input"
                @keyup.enter="performSearch"
              />
              <button @click="performSearch" class="btn btn-primary">Search</button>
              <button @click="clearSearch" class="btn btn-secondary ml-2">Clear</button>
            </div>
            
            <div v-if="searchResults.length" class="search-results">
              <h3>Search Results ({{ searchResults.length }} found)</h3>
              
              <!-- Parking Lots Results -->
              <div v-if="searchResults.filter(r => r.type === 'Parking Lot').length" class="result-section">
                <h4>Parking Lots</h4>
                <div class="results-grid">
                  <div v-for="result in searchResults.filter(r => r.type === 'Parking Lot')" :key="'lot-' + result.id" class="result-card">
                    <div class="result-info">
                      <h5>{{ result.name }}</h5>
                      <p><strong>Address:</strong> {{ result.address }}</p>
                      <p><strong>PIN Code:</strong> {{ result.pincode }}</p>
                      <p><strong>Price:</strong> ₹{{ result.price }}/hour</p>
                      <p><strong>Total Slots:</strong> {{ result.total_slots || result.slots }}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Users Results -->
              <div v-if="searchResults.filter(r => r.type === 'User').length" class="result-section">
                <h4>Users</h4>
                <div class="results-grid">
                  <div v-for="result in searchResults.filter(r => r.type === 'User')" :key="'user-' + result.id" class="result-card">
                    <div class="result-info">
                      <h5>{{ result.name }}</h5>
                      <p><strong>Email:</strong> {{ result.email }}</p>
                      <p v-if="result.phone"><strong>Phone:</strong> {{ result.phone }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-else-if="searchQuery && searchPerformed" class="empty-search">
              <p>No results found for "{{ searchQuery }}"</p>
            </div>
            
            <div v-else-if="!searchQuery" class="search-help">
              <p>Enter a search term to find parking lots by address or PIN code, or users by name.</p>
            </div>
          </section>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      currentTab: 'home',
      parkingLots: [
        // Real data will be loaded from API
      ],
      users: [
        // Real data will be loaded from API
      ],
      showAddLotForm: false,
      showEditLotForm: false,
      editingLot: null,
      searchQuery: '',
      searchResults: [],
      searchPerformed: false,
      showSlotDetailsModal: false,
      selectedSlotDetails: null,
      summaryData: {
        // Primary KPIs
        totalBookings: 0,
        totalRevenue: 0,
        averageRevenue: 0,
        peakTime: '10:00 AM',
        occupancyRate: 0,
        
        // Secondary KPIs  
        activeBookings: 0,
        todayRevenue: 0,
        averageDuration: 0,
        totalUsers: 0,
        totalLots: 0,
        totalSlots: 0,
        availableSlots: 0,
        occupiedSlots: 0,
        thisWeekBookings: 0,
        mostPopularLot: 'N/A'
      },
      
      // Booking History Data
      bookingHistory: [],
      filteredBookingHistory: [],
      loadingHistory: false,
      historyFilter: 'all',
      currentBookingPage: 1,
      bookingsPerPage: 10,
      totalBookingPages: 1,
      
      newLot: {
        name: '',
        address: '',
        slots: '',
        pincode: '',
        price: ''
      },
      scrollPositions: {}, // Track scroll position for each lot
      slotStatuses: {}, // Track actual slot status for each lot
      reservationRefreshInterval: null // Interval for refreshing reservations
    };
  },
  computed: {
    // Force reactivity for parking lots display
    reactiveLotsDisplay() {
      return this.parkingLots.map(lot => ({
        ...lot,
        displaySlots: this.getTotalSlots(lot),
        displayOccupied: this.getOccupiedCount(lot)
      }));
    }
  },
  mounted() {
    console.log('AdminDashboard Component Mounted'); // Debugging log
    console.log('Current URL:', window.location.href); // Debug log
    console.log('API Base URL check:', '/api/parking-lots'); // Debug log
    
    // Add a small delay to ensure DOM is ready
    setTimeout(() => {
      this.fetchParkingLots();
      this.fetchUsers();
      this.fetchSummaryData();
      this.fetchBookingHistory();
    }, 100);
    
    // Set up periodic refresh for reservations every 15 seconds (more frequent for real-time updates)
    this.reservationRefreshInterval = setInterval(() => {
      this.refreshAllReservations();
    }, 15000);
  },
  beforeDestroy() {
    // Clean up interval
    if (this.reservationRefreshInterval) {
      clearInterval(this.reservationRefreshInterval);
    }
  },
  methods: {
    navigateTo(tab) {
      this.currentTab = tab;
      
      // Fetch users when Users tab is clicked
      if (tab === 'users') {
        this.fetchUsers();
      }
      
      // Don't navigate away from the current page, just change tabs
      // if (tab === 'home') {
      //   this.$router.push('/admin-dashboard');
      // }
    },
    getOrGenerateSlots(lot) {
      // This method is kept for compatibility but should not be used in template
      // Use individual utility methods instead
      if (lot.slots && lot.slots.length > 0) {
        return lot.slots;
      }
      
      // Return empty array if no slots exist
      return [];
    },
    getTotalSlots(lot) {
      // Return the total number of slots for a lot with error handling
      try {
        if (!lot) return 20;
        
        // Check if slots is a number (from API response)
        if (typeof lot.slots === 'number') {
          return lot.slots;
        }
        
        // Check if slots is an array (legacy format)
        if (lot.slots && Array.isArray(lot.slots) && lot.slots.length > 0) {
          return lot.slots.length;
        }
        
        // Fallback to total_slots or default
        return lot.total_slots || 20;
      } catch (error) {
        console.warn('Error in getTotalSlots:', error);
        return 20;
      }
    },
    getOccupiedCount(lot) {
      // Return the number of occupied slots with proper tracking
      try {
        if (!lot) return 0;
        
        // Initialize slot statuses if not exists
        if (!this.slotStatuses[lot.id]) {
          this.initializeSlotStatuses(lot);
        }
        
        // Count occupied slots from our managed statuses
        const statuses = this.slotStatuses[lot.id];
        let occupiedCount = 0;
        
        for (let i = 1; i <= this.getTotalSlots(lot); i++) {
          if (statuses[i] === 'occupied') {
            occupiedCount++;
          }
        }
        
        return occupiedCount;
      } catch (error) {
        console.warn('Error in getOccupiedCount:', error);
        return 0;
      }
    },
    isSlotOccupied(lot, slotNumber) {
      // Check if a specific slot is occupied with proper tracking
      try {
        if (!lot || !slotNumber) return false;
        
        // Initialize slot statuses for this lot if not exists
        if (!this.slotStatuses[lot.id]) {
          this.initializeSlotStatuses(lot);
        }
        
        // Check from our managed slot statuses
        return this.slotStatuses[lot.id] && this.slotStatuses[lot.id][slotNumber] === 'occupied';
      } catch (error) {
        console.warn('Error in isSlotOccupied:', error);
        return false;
      }
    },
    initializeSlotStatuses(lot) {
      // Initialize all slots as available by default
      if (!lot) return;
      
      this.slotStatuses[lot.id] = {};
      const totalSlots = this.getTotalSlots(lot);
      
      // All slots start as available - actual status will be updated from reservations
      for (let i = 1; i <= totalSlots; i++) {
        this.slotStatuses[lot.id][i] = 'available';
      }
      
      // Fetch current reservations to update slot statuses
      this.fetchCurrentReservations(lot.id);
    },
    async fetchCurrentReservations(lotId) {
      // Fetch current reservations from the backend
      try {
        const response = await fetch(`/api/parking-lots/${lotId}/slots`);
        if (response.ok) {
          const slots = await response.json();
          
          // Update slot statuses based on current slot data from backend
          if (this.slotStatuses[lotId]) {
            // Reset all slots to available first
            const totalSlots = this.getTotalSlots(this.parkingLots.find(lot => lot.id === lotId));
            for (let i = 1; i <= totalSlots; i++) {
              this.slotStatuses[lotId][i] = 'available';
            }
            
            // Update based on actual slot data
            slots.forEach(slot => {
              if (slot.slot_number && slot.slot_number <= totalSlots) {
                this.slotStatuses[lotId][slot.slot_number] = slot.is_available ? 'available' : 'occupied';
                
                // Store slot details for click functionality
                if (!slot.is_available) {
                  this.slotStatuses[lotId][`slot_${slot.slot_number}_details`] = {
                    id: slot.id,
                    slot_number: slot.slot_number,
                    current_user_name: slot.current_user_name,
                    current_user_email: slot.current_user_email,
                    booking_id: slot.booking_id,
                    vehicle_number: slot.vehicle_number,
                    booking_start_time: slot.booking_start_time,
                    current_duration_hours: slot.current_duration_hours,
                    estimated_current_cost: slot.estimated_current_cost
                  };
                }
              }
            });
          }
        }
      } catch (error) {
        console.warn('Could not fetch current slot data:', error);
        // Keep existing slot statuses if fetch fails
      }
    },
    
    handleSlotClick(lot, slotNumber) {
      console.log('Slot clicked:', lot.id, slotNumber);
      
      // Only handle clicks on occupied slots
      if (!this.isSlotOccupied(lot, slotNumber)) {
        return;
      }
      
      // Get slot details from stored data
      const slotDetails = this.slotStatuses[lot.id] && this.slotStatuses[lot.id][`slot_${slotNumber}_details`];
      
      if (slotDetails) {
        this.selectedSlotDetails = {
          ...slotDetails,
          lot_name: lot.name,
          lot_address: lot.address,
          hourly_rate: lot.price
        };
        this.showSlotDetailsModal = true;
      } else {
        // Fallback: fetch fresh slot data
        this.fetchSlotDetails(lot.id, slotNumber);
      }
    },
    
    async fetchSlotDetails(lotId, slotNumber) {
      try {
        const response = await fetch(`/api/admin/parking-lots/${lotId}/slots`);
        if (response.ok) {
          const slots = await response.json();
          const slot = slots.find(s => s.slot_number === slotNumber);
          
          if (slot && !slot.is_available) {
            const lot = this.parkingLots.find(l => l.id === lotId);
            
            // Calculate duration if we have booking start time
            let durationHours = 0;
            let currentCost = 0;
            
            if (slot.booking_start_time) {
              const startTime = new Date(slot.booking_start_time);
              const currentTime = new Date();
              durationHours = (currentTime - startTime) / (1000 * 60 * 60); // Hours
              currentCost = durationHours * (lot ? lot.price_per_hour || lot.price || 0 : 0);
            }
            
            this.selectedSlotDetails = {
              id: slot.id,
              slot_number: slot.slot_number,
              current_user_name: slot.current_user_name || 'Unknown User',
              current_user_email: slot.current_user_email || 'Unknown Email',
              booking_id: slot.booking_id || (slot.booking && slot.booking.booking_id) || 'N/A',
              vehicle_number: slot.vehicle_number || 'N/A',
              booking_start_time: slot.booking_start_time,
              planned_duration_hours: slot.planned_duration_hours || 0,
              current_duration_hours: durationHours,
              estimated_current_cost: currentCost,
              lot_name: lot ? lot.name : 'Unknown Lot',
              lot_address: lot ? lot.address : 'Unknown Address',
              hourly_rate: lot ? (lot.price_per_hour || lot.price || 0) : 0
            };
            this.showSlotDetailsModal = true;
          } else {
            alert('Slot is not occupied or could not be found.');
          }
        }
      } catch (error) {
        console.error('Error fetching slot details:', error);
        alert('Could not fetch slot details. Please try again.');
      }
    },
    
    closeSlotDetailsModal() {
      this.showSlotDetailsModal = false;
      this.selectedSlotDetails = null;
    },
    refreshAllReservations() {
      console.log('Refreshing all reservations...');
      // Refresh reservations for all parking lots
      this.parkingLots.forEach(lot => {
        this.fetchCurrentReservations(lot.id);
      });
      
      // Also refresh summary data to update occupancy rates and stats
      this.fetchSummaryData();
      
      console.log('Reservations refresh completed');
    },
    scrollSlots(lotId, direction) {
      // Vertical scrolling for parking slots
      const gridElement = this.$refs[`grid-${lotId}`];
      if (!gridElement || !gridElement[0]) return;
      
      const grid = gridElement[0];
      const scrollAmount = 100; // Pixels to scroll vertically
      
      if (direction === 'up') {
        grid.scrollTop -= scrollAmount;
      } else if (direction === 'down') {
        grid.scrollTop += scrollAmount;
      }
      
      // Update scroll position tracking
      this.scrollPositions[lotId] = grid.scrollTop;
    },
    getVisibleSlotRange(lotId) {
      // Calculate which slots are currently visible with vertical scrolling
      const gridElement = this.$refs[`grid-${lotId}`];
      if (!gridElement || !gridElement[0]) return '1-20';
      
      const grid = gridElement[0];
      const slotHeight = 50; // Approximate slot height including gap
      const visibleHeight = grid.clientHeight;
      const slotsPerRow = 5; // Fixed 5 columns
      const visibleRows = Math.floor(visibleHeight / slotHeight);
      const scrolledRows = Math.floor(grid.scrollTop / slotHeight);
      
      const startSlot = scrolledRows * slotsPerRow + 1;
      const endSlot = Math.min(startSlot + (visibleRows * slotsPerRow) - 1, this.getTotalSlots(this.parkingLots.find(lot => lot.id === lotId)));
      
      return `${startSlot}-${endSlot}`;
    },
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/');
    },
    editLot(id) {
      console.log('Editing parking lot:', id); // Debug log
      const lot = this.parkingLots.find(lot => lot.id === id);
      if (lot) {
        // Create a copy for editing with proper field mapping
        this.editingLot = { 
          ...lot,
          total_slots: lot.slots // Map slots to total_slots for form binding
        };
        console.log('Edit lot data:', this.editingLot); // Debug log
        this.showEditLotForm = true;
      } else {
        alert('Parking lot not found!');
      }
    },
    cancelEdit() {
      this.showEditLotForm = false;
      this.editingLot = null;
    },
    async updateParkingLot() {
      console.log('Updating parking lot:', this.editingLot); // Debug log
      console.log('Original parking lots before update:', this.parkingLots); // Debug log
      
      try {
        const token = localStorage.getItem('token');
        const url = `/api/parking-lots/${this.editingLot.id}`;
        console.log('PUT request URL:', url); // Debug log
        
        const requestBody = {
          name: this.editingLot.name,
          address: this.editingLot.address,
          pincode: this.editingLot.pincode,
          price: parseFloat(this.editingLot.price),
          total_slots: parseInt(this.editingLot.total_slots)
        };
        console.log('PUT request body:', requestBody); // Debug log
        
        const response = await fetch(url, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
          },
          body: JSON.stringify(requestBody)
        });

        console.log('Update lot response status:', response.status); // Debug log
        console.log('Update lot response URL:', response.url); // Debug log

        if (response.ok) {
          const updatedLot = await response.json();
          console.log('Updated lot response:', updatedLot); // Debug log
          
          // Update the lot in the local array with proper field mapping
          const index = this.parkingLots.findIndex(lot => lot.id === this.editingLot.id);
          console.log('Found lot at index:', index); // Debug log
          
          if (index !== -1) {
            console.log('Before update:', this.parkingLots[index]); // Debug log
            
            // Update the lot with the response data using direct assignment (Vue 3)
            const updatedLotData = { 
              ...this.parkingLots[index], // Keep existing data
              id: updatedLot.id,
              name: updatedLot.name,
              address: updatedLot.address,
              pincode: updatedLot.pincode,
              price: updatedLot.price,
              slots: updatedLot.slots // Backend now returns 'slots' consistently
            };
            
            // Direct assignment for Vue 3 reactivity
            this.parkingLots[index] = updatedLotData;
            
            console.log('After update:', this.parkingLots[index]); // Debug log
            
            // Re-initialize slot statuses with new slot count
            this.initializeSlotStatuses(this.parkingLots[index]);
            
            // Force Vue to update the display
            this.$forceUpdate();
            
            // Wait a bit and force another update to ensure reactivity
            this.$nextTick(() => {
              this.$forceUpdate();
            });
          }
          
          // Close modal
          this.showEditLotForm = false;
          this.editingLot = null;
          
          alert('Parking lot updated successfully!');
        } else {
          const errorText = await response.text();
          console.error('Update lot error response:', errorText);
          console.error('Update lot error status:', response.status);
          console.error('Update lot error status text:', response.statusText);
          throw new Error(`Failed to update parking lot: ${response.status} ${response.statusText}: ${errorText}`);
        }
      } catch (error) {
        console.error('Error updating parking lot:', error);
        alert('Error updating parking lot: ' + error.message);
      }
    },
    deleteLot(id) {
      const lot = this.parkingLots.find(l => l.id === id);
      const lotName = lot ? lot.name : `Lot ${id}`;
      
      if (confirm(`Are you sure you want to delete "${lotName}"? This action cannot be undone.`)) {
        console.log('Deleting parking lot:', id); // Debug log
        
        try {
          // Use SQLAlchemy API endpoint
          fetch(`/api/parking-lots/${id}`, {
            method: 'DELETE'
          })
          .then(response => {
            console.log('Delete lot response status:', response.status); // Debug log
            if (response.ok) {
              // Remove from local array
              this.parkingLots = this.parkingLots.filter(lot => lot.id !== id);
              console.log('Parking lot deleted successfully'); // Debug log
              alert('Parking lot deleted successfully!');
            } else {
              return response.text().then(text => {
                console.error('Delete lot error response:', text);
                throw new Error('Failed to delete parking lot: ' + text);
              });
            }
          })
          .catch(error => {
            console.error('API delete failed, using local delete:', error);
            // Fallback to local delete
            this.parkingLots = this.parkingLots.filter(lot => lot.id !== id);
            alert('Parking lot deleted locally (API unavailable)');
          });
        } catch (error) {
          console.error('Error deleting parking lot:', error);
          // Fallback to local delete
          this.parkingLots = this.parkingLots.filter(lot => lot.id !== id);
          alert('Parking lot deleted locally due to error: ' + error.message);
        }
      }
    },
    deleteUser(id) {
      if (confirm('Are you sure you want to delete this user?')) {
        console.log('Deleting user:', id); // Debug log
        
        fetch(`/api/users/${id}`, {
          method: 'DELETE'
        })
        .then(response => {
          console.log('Delete user response status:', response.status); // Debug log
          if (response.ok) {
            // Remove from local array
            this.users = this.users.filter(user => user.id !== id);
            console.log('User deleted successfully'); // Debug log
          } else {
            return response.text().then(text => {
              console.error('Delete user error response:', text);
              throw new Error('Failed to delete user: ' + text);
            });
          }
        })
        .catch(error => {
          console.error('Error deleting user:', error);
          alert('Error deleting user: ' + error.message);
        });
      }
    },
    addParkingLot() {
      console.log('Adding parking lot:', this.newLot); // Debug log
      
      // Validate input
      if (!this.newLot.name || !this.newLot.address || !this.newLot.slots || !this.newLot.price) {
        alert('Please fill in all fields');
        return;
      }
      
      const newLot = { ...this.newLot };
      
      // Convert strings to appropriate types
      newLot.price = parseFloat(newLot.price);
      const numberOfSlots = parseInt(newLot.slots);
      newLot.total_slots = numberOfSlots;
      
      // Validate number of slots
      if (numberOfSlots <= 0 || numberOfSlots > 100) {
        alert('Number of slots must be between 1 and 100');
        return;
      }
      
      // Generate a unique ID for the new lot (timestamp-based to avoid conflicts)
      const newId = Date.now();
      
      // Generate slots array - ALWAYS create slots
      const slots = [];
      for (let i = 1; i <= numberOfSlots; i++) {
        slots.push({
          id: newId * 1000 + i, // Unique slot ID
          status: i % 3 === 0 ? 'occupied' : 'available', // Mix of available and occupied
          price: newLot.price,
          lot_id: newId,
          slot_number: i
        });
      }
      
      // Create the lot with slots - Use Vue.set equivalent or direct assignment
      const lotWithSlots = {
        id: newId,
        name: newLot.name,
        address: newLot.address,
        pincode: newLot.pincode,
        price: newLot.price,
        total_slots: numberOfSlots,
        slots: slots // Assign the slots array directly
      };
      
      console.log('Creating lot with slots:', lotWithSlots); // Debug log
      console.log('Slots generated:', slots.length); // Debug log
      
      // Add to parkingLots array immediately to ensure UI updates
      this.parkingLots.push(lotWithSlots);
      
      // Force reactivity update
      this.$forceUpdate();
      
      console.log('Parking lots after addition:', this.parkingLots); // Debug log
      console.log('Last added lot slots:', this.parkingLots[this.parkingLots.length - 1].slots); // Debug log
      
      // Try API call in background (non-blocking)
      fetch('/api/parking-lots', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: newLot.name,
          address: newLot.address,
          pincode: newLot.pincode,
          price: newLot.price,
          total_slots: numberOfSlots
        })
      })
        .then(response => {
          console.log('Add lot API response status:', response.status); // Debug log
          if (response.ok) {
            return response.json();
          }
          throw new Error('API call failed');
        })
        .then(data => {
          console.log('API parking lot response:', data); // Debug log
          
          // Update the lot ID if API provides one
          if (data.id && data.id !== newId) {
            const lotIndex = this.parkingLots.findIndex(lot => lot.id === newId);
            if (lotIndex !== -1) {
              this.parkingLots[lotIndex].id = data.id;
              // Update slot lot_ids too
              this.parkingLots[lotIndex].slots.forEach(slot => {
                slot.lot_id = data.id;
              });
            }
          }
          
          console.log('Parking lot synced with API successfully');
        })
        .catch(error => {
          console.warn('API call failed, lot created locally only:', error);
          // Lot already added locally, so this is just a warning
        });
      
      // Reset form and close modal
      this.newLot = { name: '', address: '', slots: '', pincode: '', price: '' };
      this.showAddLotForm = false;
      
      alert(`Parking lot "${lotWithSlots.name}" created successfully with ${numberOfSlots} slots!`);
    },
    async fetchParkingLots() {
      console.log('Fetching parking lots...'); // Debug log
      try {
        const response = await fetch('http://localhost:5001/api/parking-lots');
        console.log('Response status:', response.status); // Debug log
        
        if (response.ok) {
          const lots = await response.json();
          console.log('API response lots:', lots); // Debug log
          
          // Clear existing test data and use real data
          this.parkingLots = lots;
          
          // Initialize slot statuses for all lots
          this.parkingLots.forEach(lot => {
            this.initializeSlotStatuses(lot);
          });
          
          console.log('Final parking lots:', this.parkingLots); // Debug log
        } else {
          console.error('Failed to fetch parking lots, status:', response.status);
          const errorText = await response.text();
          console.error('Error response:', errorText);
          // Set empty array as fallback
          this.parkingLots = [];
        }
      } catch (error) {
        console.error('Error fetching parking lots:', error);
        this.parkingLots = [];
      }
    },
    async fetchUsers() {
      console.log('Fetching users...'); // Debug log
      try {
        const response = await fetch('http://localhost:5001/api/users');
        console.log('Users response status:', response.status); // Debug log
        
        if (response.ok) {
          const data = await response.json();
          console.log('Fetched users data:', data); // Debug log
          this.users = Array.isArray(data) ? data : [];
          console.log('Final users:', this.users); // Debug log
        } else {
          console.error('Failed to fetch users, status:', response.status);
          const errorText = await response.text();
          console.error('Users error response:', errorText);
          this.users = [];
        }
      } catch (error) {
        console.error('Error fetching users:', error);
        this.users = [];
      }
    },
    async fetchSummaryData() {
      console.log('Fetching summary data...'); // Debug log
      try {
        const response = await fetch('http://localhost:5001/api/bookings/stats');
        console.log('Summary response status:', response.status); // Debug log
        
        if (response.ok) {
          const data = await response.json();
          console.log('Summary data received:', data); // Debug log
          this.summaryData = data;
        } else {
          console.error('Failed to fetch summary data, status:', response.status);
          // Calculate fallback data from current parking lots
          this.calculateLocalSummaryData();
        }
      } catch (error) {
        console.error('Error fetching summary data:', error);
        // Calculate fallback data from current parking lots
        this.calculateLocalSummaryData();
      }
    },
    
    calculateLocalSummaryData() {
      // Calculate summary data from local parking lots data
      let totalSlots = 0;
      let occupiedSlots = 0;
      
      this.parkingLots.forEach(lot => {
        const slots = this.getTotalSlots(lot);
        const occupied = this.getOccupiedCount(lot);
        totalSlots += slots;
        occupiedSlots += occupied;
      });
      
      const occupancyRate = totalSlots > 0 ? (occupiedSlots / totalSlots) * 100 : 0;
      
      // Set fallback summary data
      this.summaryData = {
        // Primary KPIs
        totalBookings: 0, // No historical data in fallback
        totalRevenue: 0,
        averageRevenue: 0,
        peakTime: '10:00 AM', // Default peak time
        occupancyRate: Math.round(occupancyRate * 10) / 10, // Round to 1 decimal
        
        // Secondary KPIs
        activeBookings: occupiedSlots,
        todayRevenue: 0,
        averageDuration: 0,
        totalUsers: 0,
        totalLots: this.parkingLots.length,
        totalSlots: totalSlots,
        availableSlots: totalSlots - occupiedSlots,
        occupiedSlots: occupiedSlots,
        thisWeekBookings: 0,
        mostPopularLot: this.parkingLots.length > 0 ? this.parkingLots[0].name : 'N/A'
      };
      
      console.log('Calculated local summary data:', this.summaryData);
    },
    performSearch() {
      if (!this.searchQuery.trim()) {
        this.searchResults = [];
        this.searchPerformed = false;
        return;
      }
      
      this.searchPerformed = true;
      this.searchResults = [];
      const query = this.searchQuery.toLowerCase().trim();
      
      // Search through parking lots
      this.parkingLots.forEach(lot => {
        const matches = 
          (lot.name && lot.name.toLowerCase().includes(query)) ||
          (lot.address && lot.address.toLowerCase().includes(query)) ||
          (lot.pincode && lot.pincode.toString().includes(query)) ||
          (lot.pin_code && lot.pin_code.toString().includes(query));
          
        if (matches) {
          this.searchResults.push({
            id: lot.id,
            type: 'Parking Lot',
            name: lot.name,
            address: lot.address,
            pincode: lot.pincode || lot.pin_code,
            price: lot.price,
            total_slots: lot.total_slots || (Array.isArray(lot.slots) ? lot.slots.length : lot.slots)
          });
        }
      });
      
      // Search through users
      this.users.forEach(user => {
        const matches = 
          (user.name && user.name.toLowerCase().includes(query)) ||
          (user.username && user.username.toLowerCase().includes(query)) ||
          (user.email && user.email.toLowerCase().includes(query));
          
        if (matches) {
          this.searchResults.push({
            id: user.id,
            type: 'User',
            name: user.username || user.name,
            email: user.email,
            phone: user.phone
          });
        }
      });
      
      console.log('Search results:', this.searchResults);
    },
    
    clearSearch() {
      this.searchQuery = '';
      this.searchResults = [];
      this.searchPerformed = false;
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      try {
        return new Date(dateString).toLocaleDateString();
      } catch (error) {
        return 'N/A';
      }
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      try {
        return new Date(dateString).toLocaleString('en-IN', {
          timeZone: 'Asia/Kolkata',
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        });
      } catch (error) {
        return 'N/A';
      }
    },

    // =============================================================================
    // BOOKING HISTORY METHODS
    // =============================================================================
    
    async fetchBookingHistory() {
      console.log('Fetching booking history...');
      this.loadingHistory = true;
      
      try {
        const response = await fetch(`http://localhost:5001/api/bookings?page=${this.currentBookingPage}&per_page=${this.bookingsPerPage}&status=${this.historyFilter}`);
        console.log('Booking history response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Fetched booking history data:', data);
          
          this.bookingHistory = data.bookings || [];
          this.filteredBookingHistory = [...this.bookingHistory];
          
          // Update pagination info
          if (data.pagination) {
            this.totalBookingPages = data.pagination.total_pages || 1;
            this.currentBookingPage = data.pagination.page || 1;
          }
          
          console.log('Final booking history:', this.filteredBookingHistory);
          console.log('Pagination info:', { 
            totalPages: this.totalBookingPages, 
            currentPage: this.currentBookingPage 
          });
        } else {
          console.error('Failed to fetch booking history, status:', response.status);
          const errorText = await response.text();
          console.error('Error response:', errorText);
          this.bookingHistory = [];
          this.filteredBookingHistory = [];
        }
      } catch (error) {
        console.error('Error fetching booking history:', error);
        this.bookingHistory = [];
        this.filteredBookingHistory = [];
      } finally {
        this.loadingHistory = false;
      }
    },

    async refreshBookingHistory() {
      console.log('Refreshing booking history...');
      await this.fetchBookingHistory();
    },

    filterBookingHistory() {
      console.log('Filtering booking history by:', this.historyFilter);
      // The filtering is now handled server-side through the API
      // Just refetch data with the new filter
      this.currentBookingPage = 1; // Reset to first page when filtering
      this.fetchBookingHistory();
    },

    changeBookingPage(page) {
      if (page >= 1 && page <= this.totalBookingPages) {
        this.currentBookingPage = page;
        this.fetchBookingHistory();
      }
    },

    formatCurrency(amount) {
      if (!amount || isNaN(amount)) return '₹0.00';
      return `₹${parseFloat(amount).toFixed(2)}`;
    }
  }
};
</script>

<style scoped>
/* Prevent horizontal scroll globally */
* {
  box-sizing: border-box;
}

/* Wrapper and Container */
.dashboard-wrapper {
  width: 100%;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow-x: hidden;
  background: #f5f5f5;
  padding: clamp(5px, 1vw, 10px);
  padding-top: clamp(5px, 0.5vw, 8px); /* Reduced top padding to move layout up */
}

.dashboard-container {
  background: #fff;
  width: 100%;
  max-width: min(98vw, 1400px);
  min-height: calc(100vh - clamp(10px, 2vw, 20px));
  padding: clamp(10px, 2vw, 15px); /* Reduced padding to move content up */
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  font-family: Arial, sans-serif;
  border-radius: clamp(5px, 1vw, 10px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-top: -10px; /* Negative margin to pull the container up */
}

/* Header */
.dashboard-header {
  text-align: center;
  margin-bottom: clamp(10px, 2vw, 15px); /* Reduced bottom margin */
  padding: clamp(2px, 0.5vw, 5px) 0; /* Reduced padding */
}

.dashboard-title {
  font-size: clamp(1.5rem, 5vw, 2.5rem);
  color: #333;
  margin: 0;
  font-weight: bold;
}

/* Navigation Bar */
.nav-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f8f9fa;
  border-radius: clamp(6px, 1vw, 8px);
  padding: clamp(8px, 2vw, 10px);
  margin-bottom: clamp(15px, 3vw, 20px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex-wrap: wrap;
  gap: clamp(4px, 1vw, 8px);
}

.nav-btn {
  background: transparent;
  border: none;
  padding: clamp(6px, 1.5vw, 12px) clamp(8px, 2vw, 24px);
  margin: 0 clamp(1px, 0.5vw, 2px);
  border-radius: clamp(4px, 1vw, 6px);
  cursor: pointer;
  font-size: clamp(0.75rem, 2.5vw, 1rem);
  font-weight: 500;
  color: #666;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: clamp(60px, 15vw, 80px);
}

.nav-btn:hover {
  background: #e9ecef;
  color: #333;
}

.nav-btn.active {
  background: #007bff;
  color: white;
}

.logout-btn {
  background: #dc3545 !important;
  color: white !important;
  margin-left: auto;
}

.logout-btn:hover {
  background: #c82333 !important;
}

/* Main */
.dashboard-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: clamp(15px, 3vw, 20px);
  min-height: 0;
  width: 100%;
}

/* Sections */
.section {
  background: #ffffff;
  border-radius: clamp(6px, 1vw, 8px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  padding: clamp(12px, 3vw, 25px);
  flex: 1;
  overflow-y: auto;
  min-height: clamp(150px, 30vh, 200px);
  width: 100%;
}

.section-title {
  font-size: clamp(1.1rem, 3.5vw, 1.5rem);
  margin-bottom: clamp(10px, 2vw, 15px);
  color: #333;
}

/* Lists */
.list-group {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
}

.list-group-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: clamp(8px, 2vw, 15px);
  border: 1px solid #ddd;
  border-radius: clamp(3px, 0.5vw, 4px);
  margin-bottom: clamp(8px, 2vw, 10px);
  background: #f8f9fa;
  font-size: clamp(0.85rem, 2.5vw, 1rem);
  flex-wrap: wrap;
  gap: clamp(5px, 1vw, 10px);
}

.actions {
  display: flex;
  gap: clamp(5px, 1vw, 10px);
  flex-wrap: wrap;
}

.actions button {
  margin: 0;
}

/* Buttons */
.btn {
  padding: clamp(6px, 1.5vw, 16px) clamp(8px, 2vw, 16px);
  border: none;
  border-radius: clamp(4px, 1vw, 6px);
  cursor: pointer;
  font-size: clamp(0.8rem, 2.5vw, 1rem);
  font-weight: bold;
  transition: all 0.3s ease;
  min-width: clamp(60px, 15vw, 80px);
}
.btn-warning {
  background: #ffc107;
  color: #fff;
}
.btn-danger {
  background: #dc3545;
  color: #fff;
}
.btn-primary {
  background: #007bff;
  color: #fff;
}
.btn-info {
  background: #17a2b8;
  color: #fff;
}
.btn-success {
  background: #28a745;
  color: #fff;
  margin-right: 10px;
}
.btn-secondary {
  background: #6c757d;
  color: #fff;
}
.btn-success:hover {
  background: #218838;
}
.btn-secondary:hover {
  background: #5a6268;
}
.btn-info:hover {
  background: #138496;
}

/* Modal */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: clamp(10px, 2vw, 20px);
}

.modal-content {
  background: #ffffff;
  padding: clamp(15px, 4vw, 30px);
  border-radius: clamp(8px, 2vw, 12px);
  width: 100%;
  max-width: min(95vw, 800px);
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.modal-content h3 {
  font-size: clamp(1.2rem, 4vw, 2rem);
  margin-bottom: clamp(15px, 3vw, 20px);
  text-align: center;
  color: #333;
}

/* Slot Details Modal Specific Styles */
.slot-details-modal {
  min-width: 500px;
  max-width: 600px;
}

.slot-details-modal .modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
  margin: -30px -30px 20px -30px;
}

.slot-details-modal .modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: white;
  text-align: left;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: white;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.slot-detail-grid {
  display: grid;
  gap: 16px;
}

.detail-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 12px;
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

.cost-highlight {
  color: #38a169 !important;
  font-weight: 700 !important;
  font-size: 16px !important;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.form-group {
  margin-bottom: clamp(15px, 3vw, 20px);
}

.form-group label {
  display: block;
  margin-bottom: clamp(5px, 1vw, 8px);
  font-weight: bold;
  color: #555;
  font-size: clamp(0.85rem, 2.5vw, 1rem);
}

.form-group input {
  width: 100%;
  padding: clamp(8px, 2vw, 12px);
  border: 1px solid #ddd;
  border-radius: clamp(4px, 1vw, 6px);
  font-size: clamp(0.85rem, 2.5vw, 1rem);
  box-sizing: border-box;
}

.form-group input:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 0.15rem rgba(0, 123, 255, 0.25);
}

/* Form Rows */
.form-row {
  display: flex;
  gap: clamp(10px, 2vw, 15px);
  margin-bottom: clamp(15px, 3vw, 20px);
  flex-wrap: wrap;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
  min-width: clamp(150px, 35vw, 200px);
}

/* Parking Lots Display */
.lots-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(clamp(250px, 35vw, 300px), 1fr));
  gap: clamp(15px, 3vw, 20px);
  width: 100%;
}

.lot-box {
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: clamp(6px, 1vw, 8px);
  padding: clamp(12px, 3vw, 15px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.lot-box:hover {
  transform: translateY(-2px);
}

.lot-box h3 {
  font-size: clamp(1rem, 3vw, 1.2rem);
  margin: 0 0 clamp(8px, 2vw, 10px) 0;
}

.lot-box p {
  font-size: clamp(0.85rem, 2.5vw, 0.95rem);
  margin: 0 0 clamp(10px, 2vw, 15px) 0;
  color: #666;
}

.slots-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(clamp(120px, 20vw, 150px), 1fr));
  gap: clamp(8px, 1.5vw, 10px);
  margin-top: clamp(8px, 2vw, 10px);
}

.slot-box {
  background: #ffffff;
  border: 1px solid #007bff;
  border-radius: clamp(3px, 0.5vw, 4px);
  padding: clamp(6px, 1.5vw, 10px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  text-align: center;
  font-size: clamp(0.75rem, 2vw, 0.85rem);
}

.slot-box p {
  margin: clamp(2px, 0.5vw, 4px) 0;
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: clamp(15px, 3vw, 20px);
  flex-wrap: wrap;
  gap: clamp(10px, 2vw, 15px);
}

.add-lot-btn {
  background: linear-gradient(135deg, #28a745, #20c997) !important;
  border: none;
  padding: clamp(8px, 2vw, 12px) clamp(16px, 3vw, 24px);
  border-radius: clamp(6px, 1vw, 8px);
  font-weight: bold;
  font-size: clamp(0.85rem, 2.5vw, 1rem);
  color: white;
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
  transition: all 0.3s ease;
  white-space: nowrap;
}

.add-lot-btn:hover {
  background: linear-gradient(135deg, #20c997, #28a745) !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(40, 167, 69, 0.4);
}

/* New Parking Floor Styles */
.lots-floor-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(clamp(320px, 30vw, 450px), 1fr));
  max-width: 100%;
  gap: clamp(20px, 4vw, 30px);
  width: 100%;
}

/* Ensure max 3 columns */
@supports (grid-template-columns: subgrid) {
  .lots-floor-container {
    grid-template-columns: repeat(auto-fit, minmax(clamp(320px, 30vw, 450px), 1fr));
  }
}

/* Fallback for 3 columns max */
@media (min-width: 1200px) {
  .lots-floor-container {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 800px) and (max-width: 1199px) {
  .lots-floor-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 799px) {
  .lots-floor-container {
    grid-template-columns: 1fr;
  }
}

.parking-floor-tile {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid #dee2e6;
  border-radius: clamp(12px, 2vw, 16px);
  padding: clamp(15px, 3vw, 25px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.parking-floor-tile:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.parking-floor-tile::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #007bff, #28a745, #ffc107);
}

.lot-header {
  margin-bottom: clamp(15px, 3vw, 20px);
  text-align: center;
}

.lot-title {
  font-size: clamp(1.2rem, 4vw, 1.8rem);
  font-weight: bold;
  color: #212529;
  margin: 0 0 clamp(5px, 1vw, 8px) 0;
}

.lot-address {
  font-size: clamp(0.9rem, 2.5vw, 1rem);
  color: #6c757d;
  margin: 0 0 clamp(10px, 2vw, 12px) 0;
}

.lot-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: clamp(8px, 2vw, 10px);
}

.lot-price {
  background: #007bff;
  color: white;
  padding: clamp(4px, 1vw, 6px) clamp(8px, 2vw, 12px);
  border-radius: clamp(12px, 2vw, 16px);
  font-size: clamp(0.8rem, 2vw, 0.9rem);
  font-weight: bold;
}

.lot-capacity {
  background: #6c757d;
  color: white;
  padding: clamp(4px, 1vw, 6px) clamp(8px, 2vw, 12px);
  border-radius: clamp(12px, 2vw, 16px);
  font-size: clamp(0.8rem, 2vw, 0.9rem);
  font-weight: bold;
}

.parking-floor {
  background: #ffffff;
  border: 2px solid #dee2e6;
  border-radius: clamp(8px, 1.5vw, 12px);
  padding: clamp(15px, 3vw, 20px);
  margin-bottom: clamp(15px, 3vw, 20px);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative; /* Add relative positioning for absolute legend */
}

.floor-grid-wrapper {
  position: relative;
  overflow: hidden;
}

.floor-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* Fixed 5 columns for consistent layout */
  gap: clamp(3px, 0.8vw, 5px);
  justify-content: center;
  max-width: 100%;
  padding: clamp(5px, 1vw, 10px);
  overflow-x: hidden;
  overflow-y: auto; /* Vertical scrolling */
  scroll-behavior: smooth;
  max-height: 300px; /* Limit height to enable vertical scrolling */
  scrollbar-width: thin;
  scrollbar-color: #007bff #f1f1f1;
}

.floor-grid::-webkit-scrollbar {
  width: 6px; /* Changed from height to width for vertical scrollbar */
}

.floor-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.floor-grid::-webkit-scrollbar-thumb {
  background: #007bff;
  border-radius: 3px;
}

.floor-grid::-webkit-scrollbar-thumb:hover {
  background: #0056b3;
}

.scroll-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(10px, 2vw, 15px);
  margin-top: clamp(8px, 1.5vw, 12px);
  padding: clamp(5px, 1vw, 8px);
}

.scroll-btn {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
  border: none;
  border-radius: 50%;
  width: clamp(30px, 6vw, 40px);
  height: clamp(30px, 6vw, 40px);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: clamp(16px, 3vw, 20px);
  font-weight: bold;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
}

.scroll-btn:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
}

.scroll-btn:active {
  transform: scale(0.95);
}

.scroll-info {
  background: rgba(108, 117, 125, 0.1);
  padding: clamp(4px, 1vw, 6px) clamp(8px, 2vw, 12px);
  border-radius: clamp(4px, 1vw, 6px);
  font-size: clamp(0.7rem, 1.8vw, 0.8rem);
  color: #6c757d;
  font-weight: 500;
  min-width: clamp(80px, 15vw, 120px);
  text-align: center;
}

.parking-slot {
  width: 100%;
  aspect-ratio: 1;
  min-width: clamp(28px, 6vw, 40px);
  min-height: clamp(28px, 6vw, 40px);
  max-width: clamp(45px, 10vw, 55px);
  max-height: clamp(45px, 10vw, 55px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: clamp(0.6rem, 1.5vw, 0.8rem);
  border-radius: clamp(4px, 1vw, 6px);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  user-select: none;
}

.parking-slot.available {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border-color: #1e7e34;
}

.parking-slot.available:hover {
  background: linear-gradient(135deg, #20c997, #28a745);
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
}

.parking-slot.occupied {
  background: linear-gradient(135deg, #dc3545, #e74c3c);
  color: white;
  border-color: #bd2130;
}

.parking-slot.occupied.clickable {
  cursor: pointer;
  transition: all 0.3s ease;
}

.parking-slot.occupied.clickable:hover {
  background: linear-gradient(135deg, #c82333, #dc3545);
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(220, 53, 69, 0.5);
  border-color: #a71e2a;
}

.lot-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: clamp(8px, 2vw, 12px);
  margin-bottom: clamp(15px, 3vw, 20px);
  flex-wrap: wrap;
}

.btn-sm {
  padding: clamp(4px, 1vw, 6px) clamp(8px, 2vw, 12px);
  font-size: clamp(0.75rem, 2vw, 0.85rem);
  min-width: clamp(60px, 12vw, 80px);
}

.slot-legend {
  position: absolute;
  bottom: 10px;
  left: 10px;
  display: flex;
  align-items: center;
  gap: clamp(10px, 2vw, 15px);
  padding: clamp(6px, 1.5vw, 8px) clamp(8px, 2vw, 12px);
  background: rgba(255, 255, 255, 0.95);
  border-radius: clamp(6px, 1vw, 8px);
  border: 1px solid #dee2e6;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  font-size: clamp(0.7rem, 1.8vw, 0.8rem);
  z-index: 15; /* Ensure legend is always visible */
}

.legend-item {
  display: flex;
  align-items: center;
  gap: clamp(4px, 1vw, 6px);
  font-size: clamp(0.7rem, 1.8vw, 0.8rem);
  font-weight: 500;
  color: #495057;
}

.legend-slot {
  width: clamp(20px, 4vw, 24px);
  height: clamp(20px, 4vw, 24px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: clamp(0.6rem, 1.5vw, 0.7rem);
  border-radius: clamp(3px, 0.5vw, 4px);
  border: 2px solid transparent;
}

.legend-slot.available {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border-color: #1e7e34;
}

.legend-slot.occupied {
  background: linear-gradient(135deg, #dc3545, #e74c3c);
  color: white;
  border-color: #bd2130;
}

.no-lots-message {
  text-align: center;
  font-size: clamp(1rem, 3vw, 1.2rem);
  color: #6c757d;
  padding: clamp(20px, 4vw, 40px);
  background: #f8f9fa;
  border-radius: clamp(8px, 1.5vw, 12px);
  border: 2px dashed #dee2e6;
}

/* Summary Cards Container */
.summary-cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(clamp(180px, 25vw, 220px), 1fr));
  gap: clamp(12px, 2.5vw, 20px);
  margin-top: clamp(15px, 3vw, 20px);
  max-width: 100%;
}

/* Base Summary Card Styles */
.summary-card {
  color: white;
  padding: clamp(15px, 3.5vw, 25px);
  border-radius: clamp(6px, 1vw, 10px);
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.summary-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

/* Primary KPI Cards (First Row) */
.summary-card.primary {
  background: linear-gradient(135deg, #007bff, #0056b3);
  min-height: clamp(100px, 18vh, 130px);
}

.summary-card.primary h3 {
  margin: 0 0 clamp(8px, 2vw, 12px) 0;
  font-size: clamp(0.85rem, 2.8vw, 1.1rem);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
}

.summary-card.primary .summary-value {
  font-size: clamp(1.4rem, 4.5vw, 2.2rem);
  font-weight: bold;
  margin: 0;
  color: white;
}

.summary-card.primary .summary-subtitle {
  font-size: clamp(0.7rem, 1.8vw, 0.85rem);
  opacity: 0.85;
  margin-top: clamp(4px, 1vw, 8px);
  display: block;
  color: rgba(255, 255, 255, 0.8);
}

/* Secondary KPI Cards (Second Row) */
.summary-card.secondary {
  background: linear-gradient(135deg, #28a745, #1e7e34);
  min-height: clamp(80px, 14vh, 110px);
}

.summary-card.secondary h4 {
  margin: 0 0 clamp(6px, 1.5vw, 10px) 0;
  font-size: clamp(0.75rem, 2.2vw, 0.95rem);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
}

.summary-card.secondary .summary-value-small {
  font-size: clamp(1.1rem, 3.8vw, 1.6rem);
  font-weight: bold;
  margin: 0;
  color: white;
}

/* Responsive Grid Adjustments */
@media (max-width: 1200px) {
  .summary-cards-container {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: clamp(10px, 2vw, 16px);
  }
}

@media (max-width: 900px) {
  .summary-cards-container {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: clamp(8px, 1.5vw, 12px);
  }
  
  .summary-card.primary {
    min-height: clamp(90px, 16vh, 110px);
  }
  
  .summary-card.secondary {
    min-height: clamp(70px, 12vh, 90px);
  }
}

@media (max-width: 600px) {
  .summary-cards-container {
    grid-template-columns: repeat(2, 1fr);
    gap: clamp(6px, 1vw, 10px);
  }
  
  .summary-card {
    padding: clamp(10px, 2.5vw, 18px);
  }
  
  .summary-card.primary {
    min-height: clamp(80px, 14vh, 95px);
  }
  
  .summary-card.secondary {
    min-height: clamp(65px, 10vh, 80px);
  }
}

@media (max-width: 400px) {
  .summary-cards-container {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }
}

/* Highlight Section */
.summary-highlight {
  background: linear-gradient(135deg, #ffc107, #e0a800);
  color: #333;
  padding: clamp(15px, 4vw, 25px);
  border-radius: clamp(8px, 1.5vw, 12px);
  text-align: center;
  margin-top: clamp(20px, 4vw, 30px);
  box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
}

.summary-highlight h3 {
  margin: 0 0 clamp(10px, 2vw, 15px) 0;
  font-size: clamp(1rem, 3vw, 1.3rem);
  font-weight: 600;
}

.highlight-value {
  font-size: clamp(1.2rem, 4vw, 1.8rem);
  font-weight: bold;
  margin: 0;
}

/* Search */
.search-container {
  display: flex;
  gap: clamp(8px, 2vw, 10px);
  margin-bottom: clamp(15px, 3vw, 20px);
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  padding: clamp(8px, 2vw, 12px);
  border: 1px solid #ddd;
  border-radius: clamp(4px, 1vw, 6px);
  font-size: clamp(0.85rem, 2.5vw, 1rem);
  min-width: clamp(200px, 40vw, 300px);
}

.search-results {
  margin-top: 20px;
}

.search-results h3 {
  color: #333;
  margin-bottom: 15px;
}

/* Search Section */
.search-section {
  max-width: 100%;
  margin: 0 auto;
}

.search-controls {
  display: flex;
  flex-wrap: wrap;
  gap: clamp(10px, 2vw, 15px);
  margin-bottom: 20px;
  align-items: flex-end;
}

.search-group {
  flex: 1;
  min-width: 200px;
}

.search-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  font-size: clamp(0.9rem, 2vw, 1rem);
}

.search-group input,
.search-group select {
  width: 100%;
  padding: clamp(8px, 2vw, 12px);
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: clamp(0.9rem, 2vw, 1rem);
  box-sizing: border-box;
}

.search-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: clamp(10px 15px, 2vw, 12px 20px);
  border-radius: 5px;
  cursor: pointer;
  font-size: clamp(0.9rem, 2vw, 1rem);
  min-width: 80px;
  height: fit-content;
}

.search-btn:hover {
  background: #0056b3;
}

/* Mobile and Tablet Responsiveness */
@media (max-width: 1024px) {
  .dashboard-wrapper {
    padding: clamp(3px, 0.5vw, 5px);
  }
  
  .dashboard-container {
    border-radius: clamp(3px, 0.5vw, 6px);
    padding: clamp(10px, 2vw, 15px);
  }
  
  .nav-bar {
    justify-content: flex-start;
    overflow-x: auto;
    scrollbar-width: thin;
  }
  
  .lots-container {
    grid-template-columns: repeat(auto-fit, minmax(clamp(200px, 45vw, 280px), 1fr));
  }
  
  .lots-floor-container {
    grid-template-columns: repeat(auto-fit, minmax(clamp(280px, 70vw, 400px), 1fr));
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }
  
  .add-lot-btn {
    width: 100%;
    margin-top: clamp(10px, 2vw, 15px);
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    min-height: calc(100vh - clamp(6px, 1vw, 10px));
    padding: clamp(8px, 2vw, 12px);
  }

  .dashboard-title {
    font-size: clamp(1.3rem, 6vw, 2rem);
  }

  .nav-bar {
    padding: clamp(6px, 1.5vw, 8px);
    gap: clamp(3px, 0.5vw, 5px);
  }

  .nav-btn {
    padding: clamp(5px, 1vw, 8px) clamp(6px, 1.5vw, 12px);
    font-size: clamp(0.7rem, 3vw, 0.85rem);
    min-width: clamp(50px, 12vw, 70px);
  }

  .modal-content {
    width: 95%;
    padding: clamp(12px, 3vw, 20px);
    margin: clamp(5px, 1vh, 15px) auto;
  }

  .btn {
    font-size: clamp(0.7rem, 3vw, 0.85rem);
    padding: clamp(5px, 1vw, 8px) clamp(6px, 1.5vw, 12px);
  }

  .modal-content h3 {
    font-size: clamp(1.1rem, 5vw, 1.5rem);
  }

  .lot-box {
    padding: clamp(8px, 2vw, 12px);
  }
  
  /* Mobile parking floor styles */
  .lots-floor-container {
    grid-template-columns: 1fr;
    gap: clamp(15px, 3vw, 20px);
  }
  
  .parking-floor-tile {
    padding: clamp(12px, 2.5vw, 18px);
  }
  
  .floor-grid {
    grid-template-columns: repeat(auto-fit, minmax(clamp(25px, 6vw, 32px), 1fr));
    gap: clamp(2px, 0.6vw, 4px);
    padding: clamp(3px, 0.8vw, 8px);
  }
  
  .parking-slot {
    min-width: clamp(25px, 6vw, 32px);
    min-height: clamp(25px, 6vw, 32px);
    max-width: clamp(35px, 8vw, 40px);
    max-height: clamp(35px, 8vw, 40px);
    font-size: clamp(0.6rem, 1.8vw, 0.75rem);
  }
  
  .lot-controls {
    gap: clamp(6px, 1.5vw, 8px);
  }
  
  .slot-legend {
    flex-direction: column;
    gap: clamp(8px, 2vw, 12px);
  }
  
  .legend-slot {
    width: clamp(20px, 5vw, 25px);
    height: clamp(20px, 5vw, 25px);
    font-size: clamp(0.6rem, 1.8vw, 0.7rem);
  }

  .search-container {
    flex-direction: column;
    gap: clamp(6px, 1.5vw, 10px);
  }

  .search-input {
    min-width: 100%;
  }

  .search-btn {
    width: 100%;
    padding: clamp(8px, 2vw, 12px);
  }

  .slots-container {
    grid-template-columns: repeat(auto-fit, minmax(clamp(100px, 25vw, 120px), 1fr));
    gap: clamp(5px, 1vw, 8px);
  }
  
  .list-group-item {
    flex-direction: column;
    align-items: flex-start;
    gap: clamp(8px, 2vw, 10px);
  }
  
  .actions {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .nav-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .nav-btn {
    width: 100%;
    text-align: center;
    margin: 0;
  }
  
  .logout-btn {
    margin-left: 0;
    margin-top: clamp(5px, 1vw, 8px);
  }
  
  .lots-container {
    grid-template-columns: 1fr;
  }
  
  .lots-floor-container {
    grid-template-columns: 1fr;
  }
  
  .floor-grid {
    grid-template-columns: repeat(auto-fit, minmax(22px, 1fr));
    gap: 2px;
    padding: 2px;
  }
  
  .parking-slot {
    min-width: 22px;
    min-height: 22px;
    max-width: 28px;
    max-height: 28px;
    font-size: 0.5rem;
  }
  
  .lot-controls {
    flex-direction: column;
    gap: clamp(4px, 1vw, 6px);
  }
  
  .btn-sm {
    width: 100%;
    min-width: auto;
  }
  
  .slot-legend {
    flex-direction: row;
    gap: clamp(10px, 2vw, 15px);
  }
  
  .legend-slot {
    width: 18px;
    height: 18px;
    font-size: 0.5rem;
  }
  
  .slots-container {
    grid-template-columns: repeat(auto-fit, minmax(clamp(80px, 20vw, 100px), 1fr));
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-row .form-group {
    min-width: 100%;
  }
}

/* Users Tab Styles */
.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.user-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.user-info h4 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.user-info p {
  margin: 5px 0;
  color: #666;
  font-size: 0.9rem;
}

.user-actions {
  display: flex;
  gap: 10px;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 0.8rem;
}

/* Search Tab Styles */
.search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 300px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.ml-2 {
  margin-left: 10px;
}

.search-results {
  margin-top: 20px;
}

.search-results h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.result-section {
  margin-bottom: 30px;
}

.result-section h4 {
  color: #495057;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.result-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.result-info h5 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 1rem;
}

.result-info p {
  margin: 5px 0;
  color: #666;
  font-size: 0.9rem;
}

.empty-search, .search-help {
  text-align: center;
  padding: 40px 20px;
  color: #666;
  font-style: italic;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}

/* Responsive adjustments for search and users */
@media (max-width: 768px) {
  .search-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    min-width: 100%;
  }
  
  .users-grid,
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .user-card {
    flex-direction: column;
    gap: 15px;
  }
  
  .user-actions {
    align-self: flex-start;
  }
}

/* ===== BOOKING HISTORY STYLES ===== */
.booking-history-section {
  margin-top: 30px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.section-title {
  margin: 0;
  color: #2c3e50;
  font-size: 1.4rem;
  font-weight: bold;
}

.history-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #333;
  font-size: 0.9rem;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s ease;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-sm {
  padding: 6px 10px;
  font-size: 0.8rem;
}

.loading-spinner {
  text-align: center;
  padding: 40px;
  color: #666;
}

.no-bookings {
  text-align: center;
  padding: 40px;
  color: #666;
  font-style: italic;
}

.booking-history-table {
  overflow-x: auto;
  background: white;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  background: white;
}

.history-table th {
  background: #f8f9fa;
  color: #2c3e50;
  font-weight: bold;
  padding: 12px 8px;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  font-size: 0.9rem;
  white-space: nowrap;
}

.history-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #dee2e6;
  font-size: 0.85rem;
  color: #333;
  background: white;
}

.history-row:hover {
  background-color: #f8f9fa !important;
}

.history-row:hover td {
  background-color: #f8f9fa !important;
}

.booking-id {
  font-weight: bold;
  color: #007bff !important;
}

.user-info {
  min-width: 120px;
}

.user-name {
  font-weight: bold;
  color: #2c3e50 !important;
  margin-bottom: 2px;
}

.user-email {
  color: #666 !important;
  font-size: 0.8rem;
}

.lot-info {
  min-width: 150px;
}

.lot-name {
  font-weight: bold;
  color: #2c3e50 !important;
  margin-bottom: 2px;
}

.lot-address {
  color: #666 !important;
  font-size: 0.8rem;
}

.slot-number {
  font-weight: bold;
  color: #17a2b8 !important;
  text-align: center;
}

.vehicle {
  font-weight: bold;
  color: #28a745 !important;
}

.time {
  color: #555 !important;
  font-size: 0.8rem;
  white-space: nowrap;
}

.duration {
  font-weight: bold;
  color: #fd7e14 !important;
  text-align: center;
}

.cost {
  font-weight: bold;
  color: #dc3545 !important;
  text-align: right;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  color: white !important;
}

.status-badge.completed {
  background: #28a745;
  color: white !important;
}

.status-badge.cancelled {
  background: #dc3545;
  color: white !important;
}

.status-badge.active {
  background: #007bff;
  color: white !important;
}

/* Pagination Styles */
.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 10px;
}

.pagination-info {
  color: #666;
  font-size: 0.9rem;
}

.pagination-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #0056b3;
}

.pagination-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Responsive Design for Booking History */
@media (max-width: 1200px) {
  .history-table th,
  .history-table td {
    padding: 8px 6px;
    font-size: 0.8rem;
  }
  
  .user-email,
  .lot-address {
    display: none;
  }
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .history-controls {
    justify-content: center;
  }
  
  .history-table {
    font-size: 0.75rem;
  }
  
  .history-table th,
  .history-table td {
    padding: 6px 4px;
  }
  
  .user-info,
  .lot-info {
    min-width: auto;
  }
}
</style>
