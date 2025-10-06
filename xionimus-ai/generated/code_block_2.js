// Are you awaiting the hash comparison?
const valid = await bcrypt.compare(password, hash); // ✓
const valid = bcrypt.compare(password, hash); // ✗ returns Promise