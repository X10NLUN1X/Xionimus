// Test file with JavaScript bugs

function divideNumbers(a, b) {
    // BUG: No check for division by zero
    return a / b;
}

function getProperty(obj, prop) {
    // BUG: No null check
    return obj[prop].toUpperCase();  // Will crash if obj is null or prop doesn't exist
}

async function fetchData(url) {
    // BUG: No error handling
    const response = await fetch(url);
    const data = await response.json();  // Will crash on non-JSON response
    return data;
}

class Calculator {
    constructor() {
        // BUG: Typo in property
        this.resuIt = 0;  // Should be result
    }
    
    add(a, b) {
        // BUG: Using wrong property name
        this.result = a + b;  // ReferenceError!
        return this.result;
    }
}

// Test code
console.log("Testing buggy JavaScript...");
console.log(divideNumbers(10, 0));  // Infinity, but should handle better
console.log(getProperty(null, "test"));  // Will crash