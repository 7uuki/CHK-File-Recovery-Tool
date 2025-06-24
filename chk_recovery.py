import os
import zipfile
from datetime import datetime
import struct
import xml.etree.ElementTree as ET

# Known file signatures (Hex → File extension)
SIGNATURES = {

    b'\x0A': '.pcx',  # PCX (ZBrush)
    b'L\x00\x00\x00': '.lnk',  # Windows shortcut
    b'ftypqt': '.mov',  # QuickTime

    # Images
    b'\xFF\xD8\xFF': '.jpg',
    b'\x89PNG\r\n\x1a\n': '.png',
    b'GIF87a': '.gif',
    b'GIF89a': '.gif',
    b'\x42\x4D': '.bmp',
    b'\x00\x00\x01\x00': '.ico',
    b'\x49\x49\x2A\x00': '.tif',
    b'\x4D\x4D\x00\x2A': '.tif',
    b'RIFF': '.webp',  # Will be refined in detect_file_type

    # Documents
    b'%PDF-': '.pdf',
    b'\x25\x21\x50\x53': '.ps',
    b'PK\x03\x04': '.zip',  # ZIP files (including Office documents)

    # Audio
    b'ID3': '.mp3',
    b'\xFF\xFB': '.mp3',
    b'\xFF\xF3': '.mp3',
    b'\xFF\xF2': '.mp3',
    b'OggS': '.ogg',
    b'fLaC': '.flac',
    b'RIFF': '.wav',  # Will be refined in detect_file_type

    # Video
    b'\x00\x00\x00\x18ftypmp4': '.mp4',
    b'\x00\x00\x00\x20ftypmp4': '.mp4',
    b'\x00\x00\x00\x1Cftypmp4': '.mp4',
    b'ftypmp4': '.mp4',
    b'ftypisom': '.mp4',
    b'ftypMSNV': '.mp4',
    b'ftypM4V': '.m4v',
    b'RIFF': '.avi',  # Will be refined in detect_file_type
    b'\x1A\x45\xDF\xA3': '.mkv',
    b'FLV\x01': '.flv',
    b'\x00\x00\x01\xBA': '.mpg',
    b'\x00\x00\x01\xB3': '.mpg',

    # Archives
    b'Rar!\x1A\x07\x00': '.rar',
    b'Rar!\x1A\x07\x01\x00': '.rar',
    b'\x37\x7A\xBC\xAF\x27\x1C': '.7z',

    # Office (legacy)
    b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': '.ole',  # MS Office legacy + .msg
}


def print_header():
    """Display program logo and information"""
    print("=" * 60)
    print("    CHK FILE RECOVERY TOOL")
    print("    Recovers .chk files")
    print("    Filename based on 'Date Last Saved'")
    print("=" * 60)
    print()


def detect_file_type(file_path):
    """Detect file type based on signature"""
    try:
        # Read first 512 bytes
        with open(file_path, 'rb') as f:
            header = f.read(512)

            # Check for text files first (UTF-8, ASCII)
            if is_text_file(header):
                return '.txt'

            # Check specific RIFF-based formats
            if header.startswith(b'RIFF') and len(header) >= 12:
                riff_type = header[8:12]
                if riff_type == b'WAVE':
                    return '.wav'
                elif riff_type == b'AVI ':
                    return '.avi'
                elif riff_type == b'WEBP':
                    return '.webp'

            # Check for video formats with ftyp
            if b'ftyp' in header[:32]:
                ftyp_pos = header.find(b'ftyp')
                if ftyp_pos != -1 and ftyp_pos + 8 <= len(header):
                    brand = header[ftyp_pos + 4:ftyp_pos + 8]
                    if brand in [b'mp41', b'mp42', b'isom', b'M4V ', b'MSNV']:
                        return '.mp4'
                    elif brand == b'M4V ':
                        return '.m4v'

            # Check standard signatures
            for sig, ext in SIGNATURES.items():
                if header.startswith(sig):
                    if ext == '.ole':
                        # Check specifically for .msg
                        if b'__substg1.0_1000001E' in header:
                            return '.msg'
                        # Default to .doc for OLE
                        return '.doc'
                    elif ext == '.zip':
                        # Analyze ZIP content to determine specific type
                        return analyze_zip_content(file_path)
                    else:
                        return ext

    except Exception:
        pass

    return None


