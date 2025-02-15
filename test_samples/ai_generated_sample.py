def calculate_fibonacci_sequence(n: int) -> list[int]:
    """
    Calculate the Fibonacci sequence up to the nth number using dynamic programming.
    
    Args:
        n (int): The number of Fibonacci sequence elements to generate
        
    Returns:
        list[int]: A list containing the first n numbers in the Fibonacci sequence
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Number of elements must be non-negative")
    
    # Initialize the sequence with base cases
    fibonacci_sequence = [0, 1]
    
    # Generate subsequent numbers
    for i in range(2, n):
        fibonacci_sequence.append(fibonacci_sequence[i-1] + fibonacci_sequence[i-2])
    
    return fibonacci_sequence[:n]

def main():
    try:
        # Get user input for sequence length
        sequence_length = int(input("Enter the length of Fibonacci sequence: "))
        
        # Calculate and display the sequence
        result = calculate_fibonacci_sequence(sequence_length)
        print(f"Fibonacci sequence of length {sequence_length}:")
        print(result)
        
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
