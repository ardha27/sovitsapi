import json

def sovits_data(speaker_value, duration_value, status_value):
    # Load existing data from the database.json file
    try:
        with open("database.json", "r", encoding='utf-8') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    # Determine the next id by incrementing the last id if available
    if existing_data:
        last_id = max(existing_data, key=lambda x: x["id"])["id"]
        next_id = last_id + 1
    else:
        next_id = 1

    data = {
        "id": next_id,
        "speaker": speaker_value,
        "duration": round(duration_value, 2),
        "status": status_value
    }

    # Append the new data to the existing data
    existing_data.append(data)

    # Save the updated data to the database.json file
    with open("database.json", "w", encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4)

    return next_id

def update_status(id_value, new_status):
    # Load existing data from the database.json file
    try:
        with open("database.json", "r", encoding='utf-8') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    # Find the data with the matching ID
    for data in existing_data:
        if data["id"] == id_value:
            # Update the status
            data["status"] = new_status
            break
    else:
        print(f"Data with ID {id_value} not found.")

    # Save the updated data to the database.json file
    with open("database.json", "w", encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4)