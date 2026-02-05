# PDF Table Extractor

A Streamlit application for extracting tables from PDF documents using AI-powered OCR (PaddleOCR) with special support for Korean permit/compliance documents.

![PDF Table Extractor](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Features

- 📄 **PDF Table Extraction**: Extract tables from PDF documents with high accuracy
- 🌐 **Multi-language OCR**: Support for Korean, English, Chinese, Japanese, French, and German
- 🎯 **Korean Permit Filter**: Special filtering for Korean permit/compliance tables (반영여부, 적합여부)
- 📊 **Interactive Preview**: View extracted tables directly in the browser
- 💾 **Export Options**: Download tables as CSV or Excel files
- ⚙️ **Configurable Settings**: Adjust OCR confidence, page selection, and more

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd "d:\doAZ\Permit Table Extraction Demo"
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Upload a PDF** and configure the extraction settings

4. **Click "Extract Tables"** to process the document

5. **Download** the extracted tables as CSV or Excel

## Configuration Options

### OCR Settings
- **Language**: Select the primary language of your document
- **Minimum Confidence**: Set the OCR confidence threshold (0-100)

### Page Settings
- **All Pages**: Process entire document
- **Specific Pages**: Enter page numbers (e.g., "1,2,5" or "1-5")

### Extraction Settings
- **Implicit Rows**: Detect rows without explicit borders
- **Implicit Columns**: Detect columns without explicit borders
- **Borderless Tables**: Detect tables without visible borders

### Post-Processing
- **Korean Table Filter**: Apply special filtering for Korean permit documents

## Korean Table Filter

The Korean table filter is designed for permit/compliance documents that contain:
- Tables with columns like "반영여부" (reflection status) or "적합여부" (conformity status)
- Rows containing values like:
  - ✅ Include: 반영, 부분반영, 권고, 적합, 조건부적합
  - ❌ Skip: 미반영, 해당없음, 해당사항 없음

## Project Structure

```
Permit Table Extraction Demo/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Dependencies

- **streamlit**: Web application framework
- **img2table**: Table extraction library
- **paddleocr**: OCR engine
- **paddlepaddle**: Deep learning framework
- **pandas**: Data manipulation
- **pydantic**: Data validation
- **opencv-python**: Image processing
- **pdf2image**: PDF to image conversion
- **openpyxl**: Excel file support

## Troubleshooting

### Common Issues

1. **PaddlePaddle installation fails**:
   ```bash
   pip install paddlepaddle -f https://www.paddlepaddle.org.cn/whl/windows/cpu-mkl-avx/stable.html
   ```

2. **Poppler not found** (for pdf2image):
   - Windows: Download from [poppler releases](https://github.com/osber/poppler-for-windows/releases) and add to PATH
   - Linux: `sudo apt-get install poppler-utils`
   - Mac: `brew install poppler`

3. **Memory issues with large PDFs**:
   - Process specific pages instead of the entire document
   - Increase system memory allocation

## License

MIT License - feel free to use and modify as needed.
