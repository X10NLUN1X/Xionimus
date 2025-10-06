"""
Code Templates for Cloud Sandbox
Provides starter code for all 12 supported languages
"""

CODE_TEMPLATES = {
    "python": {
        "name": "Python",
        "hello_world": '''print("Hello, World!")

# Your code here
name = input("Enter your name: ")
print(f"Hello, {name}!")
''',
        "fibonacci": '''def fibonacci(n):
    """Calculate nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Test
for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
''',
        "data_structures": '''# Lists
numbers = [1, 2, 3, 4, 5]
print("Numbers:", numbers)

# Dictionaries
person = {"name": "John", "age": 30, "city": "New York"}
print("Person:", person)

# List comprehension
squares = [x**2 for x in range(10)]
print("Squares:", squares)
'''
    },
    
    "javascript": {
        "name": "JavaScript",
        "hello_world": '''console.log("Hello, World!");

// Your code here
const name = "JavaScript";
console.log(`Hello, ${name}!`);
''',
        "fibonacci": '''function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Test
for (let i = 0; i < 10; i++) {
    console.log(`fib(${i}) = ${fibonacci(i)}`);
}
''',
        "data_structures": '''// Arrays
const numbers = [1, 2, 3, 4, 5];
console.log("Numbers:", numbers);

// Objects
const person = {
    name: "John",
    age: 30,
    city: "New York"
};
console.log("Person:", person);

// Array methods
const doubled = numbers.map(x => x * 2);
console.log("Doubled:", doubled);
'''
    },
    
    "typescript": {
        "name": "TypeScript",
        "hello_world": '''console.log("Hello, World!");

// Type-safe code
const greet = (name: string): string => {
    return `Hello, ${name}!`;
};

console.log(greet("TypeScript"));
''',
        "fibonacci": '''function fibonacci(n: number): number {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Test
for (let i: number = 0; i < 10; i++) {
    console.log(`fib(${i}) = ${fibonacci(i)}`);
}
''',
        "data_structures": '''interface Person {
    name: string;
    age: number;
    city: string;
}

const person: Person = {
    name: "John",
    age: 30,
    city: "New York"
};

console.log("Person:", person);

// Generics
function identity<T>(arg: T): T {
    return arg;
}

console.log(identity<string>("Hello"));
console.log(identity<number>(42));
'''
    },
    
    "java": {
        "name": "Java",
        "hello_world": '''public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        
        String name = "Java";
        System.out.println("Hello, " + name + "!");
    }
}
''',
        "fibonacci": '''public class Fibonacci {
    public static int fibonacci(int n) {
        if (n <= 1) return n;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    public static void main(String[] args) {
        for (int i = 0; i < 10; i++) {
            System.out.println("fib(" + i + ") = " + fibonacci(i));
        }
    }
}
''',
        "data_structures": '''import java.util.*;

public class DataStructures {
    public static void main(String[] args) {
        // ArrayList
        ArrayList<Integer> numbers = new ArrayList<>();
        numbers.add(1);
        numbers.add(2);
        numbers.add(3);
        System.out.println("Numbers: " + numbers);
        
        // HashMap
        HashMap<String, Integer> map = new HashMap<>();
        map.put("age", 30);
        map.put("year", 2025);
        System.out.println("Map: " + map);
    }
}
'''
    },
    
    "cpp": {
        "name": "C++",
        "hello_world": '''#include <iostream>
#include <string>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    
    string name = "C++";
    cout << "Hello, " << name << "!" << endl;
    
    return 0;
}
''',
        "fibonacci": '''#include <iostream>
using namespace std;

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    for (int i = 0; i < 10; i++) {
        cout << "fib(" << i << ") = " << fibonacci(i) << endl;
    }
    return 0;
}
''',
        "data_structures": '''#include <iostream>
#include <vector>
#include <map>
using namespace std;

int main() {
    // Vector
    vector<int> numbers = {1, 2, 3, 4, 5};
    cout << "Numbers: ";
    for (int n : numbers) {
        cout << n << " ";
    }
    cout << endl;
    
    // Map
    map<string, int> ages;
    ages["John"] = 30;
    ages["Jane"] = 25;
    
    for (auto& pair : ages) {
        cout << pair.first << ": " << pair.second << endl;
    }
    
    return 0;
}
'''
    },
    
    "c": {
        "name": "C",
        "hello_world": '''#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    
    char name[] = "C";
    printf("Hello, %s!\\n", name);
    
    return 0;
}
''',
        "fibonacci": '''#include <stdio.h>

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    for (int i = 0; i < 10; i++) {
        printf("fib(%d) = %d\\n", i, fibonacci(i));
    }
    return 0;
}
''',
        "data_structures": '''#include <stdio.h>

int main() {
    // Arrays
    int numbers[] = {1, 2, 3, 4, 5};
    int size = sizeof(numbers) / sizeof(numbers[0]);
    
    printf("Numbers: ");
    for (int i = 0; i < size; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\\n");
    
    // Strings
    char name[] = "John";
    printf("Name: %s\\n", name);
    
    return 0;
}
'''
    },
    
    "csharp": {
        "name": "C#",
        "hello_world": '''using System;

class Program {
    static void Main() {
        Console.WriteLine("Hello, World!");
        
        string name = "C#";
        Console.WriteLine($"Hello, {name}!");
    }
}
''',
        "fibonacci": '''using System;

class Fibonacci {
    static int Fib(int n) {
        if (n <= 1) return n;
        return Fib(n - 1) + Fib(n - 2);
    }
    
    static void Main() {
        for (int i = 0; i < 10; i++) {
            Console.WriteLine($"fib({i}) = {Fib(i)}");
        }
    }
}
''',
        "data_structures": '''using System;
using System.Collections.Generic;

class DataStructures {
    static void Main() {
        // List
        var numbers = new List<int> { 1, 2, 3, 4, 5 };
        Console.WriteLine("Numbers: " + string.Join(", ", numbers));
        
        // Dictionary
        var ages = new Dictionary<string, int> {
            {"John", 30},
            {"Jane", 25}
        };
        
        foreach (var pair in ages) {
            Console.WriteLine($"{pair.Key}: {pair.Value}");
        }
    }
}
'''
    },
    
    "go": {
        "name": "Go",
        "hello_world": '''package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
    
    name := "Go"
    fmt.Printf("Hello, %s!\\n", name)
}
''',
        "fibonacci": '''package main

import "fmt"

func fibonacci(n int) int {
    if n <= 1 {
        return n
    }
    return fibonacci(n-1) + fibonacci(n-2)
}

func main() {
    for i := 0; i < 10; i++ {
        fmt.Printf("fib(%d) = %d\\n", i, fibonacci(i))
    }
}
''',
        "data_structures": '''package main

import "fmt"

func main() {
    // Slices
    numbers := []int{1, 2, 3, 4, 5}
    fmt.Println("Numbers:", numbers)
    
    // Maps
    ages := map[string]int{
        "John": 30,
        "Jane": 25,
    }
    
    for name, age := range ages {
        fmt.Printf("%s: %d\\n", name, age)
    }
}
'''
    },
    
    "php": {
        "name": "PHP",
        "hello_world": '''<?php
echo "Hello, World!\\n";

$name = "PHP";
echo "Hello, $name!\\n";
''',
        "fibonacci": '''<?php
function fibonacci($n) {
    if ($n <= 1) return $n;
    return fibonacci($n - 1) + fibonacci($n - 2);
}

for ($i = 0; $i < 10; $i++) {
    echo "fib($i) = " . fibonacci($i) . "\\n";
}
''',
        "data_structures": '''<?php
// Arrays
$numbers = [1, 2, 3, 4, 5];
echo "Numbers: " . implode(", ", $numbers) . "\\n";

// Associative arrays
$person = [
    "name" => "John",
    "age" => 30,
    "city" => "New York"
];

foreach ($person as $key => $value) {
    echo "$key: $value\\n";
}
'''
    },
    
    "ruby": {
        "name": "Ruby",
        "hello_world": '''puts "Hello, World!"

name = "Ruby"
puts "Hello, #{name}!"
''',
        "fibonacci": '''def fibonacci(n)
  return n if n <= 1
  fibonacci(n - 1) + fibonacci(n - 2)
end

10.times do |i|
  puts "fib(#{i}) = #{fibonacci(i)}"
end
''',
        "data_structures": '''# Arrays
numbers = [1, 2, 3, 4, 5]
puts "Numbers: #{numbers}"

# Hashes
person = {
  name: "John",
  age: 30,
  city: "New York"
}

person.each do |key, value|
  puts "#{key}: #{value}"
end

# Array methods
doubled = numbers.map { |n| n * 2 }
puts "Doubled: #{doubled}"
'''
    },
    
    "perl": {
        "name": "Perl",
        "hello_world": '''print "Hello, World!\\n";

my $name = "Perl";
print "Hello, $name!\\n";
''',
        "fibonacci": '''sub fibonacci {
    my $n = shift;
    return $n if $n <= 1;
    return fibonacci($n - 1) + fibonacci($n - 2);
}

for my $i (0..9) {
    print "fib($i) = " . fibonacci($i) . "\\n";
}
''',
        "data_structures": '''# Arrays
my @numbers = (1, 2, 3, 4, 5);
print "Numbers: @numbers\\n";

# Hashes
my %person = (
    name => "John",
    age => 30,
    city => "New York"
);

while (my ($key, $value) = each %person) {
    print "$key: $value\\n";
}
'''
    },
    
    "bash": {
        "name": "Bash",
        "hello_world": '''#!/bin/bash
echo "Hello, World!"

name="Bash"
echo "Hello, $name!"
''',
        "fibonacci": '''#!/bin/bash
fibonacci() {
    local n=$1
    if [ $n -le 1 ]; then
        echo $n
    else
        echo $(( $(fibonacci $(( n - 1 ))) + $(fibonacci $(( n - 2 ))) ))
    fi
}

for i in {0..9}; do
    echo "fib($i) = $(fibonacci $i)"
done
''',
        "data_structures": '''#!/bin/bash
# Arrays
numbers=(1 2 3 4 5)
echo "Numbers: ${numbers[@]}"

# Associative arrays
declare -A person
person[name]="John"
person[age]=30
person[city]="New York"

for key in "${!person[@]}"; do
    echo "$key: ${person[$key]}"
done
'''
    }
}


def get_template(language: str, template_type: str = "hello_world") -> str:
    """
    Get code template for specified language and type
    
    Args:
        language: Programming language (python, javascript, etc.)
        template_type: Template type (hello_world, fibonacci, data_structures)
    
    Returns:
        Template code string or empty string if not found
    """
    if language not in CODE_TEMPLATES:
        return ""
    
    templates = CODE_TEMPLATES[language]
    return templates.get(template_type, templates.get("hello_world", ""))


def get_all_templates(language: str) -> dict:
    """Get all available templates for a language"""
    if language not in CODE_TEMPLATES:
        return {}
    
    return CODE_TEMPLATES[language]


def get_available_languages() -> list:
    """Get list of languages with templates"""
    return list(CODE_TEMPLATES.keys())


def get_available_template_types() -> list:
    """Get list of available template types"""
    return ["hello_world", "fibonacci", "data_structures"]