def is_text_file(data):
    """Check if data represents a text file"""
    if not data:
        return False

    # Check for BOM (Byte Order Mark)
    if data.startswith(b'\xEF\xBB\xBF'):  # UTF-8 BOM
        return True
    if data.startswith(b'\xFF\xFE') or data.startswith(b'\xFE\xFF'):  # UTF-16 BOM
        return True

    # Check first 512 bytes for text characteristics
    text_characters = 0
    printable_chars = 0

    for byte in data[:512]:
        if 32 <= byte <= 126:  # Printable ASCII
            printable_chars += 1
            text_characters += 1
        elif byte in [9, 10, 13]:  # Tab, LF, CR
            text_characters += 1
        elif byte < 32 or byte > 126:  # Non-printable
            # Allow some non-printable characters for UTF-8
            if byte >= 128:  # Potential UTF-8
                text_characters += 0.5

    # If more than 70% are text characters, consider it a text file
    if len(data) > 0:
        text_ratio = text_characters / len(data[:512])
        return text_ratio > 0.7

    return False


def analyze_zip_content(file_path):
    """Analyze ZIP file content to determine specific type"""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            namelist = zip_ref.namelist()

            # Check for Office document signatures
            if '[Content_Types].xml' in namelist:
                if any(name.startswith('word/') for name in namelist):
                    return '.docx'
                elif any(name.startswith('xl/') for name in namelist):
                    return '.xlsx'
                elif any(name.startswith('ppt/') for name in namelist):
                    return '.pptx'

            # Check for other specific ZIP-based formats
            if 'META-INF/MANIFEST.MF' in namelist:
                return '.jar'  # Java Archive

            if 'AndroidManifest.xml' in namelist:
                return '.apk'  # Android Package

            # Default to regular ZIP file
            return '.zip'

    except zipfile.BadZipFile:
        # If it starts with PK but isn't a valid ZIP, might be corrupted
        return '.zip'
    except Exception:
        pass

    return '.zip'


def get_office_last_saved(file_path, file_ext):
    """Try to extract 'Date Last Saved' from Office documents"""
    try:
        # For modern Office formats (docx, xlsx, pptx)
        if file_ext in ['.docx', '.xlsx', '.pptx']:
            return get_office_xml_date(file_path)

        # For old Office formats (.doc, .xls, .ppt) - OLE-based
        elif file_ext in ['.doc', '.xls', '.ppt'] or file_ext == '.ole':
            return get_ole_document_date(file_path)

    except Exception:
        pass

    return None


def get_office_xml_date(file_path):
    """Extract Last Saved Date from modern Office documents (XML-based)"""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Read Core Properties
            if 'docProps/core.xml' in zip_ref.namelist():
                core_xml = zip_ref.read('docProps/core.xml').decode('utf-8')
                root = ET.fromstring(core_xml)

                # Define namespace
                namespaces = {
                    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
                    'dcterms': 'http://purl.org/dc/terms/'
                }

                # Search for Last Modified Date
                modified_elem = root.find('.//dcterms:modified', namespaces)
                if modified_elem is not None and modified_elem.text:
                    # Parse ISO 8601 format: 2024-01-15T14:30:22Z
                    date_str = modified_elem.text.replace('Z', '+00:00')
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return date_obj.strftime("%Y-%m-%d_%H-%M-%S")

    except Exception:
        pass

    return None


def get_ole_document_date(file_path):
    """Try to extract Last Saved Date from OLE documents (simplified)"""
    try:
        with open(file_path, 'rb') as f:
            # Skip OLE header and search for metadata
            f.seek(0)
            data = f.read(8192)  # Read first 8KB

            # Search for FILETIME structures (8 bytes, Windows time format)
            # This is a simplified heuristic
            for i in range(len(data) - 8):
                try:
                    # Read FILETIME as 64-bit integer
                    filetime = struct.unpack('<Q', data[i:i + 8])[0]

                    # Convert FILETIME to Unix timestamp
                    # FILETIME = 100-nanoseconds since January 1, 1601
                    if filetime > 116444736000000000:  # Reasonable range
                        unix_timestamp = (filetime - 116444736000000000) / 10000000
                        if 946684800 < unix_timestamp < 2147483647:  # 2000-2038
                            date_obj = datetime.fromtimestamp(unix_timestamp)
                            return date_obj.strftime("%Y-%m-%d_%H-%M-%S")
                except:
                    continue

    except Exception:
        pass

    return None


