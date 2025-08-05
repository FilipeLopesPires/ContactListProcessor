#!/usr/bin/env python3
"""
Contact List Processor

A comprehensive tool for processing VCF (vCard) files with various operations
including encoding conversion, picture removal, number formatting, name formatting,
automatic type setting, and version upgrading.
"""

import quopri
import re
import argparse
import os

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process VCF files with various operations")
    parser.add_argument("-i", "--input", required=True, help="Path to the input VCF file")
    parser.add_argument("-o", "--output", help="Path to the output VCF file (default: input_path with \"_processed\" suffix)")
    parser.add_argument("-r", "--readable", action="store_true", help="Convert quoted-printable encoding to readable format")
    parser.add_argument("--remove-pictures", action="store_true", help="Remove contact pictures from the VCF file")
    parser.add_argument("--remove-optional-fields", action="store_true", help="Remove non-mandatory fields (BDAY, ADR, EMAIL, etc.) keeping only essential contact info")
    parser.add_argument("--format-numbers", action="store_true", help="Format contact phone numbers (remove +351 and format 9-digit numbers)")
    parser.add_argument("--format-names", action="store_true", help="Format contact names (ensure FN field is properly formatted)")
    parser.add_argument("--auto-set-types", action="store_true", help="Automatically set contact types based on phone number patterns")
    parser.add_argument("-u", "--update-version", action="store_true", help="Upgrade VCF from version 2.1 to 3.0")
    parser.add_argument("-s", "--sort-by-name", action="store_true", help="Sort all contacts alphabetically by name")
    parser.add_argument("-a", "--all", action="store_true", help="Apply all operations (equivalent to -r --remove-pictures --format-numbers --format-names --auto-set-types -u)")
    
    # Parse arguments
    args = parser.parse_args()
    
    input_path = args.input
    
    # Set output path - if not provided, use input path with "_processed" suffix
    if args.output:
        output_path = args.output
    else:
        # Split the input path into base and extension
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_processed{ext}"

    # Check if at least one operation is specified
    if not args.readable and not args.remove_pictures and not args.remove_optional_fields and not args.format_numbers and not args.format_names and not args.auto_set_types and not args.update_version and not args.sort_by_name and not args.all:
        print("Error: At least one operation must be specified. Use -r/--readable, --remove-pictures, --remove-optional-fields, --format-numbers, --format-names, --auto-set-types, -u/--update-version, -s/--sort-by-name, or -a/--all")
        return

    # Read the input file
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    # Process the VCF file based on specified operations
    processed_lines = lines
    
    # Handle --all flag: apply all operations
    if args.all:
        processed_lines = convertToReadable(processed_lines)
        print("Converted quoted-printable encoding to readable format")
        
        processed_lines = removeContactPictures(processed_lines)
        print("Removed contact pictures")
        
        processed_lines = removeOptionalFields(processed_lines)
        print("Removed non-mandatory fields")
        
        processed_lines = formatContactNumbers(processed_lines)
        print("Formatted contact phone numbers")
        
        processed_lines = formatContactNames(processed_lines)
        print("Formatted contact names")
        
        processed_lines = autoSetContactTypes(processed_lines)
        print("Automatically set contact types based on phone number patterns")
        
        processed_lines = upgradeVcfVersion(processed_lines)
        print("Upgraded VCF from version 2.1 to 3.0")
        
        processed_lines = sortContactsByName(processed_lines)
        print("Sorted contacts alphabetically by name")
    else:
        # Individual operations
        if args.readable:
            processed_lines = convertToReadable(processed_lines)
            print("Converted quoted-printable encoding to readable format")
        
        if args.remove_pictures:
            processed_lines = removeContactPictures(processed_lines)
            print("Removed contact pictures")
        
        if args.remove_optional_fields:
            processed_lines = removeOptionalFields(processed_lines)
            print("Removed non-mandatory fields")
        
        if args.format_numbers:
            processed_lines = formatContactNumbers(processed_lines)
            print("Formatted contact phone numbers")
        
        if args.format_names:
            processed_lines = formatContactNames(processed_lines)
            print("Formatted contact names")
        
        if args.auto_set_types:
            processed_lines = autoSetContactTypes(processed_lines)
            print("Automatically set contact types based on phone number patterns")
        
        if args.update_version:
            processed_lines = upgradeVcfVersion(processed_lines)
            print("Upgraded VCF from version 2.1 to 3.0")
        
        if args.sort_by_name:
            processed_lines = sortContactsByName(processed_lines)
            print("Sorted contacts alphabetically by name")

    # Write the final result to output file
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.writelines(processed_lines)

    print(f"Processed VCF file saved to: {output_path}")

