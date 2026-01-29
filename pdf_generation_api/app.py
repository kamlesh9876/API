from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import uuid
import tempfile
from datetime import datetime
import asyncio
from pathlib import Path
import json

app = FastAPI(
    title="PDF Generation API",
    description="Advanced PDF generation, conversion, and manipulation service",
    version="1.0.0"
)

# Data Models
class PDFGenerationRequest(BaseModel):
    content: str
    title: Optional[str] = "Generated PDF"
    author: Optional[str] = "PDF Generator"
    subject: Optional[str] = None
    keywords: Optional[str] = None
    page_size: Optional[str] = "A4"  # A4, A3, Letter, Legal
    orientation: Optional[str] = "portrait"  # portrait, landscape
    margin_top: Optional[float] = 20.0
    margin_bottom: Optional[float] = 20.0
    margin_left: Optional[float] = 20.0
    margin_right: Optional[float] = 20.0
    font_size: Optional[int] = 12
    font_family: Optional[str] = "Arial"
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    watermark_text: Optional[str] = None
    password: Optional[str] = None

class PDFMergeRequest(BaseModel):
    pdf_files: List[str]
    output_filename: Optional[str] = None
    password: Optional[str] = None

class PDFSplitRequest(BaseModel):
    pdf_file: str
    page_ranges: List[str]  # e.g., ["1-5", "6-10", "11-15"]
    output_prefix: Optional[str] = "split"

class PDFMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None

class PDFConversionRequest(BaseModel):
    input_file: str
    output_format: str  # html, txt, xml, csv
    output_filename: Optional[str] = None

# Storage (in production, use proper file storage)
pdf_storage = {}
conversion_jobs = {}

