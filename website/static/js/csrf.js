// csrf.js

// Get CSRF token from cookies
// Returns the CSRF token value from the document cookies
function getCSRFToken() {
  return document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
}

// Make a POST request with CSRF token
// Sends a POST request to the specified URL with JSON data and CSRF token in headers
async function apiPost(url, data) {
  const csrftoken = getCSRFToken();

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  return response.json();
}