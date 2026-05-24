from datetime import datetime, UTC, timezone

print ("Hello, World!")

# Get current date and time
print(f"Current time: {datetime.now()}") 
print(f"Current UTC time (3.11+): {datetime.now(UTC)}")
print(f"Current UTC time (3.2+): {datetime.now(timezone.utc)}") 

