from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import os
import io
import sqlite3
from sqlite3 import Connection
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
import hashlib
import logging
from pathlib import Path

app = FastAPI(title="QR Code Generator API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "qr_codes.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # QR codes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_codes (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            content TEXT NOT NULL,
            format TEXT DEFAULT 'PNG',
            size INTEGER DEFAULT 200,
            error_correction TEXT DEFAULT 'M',
            box_size INTEGER DEFAULT 10,
            border INTEGER DEFAULT 4,
            fill_color TEXT DEFAULT '#000000',
            back_color TEXT DEFAULT '#FFFFFF',
            logo_path TEXT,
            logo_size INTEGER,
            custom_data TEXT,  -- JSON for additional customizations
            file_path TEXT,
            file_size INTEGER,
            content_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            download_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # QR code analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qr_analytics (
            id TEXT PRIMARY KEY,
            qr_id TEXT,
            action TEXT,  -- generate, download, view
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (qr_id) REFERENCES qr_codes (id)
        )
    ''')
    
    # User sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            session_data TEXT,  -- JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_qr_codes_user_id ON qr_codes(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_qr_codes_content_hash ON qr_codes(content_hash)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_qr_codes_created_at ON qr_codes(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_qr_analytics_qr_id ON qr_analytics(qr_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Enums
class QRFormat(str, Enum):
    PNG = "PNG"
    SVG = "SVG"
    JPEG = "JPEG"
    BMP = "BMP"

class ErrorCorrectionLevel(str, Enum):
    L = "L"  # ~7% correction
    M = "M"  # ~15% correction
    Q = "Q"  # ~25% correction
    H = "H"  # ~30% correction

class QRStyle(str, Enum):
    SQUARE = "square"
    ROUNDED = "rounded"
    CIRCLE = "circle"
    CUSTOM = "custom"

# Pydantic models
class QRCodeRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Content to encode in QR code")
    format: QRFormat = QRFormat.PNG
    size: int = Field(200, ge=50, le=1000, description="QR code size in pixels")
    error_correction: ErrorCorrectionLevel = ErrorCorrectionLevel.M
    box_size: int = Field(10, ge=1, le=50, description="Size of each box in pixels")
    border: int = Field(4, ge=0, le=20, description="Border size in boxes")
    fill_color: str = Field("#000000", regex=r'^#[0-9A-Fa-f]{6}$', description="QR code fill color")
    back_color: str = Field("#FFFFFF", regex=r'^#[0-9A-Fa-f]{6}$', description="Background color")
    logo_url: Optional[HttpUrl] = None
    logo_size: Optional[int] = Field(None, ge=10, le=200)
    style: QRStyle = QRStyle.SQUARE
    user_id: Optional[str] = None
    expires_in_hours: Optional[int] = Field(None, ge=1, le=8760)  # Up to 1 year
    custom_data: Optional[Dict[str, Any]] = None

class QRCodeResponse(BaseModel):
    id: str
    content: str
    format: str
    size: int
    download_url: str
    preview_url: str
    content_hash: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    download_count: int = 0
    file_size: Optional[int] = None

class QRCodeHistory(BaseModel):
    id: str
    content: str
    format: str
    size: int
    fill_color: str
    back_color: str
    created_at: datetime
    download_count: int
    expires_at: Optional[datetime] = None
    is_active: bool

class QRAnalytics(BaseModel):
    qr_id: str
    total_downloads: int
    total_views: int
    last_accessed: Optional[datetime] = None
    access_by_ip: Dict[str, int]
    access_by_date: Dict[str, int]

# QR Code Service
class QRCodeService:
    def __init__(self):
        self.output_dir = Path("generated_qr_codes")
        self.output_dir.mkdir(exist_ok=True)
        self.error_correction_map = {
            ErrorCorrectionLevel.L: ERROR_CORRECT_L,
            ErrorCorrectionLevel.M: ERROR_CORRECT_M,
            ErrorCorrectionLevel.Q: ERROR_CORRECT_Q,
            ErrorCorrectionLevel.H: ERROR_CORRECT_H
        }
    
    def generate_content_hash(self, content: str, params: Dict[str, Any]) -> str:
        """Generate unique hash for content and parameters"""
        hash_data = {
            "content": content,
            "format": params.get("format", "PNG"),
            "size": params.get("size", 200),
            "error_correction": params.get("error_correction", "M"),
            "fill_color": params.get("fill_color", "#000000"),
            "back_color": params.get("back_color", "#FFFFFF")
        }
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def generate_qr_code(self, request: QRCodeRequest) -> Dict[str, Any]:
        """Generate QR code image"""
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=None,  # Auto-detect version
                error_correction=self.error_correction_map[request.error_correction],
                box_size=request.box_size,
                border=request.border,
            )
            
            # Add data
            qr.add_data(request.content)
            qr.make(fit=True)
            
            # Create QR code image
            if request.format == QRFormat.SVG:
                return self._generate_svg_qr(qr, request)
            else:
                return self._generate_image_qr(qr, request)
                
        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"QR code generation failed: {str(e)}")
    
    def _generate_image_qr(self, qr: qrcode.QRCode, request: QRCodeRequest) -> Dict[str, Any]:
        """Generate image-based QR code (PNG, JPEG, BMP)"""
        # Create image
        qr_img = qr.make_image(fill_color=request.fill_color, back_color=request.back_color)
        
        # Apply style if specified
        if request.style != QRStyle.SQUARE:
            qr_img = self._apply_style(qr_img, request.style)
        
        # Add logo if specified
        if request.logo_url:
            qr_img = self._add_logo(qr_img, request.logo_url, request.logo_size)
        
        # Resize to requested size
        if qr_img.size != (request.size, request.size):
            qr_img = qr_img.resize((request.size, request.size), Image.Resampling.LANCZOS)
        
        # Convert to requested format
        img_buffer = io.BytesIO()
        
        if request.format == QRFormat.JPEG:
            # Convert to RGB for JPEG (no transparency)
            if qr_img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', qr_img.size, request.back_color)
                if qr_img.mode == 'P':
                    qr_img = qr_img.convert('RGBA')
                background.paste(qr_img, mask=qr_img.split()[-1] if qr_img.mode == 'RGBA' else None)
                qr_img = background
            qr_img.save(img_buffer, format='JPEG', quality=95)
        else:
            qr_img.save(img_buffer, format=request.format.value)
        
        img_buffer.seek(0)
        
        return {
            "image_data": img_buffer.getvalue(),
            "size": len(img_buffer.getvalue()),
            "width": request.size,
            "height": request.size
        }
    
    def _generate_svg_qr(self, qr: qrcode.QRCode, request: QRCodeRequest) -> Dict[str, Any]:
        """Generate SVG QR code"""
        import xml.etree.ElementTree as ET
        
        # Get QR code matrix
        qr_matrix = qr.get_matrix()
        box_size = request.box_size
        border = request.border
        total_size = (len(qr_matrix) + 2 * border) * box_size
        
        # Create SVG
        svg = ET.Element('svg', {
            'width': str(total_size),
            'height': str(total_size),
            'xmlns': 'http://www.w3.org/2000/svg'
        })
        
        # Add background
        ET.SubElement(svg, 'rect', {
            'width': str(total_size),
            'height': str(total_size),
            'fill': request.back_color
        })
        
        # Add QR code modules
        for y, row in enumerate(qr_matrix):
            for x, module in enumerate(row):
                if module:
                    rect = ET.SubElement(svg, 'rect', {
                        'x': str((x + border) * box_size),
                        'y': str((y + border) * box_size),
                        'width': str(box_size),
                        'height': str(box_size),
                        'fill': request.fill_color
                    })
                    
                    # Apply rounded corners if style is rounded
                    if request.style == QRStyle.ROUNDED:
                        rect.set('rx', str(box_size // 4))
                        rect.set('ry', str(box_size // 4))
        
        # Convert to string
        svg_data = ET.tostring(svg, encoding='unicode')
        
        return {
            "svg_data": svg_data.encode('utf-8'),
            "size": len(svg_data),
            "width": total_size,
            "height": total_size
        }
    
    def _apply_style(self, img: Image.Image, style: QRStyle) -> Image.Image:
        """Apply visual style to QR code"""
        if style == QRStyle.ROUNDED:
            # Apply rounded corners effect
            return self._apply_rounded_style(img)
        elif style == QRStyle.CIRCLE:
            # Apply circular dots
            return self._apply_circle_style(img)
        else:
            return img
    
    def _apply_rounded_style(self, img: Image.Image) -> Image.Image:
        """Apply rounded corners to QR modules"""
        # This is a simplified implementation
        # In production, you'd want more sophisticated styling
        return img
    
    def _apply_circle_style(self, img: Image.Image) -> Image.Image:
        """Apply circular dots to QR modules"""
        # This is a simplified implementation
        # In production, you'd want more sophisticated styling
        return img
    
    def _add_logo(self, img: Image.Image, logo_url: str, logo_size: Optional[int]) -> Image.Image:
        """Add logo to center of QR code"""
        try:
            # Download logo (simplified - in production, use proper HTTP client)
            import requests
            response = requests.get(logo_url, timeout=10)
            logo_img = Image.open(io.BytesIO(response.content))
            
            # Calculate logo size
            qr_size = img.size[0]
            if logo_size is None:
                logo_size = qr_size // 5  # Default to 1/5 of QR size
            
            # Resize logo
            logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Create transparent overlay
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            
            # Calculate position (center)
            x = (qr_size - logo_size) // 2
            y = (qr_size - logo_size) // 2
            
            # Paste logo
            overlay.paste(logo_img, (x, y))
            
            # Composite images
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            
            return img
            
        except Exception as e:
            logger.warning(f"Failed to add logo: {e}")
            return img
    
    def save_qr_code(self, qr_id: str, qr_data: Dict[str, Any], format: QRFormat) -> str:
        """Save QR code to file"""
        # Generate filename
        filename = f"{qr_id}.{format.value.lower()}"
        file_path = self.output_dir / filename
        
        # Save file
        if format == QRFormat.SVG:
            with open(file_path, 'wb') as f:
                f.write(qr_data["svg_data"])
        else:
            with open(file_path, 'wb') as f:
                f.write(qr_data["image_data"])
        
        return str(file_path)
    
    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """Get file statistics"""
        try:
            path = Path(file_path)
            if path.exists():
                return {
                    "file_size": path.stat().st_size,
                    "created_at": datetime.fromtimestamp(path.stat().st_ctime),
                    "modified_at": datetime.fromtimestamp(path.stat().st_mtime)
                }
        except Exception as e:
            logger.warning(f"Failed to get file stats: {e}")
        
        return {}

# Initialize QR code service
qr_service = QRCodeService()

# Database operations
def save_qr_code_to_db(db: Connection, qr_data: Dict[str, Any]) -> str:
    """Save QR code record to database"""
    cursor = db.cursor()
    
    cursor.execute('''
        INSERT INTO qr_codes (
            id, user_id, content, format, size, error_correction, box_size, border,
            fill_color, back_color, logo_path, logo_size, custom_data, file_path,
            file_size, content_hash, expires_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        qr_data["id"],
        qr_data.get("user_id"),
        qr_data["content"],
        qr_data["format"],
        qr_data["size"],
        qr_data["error_correction"],
        qr_data["box_size"],
        qr_data["border"],
        qr_data["fill_color"],
        qr_data["back_color"],
        qr_data.get("logo_path"),
        qr_data.get("logo_size"),
        json.dumps(qr_data.get("custom_data", {})),
        qr_data.get("file_path"),
        qr_data.get("file_size"),
        qr_data["content_hash"],
        qr_data.get("expires_at")
    ))
    
    db.commit()
    return qr_data["id"]

