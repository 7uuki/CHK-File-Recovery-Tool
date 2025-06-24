# CHK File Recovery Tool

A Python tool for automatic recovery of `.chk` files that are typically created after a disk repair with `chkdsk`.

## What does the script do?

The CHK File Recovery Tool analyzes `.chk` files and recovers them based on their file signatures. For Office documents, it additionally extracts the "Date Last Saved" from the metadata and uses it as the filename to enable meaningful naming.

### Main Features:
- **Automatic file type detection** through file signature analysis
- **Intelligent renaming** for Office documents based on last saved date
- **Batch processing** of all `.chk` files in a folder
- **Duplicate prevention** through automatic numbering in case of name conflicts
- **User-friendly interface** with progress display

## Supported File Types

### Images & Graphics
- **JPEG** (`.jpg`) - `FF D8 FF`
- **PNG** (`.png`) - `89 50 4E 47 0D 0A 1A 0A`
- **GIF** (`.gif`) - `47 49 46 38 37 61` / `47 49 46 38 39 61`
- **BMP** (`.bmp`) - `42 4D`
- **TIFF** (`.tif`) - `49 49 2A 00` / `4D 4D 00 2A`
- **ICO** (`.ico`) - `00 00 01 00`
- **WebP** (`.webp`) - `52 49 46 46` + `57 45 42 50`

### Documents & Text
- **PDF** (`.pdf`) - `25 50 44 46`
- **PostScript** (`.ps`) - `25 21 50 53`
- **Text Files** (`.txt`) - Detected by content analysis (UTF-8, ASCII)

### Microsoft Office (Modern Formats)
- **Word** (`.docx`) - ZIP-based with Word-specific structures
- **Excel** (`.xlsx`) - ZIP-based with Excel-specific structures  
- **PowerPoint** (`.pptx`) - ZIP-based with PowerPoint-specific structures

### Microsoft Office (Legacy Formats)
- **Word/Excel/PowerPoint** (`.doc/.xls/.ppt`) - OLE-based formats
- **Outlook Messages** (`.msg`) - OLE-based with MSG-specific structures

### Audio
- **MP3** (`.mp3`) - `49 44 33` / `FF FB` / `FF F3` / `FF F2`
- **WAV** (`.wav`) - `52 49 46 46` + `57 41 56 45`
- **OGG** (`.ogg`) - `4F 67 67 53`
- **FLAC** (`.flac`) - `66 4C 61 43`

### Video
- **MP4** (`.mp4`) - `66 74 79 70` (ftyp) with various brands
- **M4V** (`.m4v`) - `66 74 79 70` + `4D 34 56 20`
- **AVI** (`.avi`) - `52 49 46 46` + `41 56 49 20`
- **MKV** (`.mkv`) - `1A 45 DF A3`
- **FLV** (`.flv`) - `46 4C 56 01`
- **MPG/MPEG** (`.mpg`) - `00 00 01 BA` / `00 00 01 B3`

### Archives
- **ZIP** (`.zip`) - `50 4B 03 04` (also detects JAR, APK)
- **RAR** (`.rar`) - `52 61 72 21 1A 07`
- **7-Zip** (`.7z`) - `37 7A BC AF 27 1C`

## Installation & Usage

### Requirements
- Python 3.6 or higher
- No additional packages required (uses only standard libraries)

### Usage

1. **Download the script**:
   ```bash
   git clone https://github.com/yourusername/chk-file-recovery.git
   cd chk-file-recovery
   ```

2. **Run the script**:
   ```bash
   python chk_recovery.py
   ```

3. **Enter folder path**:
   - Enter the full path to your `FOUND.000` folder
   - Example: `C:\Users\YourName\Desktop\FOUND.000`
   - The path can also be copied from Windows Explorer

4. **Confirm recovery**:
   - The program displays the number of `.chk` files found
   - Confirm the process with `y` (yes)

### Example Output

```
[  1/150] FILE0001.CHK... ✓ → 2024-01-15_14-30-22.docx
[  2/150] FILE0002.CHK... ✓ → FILE0002.pdf
[  3/150] FILE0003.CHK... ✓ → 2024-01-10_09-15-30.xlsx
[  4/150] FILE0004.CHK... ❓ Unknown format
[  5/150] FILE0005.CHK... ✓ → FILE0005.jpg
```

## Special Features

### Office Document Dating
For Microsoft Office documents (Word, Excel, PowerPoint), the tool extracts the "Date Last Saved" from the metadata and uses it as the filename in the format `YYYY-MM-DD_HH-MM-SS.ext`.

### Safe Processing
- **Duplicate prevention**: In case of name conflicts, a number is automatically appended (`_001`, `_002`, etc.)
- **Error handling**: Corrupted files are skipped and reported
- **Safety confirmation**: Warning before irreversible renaming

## Limitations

- **Unknown formats**: Files without recognizable signature cannot be recovered
- **Corrupted files**: Heavily corrupted files may not be processed correctly
- **OLE dating**: Extraction of last saved date from old Office formats is heuristic and not always reliable

## Security Notice

⚠️ **IMPORTANT**: The script renames the original `.chk` files. This process cannot be undone. Create a backup copy of your `FOUND.000` folder before using.

## Contributing

Contributions are welcome! Please open an issue or create a pull request.

### Desired Extensions
- Support for additional file formats
- Improved metadata extraction
- GUI version
- Batch processing of multiple folders