def convertToReadable(lines):
    """
    Process VCF lines to convert quoted-printable encoding to readable format.
    
    Args:
        lines (list): List of VCF file lines
        
    Returns:
        list: Processed VCF lines with readable encoding
    """
    readable_lines = []
    buffer = ""
    processing_buffer = False

    for line in lines:
        line_stripped = line.rstrip("\r\n")

        # Handle line continuations (soft line breaks in quoted-printable)
        if line_stripped.endswith("="):
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
                    readable_line = f"{key}:{decoded}\n"
                    readable_lines.append(readable_line)
                except Exception as e:
                    # If decoding fails, keep original line
                    print(f"Warning: couldn't decode line: {line_stripped}")
                    readable_lines.append(line)
            else:
                readable_lines.append(line)
        else:
            readable_lines.append(line)

    return readable_lines

def removeContactPictures(lines):
    """
    Remove contact pictures from VCF lines.
    
    Args:
        lines (list): List of VCF file lines
        
    Returns:
        list: VCF lines with contact pictures removed
    """
    lines_without_pictures = []
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
            lines_without_pictures.append(line)

    return lines_without_pictures

def removeOptionalFields(lines):
    """
    Remove non-mandatory fields from VCF lines, keeping only essential contact information.
    
    Args:
        lines (list): List of VCF file lines
        
    Returns:
        list: VCF lines with non-mandatory fields removed
    """
    lines_without_optional = []
    current_contact = []

    # Define mandatory fields that should be kept
    mandatory_fields = {
        "BEGIN:VCARD",
        "END:VCARD", 
        "VERSION",
        "FN",  # Formatted Name
        "N",   # Name
        "TEL"  # Telephone
    }

    def is_mandatory_field(line):
        """Check if a line contains a mandatory field."""
        stripped = line.strip().upper()
        
        # Check for exact matches first
        if stripped in ["BEGIN:VCARD", "END:VCARD"]:
            return True
        
        # Check for field prefixes
        for field in mandatory_fields:
            if stripped.startswith(field):
                return True
        
        # Handle TEL with TYPE parameters
        if stripped.startswith("TEL;TYPE="):
            return True
        
        return False

    # Process each contact
    for line in lines:
        if line.strip().upper() == "BEGIN:VCARD":
            current_contact = [line]
        elif line.strip().upper() == "END:VCARD":
            current_contact.append(line)
            lines_without_optional.extend(current_contact)
            lines_without_optional.append("\n")  # Add blank line between contacts
            current_contact = []
        else:
            # Only keep mandatory fields
            if is_mandatory_field(line):
                current_contact.append(line)
            # Skip non-mandatory fields (BDAY, ADR, EMAIL, ORG, TITLE, etc.)

    return lines_without_optional

