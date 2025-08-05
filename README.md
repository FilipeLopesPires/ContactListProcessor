# Contact List Processor

A comprehensive command-line tool for processing VCF (vCard) files with various operations including encoding conversion, picture removal, number formatting, name formatting, automatic type setting, and version upgrading. Also includes an interactive tool for selectively deleting contacts.

## Features

The Contact List Processor provides 6 independent operations that can be combined in any order:

1. **Convert to Readable Format** (`-r`, `--readable`)
   - Converts quoted-printable encoding to readable format
   - Removes CHARSET and ENCODING tags
   - Handles line continuations properly

2. **Remove Contact Pictures** (`--remove-pictures`)
   - Removes PHOTO fields and associated base64-encoded data
   - Reduces file size significantly
   - Preserves all other contact information

3. **Format Phone Numbers** (`--format-numbers`)
   - Removes +351 country code prefix
   - Formats 9-digit numbers with spaces (XXX XXX XXX)
   - Only affects TEL fields

4. **Format Contact Names** (`--format-names`)
   - Ensures FN (Formatted Name) field is properly formatted
   - Creates FN field from N field if missing
   - Maintains proper vCard structure

5. **Auto-Set Contact Types** (`--auto-set-types`)
   - Automatically determines contact types based on phone number patterns
   - Numbers starting with "2" → HOME
   - Numbers starting with "9" → CELL
   - Other numbers → VOICE
   - Handles both raw (+351) and formatted numbers

6. **Upgrade VCF Version** (`-u`, `--update-version`)
   - Upgrades VCF from version 2.1 to 3.0
   - Applies proper escaping for special characters
   - Normalizes TYPE fields for TEL and EMAIL entries
   - Ensures proper vCard 3.0 structure

7. **Sort Contacts by Name** (`-s`, `--sort-by-name`)
   - Sorts all contacts alphabetically by name
   - Uses FN field as primary sort key, N field as fallback
   - Case-insensitive sorting
   - Maintains complete contact information
   - Adds blank lines between contacts for readability

## Installation

### Prerequisites

- Python 3.6 or higher
- No additional dependencies required (uses only standard library modules)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ContactListProcessor
   ```

2. Make the scripts executable (optional):
   ```bash
   chmod +x contact-list-processor.py
   chmod +x contact-list-delete-iterator.py
   ```

## Usage

### Main Processing Tool

```bash
python3 contact-list-processor.py -i input.vcf [options]
```

### Interactive Contact Deletion Tool

```bash
python3 contact-list-delete-iterator.py -i input.vcf [options]
```

### Main Processing Tool Arguments

#### Required Arguments
- `-i`, `--input`: Path to the input VCF file (required)

#### Optional Arguments
- `-o`, `--output`: Path to the output VCF file (default: input_path with "_processed" suffix)
- `-r`, `--readable`: Convert quoted-printable encoding to readable format
- `--remove-pictures`: Remove contact pictures from the VCF file
- `--format-numbers`: Format contact phone numbers (remove +351 and format 9-digit numbers)
- `--format-names`: Format contact names (ensure FN field is properly formatted)
- `--auto-set-types`: Automatically set contact types based on phone number patterns
- `-u`, `--update-version`: Upgrade VCF from version 2.1 to 3.0
- `-s`, `--sort-by-name`: Sort all contacts alphabetically by name
- `-a`, `--all`: Apply all operations (equivalent to -r --remove-pictures --format-numbers --format-names --auto-set-types -u -s)
- `-h`, `--help`: Show help message

### Interactive Contact Deletion Tool Arguments

#### Required Arguments
- `-i`, `--input`: Path to the input VCF file (required)

#### Optional Arguments
- `-o`, `--output`: Path to the output VCF file (default: input_path with "_cleaned" suffix)
- `-h`, `--help`: Show help message

### Usage Examples

#### Main Processing Tool - Single Operation
```bash
# Only convert to readable format
python3 contact-list-processor.py -i contacts.vcf -r

# Only remove pictures
python3 contact-list-processor.py -i contacts.vcf --remove-pictures

# Only format phone numbers
python3 contact-list-processor.py -i contacts.vcf --format-numbers

# Only sort contacts by name
python3 contact-list-processor.py -i contacts.vcf -s
```

#### Interactive Contact Deletion Tool
```bash
# Interactive contact deletion with default output
python3 contact-list-delete-iterator.py -i contacts.vcf

# Interactive contact deletion with custom output
python3 contact-list-delete-iterator.py -i contacts.vcf -o cleaned_contacts.vcf
```

#### Main Processing Tool - Multiple Operations
```bash
# Convert encoding and remove pictures
python3 contact-list-processor.py -i contacts.vcf -r --remove-pictures

# Format numbers and names
python3 contact-list-processor.py -i contacts.vcf --format-numbers --format-names

