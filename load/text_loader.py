import os
from ebooklib import epub
import PyPDF2
from bs4 import BeautifulSoup

class TextLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_text(self):
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext == '.epub':
            return self._load_epub()
        elif ext == '.pdf':
            return self._load_pdf()
        else:
            return self._load_plain_text()

    def _load_pdf(self):
        if PyPDF2 is None:
            raise ImportError("Please install the 'PyPDF2' package to read PDF files.")
        text = []
        with open(self.file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)

    def _load_plain_text(self):
        with open(self.file_path, encoding="utf-8") as f:
            return f.read()

    def _load_epub(self):
        """Load text from EPUB file, extracting and cleaning HTML content."""
        book = epub.read_epub(self.file_path)
        text_parts = []
        
        for item in book.get_items():
            if item.get_type() == 9:  # ITEM_DOCUMENT
                # Parse HTML content
                content = item.get_content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text and clean up whitespace
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                if text:
                    text_parts.append(text)
        
        return "\n\n".join(text_parts)