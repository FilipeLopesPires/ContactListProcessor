import re

input_path = "00006.vcf"
output_path = "00007.vcf"

with open(input_path, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

cleaned_lines = []

for line in lines:
    # Target lines with TYPE=... followed by colon
    if re.match(r'^TEL;TYPE=.*?:', line.strip(), re.IGNORECASE):
        # Extract everything after the colon (the actual number or value)
        parts = line.strip().split(":", 1)
        if len(parts) == 2:
            _, value = parts
            # Replace line with simplified TYPE=value
            new_line = f"TEL;TYPE={value}\n"
            cleaned_lines.append(new_line)
        else:
            cleaned_lines.append(line)
    else:
        cleaned_lines.append(line)

# Write output
with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(cleaned_lines)

print(f"Cleaned vCard with TYPE values replaced: {output_path}")
