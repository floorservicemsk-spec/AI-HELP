from typing import List, Dict, Optional
import logging
import xml.etree.ElementTree as ET
import httpx
from pathlib import Path
import PyPDF2
import docx
import markdown
from config import settings
from services.logging_config import logger


class IngestionService:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, source: str = "", metadata: Dict = None) -> List[Dict]:
        """??????? ????? ?? ?????"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "source": source,
                "metadata": metadata or {}
            })
        
        return chunks
    
    async def ingest_xml(self, url: str) -> List[Dict]:
        """????????? ? ?????????? XML ????"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                xml_content = response.text
            
            root = ET.fromstring(xml_content)
            chunks = []
            
            # ?????? XML ? ????????? ?????????? ? ???????
            for product in root.findall(".//product") or root.findall(".//item"):
                product_data = {}
                product_text = []
                
                for child in product:
                    tag = child.tag
                    text = child.text or ""
                    product_data[tag] = text
                    product_text.append(f"{tag}: {text}")
                
                product_text_str = "\n".join(product_text)
                product_chunks = self.chunk_text(
                    product_text_str,
                    source=url,
                    metadata={"type": "product", "data": product_data}
                )
                chunks.extend(product_chunks)
            
            logger.info(f"Parsed {len(chunks)} chunks from XML")
            return chunks
        except Exception as e:
            logger.error(f"Error ingesting XML: {e}")
            raise
    
    def ingest_file(self, file_path: str, file_type: str) -> List[Dict]:
        """????????? ? ?????????? ????"""
        chunks = []
        source = Path(file_path).name
        
        try:
            if file_type == "application/pdf":
                chunks = self._parse_pdf(file_path, source)
            elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                chunks = self._parse_docx(file_path, source)
            elif file_type == "text/plain":
                chunks = self._parse_txt(file_path, source)
            elif file_type == "text/markdown":
                chunks = self._parse_markdown(file_path, source)
            else:
                # ??????? ??? ????????? ????
                chunks = self._parse_txt(file_path, source)
            
            logger.info(f"Parsed {len(chunks)} chunks from file {source}")
            return chunks
        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {e}")
            raise
    
    def _parse_pdf(self, file_path: str, source: str) -> List[Dict]:
        """??????? PDF"""
        chunks = []
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            chunks = self.chunk_text(text, source=source, metadata={"type": "pdf"})
        return chunks
    
    def _parse_docx(self, file_path: str, source: str) -> List[Dict]:
        """??????? DOCX"""
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        chunks = self.chunk_text(text, source=source, metadata={"type": "docx"})
        return chunks
    
    def _parse_txt(self, file_path: str, source: str) -> List[Dict]:
        """??????? TXT"""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = self.chunk_text(text, source=source, metadata={"type": "txt"})
        return chunks
    
    def _parse_markdown(self, file_path: str, source: str) -> List[Dict]:
        """??????? Markdown"""
        with open(file_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        # ???????????? markdown ? ?????
        html = markdown.markdown(md_content)
        # ??????? ???????? HTML ?????
        import re
        text = re.sub(r'<[^>]+>', '', html)
        chunks = self.chunk_text(text, source=source, metadata={"type": "markdown"})
        return chunks
