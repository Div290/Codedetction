# Quick script to process some data
# TODO: Clean this up later, bit messy but works for now

data = []  # will store processed items

def process_item(x):
    # hacky fix for weird edge case
    if x < 0:
        x = abs(x) # probably should handle this better
    
    # main logic
    result = x * 2
    if result > 100:
        result = 100  # cap it
    
    return result

# process everything
nums = [1, -5, 60, 42, -10, 200]
for n in nums:
    # skip zeros, they break things
    if n == 0:
        continue
        
    processed = process_item(n)
    data.append(processed)
    
# print results
print("Processed data:")
for item in data:
    print(f"- {item}")
