<template>
  <div class="homepage-container">
    <!-- Logo at top left -->
    <div class="logo-container">
      <div class="logo">
        <span class="logo-icon">🅿️</span>
        <span class="logo-text">ParkEase</span>
      </div>
    </div>
    
    <!-- Header with navigation buttons at top right -->
    <div class="header">
      <button class="btn btn-primary" @click="goToAdminLogin">Admin Login</button>
      <button class="btn btn-success" @click="goToUserRegister">User Register</button>
      <button class="btn btn-secondary" @click="goToUserLogin">User Login</button>
    </div>
    
    <div class="content">
      <p class="description">Welcome to the Vehicle Parking App. Manage parking spots, reservations, and more with ease.</p>
    </div>
    <div class="footer">
      <p>All rights reserved @2025</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomePage",
  methods: {
    goToAdminLogin() {
      this.$router.push("/admin-login");
    },
    goToUserRegister() {
      this.$router.push("/user-register");
    },
    goToUserLogin() {
      this.$router.push("/user-login");
    },
  },
};
</script>

<style>
.homepage-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  height: 100vh;
  padding: clamp(15px, 3vw, 20px);
  background: #e0e0e0;
  color: black;
  text-align: center;
  position: relative;
}

/* Logo styles */
.logo-container {
  position: absolute;
  top: clamp(15px, 3vw, 20px);
  left: clamp(15px, 3vw, 20px);
  z-index: 10;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 10px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #2980b9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Header styles */
.header {
  position: absolute;
  top: clamp(15px, 3vw, 20px);
  right: clamp(15px, 3vw, 20px);
  display: flex;
  flex-wrap: wrap;
  gap: clamp(8px, 2vw, 10px);
}

.header button {
  background-color: #2980b9;
  border: none;
  color: white;
  padding: clamp(8px 12px, 2vw, 10px 15px);
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: clamp(0.8rem, 2.5vw, 1rem);
  min-width: 80px;
}

.header button:hover {
  background-color: #1abc9c;
}

.content {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: clamp(10px, 3vw, 20px);
}

.description {
  font-size: clamp(1rem, 3vw, 1.125rem);
  max-width: min(90vw, 600px);
  background-color: rgba(255, 255, 255, 0.8);
  padding: clamp(15px, 3vw, 20px);
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
}

.footer {
  font-size: clamp(0.8rem, 2.5vw, 0.875rem);
  background-color: #d0d0d0;
  color: black;
  padding: clamp(8px, 2vw, 10px);
  width: 100%;
  text-align: center;
}

@media (max-width: 768px) {
  .logo-container {
    position: relative;
    top: auto;
    left: auto;
    align-self: flex-start;
    margin-bottom: 15px;
  }
  
  .header {
    position: relative;
    top: auto;
    right: auto;
    width: 100%;
    justify-content: center;
    margin-bottom: 20px;
  }

  .header button {
    flex: 1;
    min-width: 100px;
  }

  .homepage-container {
    padding: clamp(10px, 2vw, 15px);
    align-items: stretch;
  }
  
  .content {
    align-items: center;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .logo {
    padding: 8px 12px;
  }
  
  .logo-icon {
    font-size: 20px;
  }
  
  .logo-text {
    font-size: 16px;
  }
  
  .header {
    flex-direction: column;
    gap: clamp(6px, 1.5vw, 8px);
  }

  .header button {
    width: 100%;
  }
}
</style>
