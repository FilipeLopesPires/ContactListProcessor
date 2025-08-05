import re

input_path = "00008.vcf"
output_path = "00009.vcf"

with open(input_path, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

converted_lines = []
current_contact = []

# vCard 3.0 escaping rules
def escape_vcard_value(value):
    return value.replace("\\", "\\\\") \
                .replace(";", r"\;") \
                .replace(",", r"\,") \
                .replace("\n", r"\n")

# Process each individual vCard
def process_contact(contact_lines):
    processed = []
    version_line = None
    other_lines = []

    for line in contact_lines:
        stripped = line.strip()

        if stripped.upper() == "VERSION:2.1":
            version_line = "VERSION:3.0\n"
        elif stripped.upper() in ["BEGIN:VCARD", "END:VCARD"]:
            other_lines.append(stripped + "\n")
        elif stripped.upper().startswith("FN:"):
            # Escape special characters for FN
            value = line.strip()[3:]
            escaped_value = escape_vcard_value(value)
            other_lines.append(f"FN:{escaped_value}\n")
        elif stripped.upper().startswith("N:"):
            # Escape N: values but leave structure intact
            value = line.strip()[2:]
            parts = value.split(";")
            escaped_parts = [escape_vcard_value(p) for p in parts]
            other_lines.append(f"N:{';'.join(escaped_parts)}\n")
        elif stripped.upper().startswith("TEL;TYPE="):
            parts = line.strip().split(":", 1)
            if len(parts) == 2:
                left, number = parts
                # Extract and normalize type(s)
                type_match = re.match(r"TEL;TYPE=([\w;,\-]+)", left, re.IGNORECASE)
                if type_match:
                    raw_type = type_match.group(1)
                    types = re.split(r"[;,]", raw_type)
                    types = [t.lower() for t in types if t]
                    joined_types = ",".join(types)
                    other_lines.append(f"TEL;TYPE={joined_types}:{number.strip()}\n")
                else:
                    other_lines.append(line)
            else:
                other_lines.append(line)
        elif stripped.upper().startswith("EMAIL;TYPE="):
            parts = line.strip().split(":", 1)
            if len(parts) == 2:
                left, email = parts
                type_match = re.match(r"EMAIL;TYPE=([\w;,\-]+)", left, re.IGNORECASE)
                if type_match:
                    raw_type = type_match.group(1)
                    types = re.split(r"[;,]", raw_type)
                    types = [t.lower() for t in types if t]
                    joined_types = ",".join(types)
                    other_lines.append(f"EMAIL;TYPE={joined_types}:{email.strip()}\n")
                else:
                    other_lines.append(line)
            else:
                other_lines.append(line)
        else:
            # Escape special characters in other fields, but preserve field name
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                escaped_value = escape_vcard_value(value)
                other_lines.append(f"{key}:{escaped_value}\n")
            else:
                other_lines.append(line)

    # Reorder lines: BEGIN:VCARD, VERSION, then everything else
    for line in other_lines:
        if line.strip().upper() == "BEGIN:VCARD":
            processed.append(line)
            if version_line:
                processed.append(version_line)
        elif line.strip().upper() == "END:VCARD":
            processed.append(line)
        else:
            processed.append(line)

    return processed

# Group contacts and process each
for line in lines:
    if line.strip().upper() == "BEGIN:VCARD":
        current_contact = [line]
    elif line.strip().upper() == "END:VCARD":
        current_contact.append(line)
        converted_contact = process_contact(current_contact)
        converted_lines.extend(converted_contact)
        converted_lines.append("\n")  # blank line between contacts
        current_contact = []
    else:
        current_contact.append(line)

# Write output
with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(converted_lines)

print(f"✅ vCard 2.1 → 3.0 conversion complete: {output_path}")
