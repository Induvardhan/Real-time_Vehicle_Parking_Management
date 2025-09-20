<script setup>
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <div id="app">
    <div class="app-container">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f8f9fa;
  min-height: 100vh;
  width: 100%;
}

.app-container {
  max-width: min(95vw, 1200px);
  margin: clamp(1rem, 3vw, 2rem) auto;
  padding: 0 clamp(10px, 2vw, 20px);
  width: 100%;
  box-sizing: border-box;
}

nav a {
  text-decoration: none;
}

/* Global responsive utilities */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

@media (max-width: 768px) {
  .app-container {
    margin: clamp(0.5rem, 2vw, 1rem) auto;
    padding: 0 clamp(5px, 1vw, 10px);
  }
}
</style>