def formatContactNumbers(lines):
    """
    Format contact phone numbers by removing +351 prefix and formatting 9-digit numbers.
    
    Args:
        lines (list): List of VCF file lines
        
    Returns:
        list: VCF lines with formatted phone numbers
    """
    formatted_lines = []
    
    # Helper function to clean and format a 9-digit number
    def normalize_phone_number(line):
        # Standardize TEL format first
        line = standardize_tel_format(line)
        
        # Remove +351 with or without separators
        line = re.sub(r"\+351[\s\-\.\\\/]*", "", line)

        # Function to reformat matched 9-digit sequence
        def replacer(match):
            digits = re.findall(r"\d", match.group(0))
            if len(digits) == 9:
                return f"{digits[0]}{digits[1]}{digits[2]} {digits[3]}{digits[4]}{digits[5]} {digits[6]}{digits[7]}{digits[8]}"
            else:
                return match.group(0)

        # Apply replacement only to likely number sections (after "TEL")
        if "TEL" in line.upper():
            # Replace all 9-digit patterns, allowing for existing separators
            line = re.sub(r"(?<!\d)([\d\D]{9,15}?)(?!\d)", replacer, line)
        return line

    def standardize_tel_format(line):
        """Standardize TEL format to TEL;TYPE=type:number format."""
        stripped = line.strip()
        
        # Handle TEL;TYPE=CELL: format (already correct)
        if re.match(r"^TEL;TYPE=[^:]+:", stripped, re.IGNORECASE):
            return line
        
        # Handle TEL;CELL:, TEL;WORK:, TEL;HOME:, etc. format
        tel_type_match = re.match(r"^TEL;([^:]+):(.+)$", stripped, re.IGNORECASE)
        if tel_type_match:
            type_value = tel_type_match.group(1).strip()
            number = tel_type_match.group(2).strip()
            
            # Map common type values to standard types
            type_mapping = {
                "CELL": "cell",
                "MOBILE": "cell", 
                "WORK": "work",
                "HOME": "home",
                "VOICE": "voice",
                "FAX": "fax",
                "PAGER": "pager",
                "VIDEO": "video",
                "TEXT": "text",
                "TEXTPHONE": "textphone"
            }
            
            # Convert to lowercase and map to standard type
            type_lower = type_value.lower()
            standardized_type = type_mapping.get(type_lower, type_lower)
            
            return f"TEL;TYPE={standardized_type}:{number}\n"
        
        # Handle simple TEL: format (no type specified)
        if re.match(r"^TEL:", stripped, re.IGNORECASE):
            # Extract the number after TEL:
            number = stripped[4:].strip()
            return f"TEL;TYPE=voice:{number}\n"
        
        return line

    # Process each line
    for line in lines:
        if line.strip().upper().startswith("TEL"):
            formatted_line = normalize_phone_number(line)
            formatted_lines.append(formatted_line)
        else:
            formatted_lines.append(line)

    return formatted_lines

def formatContactNames(lines):
    """
    Format contact names by ensuring FN field is properly formatted from N field if needed.
    
    Args:
        lines (list): List of VCF file lines
        
    Returns:
        list: VCF lines with properly formatted contact names
    """
    formatted_lines = []
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
            formatted_contact = process_contact(current_contact)
            formatted_lines.extend(formatted_contact)
            formatted_lines.append("\n")  # Add empty line between contacts
            current_contact = []
        else:
            current_contact.append(line)

    return formatted_lines

