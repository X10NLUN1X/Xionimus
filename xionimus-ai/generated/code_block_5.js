try {
  console.log('1. Login attempt for:', email);
  const user = await findUser(email);
  console.log('2. User found:', !!user);
  const valid = await checkPassword(password, user.hash);
  console.log('3. Password valid:', valid);
  const token = generateJWT(user);
  console.log('4. Token generated:', !!token);
  return token;
} catch (error) {
  console.error('ACTUAL ERROR:', error); // ← What does THIS say?
  throw error;
}