import re

input_path = "00003.vcf"
output_path = "00004.vcf"

with open(input_path, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

cleaned_lines = []
skip_photo = False

for line in lines:
    # Start skipping when PHOTO line begins
    if re.match(r"^PHOTO(;.*)?:", line.strip(), re.IGNORECASE):
        skip_photo = True
        continue

    # Continue skipping if line is part of base64-encoded photo (indented or long data)
    if skip_photo:
        if line.startswith(" ") or line.startswith("\t") or line.strip() == "":
            continue
        else:
            skip_photo = False  # End of photo section

    # Append line if we're not in a photo block
    if not skip_photo:
        cleaned_lines.append(line)

# Write output
with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(cleaned_lines)

print(f"Cleaned vCard (without contact photos) saved to: {output_path}")
