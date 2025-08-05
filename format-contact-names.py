import re

input_path = "00005.vcf"
output_path = "00006.vcf"

with open(input_path, "r", encoding="utf-8") as infile:
    lines = infile.readlines()

cleaned_lines = []
current_contact = []

def process_contact(contact_lines):
    fn_line = None
    n_line = None
    other_lines = []

    for line in contact_lines:
        stripped = line.strip()
        if stripped.upper().startswith("FN:"):
            if not fn_line:
                fn_line = stripped  # keep only first FN
        elif stripped.upper().startswith("N:"):
            n_line = stripped[2:]  # Remove "N:"
        elif stripped.upper().startswith("BEGIN:VCARD") or stripped.upper().startswith("END:VCARD"):
            continue  # handled separately
        else:
            other_lines.append(line)

    # If no FN, build from N
    if not fn_line and n_line:
        parts = n_line.split(";")
        family = parts[0].strip() if len(parts) > 0 else ""
        given = parts[1].strip() if len(parts) > 1 else ""
        additional = parts[2].strip() if len(parts) > 2 else ""
        fn_parts = [given, additional, family]
        fn_combined = " ".join(part for part in fn_parts if part)
        fn_line = f"FN:{fn_combined}"

    # Rebuild full contact
    processed = ["BEGIN:VCARD\n"]
    if fn_line:
        processed.append(fn_line + "\n")
    processed.extend(other_lines)
    processed.append("END:VCARD\n")
    return processed

# Read and group contacts
for line in lines:
    if line.strip().upper() == "BEGIN:VCARD":
        current_contact = [line]
    elif line.strip().upper() == "END:VCARD":
        current_contact.append(line)
        cleaned_contact = process_contact(current_contact)
        cleaned_lines.extend(cleaned_contact)
        cleaned_lines.append("\n")  # Add empty line between contacts
        current_contact = []
    else:
        current_contact.append(line)

# Write output
with open(output_path, "w", encoding="utf-8") as outfile:
    outfile.writelines(cleaned_lines)

print(f"✅ Cleaned vCard written to: {output_path} (with blank lines between contacts)")
