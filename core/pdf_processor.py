"""
PDF Processor สำหรับอ่านและแยกข้อมูลจาก PDF โปรโมชั่น
ใช้ PyPDF2 หรือ pdfplumber สำหรับ extract text และ images
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try import PDF libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning(" PyPDF2 not installed")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning(" pdfplumber not installed")


class PDFProcessor:
    """PDF Processor สำหรับโปรโมชั่น Seoulholic Clinic"""
    
    def __init__(self, pdf_dir: str = "."):
        """
        Initialize PDF Processor
        
        Args:
            pdf_dir: Directory ที่เก็บ PDF files
        """
        self.pdf_dir = Path(pdf_dir)
        self.promotions = []
    
    def extract_text_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2"""
        if not PYPDF2_AVAILABLE:
            return ""
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f" PyPDF2 extraction failed for {pdf_path}: {e}")
            return ""
    
    def extract_text_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber (better quality)"""
        if not PDFPLUMBER_AVAILABLE:
            return ""
        
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f" pdfplumber extraction failed for {pdf_path}: {e}")
            return ""
    
    def extract_text(self, pdf_path: Path) -> str:
        """Extract text (try pdfplumber first, fallback to PyPDF2)"""
        text = self.extract_text_pdfplumber(pdf_path)
        if not text:
            text = self.extract_text_pypdf2(pdf_path)
        return text
    
    def parse_promotion_info(self, text: str, filename: str) -> Dict:
        """
        แยกข้อมูลโปรโมชั่นจาก text
        
        Args:
            text: Text จาก PDF
            filename: ชื่อไฟล์ PDF
        
        Returns:
            Dict ข้อมูลโปรโมชั่น
        """
        # Clean filename
        promo_name = filename.replace('.pdf', '').replace('_', ' ')
        
        # Parse ราคาจาก text
        prices = []
        import re
        
        # หาราคา (เช่น 3,990, 999, etc.)
        price_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:บาท|baht|THB)',  # 3,990 บาท
            r'฿\s*(\d{1,3}(?:,\d{3})*)',  # ฿3,990
            r'(\d{3,5})\s*(?:บาท|baht)',  # 999 บาท
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            prices.extend([m.replace(',', '') for m in matches])
        
        # หา session/times
        sessions = []
        session_patterns = [
            r'(\d+)\s*(?:sessions?|ครั้ง|times?)',
            r'(?:sessions?|ครั้ง)\s*(\d+)',
        ]
        
        for pattern in session_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            sessions.extend(matches)
        
        # สร้าง summary
        summary = f"โปรโมชั่น {promo_name}"
        if prices:
            summary += f" ราคา {prices[0]} บาท"
        if sessions:
            summary += f" {sessions[0]} ครั้ง"
        
        return {
            "name": promo_name,
            "filename": filename,
            "prices": prices,
            "sessions": sessions,
            "full_text": text[:500],  # เก็บแค่ 500 ตัวอักษรแรก
            "summary": summary,
            "text_length": len(text)
        }
    
    def process_pdf(self, pdf_path: Path) -> Optional[Dict]:
        """
        Process single PDF file
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Promotion info dict
        """
        if not pdf_path.exists():
            logger.error(f" File not found: {pdf_path}")
            return None
        
        logger.info(f"📄 Processing: {pdf_path.name}")
        
        # Extract text
        text = self.extract_text(pdf_path)
        
        if not text:
            logger.warning(f" No text extracted from {pdf_path.name}")
            # สร้าง basic info จากชื่อไฟล์
            return {
                "name": pdf_path.stem,
                "filename": pdf_path.name,
                "prices": [],
                "sessions": [],
                "full_text": "",
                "summary": f"โปรโมชั่น {pdf_path.stem} (ดูรายละเอียดเพิ่มเติมได้ค่ะ)",
                "text_length": 0,
                "error": "ไม่สามารถอ่าน PDF ได้ กรุณาติดต่อพนักงานค่ะ"
            }
        
        # Parse promotion info
        promo_info = self.parse_promotion_info(text, pdf_path.name)
        promo_info["pdf_path"] = str(pdf_path)
        
        logger.info(f" Extracted: {promo_info['summary']}")
        
        return promo_info
    
    def process_all_pdfs(self) -> List[Dict]:
        """Process all PDF files in directory"""
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f" No PDF files found in {self.pdf_dir}")
            return []
        
        logger.info(f"📚 Found {len(pdf_files)} PDF files")
        
        promotions = []
        for pdf_file in pdf_files:
            promo = self.process_pdf(pdf_file)
            if promo:
                promotions.append(promo)
        
        self.promotions = promotions
        return promotions
    
    def save_to_json(self, output_path: str = "data/pdf_promotions.json"):
        """Save extracted promotions to JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.promotions, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved {len(self.promotions)} promotions to {output_path}")
    
    def generate_rag_documents(self) -> List[Dict]:
        """
        สร้าง documents สำหรับ RAG system
        
        Returns:
            List of dicts with text and metadata
        """
        documents = []
        
        for promo in self.promotions:
            # สร้าง text ที่เหมาะสำหรับ RAG
            rag_text = f"""
โปรโมชั่น: {promo['name']}

{promo['summary']}

รายละเอียดเพิ่มเติม:
{promo['full_text']}

ราคา: {', '.join(promo['prices']) if promo['prices'] else 'สอบถามพนักงาน'}
จำนวนครั้ง: {', '.join(promo['sessions']) if promo['sessions'] else 'ตามแพ็คเกจ'}

สอบถามรายละเอียดเพิ่มเติมได้ที่คลินิกค่ะ
            """.strip()
            
            documents.append({
                "text": rag_text,
                "metadata": {
                    "source": "pdf_promotion",
                    "filename": promo['filename'],
                    "promotion_name": promo['name'],
                    "type": "promotion_detail"
                }
            })
        
        return documents


def process_clinic_pdfs(pdf_paths: List[str]) -> List[Dict]:
    """
    Helper function: Process specific PDF files
    
    Args:
        pdf_paths: List of PDF file paths
    
    Returns:
        List of promotion info dicts
    """
    promotions = []
    processor = PDFProcessor()
    
    for pdf_path in pdf_paths:
        path = Path(pdf_path)
        if path.exists():
            promo = processor.process_pdf(path)
            if promo:
                promotions.append(promo)
    
    return promotions


if __name__ == "__main__":
    # Test with specific files
    pdf_files = [
        "/Users/king_phuripol/Work/Area-Zero/P-Fivem/Essential Glow Drip 5 Sessions.pdf",
        "/Users/king_phuripol/Work/Area-Zero/P-Fivem/Meso Promotion 5 Times 999.pdf",
        "/Users/king_phuripol/Work/Area-Zero/P-Fivem/Pro Filler 3990.pdf",
        "/Users/king_phuripol/Work/Area-Zero/P-Fivem/Promotion Buy 1 Get 1.pdf"
    ]
    
    processor = PDFProcessor()
    
    for pdf_path in pdf_files:
        path = Path(pdf_path)
        if path.exists():
            promo = processor.process_pdf(path)
            print(f"\n{'='*60}")
            print(json.dumps(promo, ensure_ascii=False, indent=2))
