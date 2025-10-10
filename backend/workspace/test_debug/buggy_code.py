"""Test file with intentional bugs for debugging demo"""

def calculate_average(numbers):
    """Calculate average - has division by zero bug"""
    # BUG: No check for empty list
    total = sum(numbers)
    return total / len(numbers)  # Will crash on empty list!

def process_data(data):
    """Process data - has type error"""
    # BUG: Assumes data is always a dict
    return data['value'] * 2  # Will crash if data is not a dict!

def find_max(items):
    """Find maximum - has edge case bug"""
    # BUG: Doesn't handle empty list
    max_val = items[0]  # IndexError on empty list!
    for item in items:
        if item > max_val:
            max_val = item
    return max_val

class DataProcessor:
    def __init__(self):
        # BUG: Typo in attribute name
        self.procesor_count = 0  # Should be processor_count
    
    def process(self, data):
        # BUG: Using undefined attribute
        self.processor_count += 1  # AttributeError!
        return data * 2

# Test code that will fail
if __name__ == "__main__":
    # This will cause errors when run
    print("Testing buggy code...")
    
    # Test 1: Division by zero
    result = calculate_average([])
    print(f"Average: {result}")
    
    # Test 2: Type error
    result = process_data("not a dict")
    print(f"Processed: {result}")
    
    # Test 3: Index error
    result = find_max([])
    print(f"Max: {result}")