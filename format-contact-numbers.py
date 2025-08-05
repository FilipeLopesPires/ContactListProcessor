import re

input_path = "00004.vcf"
output_path = "00005.vcf"

with open(input_path, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

cleaned_lines = []

# Helper function to clean and format a 9-digit number
def normalize_phone_number(line):
    # Remove +351 with or without separators
    line = re.sub(r'\+351[\s\-\.\\\/]*', '', line)

    # Function to reformat matched 9-digit sequence
    def replacer(match):
        digits = re.findall(r'\d', match.group(0))
        if len(digits) == 9:
            return f"{digits[0]}{digits[1]}{digits[2]} {digits[3]}{digits[4]}{digits[5]} {digits[6]}{digits[7]}{digits[8]}"
        else:
            return match.group(0)

    # Apply replacement only to likely number sections (after "TEL")
    if "TEL" in line.upper():
        # Replace all 9-digit patterns, allowing for existing separators
        line = re.sub(r'(?<!\d)([\d\D]{9,15}?)(?!\d)', replacer, line)
    return line

# Process each line
for line in lines:
    if line.strip().upper().startswith("TEL"):
        cleaned_line = normalize_phone_number(line)
        cleaned_lines.append(cleaned_line)
    else:
        cleaned_lines.append(line)

# Write cleaned vCard
with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(cleaned_lines)

print(f"vCard saved with normalized 9-digit numbers (without +351) to: {output_path}")
