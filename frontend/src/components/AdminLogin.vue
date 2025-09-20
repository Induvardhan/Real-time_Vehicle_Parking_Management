<template>
  <div class="container d-flex align-items-center justify-content-center min-vh-100">
    <header class="header">
      <button @click="$router.push('/')" class="btn btn-link">Go to Homepage</button>
    </header>
    <div class="card shadow p-4">
      <h2 class="mb-4 text-center">Admin Login</h2>
      <form @submit.prevent="login">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input v-model="username" type="text" id="username" class="form-control" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input v-model="password" type="password" id="password" class="form-control" required />
        </div>
        <button type="submit" class="btn btn-primary w-100">Login</button>
      </form>
      <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminLogin',
  data() {
    return {
      username: '',
      password: '',
      error: ''
    };
  },
  mounted() {
    if (localStorage.getItem('token')) {
      this.$router.push('/admin/dashboard');
    }
  },
  methods: {
    login() {
      this.error = '';
      if (this.username === 'admin' && this.password === 'password123') {
        localStorage.setItem('token', 'dummy-token');
        this.$router.push('/admin/dashboard');
      } else {
        this.error = 'Invalid username or password.';
      }
    }
  }
};
</script>

<<style scoped>
.container {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: #fff;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(1rem, 3vw, 2rem);
}

.card {
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: clamp(1.5rem, 4vw, 2rem);
  max-width: min(90vw, 400px);
  width: 100%;
}

.card h2 {
  color: #333;
  font-weight: bold;
  margin-bottom: 1.5rem;
  font-size: clamp(1.5rem, 4vw, 2rem);
}

.form-label {
  font-weight: 600;
  color: #555;
  font-size: clamp(0.9rem, 2.5vw, 1rem);
}

.form-control {
  border-radius: 8px;
  border: 1px solid #ddd;
  padding: clamp(0.6rem, 2vw, 0.75rem);
  font-size: clamp(0.9rem, 2.5vw, 1rem);
}

.form-control:focus {
  border-color: #6a11cb;
  box-shadow: 0 0 0 0.2rem rgba(106, 17, 203, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  border: none;
  border-radius: 8px;
  padding: clamp(0.6rem, 2vw, 0.75rem);
  font-weight: bold;
  font-size: clamp(0.9rem, 2.5vw, 1rem);
  transition: background 0.3s;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #2575fc 0%, #6a11cb 100%);
}

.alert {
  border-radius: 8px;
  padding: clamp(0.6rem, 2vw, 0.75rem);
  font-weight: 600;
  font-size: clamp(0.8rem, 2vw, 0.9rem);
}

.header {
  position: absolute;
  top: 0;
  right: 0;
  margin: clamp(0.5rem, 2vw, 1rem);
}

.header .btn {
  font-size: clamp(0.8rem, 2vw, 0.9rem);
  padding: clamp(0.4rem 0.8rem, 2vw, 0.5rem 1rem);
}
</style>
