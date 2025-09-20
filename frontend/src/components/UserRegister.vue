<template>
  <div class="auth-container">
    <!-- Header with Logo -->
    <header class="auth-header">
      <div class="logo-container">
        <router-link to="/" class="logo-link">
          <div class="logo">
            <span class="logo-icon">🅿️</span>
            <span class="logo-text">ParkEase</span>
          </div>
        </router-link>
      </div>
    </header>

    <!-- Main Content -->
    <div class="auth-content">
      <div class="auth-card">
        <div class="card-header">
          <h1 class="auth-title">Create Your Account</h1>
          <p class="auth-subtitle">Join ParkEase and find parking spots effortlessly</p>
        </div>

        <form @submit.prevent="register" class="auth-form">
          <!-- Personal Information Section -->
          <div class="form-section">
            <h3 class="section-title">Personal Information</h3>
            
            <div class="form-row">
              <div class="form-group">
                <label for="fullName" class="form-label">Full Name *</label>
                <input 
                  v-model="fullName" 
                  type="text" 
                  id="fullName" 
                  class="form-input" 
                  placeholder="Enter your full name"
                  required 
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="email" class="form-label">Email Address *</label>
                <input 
                  v-model="email" 
                  type="email" 
                  id="email" 
                  class="form-input" 
                  placeholder="Enter your email address"
                  required 
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="phone" class="form-label">Phone Number *</label>
                <input 
                  v-model="phone" 
                  type="tel" 
                  id="phone" 
                  class="form-input" 
                  placeholder="Enter your phone number"
                  pattern="[0-9]{10,}"
                  required 
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="password" class="form-label">Password *</label>
                <input 
                  v-model="password" 
                  type="password" 
                  id="password" 
                  class="form-input" 
                  placeholder="Create a strong password"
                  minlength="6"
                  required 
                />
              </div>
            </div>
          </div>

          <!-- Address Information Section -->
          <div class="form-section">
            <h3 class="section-title">Address Information</h3>
            
            <div class="form-row">
              <div class="form-group">
                <label for="addressLine1" class="form-label">Address Line 1 *</label>
                <input 
                  v-model="addressLine1" 
                  type="text" 
                  id="addressLine1" 
                  class="form-input" 
                  placeholder="Enter your street address"
                  required 
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group half-width">
                <label for="city" class="form-label">City *</label>
                <input 
                  v-model="city" 
                  type="text" 
                  id="city" 
                  class="form-input" 
                  placeholder="Enter your city"
                  required 
                />
              </div>
              <div class="form-group half-width">
                <label for="state" class="form-label">State *</label>
                <input 
                  v-model="state" 
                  type="text" 
                  id="state" 
                  class="form-input" 
                  placeholder="Enter your state"
                  required 
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group half-width">
                <label for="pinCode" class="form-label">PIN Code *</label>
                <input 
                  v-model="pinCode" 
                  type="text" 
                  id="pinCode" 
                  class="form-input" 
                  placeholder="Enter PIN code"
                  pattern="[0-9]{6}"
                  maxlength="6"
                  required 
                />
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? 'Creating Account...' : 'Create Account' }}
          </button>
        </form>

        <!-- Messages -->
        <div v-if="error" class="alert alert-error">
          <span class="alert-icon">⚠️</span>
          {{ error }}
        </div>
        <div v-if="success" class="alert alert-success">
          <span class="alert-icon">✅</span>
          Registration successful! Redirecting to login...
        </div>

        <!-- Footer Links -->
        <div class="auth-footer">
          <p>Already have an account? 
            <router-link to="/user/login" class="auth-link">Sign In</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserRegister',
  data() {
    return {
      fullName: '',
      email: '',
      phone: '',
      password: '',
      addressLine1: '',
      city: '',
      state: '',
      pinCode: '',
      error: '',
      success: false,
      loading: false
    };
  },
  mounted() {
    if (localStorage.getItem('token')) {
      this.$router.push('/user/dashboard');
    }
  },
  methods: {
    async register() {
      this.error = '';
      this.success = false;
      this.loading = true;
      
      try {
        const response = await fetch('/api/auth/user/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            fullName: this.fullName,
            email: this.email,
            phone: this.phone,
            password: this.password,
            addressLine1: this.addressLine1,
            city: this.city,
            state: this.state,
            pinCode: this.pinCode
          })
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.success = true;
          setTimeout(() => {
            this.$router.push('/user/login');
          }, 2000);
        } else {
          this.error = data.message || 'Registration failed. Please try again.';
        }
      } catch (err) {
        this.error = 'Server error. Please try again later.';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Auth Container */
.auth-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

/* Header */
.auth-header {
  padding: 20px 40px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.logo-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 10px 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.logo-link {
  text-decoration: none;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Main Content */
.auth-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  overflow: hidden;
}

.card-header {
  padding: 40px 40px 20px;
  text-align: center;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8eeff 100%);
}

.auth-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 10px;
}

.auth-subtitle {
  font-size: 1.1rem;
  color: #718096;
  margin: 0;
}

/* Form */
.auth-form {
  padding: 30px 40px;
}

.form-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.form-group.half-width {
  flex: 0.5;
}

.form-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 8px;
}

.form-input {
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  color: #2d3748;
  transition: all 0.3s ease;
  background: #f7fafc;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  color: #1a202c;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:invalid {
  border-color: #fc8181;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Alerts */
.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin: 20px 40px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.alert-error {
  background: #fed7d7;
  color: #c53030;
  border: 1px solid #fc8181;
}

.alert-success {
  background: #c6f6d5;
  color: #2f855a;
  border: 1px solid #68d391;
}

.alert-icon {
  font-size: 1.1rem;
}

/* Footer */
.auth-footer {
  padding: 20px 40px 40px;
  text-align: center;
  color: #718096;
}

.auth-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.auth-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 768px) {
  .auth-header {
    padding: 15px 20px;
  }
  
  .card-header {
    padding: 30px 20px 15px;
  }
  
  .auth-title {
    font-size: 2rem;
  }
  
  .auth-subtitle {
    font-size: 1rem;
  }
  
  .auth-form {
    padding: 20px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .form-group.half-width {
    flex: 1;
  }
  
  .alert {
    margin: 20px;
  }
  
  .auth-footer {
    padding: 15px 20px 30px;
  }
}

@media (max-width: 480px) {
  .auth-content {
    padding: 10px;
  }
  
  .auth-card {
    border-radius: 12px;
  }
  
  .card-header {
    padding: 20px 15px 10px;
  }
  
  .auth-title {
    font-size: 1.8rem;
  }
  
  .auth-form {
    padding: 15px;
  }
}
</style>
