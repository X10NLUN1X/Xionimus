// Sequential (slower)
const user = await fetchUser();
const posts = await fetchPosts();

// Parallel (faster)
const [user, posts] = await Promise.all([
  fetchUser(),
  fetchPosts()
]);