def autoSetContactTypes(lines):
    """
    Automatically set contact types based on phone number patterns.
    First removes existing type information, then sets new types based on number patterns.
    
    Args:
        lines (list): List of VCF file lines
        
    Returns:
        list: VCF lines with automatically set contact types
    """
    lines_with_auto_types = []

    def remove_types_from_line(line):
        """Remove existing type information from a TEL line."""
        # Target lines with TYPE=... followed by colon
        if re.match(r"^TEL;TYPE=.*?:", line.strip(), re.IGNORECASE):
            # Extract everything after the colon (the actual number or value)
            parts = line.strip().split(":", 1)
            if len(parts) == 2:
                _, value = parts
                # Return simplified TYPE=value format
                return f"TEL;TYPE={value}\n"
        return line

    def determine_type(phone_number: str) -> str:
        # Remove +351 prefix if present, spaces, and dashes
        number = phone_number.strip().replace(" ", "").replace("-", "")
        if number.startswith("+351"):
            number = number[4:]  # Remove +351 prefix
        elif number.startswith("351"):
            number = number[3:]  # Remove 351 prefix without +
        
        if number.startswith("2"):
            return "HOME"
        elif number.startswith("9"):
            return "CELL"
        elif number.startswith("+"):
            return "CELL"
        else:
            return "VOICE"  # fallback

    # First pass: remove existing type information
    lines_without_types = []
    for line in lines:
        lines_without_types.append(remove_types_from_line(line))

    # Second pass: set new types based on phone number patterns
    for line in lines_without_types:
        if line.strip().upper().startswith("TEL;TYPE="):
            # Extract the phone number from TEL;TYPE=phone_number format
            phone_number = line.strip().replace("TEL;TYPE=", "")
            
            # Check if the TYPE field contains digits (which means it's actually a phone number)
            if re.search(r"\d", phone_number):
                # Determine the correct type based on the phone number
                corrected_type = determine_type(phone_number)
                new_line = f"TEL;TYPE={corrected_type}:{phone_number}\n"
                lines_with_auto_types.append(new_line)
                continue
        lines_with_auto_types.append(line)

    return lines_with_auto_types

def upgradeVcfVersion(lines):
    """
    Upgrade VCF from version 2.1 to 3.0 with proper escaping and formatting.
    
    Args:
        lines (list): List of VCF file lines
        
    Returns:
        list: VCF lines upgraded to version 3.0
    """
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

    return converted_lines

def sortContactsByName(lines):
    """
    Sort all contacts alphabetically by name (FN field).
    
    Args:
        lines (list): List of VCF file lines
        
    Returns:
        list: VCF lines with contacts sorted by name
    """
    sorted_lines = []
    current_contact = []
    contacts = []

    def extract_contact_name(contact_lines):
        """Extract the name from a contact for sorting."""
        fn_name = ""
        n_name = ""
        
        for line in contact_lines:
            stripped = line.strip()
            if stripped.upper().startswith("FN:"):
                # Extract the name after "FN:"
                fn_name = stripped[3:].strip()
            elif stripped.upper().startswith("N:"):
                # Extract the name from N field as fallback
                n_value = stripped[2:].strip()
                if n_value:
                    # N field format: Family;Given;Additional;Prefix;Suffix
                    parts = n_value.split(";")
                    # Combine Given + Additional + Family for sorting
                    given = parts[1].strip() if len(parts) > 1 else ""
                    additional = parts[2].strip() if len(parts) > 2 else ""
                    family = parts[0].strip() if len(parts) > 0 else ""
                    n_parts = [given, additional, family]
                    n_name = " ".join(part for part in n_parts if part)
        
        # Prefer FN field, fallback to N field if FN is empty
        if fn_name:
            return fn_name.lower()  # Use lowercase for case-insensitive sorting
        elif n_name:
            return n_name.lower()  # Use lowercase for case-insensitive sorting
        else:
            return ""  # Return empty string if no name field found

    # Group contacts and extract names for sorting
    for line in lines:
        if line.strip().upper() == "BEGIN:VCARD":
            current_contact = [line]
        elif line.strip().upper() == "END:VCARD":
            current_contact.append(line)
            contact_name = extract_contact_name(current_contact)
            contacts.append((contact_name, current_contact))
            current_contact = []
        else:
            current_contact.append(line)

    # Sort contacts by name
    contacts.sort(key=lambda x: x[0])

    # Rebuild the file with sorted contacts
    for _, contact_lines in contacts:
        sorted_lines.extend(contact_lines)
        sorted_lines.append("\n")  # Add blank line between contacts

    return sorted_lines

if __name__ == "__main__":
    main()
