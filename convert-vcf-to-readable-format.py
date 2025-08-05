import quopri
import re

input_path = "00002.vcf"
output_path = "00003.vcf"

with open(input_path, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

cleaned_lines = []
buffer = ""
processing_buffer = False

for line in lines:
    line_stripped = line.rstrip('\r\n')

    # Handle line continuations (soft line breaks in quoted-printable)
    if line_stripped.endswith('='):
        buffer += line_stripped[:-1]
        processing_buffer = True
        continue
    elif processing_buffer:
        buffer += line_stripped
        line_stripped = buffer
        buffer = ""
        processing_buffer = False

    if "ENCODING=QUOTED-PRINTABLE" in line_stripped:
        parts = line_stripped.split(":", 1)
        if len(parts) == 2:
            key, encoded = parts
            try:
                # Remove CHARSET and ENCODING tags
                key = re.sub(r";CHARSET=[^;]+", "", key)
                key = re.sub(r";ENCODING=QUOTED-PRINTABLE", "", key)
                decoded = quopri.decodestring(encoded).decode("utf-8")
                cleaned_line = f"{key}:{decoded}\n"
                cleaned_lines.append(cleaned_line)
            except Exception as e:
                # If decoding fails, keep original line
                print(f"Warning: couldn't decode line: {line_stripped}")
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
    else:
        cleaned_lines.append(line)

# Write output
with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(cleaned_lines)

print(f"Cleaned vCard saved to: {output_path}")
