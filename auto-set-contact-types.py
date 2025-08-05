import re

input_path = "00007.vcf"
output_path = "00008.vcf"

def determine_type(phone_number: str) -> str:
    number = phone_number.strip().replace(" ", "").replace("-", "")
    if number.startswith("2"):
        return "HOME"
    elif number.startswith("9") or number.startswith("+"):
        return "CELL"
    else:
        return "VOICE"  # fallback

with open(input_path, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

cleaned_lines = []

for line in lines:
    if line.strip().upper().startswith("TEL;TYPE="):
        # Extract the phone number from TEL;TYPE=phone_number format
        phone_number = line.strip().replace("TEL;TYPE=", "")
        
        # Check if the TYPE field contains digits (which means it's actually a phone number)
        if re.search(r'\d', phone_number):
            # Determine the correct type based on the phone number
            corrected_type = determine_type(phone_number)
            new_line = f"TEL;TYPE={corrected_type}:{phone_number}\n"
            cleaned_lines.append(new_line)
            continue
    cleaned_lines.append(line)

with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(cleaned_lines)

print(f"vCard saved with corrected TYPE values: {output_path}")
