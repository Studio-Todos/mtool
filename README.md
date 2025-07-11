# mtool

A comprehensive modular CLI tool for file management, conversion, compression, media processing, web utilities, text processing, and more.

---

## Installation

### From source

```bash
git clone <repository-url>
cd mtool
pip install -e .
```

### Using pip (when published)

```bash
pip install mtool
```

---

## Usage

The basic command structure is:

```bash
mtool <category> <tool> [subtool] [options]
```

---

## Categories & Tools

### File Management (`file`)

- **Compression/Extraction**

  - `compress <input> <output>`: Compress files/directories (zip, tar, gzip, bzip2, xz)
  - `extract <input> <output_dir>`: Extract compressed files/archives

- **Management & Search**
  - `manage find-large <dir> --top N`: Find largest files
  - `manage find-duplicates <dir>`: Find duplicate files by content
  - `manage organize <dir> --by extension`: Organize files by extension
  - `manage rename-batch <pattern> <replacement> [dir]`: Batch rename files
  - `manage search <pattern> [dir]`: Find files by name (wildcards)
  - `manage search-content <text> [dir]`: Search file contents for text
  - `manage recent [dir] --days N`: Show recently modified files

---

### PDF Tools (`pdf`)

- `info show <file>`: Show PDF details (pages, size, metadata)
- `split pages <input> <output> <range>`: Extract specific pages
- `split all <input> <output_dir>`: Split into individual pages
- `merge files <file1> <file2> ... <output>`: Merge multiple PDFs
- `merge directory <dir> <output> --sort`: Merge all PDFs in a directory
- `compress basic <input> <output> --quality Q`: Compress PDF file

---

### Image Tools (`image`)

- **Processing**

  - `resize <file> --size WxH [--output out]`: Resize images
  - `watermark <file> --text TEXT [--output out]`: Add text watermark
  - `optimize <file> [--output out] [--quality Q]`: Optimize/compress images
  - `info <file>`: Show image metadata

- **Compression**
  - `compress by-percent <file> <percent> [--output out]`: Reduce file size by percent
  - `compress to-size <file> <size_kb> [--output out]`: Compress to target size (KB)

---

### Video Tools (`video`)

- **Compression**
  - `compress by-percent <file> <percent> [--output out]`: Reduce file size by percent
  - `compress to-size <file> <size_mb> [--output out]`: Compress to target size (MB)

---

### Conversion Tools (`convert`)

- **File Conversion**

  - `file image <input> <output>`: Convert image formats (JPG, PNG, etc.)
  - `file audio <input> <output>`: Convert audio formats (MP3, WAV, etc.)
  - `file video <input> <output>`: Convert video formats (MP4, AVI, etc.)

- **PDF Conversion**

  - `pdf images-to-pdf <img1> <img2> ... <output>`: Images to PDF
  - `pdf pdf-to-images <input> <output_dir> [--format F --dpi D]`: PDF to images
  - `pdf extract-text <input> <output>`: Extract text from PDF

- **Data Conversion**
  - `data csv-to-json <input> <output> [--pretty --array]`
  - `data json-to-csv <input> <output> [--flatten]`
  - `data format-json <input> <output> [--indent N --sort-keys]`
  - `data validate-json <input>`
  - `data csv-info <input>`
  - `data merge-csv <file1> <file2> ... <output>`

---

### Text Processing (`text`)

- `process count <file>`: Count lines, words, characters, bytes
- `process search <pattern> <file> [--case-sensitive --regex --line-numbers]`
- `process replace <old> <new> <file> [--regex --backup --dry-run]`
- `process sort <file> [--reverse --numeric]`
- `process dedupe <file> [--case-insensitive --count]`
- `process stats <file> [--top N]`: Text statistics and word frequency

---

### Web Tools (`web`)

- **URL Tools**

  - `url info <url>`: Get URL info
  - `url validate <url>`: Validate URL
  - `url shorten <url> [--service S]`: Shorten URL
  - `url expand <short_url>`: Expand shortened URL
  - `url encode|decode <text>`: URL encode/decode

- **Status Checking**

  - `status check <url>`
  - `status port <host> <port>`
  - `status ping <host>`
  - `status monitor <url> [--interval N --count N]`
  - `status ssl <url>`

- **Downloads**
  - `download file <url> [--progress]`
  - `download batch <url1> <url2> ... <dir>`
  - `download image <url> [--output dir]`
  - `download check <url>`
  - `download resume <url> <output>`

---

### Utility Tools (`util`)

- **QR Codes**

  - `qrcode generate <text>`: Generate/display QR code, optionally save as PNG

- **Calculator & Encodings**
  - `calc evaluate <expr>`: Simple calculator (math, trig, log, etc.)
  - `convert unit "<value> <from> to <to>"`: Unit converter (length, weight, temp, etc.)
  - `encode base64|hex|binary|url <encode|decode> <text>`: Encode/decode data
  - `encode church <number> [--show-lambda]`: Church encoding (lambda calculus)

---

## Architecture

- **Core CLI**: Handles command parsing and routing
- **Tool Categories**: Grouped by functionality (file, image, video, pdf, web, text, util, convert)
- **Tool Modules**: Individual tools within each category
- **Plugin System**: Easy to add new tools and categories

---

## Development

To add new tools:

1. Create a new tool module in the appropriate category directory
2. Implement the tool interface
3. Register the tool in the category's `__init__.py`

---

## License

MIT License
