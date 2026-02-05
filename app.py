"""
PDF Table Extraction Application using Streamlit
Extracts tables from PDF files using img2table with PaddleOCR
"""

import streamlit as st
import pandas as pd
import tempfile
import os
from typing import Optional
from pydantic import BaseModel, Field

# Page configuration
st.set_page_config(
    page_title="PDF Table Extractor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.3);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .main-header p {
        color: #b8d4e8;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #d4a853 0%, #c49b47 100%);
        color: #1e3a5f;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(212, 168, 83, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(212, 168, 83, 0.4);
    }
    
    .upload-section {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 2rem;
        border-radius: 16px;
        border: 2px dashed #1e3a5f;
        margin-bottom: 1.5rem;
    }
    
    .stats-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border-left: 4px solid #d4a853;
        margin-bottom: 1rem;
    }
    
    .stats-card h3 {
        color: #1e3a5f;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stats-card p {
        color: #1e3a5f;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0 0 0;
    }
    
    .table-container {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.1);
        margin-top: 1.5rem;
    }
    
    .sidebar .stSelectbox {
        background: #f1f5f9;
        border-radius: 8px;
    }
    
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
    
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .warning-message {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .stProgress > div > div {
        background: linear-gradient(135deg, #d4a853 0%, #c49b47 100%);
    }
</style>
""", unsafe_allow_html=True)


# Pydantic model for table structure
class Table(BaseModel):
    columns: dict = Field(..., title="Columns")
    rows: Optional[list[dict]] = Field(default_factory=list, title="Rows")
    target_index: Optional[int] = Field(None, title="Target Index")


def extract_columns(row):
    """Extract unique column names from a row"""
    columns = {}
    recent_columns = set()

    for idx, item in enumerate(row):
        if isinstance(item, str) and item not in recent_columns:
            columns[idx] = item
            recent_columns.add(item)

    return columns


def process_extracted_table(df):
    """Process the extracted table DataFrame to find specific tables"""
    table_detected = False
    curr_table = None
    extracted_tables = []

    for row in df.itertuples():
        if not table_detected:
            for index, item in enumerate(row):
                if item and isinstance(item, str):
                    if item.replace(" ", "") in ["반영여부", "적합여부"]:
                        columns = extract_columns(row)
                        table_detected = True
                        curr_table = Table(columns=columns, target_index=index)
                        break
        else:
            target_value = row[curr_table.target_index] if curr_table.target_index < len(row) else ""
            
            if isinstance(target_value, str):
                if any(txt in target_value for txt in ["반영", "부분반영", "권고", "적합", "조건부적합"]):
                    pass
                elif any(txt in target_value for txt in ["미반영", "해당없음", "해당사항 없음"]):
                    continue
                else:
                    extracted_tables.append(curr_table)
                    curr_table = None
                    table_detected = False
                    continue

                curr_row = {}
                for index, item in enumerate(row):
                    if curr_table.columns.get(index, None):
                        curr_row[curr_table.columns[index]] = item

                curr_table.rows.append(curr_row)

    if curr_table:
        extracted_tables.append(curr_table)

    return extracted_tables


@st.cache_resource
def load_ocr(lang: str):
    """Load and cache OCR engine"""
    from img2table.ocr import PaddleOCR
    return PaddleOCR(lang=lang)


def extract_tables_from_pdf(pdf_path: str, pages: list, lang: str, 
                            implicit_rows: bool, implicit_columns: bool,
                            borderless_tables: bool, min_confidence: int):
    """Extract tables from PDF using img2table"""
    from img2table.document import PDF
    
    ocr = load_ocr(lang)
    
    pdf = PDF(
        pdf_path,
        pages=pages if pages else None,
        detect_rotation=False,
        pdf_text_extraction=True
    )
    
    extracted_tables = pdf.extract_tables(
        ocr=ocr,
        implicit_rows=implicit_rows,
        implicit_columns=implicit_columns,
        borderless_tables=borderless_tables,
        min_confidence=min_confidence
    )
    
    return extracted_tables


def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 PDF Table Extractor</h1>
        <p>Extract tables from PDF documents using AI-powered OCR</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.markdown("---")
        
        # Language selection
        lang = st.selectbox(
            "🌐 OCR Language",
            options=["korean", "english", "chinese", "japanese", "french", "german"],
            index=0,
            help="Select the primary language of your document", disabled=True
        )
        
        st.markdown("---")
        st.markdown("### 📄 Page Settings")
        
        # Page selection
        page_option = st.radio(
            "Pages to extract",
            options=["All pages", "Specific pages"],
            index=0
        )
        
        pages = None
        if page_option == "Specific pages":
            page_input = st.text_input(
                "Enter page numbers",
                placeholder="e.g., 1,2,5 or 1-5",
                help="Enter comma-separated page numbers or ranges"
            )
            if page_input:
                try:
                    pages = []
                    for part in page_input.split(","):
                        if "-" in part:
                            start, end = map(int, part.split("-"))
                            pages.extend(range(start, end + 1))
                        else:
                            pages.append(int(part.strip()))
                except:
                    st.error("Invalid page format")
        
        st.markdown("---")
        st.markdown("### 🔧 Extraction Settings")
        
        min_confidence = st.slider(
            "Minimum Confidence",
            min_value=0,
            max_value=100,
            value=40,
            help="Minimum OCR confidence threshold"
        )
        
        implicit_rows = st.checkbox(
            "Detect implicit rows",
            value=False,
            help="Detect rows that are not explicitly marked"
        )
        
        implicit_columns = st.checkbox(
            "Detect implicit columns",
            value=False,
            help="Detect columns that are not explicitly marked"
        )
        
        borderless_tables = st.checkbox(
            "Detect borderless tables",
            value=False,
            help="Detect tables without visible borders"
        )
        
        st.markdown("---")
        st.markdown("### 🎯 Post-Processing")
        
        apply_korean_filter = st.checkbox(
            "Apply Korean table filter",
            value=True,
            help="Filter tables based on Korean permit/compliance patterns (반영여부, 적합여부)"
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📤 Upload PDF Document")
        uploaded_file = st.file_uploader(
            "Drop your PDF file here or click to browse",
            type=["pdf"],
            help="Supported format: PDF"
        )
    
    with col2:
        st.markdown("### 📋 Quick Guide")
        st.markdown("""
        1. Upload a PDF document
        2. Configure extraction settings
        3. Click **Extract Tables**
        4. Download results as Excel/CSV
        """)
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <h3>📁 File Name</h3>
                <p style="font-size: 1rem;">{uploaded_file.name}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            file_size = len(uploaded_file.getvalue()) / 1024
            size_unit = "KB" if file_size < 1024 else "MB"
            size_value = file_size if file_size < 1024 else file_size / 1024
            st.markdown(f"""
            <div class="stats-card">
                <h3>📦 File Size</h3>
                <p>{size_value:.1f} {size_unit}</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stats-card">
                <h3>🌐 Language</h3>
                <p style="font-size: 1.5rem;">{lang.capitalize()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Extract button
        if st.button("🚀 Extract Tables", use_container_width=True):
            with st.spinner("Extracting tables from PDF..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    progress_bar = st.progress(0, text="Initializing OCR engine...")
                    
                    progress_bar.progress(20, text="Loading PDF document...")
                    
                    # Extract tables
                    progress_bar.progress(40, text="Extracting tables...")
                    extracted_tables = extract_tables_from_pdf(
                        tmp_path,
                        pages=pages,
                        lang=lang,
                        implicit_rows=implicit_rows,
                        implicit_columns=implicit_columns,
                        borderless_tables=borderless_tables,
                        min_confidence=min_confidence
                    )
                    
                    progress_bar.progress(80, text="Processing extracted tables...")
                    
                    # Store results in session state
                    st.session_state['extracted_tables'] = extracted_tables
                    st.session_state['apply_korean_filter'] = apply_korean_filter
                    
                    progress_bar.progress(100, text="Extraction complete!")
                    
                    st.success(f"✅ Successfully extracted tables from {len(extracted_tables)} page(s)!")
                    
                except Exception as e:
                    st.error(f"❌ Error during extraction: {str(e)}")
                    st.exception(e)
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        
        # Display results if available
        if 'extracted_tables' in st.session_state and st.session_state['extracted_tables']:
            st.markdown("---")
            st.markdown("### 📊 Extracted Tables")
            
            extracted_tables = st.session_state['extracted_tables']
            
            # Count total tables across all pages
            total_tables = sum(len(tables) for tables in extracted_tables.values()) if isinstance(extracted_tables, dict) else len(extracted_tables)
            
            st.markdown(f"**Found {total_tables} table(s)**")
            
            # Process and display tables
            if isinstance(extracted_tables, dict):
                for page_num, tables in extracted_tables.items():
                    st.markdown(f"#### 📄 Page {page_num}")
                    for idx, table in enumerate(tables):
                        with st.expander(f"Table {idx + 1}", expanded=True):
                            try:
                                df = table.df
                                
                                # Apply Korean filter if enabled
                                if st.session_state.get('apply_korean_filter', False):
                                    processed_tables = process_extracted_table(df)
                                    if processed_tables:
                                        for pt_idx, pt in enumerate(processed_tables):
                                            if pt.rows:
                                                processed_df = pd.DataFrame(pt.rows)
                                                st.dataframe(processed_df, use_container_width=True)
                                                
                                                # Download button
                                                csv = processed_df.to_csv(index=False).encode('utf-8-sig')
                                                st.download_button(
                                                    "📥 Download CSV",
                                                    csv,
                                                    f"table_p{page_num}_{idx+1}_filtered_{pt_idx+1}.csv",
                                                    "text/csv"
                                                )
                                    else:
                                        st.info("No matching tables found with the Korean filter criteria.")
                                        st.dataframe(df, use_container_width=True)
                                else:
                                    st.dataframe(df, use_container_width=True)
                                    
                                    # Download button
                                    csv = df.to_csv(index=False).encode('utf-8-sig')
                                    st.download_button(
                                        "📥 Download CSV",
                                        csv,
                                        f"table_page{page_num}_{idx+1}.csv",
                                        "text/csv"
                                    )
                            except Exception as e:
                                st.error(f"Error displaying table: {e}")
            else:
                # Handle non-dict format
                for idx, table in enumerate(extracted_tables):
                    with st.expander(f"Table {idx + 1}", expanded=True):
                        try:
                            df = table.df if hasattr(table, 'df') else pd.DataFrame(table)
                            st.dataframe(df, use_container_width=True)
                            
                            csv = df.to_csv(index=False).encode('utf-8-sig')
                            st.download_button(
                                "📥 Download CSV",
                                csv,
                                f"table_{idx+1}.csv",
                                "text/csv"
                            )
                        except Exception as e:
                            st.error(f"Error displaying table: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9rem;">
        <p>Built with ❤️ using Streamlit, img2table, and PaddleOCR</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