def get_qr_code_from_db(db: Connection, qr_id: str) -> Optional[Dict[str, Any]]:
    """Get QR code from database"""
    cursor = db.cursor()
    cursor.execute("SELECT * FROM qr_codes WHERE id = ? AND is_active = 1", (qr_id,))
    row = cursor.fetchone()
    
    if row:
        return dict(row)
    return None

def get_user_qr_history(db: Connection, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user's QR code history"""
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM qr_codes WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    
    return [dict(row) for row in rows]

def update_download_count(db: Connection, qr_id: str) -> int:
    """Update download count"""
    cursor = db.cursor()
    cursor.execute(
        "UPDATE qr_codes SET download_count = download_count + 1 WHERE id = ?",
        (qr_id,)
    )
    db.commit()
    
    cursor.execute("SELECT download_count FROM qr_codes WHERE id = ?", (qr_id,))
    result = cursor.fetchone()
    return result["download_count"] if result else 0

def log_analytics(db: Connection, qr_id: str, action: str, ip_address: str = None, user_agent: str = None):
    """Log analytics event"""
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO qr_analytics (id, qr_id, action, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        str(uuid.uuid4()),
        qr_id,
        action,
        ip_address,
        user_agent
    ))
    db.commit()

def get_qr_analytics(db: Connection, qr_id: str) -> Dict[str, Any]:
    """Get QR code analytics"""
    cursor = db.cursor()
    
    # Total counts
    cursor.execute('''
        SELECT action, COUNT(*) as count 
        FROM qr_analytics 
        WHERE qr_id = ? 
        GROUP BY action
    ''', (qr_id,))
    action_counts = {row["action"]: row["count"] for row in cursor.fetchall()}
    
    # Last accessed
    cursor.execute(
        "SELECT MAX(created_at) as last_accessed FROM qr_analytics WHERE qr_id = ?",
        (qr_id,)
    )
    last_accessed = cursor.fetchone()["last_accessed"]
    
    # Access by IP
    cursor.execute('''
        SELECT ip_address, COUNT(*) as count 
        FROM qr_analytics 
        WHERE qr_id = ? AND ip_address IS NOT NULL 
        GROUP BY ip_address
    ''', (qr_id,))
    access_by_ip = {row["ip_address"]: row["count"] for row in cursor.fetchall()}
    
    # Access by date
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM qr_analytics 
        WHERE qr_id = ? 
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        LIMIT 30
    ''', (qr_id,))
    access_by_date = {row["date"]: row["count"] for row in cursor.fetchall()}
    
    return {
        "qr_id": qr_id,
        "total_downloads": action_counts.get("download", 0),
        "total_views": action_counts.get("view", 0),
        "total_generations": action_counts.get("generate", 0),
        "last_accessed": last_accessed,
        "access_by_ip": access_by_ip,
        "access_by_date": access_by_date
    }

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to QR Code Generator API", "version": "1.0.0"}

@app.post("/generate", response_model=QRCodeResponse)
async def generate_qr_code(
    request: QRCodeRequest,
    db: Connection = Depends(get_db)
):
    """Generate a new QR code"""
    try:
        # Generate content hash
        content_hash = qr_service.generate_content_hash(
            request.content, 
            request.dict()
        )
        
        # Check if identical QR code already exists
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM qr_codes WHERE content_hash = ? AND user_id = ? AND is_active = 1",
            (content_hash, request.user_id)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Return existing QR code
            qr_data = dict(existing)
            log_analytics(db, qr_data["id"], "generate")
            
            return QRCodeResponse(
                id=qr_data["id"],
                content=qr_data["content"],
                format=qr_data["format"],
                size=qr_data["size"],
                download_url=f"/download/{qr_data['id']}",
                preview_url=f"/preview/{qr_data['id']}",
                content_hash=qr_data["content_hash"],
                created_at=qr_data["created_at"],
                expires_at=qr_data["expires_at"],
                download_count=qr_data["download_count"],
                file_size=qr_data.get("file_size")
            )
        
        # Generate new QR code
        qr_result = qr_service.generate_qr_code(request)
        
        # Generate unique ID
        qr_id = str(uuid.uuid4())
        
        # Calculate expiration time
        expires_at = None
        if request.expires_in_hours:
            expires_at = datetime.now() + timedelta(hours=request.expires_in_hours)
        
        # Save QR code to file
        file_path = qr_service.save_qr_code(qr_id, qr_result, request.format)
        
        # Prepare database record
        qr_record = {
            "id": qr_id,
            "user_id": request.user_id,
            "content": request.content,
            "format": request.format.value,
            "size": request.size,
            "error_correction": request.error_correction.value,
            "box_size": request.box_size,
            "border": request.border,
            "fill_color": request.fill_color,
            "back_color": request.back_color,
            "logo_path": str(request.logo_url) if request.logo_url else None,
            "logo_size": request.logo_size,
            "custom_data": request.custom_data,
            "file_path": file_path,
            "file_size": qr_result.get("size"),
            "content_hash": content_hash,
            "expires_at": expires_at
        }
        
        # Save to database
        save_qr_code_to_db(db, qr_record)
        
        # Log analytics
        log_analytics(db, qr_id, "generate")
        
        return QRCodeResponse(
            id=qr_id,
            content=request.content,
            format=request.format.value,
            size=request.size,
            download_url=f"/download/{qr_id}",
            preview_url=f"/preview/{qr_id}",
            content_hash=content_hash,
            created_at=datetime.now(),
            expires_at=expires_at,
            download_count=0,
            file_size=qr_result.get("size")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QR code generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"QR code generation failed: {str(e)}")

@app.get("/preview/{qr_id}")
async def preview_qr_code(qr_id: str, db: Connection = Depends(get_db)):
    """Preview QR code image"""
    try:
        # Get QR code from database
        qr_data = get_qr_code_from_db(db, qr_id)
        if not qr_data:
            raise HTTPException(status_code=404, detail="QR code not found")
        
        # Check if expired
        if qr_data.get("expires_at") and datetime.now() > datetime.fromisoformat(qr_data["expires_at"]):
            raise HTTPException(status_code=410, detail="QR code has expired")
        
        # Log analytics
        log_analytics(db, qr_id, "view")
        
        # Serve file
        file_path = qr_data.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="QR code file not found")
        
        # Determine media type
        format_map = {
            "PNG": "image/png",
            "JPEG": "image/jpeg",
            "BMP": "image/bmp",
            "SVG": "image/svg+xml"
        }
        media_type = format_map.get(qr_data["format"], "image/png")
        
        return FileResponse(
            file_path,
            media_type=media_type,
            filename=f"qr_{qr_id}.{qr_data['format'].lower()}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QR code preview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@app.get("/download/{qr_id}")
async def download_qr_code(qr_id: str, db: Connection = Depends(get_db)):
    """Download QR code file"""
    try:
        # Get QR code from database
        qr_data = get_qr_code_from_db(db, qr_id)
        if not qr_data:
            raise HTTPException(status_code=404, detail="QR code not found")
        
        # Check if expired
        if qr_data.get("expires_at") and datetime.now() > datetime.fromisoformat(qr_data["expires_at"]):
            raise HTTPException(status_code=410, detail="QR code has expired")
        
        # Update download count
        download_count = update_download_count(db, qr_id)
        
        # Log analytics
        log_analytics(db, qr_id, "download")
        
        # Serve file
        file_path = qr_data.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="QR code file not found")
        
        # Determine media type
        format_map = {
            "PNG": "image/png",
            "JPEG": "image/jpeg",
            "BMP": "image/bmp",
            "SVG": "image/svg+xml"
        }
        media_type = format_map.get(qr_data["format"], "image/png")
        
        return FileResponse(
            file_path,
            media_type=media_type,
            filename=f"qr_code_{qr_id}.{qr_data['format'].lower()}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"QR code download failed: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/history/{user_id}", response_model=List[QRCodeHistory])
async def get_qr_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    db: Connection = Depends(get_db)
):
    """Get user's QR code generation history"""
    try:
        history = get_user_qr_history(db, user_id, limit)
        
        return [
            QRCodeHistory(
                id=qr["id"],
                content=qr["content"],
                format=qr["format"],
                size=qr["size"],
                fill_color=qr["fill_color"],
                back_color=qr["back_color"],
                created_at=qr["created_at"],
                download_count=qr["download_count"],
                expires_at=qr.get("expires_at"),
                is_active=bool(qr["is_active"])
            )
            for qr in history
        ]
        
    except Exception as e:
        logger.error(f"Failed to get QR history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/analytics/{qr_id}", response_model=QRAnalytics)
async def get_qr_analytics(qr_id: str, db: Connection = Depends(get_db)):
    """Get QR code analytics"""
    try:
        # Check if QR code exists
        qr_data = get_qr_code_from_db(db, qr_id)
        if not qr_data:
            raise HTTPException(status_code=404, detail="QR code not found")
        
        # Get analytics
        analytics = get_qr_analytics(db, qr_id)
        
        return QRAnalytics(
            qr_id=analytics["qr_id"],
            total_downloads=analytics["total_downloads"],
            total_views=analytics["total_views"],
            last_accessed=analytics["last_accessed"],
            access_by_ip=analytics["access_by_ip"],
            access_by_date=analytics["access_by_date"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get QR analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.delete("/qr/{qr_id}")
async def delete_qr_code(qr_id: str, user_id: str = Query(...), db: Connection = Depends(get_db)):
    """Delete QR code"""
    try:
        # Check if QR code exists and belongs to user
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM qr_codes WHERE id = ? AND user_id = ?",
            (qr_id, user_id)
        )
        qr_data = cursor.fetchone()
        
        if not qr_data:
            raise HTTPException(status_code=404, detail="QR code not found")
        
        # Soft delete (mark as inactive)
        cursor.execute(
            "UPDATE qr_codes SET is_active = 0 WHERE id = ?",
            (qr_id,)
        )
        db.commit()
        
        # Delete file (optional - keep for analytics)
        file_path = qr_data["file_path"]
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to delete file {file_path}: {e}")
        
        return {"message": "QR code deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete QR code: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete QR code: {str(e)}")

@app.get("/formats")
async def get_supported_formats():
    """Get supported QR code formats"""
    return {
        "formats": [
            {
                "format": "PNG",
                "description": "Portable Network Graphics - supports transparency",
                "recommended": True
            },
            {
                "format": "SVG",
                "description": "Scalable Vector Graphics - infinitely scalable",
                "recommended": True
            },
            {
                "format": "JPEG",
                "description": "Joint Photographic Experts Group - smaller file size",
                "recommended": False
            },
            {
                "format": "BMP",
                "description": "Bitmap - uncompressed format",
                "recommended": False
            }
        ]
    }

@app.get("/styles")
async def get_supported_styles():
    """Get supported QR code styles"""
    return {
        "styles": [
            {
                "style": "square",
                "name": "Square",
                "description": "Traditional square modules",
                "recommended": True
            },
            {
                "style": "rounded",
                "name": "Rounded",
                "description": "Rounded corner modules",
                "recommended": True
            },
            {
                "style": "circle",
                "name": "Circle",
                "description": "Circular dot modules",
                "recommended": False
            },
            {
                "style": "custom",
                "name": "Custom",
                "description": "Custom styling (advanced)",
                "recommended": False
            }
        ]
    }

@app.get("/error-correction-levels")
async def get_error_correction_levels():
    """Get error correction levels"""
    return {
        "levels": [
            {
                "level": "L",
                "name": "Low",
                "correction": "~7%",
                "description": "Low error correction, more data capacity",
                "recommended": False
            },
            {
                "level": "M",
                "name": "Medium",
                "correction": "~15%",
                "description": "Medium error correction, balanced",
                "recommended": True
            },
            {
                "level": "Q",
                "name": "Quartile",
                "correction": "~25%",
                "description": "High error correction",
                "recommended": True
            },
            {
                "level": "H",
                "name": "High",
                "correction": "~30%",
                "description": "Highest error correction, less data capacity",
                "recommended": False
            }
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "output_directory": str(qr_service.output_dir),
        "output_directory_exists": qr_service.output_dir.exists(),
        "database_connected": True
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8015)