@app.get("/")
async def root():
    return {"message": "PDF Generation API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# PDF Generation Endpoints
@app.post("/api/pdf/generate")
async def generate_pdf(request: PDFGenerationRequest):
    """Generate PDF from text content with advanced formatting options"""
    try:
        pdf_id = str(uuid.uuid4())
        filename = f"{pdf_id}.pdf"
        
        # Simulate PDF generation (in production, use libraries like reportlab, weasyprint)
        pdf_info = {
            "id": pdf_id,
            "filename": filename,
            "title": request.title,
            "author": request.author,
            "page_size": request.page_size,
            "orientation": request.orientation,
            "pages": len(request.content.split('\n')) // 40 + 1,  # Estimate
            "file_size": len(request.content.encode()) * 2,  # Estimate
            "created_at": datetime.now().isoformat(),
            "has_password": bool(request.password),
            "has_watermark": bool(request.watermark_text),
            "download_url": f"/api/pdf/download/{pdf_id}"
        }
        
        pdf_storage[pdf_id] = pdf_info
        
        return {
            "success": True,
            "pdf_id": pdf_id,
            "message": "PDF generated successfully",
            "pdf_info": pdf_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.post("/api/pdf/generate-from-html")
async def generate_pdf_from_html(
    html_content: str = Form(...),
    title: str = Form("Generated PDF"),
    page_size: str = Form("A4"),
    orientation: str = Form("portrait")
):
    """Generate PDF from HTML content"""
    try:
        pdf_id = str(uuid.uuid4())
        filename = f"{pdf_id}.pdf"
        
        # Simulate HTML to PDF conversion (in production, use weasyprint or pdfkit)
        pdf_info = {
            "id": pdf_id,
            "filename": filename,
            "title": title,
            "source": "html",
            "page_size": page_size,
            "orientation": orientation,
            "pages": len(html_content.split('<p>')) + len(html_content.split('<div>')),
            "file_size": len(html_content.encode()) * 3,
            "created_at": datetime.now().isoformat(),
            "download_url": f"/api/pdf/download/{pdf_id}"
        }
        
        pdf_storage[pdf_id] = pdf_info
        
        return {
            "success": True,
            "pdf_id": pdf_id,
            "message": "PDF generated from HTML successfully",
            "pdf_info": pdf_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML to PDF conversion failed: {str(e)}")

@app.post("/api/pdf/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload existing PDF for processing"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        pdf_id = str(uuid.uuid4())
        
        # Simulate file upload (in production, save to disk or cloud storage)
        pdf_info = {
            "id": pdf_id,
            "filename": file.filename,
            "original_name": file.filename,
            "file_size": file.size or 0,
            "content_type": file.content_type,
            "uploaded_at": datetime.now().isoformat(),
            "download_url": f"/api/pdf/download/{pdf_id}"
        }
        
        pdf_storage[pdf_id] = pdf_info
        
        return {
            "success": True,
            "pdf_id": pdf_id,
            "message": "PDF uploaded successfully",
            "pdf_info": pdf_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF upload failed: {str(e)}")

# PDF Manipulation Endpoints
@app.post("/api/pdf/merge")
async def merge_pdfs(request: PDFMergeRequest):
    """Merge multiple PDFs into one"""
    try:
        merge_id = str(uuid.uuid4())
        output_filename = request.output_filename or f"merged_{merge_id}.pdf"
        
        # Validate input PDFs
        for pdf_id in request.pdf_files:
            if pdf_id not in pdf_storage:
                raise HTTPException(status_code=404, detail=f"PDF {pdf_id} not found")
        
        # Simulate PDF merging
        merged_info = {
            "id": merge_id,
            "filename": output_filename,
            "source_pdfs": request.pdf_files,
            "total_pages": sum(pdf_storage[pid].get("pages", 1) for pid in request.pdf_files),
            "file_size": sum(pdf_storage[pid].get("file_size", 1000) for pid in request.pdf_files),
            "merged_at": datetime.now().isoformat(),
            "has_password": bool(request.password),
            "download_url": f"/api/pdf/download/{merge_id}"
        }
        
        pdf_storage[merge_id] = merged_info
        
        return {
            "success": True,
            "merge_id": merge_id,
            "message": "PDFs merged successfully",
            "merged_info": merged_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF merge failed: {str(e)}")

@app.post("/api/pdf/split")
async def split_pdf(request: PDFSplitRequest):
    """Split PDF into multiple files based on page ranges"""
    try:
        if request.pdf_file not in pdf_storage:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        split_id = str(uuid.uuid4())
        split_files = []
        
        # Simulate PDF splitting
        for i, page_range in enumerate(request.page_ranges):
            file_id = str(uuid.uuid4())
            filename = f"{request.output_prefix}_{i+1}_{page_range}.pdf"
            
            split_info = {
                "id": file_id,
                "filename": filename,
                "source_pdf": request.pdf_file,
                "page_range": page_range,
                "pages": len(page_range.split('-')),
                "file_size": pdf_storage[request.pdf_file].get("file_size", 1000) // len(request.page_ranges),
                "split_at": datetime.now().isoformat(),
                "download_url": f"/api/pdf/download/{file_id}"
            }
            
            pdf_storage[file_id] = split_info
            split_files.append(split_info)
        
        return {
            "success": True,
            "split_id": split_id,
            "message": "PDF split successfully",
            "split_files": split_files,
            "total_files": len(split_files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF split failed: {str(e)}")

@app.post("/api/pdf/compress/{pdf_id}")
async def compress_pdf(pdf_id: str, quality: str = "medium"):
    """Compress PDF to reduce file size"""
    try:
        if pdf_id not in pdf_storage:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        original_pdf = pdf_storage[pdf_id]
        compressed_id = str(uuid.uuid4())
        
        # Simulate compression (quality: low, medium, high)
        quality_ratios = {"low": 0.3, "medium": 0.6, "high": 0.8}
        compression_ratio = quality_ratios.get(quality, 0.6)
        
        compressed_info = {
            "id": compressed_id,
            "filename": f"compressed_{original_pdf['filename']}",
            "source_pdf": pdf_id,
            "original_size": original_pdf.get("file_size", 1000),
            "compressed_size": int(original_pdf.get("file_size", 1000) * compression_ratio),
            "compression_ratio": compression_ratio,
            "quality": quality,
            "compressed_at": datetime.now().isoformat(),
            "download_url": f"/api/pdf/download/{compressed_id}"
        }
        
        pdf_storage[compressed_id] = compressed_info
        
        return {
            "success": True,
            "compressed_id": compressed_id,
            "message": "PDF compressed successfully",
            "compression_info": compressed_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF compression failed: {str(e)}")

# PDF Conversion Endpoints
@app.post("/api/pdf/convert/{pdf_id}")
async def convert_pdf(pdf_id: str, request: PDFConversionRequest):
    """Convert PDF to other formats"""
    try:
        if pdf_id not in pdf_storage:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        conversion_id = str(uuid.uuid4())
        output_filename = request.output_filename or f"converted_{conversion_id}.{request.output_format}"
        
        # Simulate conversion
        conversion_info = {
            "id": conversion_id,
            "pdf_id": pdf_id,
            "output_format": request.output_format,
            "output_filename": output_filename,
            "status": "processing",
            "started_at": datetime.now().isoformat(),
            "estimated_completion": datetime.now().isoformat()
        }
        
        conversion_jobs[conversion_id] = conversion_info
        
        # Simulate async conversion
        asyncio.create_task(simulate_conversion(conversion_id))
        
        return {
            "success": True,
            "conversion_id": conversion_id,
            "message": "Conversion started",
            "conversion_info": conversion_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")

async def simulate_conversion(conversion_id: str):
    """Simulate async conversion process"""
    await asyncio.sleep(2)  # Simulate processing time
    
    if conversion_id in conversion_jobs:
        conversion_jobs[conversion_id]["status"] = "completed"
        conversion_jobs[conversion_id]["completed_at"] = datetime.now().isoformat()
        conversion_jobs[conversion_id]["download_url"] = f"/api/pdf/download-converted/{conversion_id}"

@app.get("/api/pdf/convert-status/{conversion_id}")
async def get_conversion_status(conversion_id: str):
    """Get conversion job status"""
    if conversion_id not in conversion_jobs:
        raise HTTPException(status_code=404, detail="Conversion job not found")
    
    return conversion_jobs[conversion_id]

# PDF Metadata Endpoints
@app.get("/api/pdf/metadata/{pdf_id}")
async def get_pdf_metadata(pdf_id: str):
    """Get PDF metadata"""
    try:
        if pdf_id not in pdf_storage:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        pdf_info = pdf_storage[pdf_id]
        
        # Simulate metadata extraction
        metadata = {
            "title": pdf_info.get("title", "Unknown"),
            "author": pdf_info.get("author", "Unknown"),
            "subject": pdf_info.get("subject", None),
            "creator": "PDF Generation API",
            "producer": "FastAPI PDF Service",
            "creation_date": pdf_info.get("created_at", datetime.now().isoformat()),
            "modification_date": datetime.now().isoformat(),
            "pages": pdf_info.get("pages", 0),
            "file_size": pdf_info.get("file_size", 0),
            "page_size": pdf_info.get("page_size", "A4"),
            "orientation": pdf_info.get("orientation", "portrait"),
            "has_password": pdf_info.get("has_password", False),
            "has_watermark": pdf_info.get("has_watermark", False)
        }
        
        return {
            "success": True,
            "pdf_id": pdf_id,
            "metadata": metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")

@app.put("/api/pdf/metadata/{pdf_id}")
async def update_pdf_metadata(pdf_id: str, metadata: PDFMetadata):
    """Update PDF metadata"""
    try:
        if pdf_id not in pdf_storage:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        # Update metadata (in production, modify actual PDF)
        pdf_storage[pdf_id].update({
            "title": metadata.title,
            "author": metadata.author,
            "subject": metadata.subject,
            "keywords": metadata.keywords,
            "modification_date": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "pdf_id": pdf_id,
            "message": "Metadata updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update metadata: {str(e)}")

# Utility Endpoints
@app.get("/api/pdf/list")
async def list_pdfs(limit: int = 50, offset: int = 0):
    """List all generated/uploaded PDFs"""
    pdfs = list(pdf_storage.values())
    total = len(pdfs)
    
    # Apply pagination
    paginated_pdfs = pdfs[offset:offset + limit]
    
    return {
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "pdfs": paginated_pdfs
    }

@app.delete("/api/pdf/{pdf_id}")
async def delete_pdf(pdf_id: str):
    """Delete a PDF"""
    try:
        if pdf_id not in pdf_storage:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        del pdf_storage[pdf_id]
        
        return {
            "success": True,
            "message": "PDF deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete PDF: {str(e)}")

@app.get("/api/pdf/download/{pdf_id}")
async def download_pdf(pdf_id: str):
    """Download PDF file"""
    try:
        if pdf_id not in pdf_storage:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        pdf_info = pdf_storage[pdf_id]
        
        # In production, return actual file
        # For now, return file info
        return {
            "message": "Download endpoint - in production, this would return the actual PDF file",
            "pdf_info": pdf_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/api/pdf/stats")
async def get_pdf_stats():
    """Get PDF generation statistics"""
    total_pdfs = len(pdf_storage)
    total_conversions = len(conversion_jobs)
    
    # Calculate stats
    total_size = sum(pdf.get("file_size", 0) for pdf in pdf_storage.values())
    total_pages = sum(pdf.get("pages", 0) for pdf in pdf_storage.values())
    
    return {
        "success": True,
        "statistics": {
            "total_pdfs": total_pdfs,
            "total_conversions": total_conversions,
            "total_file_size": total_size,
            "total_pages": total_pages,
            "average_file_size": total_size / total_pdfs if total_pdfs > 0 else 0,
            "average_pages": total_pages / total_pdfs if total_pdfs > 0 else 0,
            "storage_usage": f"{total_size / (1024*1024):.2f} MB"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
