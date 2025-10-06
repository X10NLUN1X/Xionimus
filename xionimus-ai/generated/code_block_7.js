// Make sure all async operations are properly awaited
// BAD
const user = db.query('SELECT * FROM users WHERE id = $1', [id]);
// GOOD
const user = await db.query('SELECT * FROM users WHERE id = $1', [id]);