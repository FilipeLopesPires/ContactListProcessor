#!/usr/bin/env python3
"""
Contact List Delete Iterator

An interactive tool for selectively deleting contacts from VCF (vCard) files.
Iterates through each contact, displaying the name and asking for user input
to decide whether to keep or delete the contact.
"""

import argparse
import os
import re

def main():
    """Main function to handle command-line interface and contact iteration."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Interactively delete contacts from VCF files")
    parser.add_argument("-i", "--input", required=True, help="Path to the input VCF file")
    parser.add_argument("-o", "--output", help="Path to the output VCF file (default: input_path with \"_cleaned\" suffix)")
    
    # Parse arguments
    args = parser.parse_args()
    
    input_path = args.input
    
    # Set output path - if not provided, use input path with "_cleaned" suffix
    if args.output:
        output_path = args.output
    else:
        # Split the input path into base and extension
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_cleaned{ext}"

    # Read the input file
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    # Process the VCF file interactively
    cleaned_lines = iterateAndDeleteContacts(lines)

    # Write the final result to output file
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.writelines(cleaned_lines)

    print(f"Cleaned VCF file saved to: {output_path}")

def extractContactName(contact_lines):
    """
    Extract the name from a contact for display.
    
    Args:
        contact_lines (list): List of lines for a single contact
        
    Returns:
        str: Contact name for display
    """
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
                # Combine Given + Additional + Family for display
                given = parts[1].strip() if len(parts) > 1 else ""
                additional = parts[2].strip() if len(parts) > 2 else ""
                family = parts[0].strip() if len(parts) > 0 else ""
                n_parts = [given, additional, family]
                n_name = " ".join(part for part in n_parts if part)
    
    # Prefer FN field, fallback to N field if FN is empty
    if fn_name:
        return fn_name
    elif n_name:
        return n_name
    else:
        return "Unknown Contact"

def iterateAndDeleteContacts(lines):
    """
    Iterate through contacts and ask user to decide whether to keep or delete each.
    
    Args:
        lines (list): List of VCF file lines
        
    Returns:
        list: VCF lines with deleted contacts removed
    """
    cleaned_lines = []
    current_contact = []
    contact_count = 0
    deleted_count = 0
    
    print("Starting contact deletion process...")
    print("For each contact, enter 'Y' to delete or 'N' to keep (default: N)")
    print("-" * 50)

    # Group contacts and process each
    for line in lines:
        if line.strip().upper() == "BEGIN:VCARD":
            current_contact = [line]
        elif line.strip().upper() == "END:VCARD":
            current_contact.append(line)
            contact_count += 1
            
            # Extract contact name for display
            contact_name = extractContactName(current_contact)
            
            # Ask user for decision
            while True:
                user_input = input(f"Contact {contact_count}: {contact_name} - Delete? (Y/N) [N]: ").strip().upper()
                
                if user_input == "" or user_input == "N":
                    # Keep the contact
                    cleaned_lines.extend(current_contact)
                    cleaned_lines.append("\n")  # Add blank line between contacts
                    print(f"  Kept: {contact_name}")
                    break
                elif user_input == "Y":
                    # Delete the contact
                    deleted_count += 1
                    print(f"  Deleted: {contact_name}")
                    break
                else:
                    print("  Invalid input. Please enter 'Y' to delete or 'N' to keep.")
            
            current_contact = []
        else:
            current_contact.append(line)

    # Print summary
    print("-" * 50)
    print(f"Process completed!")
    print(f"Total contacts processed: {contact_count}")
    print(f"Contacts kept: {contact_count - deleted_count}")
    print(f"Contacts deleted: {deleted_count}")
    
    return cleaned_lines

if __name__ == "__main__":
    main() 