# All operations with custom output
python3 contact-list-processor.py -i contacts.vcf -o processed_contacts.vcf -r --remove-pictures --format-numbers --format-names --auto-set-types -u -s
```

#### Common Workflows

**Complete Contact Cleanup (All Operations):**
```bash
python3 contact-list-processor.py -i messy_contacts.vcf -a
```

**Complete Contact Cleanup (Manual Selection):**
```bash
python3 contact-list-processor.py -i messy_contacts.vcf -r --remove-pictures --format-numbers --format-names --auto-set-types
```

**Version Upgrade with Formatting:**
```bash
python3 contact-list-processor.py -i old_contacts.vcf --format-numbers --format-names -u
```

**Interactive Contact Cleanup:**
```bash
python3 contact-list-delete-iterator.py -i contacts.vcf
```

### Output

#### Main Processing Tool
The script will:
1. Process the VCF file according to specified operations
2. Display progress messages for each operation
3. Save the result to the specified output file (or auto-generated name)
4. Show the final output path

Example output:
```
Converted quoted-printable encoding to readable format
Removed contact pictures
Formatted contact phone numbers
Formatted contact names
Automatically set contact types based on phone number patterns
Upgraded VCF from version 2.1 to 3.0
Processed VCF file saved to: contacts_processed.vcf
```

**Note**: When using `-a` or `--all`, all operations are applied in the optimal order for best results.

#### Interactive Contact Deletion Tool
The script will:
1. Display each contact name and prompt for user input
2. Ask "Y" to delete or "N" to keep (default: N)
3. Show progress with kept/deleted indicators
4. Display summary statistics at completion
5. Save the cleaned file to the specified output path

Example interactive session:
```
Starting contact deletion process...
For each contact, enter 'Y' to delete or 'N' to keep (default: N)
--------------------------------------------------
Contact 1: John Smith - Delete? (Y/N) [N]: 
  Kept: John Smith
Contact 2: Jane Doe - Delete? (Y/N) [N]: y
  Deleted: Jane Doe
Contact 3: Bob Johnson - Delete? (Y/N) [N]: n
  Kept: Bob Johnson
--------------------------------------------------
Process completed!
Total contacts processed: 3
Contacts kept: 2
Contacts deleted: 1
Cleaned VCF file saved to: contacts_cleaned.vcf
```

## File Structure

```
ContactListProcessor/
├── contact-list-processor.py        # Main processing script
├── contact-list-delete-iterator.py  # Interactive contact deletion tool
├── README.md                        # This file
├── LICENSE                          # License information
└── *.vcf                           # Example VCF files (if any)
```

## Technical Details

### Architecture

#### Main Processing Tool
- **Modular Design**: Each operation is implemented as an independent function
- **Data Flow**: Functions receive and return line lists, avoiding intermediate file I/O
- **Order Independence**: Operations can be executed in any order without dependencies
- **Error Handling**: Graceful handling of malformed data and encoding issues

#### Interactive Contact Deletion Tool
- **Interactive Design**: User-driven decision making for each contact
- **Smart Name Extraction**: Uses FN field with N field fallback for contact identification
- **Safe Operation**: Preserves original file, creates new output file
- **Progress Tracking**: Real-time feedback and summary statistics

### Supported Formats

- **Input**: VCF files (vCard 2.1 and 3.0)
- **Output**: VCF files (vCard 3.0 when using version upgrade)
- **Encoding**: UTF-8

### Performance

- **Memory Efficient**: Processes files line by line
- **Fast**: No unnecessary file I/O between operations
- **Scalable**: Handles large contact lists efficiently

## Contributing

We welcome contributions! Here's how you can help:

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/ContactListProcessor.git
   cd ContactListProcessor
   ```

3. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

### Coding Standards

Please follow these conventions:

- **Function Names**: Use camelCase (e.g., `convertToReadable`)
- **Variable Names**: Use snake_case (e.g., `input_path`, `processed_lines`)
- **String Literals**: Use double quotes (`"example"`)
- **Comments**: No emojis or emoticons in code or output text
- **Docstrings**: Include proper documentation for all functions

### Adding New Operations

1. Create a new function following the existing pattern:
   ```python
   def newOperation(lines):
       """
       Description of what the operation does.
       
       Args:
           lines (list): List of VCF file lines
           
       Returns:
           list: Processed VCF lines
       """
       # Implementation here
       return processed_lines
   ```

2. Add command-line argument in `main()`:
   ```python
   parser.add_argument("--new-operation", action="store_true", help="Description")
   ```

3. Add operation call in `main()`:
   ```python
   if args.new_operation:
       processed_lines = newOperation(processed_lines)
       print("Operation completed")
   ```

4. Update validation and help text

### Testing

1. Test with various VCF files:
   ```bash
   python3 contact-list-processor.py -i test.vcf --your-new-operation
   ```

2. Test operation combinations:
   ```bash
   python3 contact-list-processor.py -i test.vcf -r --your-new-operation
   ```

3. Test edge cases:
   - Empty files
   - Malformed VCF data
   - Large files
   - Special characters

### Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/new-operation
   ```

2. Make your changes and test thoroughly

3. Commit with a descriptive message:
   ```bash
   git commit -m "feat: Add new VCF processing operation"
   ```

4. Push to your fork:
   ```bash
   git push origin feature/new-operation
   ```

5. Create a Pull Request with:
   - Clear description of changes
   - Usage examples
   - Test results

### Issue Reporting

When reporting issues, please include:
- VCF file sample (if possible)
- Exact command used
- Error messages
- Expected vs actual behavior
- Python version and OS

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python standard library modules
- Follows vCard specification standards
- Inspired by the need for comprehensive VCF processing tools

## Project Origin

This project was developed specifically to address my personal contact list processing needs, particularly for handling VCF files with Portuguese phone numbers (+351 country code) and various encoding issues. While it was built for my specific use case, the modular architecture makes it easy to modify, improve, and extend for additional contact list processing requirements.

The tool can be easily adapted for:
- Different country codes and phone number formats
- Additional VCF field processing
- Custom contact type classification rules
- Integration with other contact management systems
- Batch processing workflows

Feel free to fork and customize this project for your own specific needs!

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/username/ContactListProcessor/issues) page
2. Create a new issue with detailed information
3. Include sample VCF files when possible

---

**Note**: This tool is designed to be safe and non-destructive. It always creates new output files and preserves the original input files.