def get_file_date(file_path, file_ext):
    """Determine Date Last Saved only for Office documents"""
    # Use Date Last Saved only for Office documents
    if file_ext in ['.docx', '.xlsx', '.pptx', '.doc', '.xls', '.ppt', '.ole']:
        office_date = get_office_last_saved(file_path, file_ext)
        if office_date:
            return office_date

    # For all other file types (PDF, images, etc.) -> use original name
    return None


def get_folder_input():
    """Ask user for folder path"""
    print("INSTRUCTIONS:")
    print("1. Enter the path to the folder containing .chk files")
    print("2. Example: C:\\Users\\YourName\\Desktop\\FOUND.000")
    print("3. You can also copy the path from Windows Explorer")
    print()

    while True:
        folder_path = input("Enter folder path: ").strip()

        # Remove quotes (if copied from Explorer)
        folder_path = folder_path.strip('"').strip("'")

        # Check if folder exists
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # Check if .chk files are present
            chk_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.chk')]
            if chk_files:
                print(f"✓ Folder found! {len(chk_files)} .chk files detected.")
                print()
                return folder_path
            else:
                print("⚠ No .chk files found in this folder!")
                retry = input("Try another folder? (y/n): ").lower()
                if retry != 'y':
                    return None
        else:
            print("❌ Folder not found!")
            print("Tips:")
            print("- Check the spelling")
            print("- Use the full path")
            print("- Copy the path from Windows Explorer")
            print()
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                return None


def process_chk_files(folder):
    """Process all .chk files in the specified folder"""
    if not folder:
        return

    print("Starting recovery...")
    print("-" * 40)

    count_success = 0
    count_unknown = 0
    count_error = 0

    chk_files = [f for f in os.listdir(folder) if f.lower().endswith('.chk')]
    total_files = len(chk_files)

    for i, filename in enumerate(chk_files, 1):
        print(f"[{i:3d}/{total_files}] {filename}...", end=" ")

        full_path = os.path.join(folder, filename)

        try:
            # Detect file type
            new_ext = detect_file_type(full_path)
            if new_ext:
                # Use Date Last Saved only for Office documents
                date_name = get_file_date(full_path, new_ext)
                if date_name:
                    new_name = date_name + new_ext
                else:
                    # For PDF, images etc.: use original name without .chk
                    new_name = os.path.splitext(filename)[0] + new_ext

                new_path = os.path.join(folder, new_name)

                # Check if file already exists, add suffix if necessary
                counter = 1
                original_new_path = new_path
                while os.path.exists(new_path):
                    name_without_ext = os.path.splitext(original_new_path)[0]
                    new_path = f"{name_without_ext}_{counter:03d}{new_ext}"
                    counter += 1

                # Rename
                os.rename(full_path, new_path)
                print(f"✓ → {os.path.basename(new_path)}")
                count_success += 1
            else:
                print("❓ Unknown format")
                count_unknown += 1

        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}...")
            count_error += 1

    # Summary
    print()
    print("=" * 50)
    print("FINISHED! Summary:")
    print(f"✓ Successfully recovered:        {count_success}")
    print(f"❓ Unknown formats:              {count_unknown}")
    print(f"❌ Errors:                       {count_error}")
    print(f"📁 Total processed:              {total_files}")
    print("=" * 50)

    if count_success > 0:
        print(f"\nThe recovered files can be found in:")
        print(f"📂 {folder}")


def main():
    """Main program"""
    print_header()

    try:
        # Get folder from user
        folder_path = get_folder_input()

        if folder_path:
            # Safety confirmation
            print("IMPORTANT NOTICE:")
            print("The .chk files will be renamed and this cannot be undone!")
            print("Create a backup copy of the folder beforehand if necessary.")
            print()

            confirm = input("Continue? (y/n): ").lower()
            if confirm == 'y':
                process_chk_files(folder_path)
            else:
                print("Operation cancelled.")
        else:
            print("Program terminated.")

    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()