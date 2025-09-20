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
          <h1 class="auth-title">Welcome Back</h1>
          <p class="auth-subtitle">Sign in to your ParkEase account</p>
        </div>

        <form @submit.prevent="login" class="auth-form">
          <div class="form-group">
            <label for="email" class="form-label">Email Address *</label>
            <input 
              v-model="email" 
              type="email" 
              id="email" 
              class="form-input" 
              placeholder="Enter your email address"
              required 
              autocomplete="email"
            />
          </div>

          <div class="form-group">
            <label for="password" class="form-label">Password *</label>
            <input 
              v-model="password" 
              type="password" 
              id="password" 
              class="form-input" 
              placeholder="Enter your password"
              required 
              autocomplete="current-password"
            />
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? 'Signing In...' : 'Sign In' }}
          </button>
        </form>

        <!-- Messages -->
        <div v-if="error" class="alert alert-error">
          <span class="alert-icon">⚠️</span>
          {{ error }}
        </div>

        <!-- Footer Links -->
        <div class="auth-footer">
          <p>Don't have an account? 
            <router-link to="/user/register" class="auth-link">Create Account</router-link>
          </p>
          <div class="additional-links">
            <a href="#" class="forgot-link">Forgot Password?</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserLogin',
  data() {
    return {
      email: '',
      password: '',
      error: '',
      loading: false
    };
  },
  mounted() {
    if (localStorage.getItem('token')) {
      this.$router.push('/user/dashboard');
    }
  },
  methods: {
    async login() {
      this.error = '';
      this.loading = true;
      
      try {
        const response = await fetch('/api/auth/user/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            email: this.email, 
            password: this.password 
          })
        });
        
        const data = await response.json();
        console.log('[DEBUG] Login response:', data);
        
        if (response.ok) {
          console.log('[DEBUG] Login successful, storing token:', data.token);
          localStorage.setItem('token', data.token);
          console.log('[DEBUG] Token stored in localStorage');
          this.$router.push('/user/dashboard');
        } else {
          this.error = data.message || 'Login failed. Please check your credentials.';
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
  max-width: 450px;
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

.form-group {
  margin-bottom: 25px;
}

.form-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 8px;
  display: block;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f7fafc;
  box-sizing: border-box;
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

.additional-links {
  margin-top: 15px;
}

.forgot-link {
  color: #a0aec0;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.forgot-link:hover {
  color: #667eea;
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
  
  .auth-footer {
    padding: 10px 15px 20px;
  }
}
</style>
