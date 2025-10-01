def calculate_sum(a, b):
    # This function has a bug - it uses print instead of return
    print(a + b)

def greet(name):
    # Another issue - using print instead of return
    print(f"Hello, {name}!")

# Main execution
if __name__ == "__main__":
    calculate_sum(5, 3)
    greet("World")
