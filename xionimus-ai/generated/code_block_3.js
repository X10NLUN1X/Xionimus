// Traditional Promise chain
function getUser() {
  return fetch('/api/user')
    .then(response => response.json())
    .then(user => {
      console.log(user);
      return user;
    })
    .catch(error => console.error(error));
}

// Async/await version
async function getUser() {
  try {
    const response = await fetch('/api/user');
    const user = await response.json();
    console.log(user);
    return user;
  } catch (error) {
    console.error(error);
  }
}