// Simple test to verify token storage works

console.log("Testing token storage...");

// Simulate a login by storing a test token
const testToken = "user_2_1234567890";
localStorage.setItem('token', testToken);

// Verify it was stored
const retrievedToken = localStorage.getItem('token');
console.log("Stored token:", testToken);
console.log("Retrieved token:", retrievedToken);
console.log("Tokens match:", testToken === retrievedToken);

// Test profile API call
fetch('/api/auth/profile', {
  headers: {
    'Authorization': `Bearer ${retrievedToken}`
  }
})
.then(response => response.json())
.then(data => {
  console.log("Profile API response:", data);
  if (data.profile) {
    console.log("User name:", data.profile.full_name);
  }
})
.catch(error => {
  console.error("Profile API error:", error);
});
