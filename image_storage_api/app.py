from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uvicorn
import os
import uuid
import hashlib
import mimetypes
from PIL import Image, ImageOps, ImageFilter
import io
import asyncio
import aiofiles
from pathlib import Path
import shutil

app = FastAPI(title="Image Upload + Cloud Storage API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = "uploads"
THUMBNAIL_DIR = "thumbnails"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
DEFAULT_QUALITY = 85
THUMBNAIL_SIZE = (300, 300)

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

# Enums
class ImageFormat(str, Enum):
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"

class ResizeMode(str, Enum):
    CONTAIN = "contain"
    COVER = "cover"
    FILL = "fill"
    PAD = "pad"

class StorageProvider(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    CLOUDINARY = "cloudinary"

# Pydantic models
class ImageInfo(BaseModel):
    filename: str
    original_name: str
    file_size: int
    mime_type: str
    width: int
    height: int
    format: ImageFormat
    color_mode: str
    has_transparency: bool
    upload_date: datetime
    file_url: str
    thumbnail_url: str
    file_hash: str
    storage_provider: StorageProvider

class ProcessedImage(BaseModel):
    original_info: ImageInfo
    processed_url: str
    operations: List[str]
    processing_time: float

class UploadResponse(BaseModel):
    success: bool
    message: str
    image_info: Optional[ImageInfo] = None
    error: Optional[str] = None

class BatchUploadResponse(BaseModel):
    total_files: int
    successful_uploads: int
    failed_uploads: int
    results: List[UploadResponse]
    processing_time: float

class ImageProcessingOptions(BaseModel):
    resize: Optional[Dict[str, Any]] = None
    compress: Optional[Dict[str, Any]] = None
    format: Optional[ImageFormat] = None
    quality: Optional[int] = Field(None, ge=1, le=100)
    rotate: Optional[float] = None
    flip: Optional[str] = None  # "horizontal", "vertical"
    crop: Optional[Dict[str, int]] = None
    filter: Optional[str] = None
    watermark: Optional[Dict[str, Any]] = None

class CloudStorageConfig(BaseModel):
    provider: StorageProvider
    bucket_name: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    region: Optional[str] = None
    cloud_name: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

# Image processing class
class ImageProcessor:
    def __init__(self):
        self.supported_formats = {
            'JPEG': ImageFormat.JPEG,
            'PNG': ImageFormat.PNG,
            'WEBP': ImageFormat.WEBP,
            'GIF': ImageFormat.GIF
        }
    
    def get_image_info(self, image: Image.Image, filename: str, file_size: int) -> Dict[str, Any]:
        """Extract comprehensive image information"""
        return {
            "filename": filename,
            "original_name": filename,
            "file_size": file_size,
            "mime_type": mimetypes.guess_type(filename)[0] or "application/octet-stream",
            "width": image.width,
            "height": image.height,
            "format": self.supported_formats.get(image.format, ImageFormat.JPEG),
            "color_mode": image.mode,
            "has_transparency": (image.mode in ('RGBA', 'LA') or 'transparency' in image.info),
            "upload_date": datetime.now(),
            "file_url": f"/uploads/{filename}",
            "thumbnail_url": f"/thumbnails/{filename}",
            "file_hash": self.calculate_file_hash(filename),
            "storage_provider": StorageProvider.LOCAL
        }
    
    def calculate_file_hash(self, filename: str) -> str:
        """Calculate SHA-256 hash of the file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except FileNotFoundError:
            return ""
    
    def resize_image(self, image: Image.Image, width: int, height: int, mode: ResizeMode = ResizeMode.CONTAIN) -> Image.Image:
        """Resize image with different modes"""
        if mode == ResizeMode.CONTAIN:
            # Resize to fit within dimensions, maintaining aspect ratio
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
            return image
        elif mode == ResizeMode.COVER:
            # Resize to cover dimensions, maintaining aspect ratio
            image_ratio = image.width / image.height
            target_ratio = width / height
            
            if image_ratio > target_ratio:
                new_height = int(width / image_ratio)
                image = image.resize((width, new_height), Image.Resampling.LANCZOS)
            else:
                new_width = int(height * image_ratio)
                image = image.resize((new_width, height), Image.Resampling.LANCZOS)
            
            # Crop to exact dimensions
            left = (image.width - width) // 2
            top = (image.height - height) // 2
            return image.crop((left, top, left + width, top + height))
        
        elif mode == ResizeMode.FILL:
            # Resize to exact dimensions, may distort
            return image.resize((width, height), Image.Resampling.LANCZOS)
        
        elif mode == ResizeMode.PAD:
            # Resize to fit, then pad to exact dimensions
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
            new_image = Image.new('RGB', (width, height), (255, 255, 255))
            
            # Center the image
            left = (width - image.width) // 2
            top = (height - image.height) // 2
            new_image.paste(image, (left, top))
            
            return new_image
        
        return image
    
    def compress_image(self, image: Image.Image, quality: int = DEFAULT_QUALITY, format: ImageFormat = ImageFormat.JPEG) -> bytes:
        """Compress image and return bytes"""
        output = io.BytesIO()
        
        # Convert format if needed
        if format == ImageFormat.JPEG and image.mode in ('RGBA', 'LA', 'P'):
            # Convert to RGB for JPEG
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Save with compression
        save_kwargs = {'quality': quality, 'optimize': True}
        
        if format == ImageFormat.PNG:
            save_kwargs.pop('quality', None)
            save_kwargs['compress_level'] = 6
        
        image.save(output, format=format.value.upper(), **save_kwargs)
        return output.getvalue()
    
    def create_thumbnail(self, image: Image.Image, size: tuple = THUMBNAIL_SIZE) -> Image.Image:
        """Create thumbnail of the image"""
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Create thumbnail
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create square thumbnail with padding
        thumbnail = Image.new('RGB', size, (255, 255, 255))
        left = (size[0] - image.width) // 2
        top = (size[1] - image.height) // 2
        thumbnail.paste(image, (left, top))
        
        return thumbnail
    
    def apply_filter(self, image: Image.Image, filter_name: str) -> Image.Image:
        """Apply filters to image"""
        filters = {
            'grayscale': ImageFilter.FIND_EDGES,
            'blur': ImageFilter.BLUR,
            'sharpen': ImageFilter.SHARPEN,
            'edge_enhance': ImageFilter.EDGE_ENHANCE,
            'smooth': ImageFilter.SMOOTH,
            'emboss': ImageFilter.EMBOSS
        }
        
        if filter_name in filters:
            return image.filter(filters[filter_name])
        elif filter_name == 'grayscale':
            return image.convert('L').convert('RGB')
        elif filter_name == 'sepia':
            # Simple sepia filter
            from PIL import ImageEnhance
            image = image.convert('RGB')
            r, g, b = image.split()
            r = r.point(lambda x: min(255, int(x * 1.5)))
            g = g.point(lambda x: min(255, int(x * 1.2)))
            b = b.point(lambda x: min(255, int(x * 0.8)))
            return Image.merge('RGB', (r, g, b))
        
        return image
    
    def add_watermark(self, image: Image.Image, text: str, position: str = "bottom-right", opacity: float = 0.7) -> Image.Image:
        """Add text watermark to image"""
        from PIL import ImageDraw, ImageFont
        
        # Ensure image is in RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create a transparent overlay
        watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # Try to load a font, fallback to default
        try:
            font_size = max(20, min(image.width, image.height) // 20)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        margin = 20
        positions = {
            "top-left": (margin, margin),
            "top-right": (image.width - text_width - margin, margin),
            "bottom-left": (margin, image.height - text_height - margin),
            "bottom-right": (image.width - text_width - margin, image.height - text_height - margin),
            "center": ((image.width - text_width) // 2, (image.height - text_height) // 2)
        }
        
        x, y = positions.get(position, positions["bottom-right"])
        
        # Draw text with transparency
        alpha = int(255 * opacity)
        draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))
        
        # Composite watermark onto original image
        return Image.alpha_composite(image.convert('RGBA'), watermark).convert('RGB')
    
    def process_image(self, image: Image.Image, options: ImageProcessingOptions) -> tuple[Image.Image, List[str]]:
        """Process image with multiple operations"""
        operations = []
        processed_image = image.copy()
        
        # Resize
        if options.resize:
            width = options.resize.get('width', processed_image.width)
            height = options.resize.get('height', processed_image.height)
            mode = ResizeMode(options.resize.get('mode', 'contain'))
            processed_image = self.resize_image(processed_image, width, height, mode)
            operations.append(f"resize_{width}x{height}_{mode}")
        
        # Crop
        if options.crop:
            left = options.crop.get('left', 0)
            top = options.crop.get('top', 0)
            right = options.crop.get('right', processed_image.width)
            bottom = options.crop.get('bottom', processed_image.height)
            processed_image = processed_image.crop((left, top, right, bottom))
            operations.append(f"crop_{left}_{top}_{right}_{bottom}")
        
        # Rotate
        if options.rotate is not None:
            processed_image = processed_image.rotate(options.rotate, expand=True)
            operations.append(f"rotate_{options.rotate}")
        
        # Flip
        if options.flip == "horizontal":
            processed_image = processed_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            operations.append("flip_horizontal")
        elif options.flip == "vertical":
            processed_image = processed_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            operations.append("flip_vertical")
        
        # Apply filter
        if options.filter:
            processed_image = self.apply_filter(processed_image, options.filter)
            operations.append(f"filter_{options.filter}")
        
        # Add watermark
        if options.watermark:
            text = options.watermark.get('text', 'Sample Watermark')
            position = options.watermark.get('position', 'bottom-right')
            opacity = options.watermark.get('opacity', 0.7)
            processed_image = self.add_watermark(processed_image, text, position, opacity)
            operations.append("watermark")
        
        # Format conversion
        if options.format:
            operations.append(f"format_{options.format}")
        
        # Quality/compression
        if options.quality:
            operations.append(f"quality_{options.quality}")
        
        return processed_image, operations

# Storage classes
class LocalStorage:
    """Local file storage"""
    
    async def save_file(self, file_content: bytes, filename: str, directory: str = UPLOAD_DIR) -> str:
        """Save file to local storage"""
        file_path = os.path.join(directory, filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return file_path
    
    async def delete_file(self, filename: str, directory: str = UPLOAD_DIR) -> bool:
        """Delete file from local storage"""
        file_path = os.path.join(directory, filename)
        
        try:
            os.remove(file_path)
            return True
        except FileNotFoundError:
            return False
    
    def get_file_url(self, filename: str, directory: str = UPLOAD_DIR) -> str:
        """Get public URL for file"""
        return f"/{directory}/{filename}"

class S3Storage:
    """AWS S3 storage (mock implementation)"""
    
    def __init__(self, bucket_name: str, access_key: str, secret_key: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        # In production, initialize boto3 client here
    
    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file to S3 (mock implementation)"""
        # In production, use boto3 to upload to S3
        # For now, save locally and return S3-style URL
        local_storage = LocalStorage()
        await local_storage.save_file(file_content, filename)
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
    
    def get_file_url(self, filename: str) -> str:
        """Get S3 URL for file"""
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"

class CloudinaryStorage:
    """Cloudinary storage (mock implementation)"""
    
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        # In production, initialize cloudinary library here
    
    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file to Cloudinary (mock implementation)"""
        # In production, use cloudinary library to upload
        # For now, save locally and return Cloudinary-style URL
        local_storage = LocalStorage()
        await local_storage.save_file(file_content, filename)
        return f"https://res.cloudinary.com/{self.cloud_name}/image/upload/{filename}"
    
    def get_file_url(self, filename: str) -> str:
        """Get Cloudinary URL for file"""
        return f"https://res.cloudinary.com/{self.cloud_name}/image/upload/{filename}"

# Initialize components
image_processor = ImageProcessor()
storage = LocalStorage()

# Helper functions
def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file.filename)
    if not mime_type or not mime_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename"""
    file_ext = os.path.splitext(original_filename)[1]
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_ext}"

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Image Upload + Cloud Storage API", "version": "1.0.0"}

@app.post("/upload", response_model=ImageInfo)
async def upload_image(
    file: UploadFile = File(...),
    resize_width: Optional[int] = Query(None, ge=1, le=10000),
    resize_height: Optional[int] = Query(None, ge=1, le=10000),
    quality: int = Query(DEFAULT_QUALITY, ge=1, le=100),
    format: Optional[ImageFormat] = Query(None),
    thumbnail: bool = Query(True),
    storage_provider: StorageProvider = Query(StorageProvider.LOCAL)
):
    """Upload and process an image"""
    import time
    start_time = time.time()
    
    # Validate file
    validate_file(file)
    
    # Read file content
    file_content = await file.read()
    
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename)
    
    # Open image
    try:
        image = Image.open(io.BytesIO(file_content))
        image.load()  # Load image data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    # Process image
    processed_image = image.copy()
    
    # Resize if requested
    if resize_width and resize_height:
        processed_image = image_processor.resize_image(processed_image, resize_width, resize_height)
    
    # Convert format if requested
    if format:
        processed_content = image_processor.compress_image(processed_image, quality, format)
        file_ext = f".{format.value}"
        if not filename.endswith(file_ext):
            filename = os.path.splitext(filename)[0] + file_ext
    else:
        processed_content = image_processor.compress_image(processed_image, quality)
    
    # Save main image
    file_url = await storage.save_file(processed_content, filename)
    
    # Create and save thumbnail
    thumbnail_filename = filename
    if thumbnail:
        thumbnail_image = image_processor.create_thumbnail(image)
        thumbnail_content = image_processor.compress_image(thumbnail_image, 80)
        await storage.save_file(thumbnail_content, thumbnail_filename, THUMBNAIL_DIR)
    
    # Get image info
    image_info_data = image_processor.get_image_info(processed_image, filename, len(processed_content))
    image_info_data["file_url"] = storage.get_file_url(filename)
    image_info_data["thumbnail_url"] = storage.get_file_url(thumbnail_filename, THUMBNAIL_DIR)
    image_info_data["storage_provider"] = storage_provider
    
    processing_time = time.time() - start_time
    image_info_data["processing_time"] = processing_time
    
    return ImageInfo(**image_info_data)

@app.post("/upload-batch", response_model=BatchUploadResponse)
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    quality: int = Query(DEFAULT_QUALITY, ge=1, le=100),
    thumbnail: bool = Query(True),
    storage_provider: StorageProvider = Query(StorageProvider.LOCAL)
):
    """Upload multiple images"""
    import time
    start_time = time.time()
    
    results = []
    successful_uploads = 0
    failed_uploads = 0
    
    for file in files:
        try:
            # Process each file
            file_content = await file.read()
            
            # Validate file
            validate_file(file)
            
            # Generate unique filename
            filename = generate_unique_filename(file.filename)
            
            # Open image
            image = Image.open(io.BytesIO(file_content))
            image.load()
            
            # Process image
            processed_content = image_processor.compress_image(image, quality)
            
            # Save file
            await storage.save_file(processed_content, filename)
            
            # Create thumbnail
            if thumbnail:
                thumbnail_image = image_processor.create_thumbnail(image)
                thumbnail_content = image_processor.compress_image(thumbnail_image, 80)
                await storage.save_file(thumbnail_content, filename, THUMBNAIL_DIR)
            
            # Get image info
            image_info_data = image_processor.get_image_info(image, filename, len(processed_content))
            image_info_data["file_url"] = storage.get_file_url(filename)
            image_info_data["thumbnail_url"] = storage.get_file_url(filename, THUMBNAIL_DIR)
            image_info_data["storage_provider"] = storage_provider
            
            results.append(UploadResponse(
                success=True,
                message="File uploaded successfully",
                image_info=ImageInfo(**image_info_data)
            ))
            successful_uploads += 1
            
        except Exception as e:
            results.append(UploadResponse(
                success=False,
                message="Upload failed",
                error=str(e)
            ))
            failed_uploads += 1
    
    processing_time = time.time() - start_time
    
    return BatchUploadResponse(
        total_files=len(files),
        successful_uploads=successful_uploads,
        failed_uploads=failed_uploads,
        results=results,
        processing_time=processing_time
    )

@app.post("/process", response_model=ProcessedImage)
async def process_existing_image(
    filename: str = Form(...),
    options: ImageProcessingOptions = Depends()
):
    """Process an existing uploaded image"""
    import time
    start_time = time.time()
    
    # Check if file exists
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Open image
    try:
        image = Image.open(file_path)
        image.load()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    # Get original info
    original_info = image_processor.get_image_info(image, filename, os.path.getsize(file_path))
    original_info["file_url"] = storage.get_file_url(filename)
    original_info["thumbnail_url"] = storage.get_file_url(filename, THUMBNAIL_DIR)
    
    # Process image
    processed_image, operations = image_processor.process_image(image, options)
    
    # Generate processed filename
    processed_filename = f"processed_{uuid.uuid4().hex[:8]}_{filename}"
    
    # Save processed image
    quality = options.quality or DEFAULT_QUALITY
    format_type = options.format or ImageFormat.JPEG
    processed_content = image_processor.compress_image(processed_image, quality, format_type)
    
    await storage.save_file(processed_content, processed_filename)
    
    processing_time = time.time() - start_time
    
    return ProcessedImage(
        original_info=ImageInfo(**original_info),
        processed_url=storage.get_file_url(processed_filename),
        operations=operations,
        processing_time=processing_time
    )

@app.get("/images/{filename}")
async def get_image(filename: str):
    """Serve uploaded image"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Read and return file
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    
    return Response(content=content, media_type=mime_type)

@app.get("/thumbnails/{filename}")
async def get_thumbnail(filename: str):
    """Serve thumbnail image"""
    file_path = os.path.join(THUMBNAIL_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Read and return file
    async with aiofiles.open(file_path, 'rb') as f:
        content = await f.read()
    
    return Response(content=content, media_type=mime_type)

@app.get("/images")
async def list_images(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    format_filter: Optional[ImageFormat] = None
):
    """List uploaded images with pagination"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):
                # Get file info
                stat = os.stat(file_path)
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Apply format filter if specified
                if format_filter and file_ext != f".{format_filter.value}":
                    continue
                
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime),
                    "file_url": storage.get_file_url(filename),
                    "thumbnail_url": storage.get_file_url(filename, THUMBNAIL_DIR)
                })
        
        # Sort by creation date (newest first)
        files.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Pagination
        total_files = len(files)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_files = files[start_idx:end_idx]
        
        total_pages = (total_files + limit - 1) // limit
        
        return {
            "files": paginated_files,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_files": total_files,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.delete("/images/{filename}")
async def delete_image(filename: str):
    """Delete an uploaded image"""
    # Delete main image
    main_deleted = await storage.delete_file(filename, UPLOAD_DIR)
    
    # Delete thumbnail
    thumbnail_deleted = await storage.delete_file(filename, THUMBNAIL_DIR)
    
    if not main_deleted and not thumbnail_deleted:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {"message": "Image deleted successfully"}

@app.get("/image-info/{filename}")
async def get_image_info(filename: str):
    """Get detailed information about an image"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        image = Image.open(file_path)
        image.load()
        
        file_size = os.path.getsize(file_path)
        image_info_data = image_processor.get_image_info(image, filename, file_size)
        image_info_data["file_url"] = storage.get_file_url(filename)
        image_info_data["thumbnail_url"] = storage.get_file_url(filename, THUMBNAIL_DIR)
        
        return ImageInfo(**image_info_data)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading image: {str(e)}")

@app.post("/configure-storage")
async def configure_storage(config: CloudStorageConfig):
    """Configure cloud storage provider"""
    global storage
    
    if config.provider == StorageProvider.S3:
        if not all([config.bucket_name, config.access_key, config.secret_key]):
            raise HTTPException(status_code=400, detail="S3 configuration incomplete")
        
        storage = S3Storage(
            bucket_name=config.bucket_name,
            access_key=config.access_key,
            secret_key=config.secret_key,
            region=config.region or "us-east-1"
        )
        
    elif config.provider == StorageProvider.CLOUDINARY:
        if not all([config.cloud_name, config.api_key, config.api_secret]):
            raise HTTPException(status_code=400, detail="Cloudinary configuration incomplete")
        
        storage = CloudinaryStorage(
            cloud_name=config.cloud_name,
            api_key=config.api_key,
            api_secret=config.api_secret
        )
    
    else:
        storage = LocalStorage()
    
    return {"message": f"Storage configured to use {config.provider.value}", "provider": config.provider.value}

@app.get("/storage-info")
async def get_storage_info():
    """Get current storage configuration and statistics"""
    # Count files in local storage
    local_files = len([f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))])
    thumbnail_files = len([f for f in os.listdir(THUMBNAIL_DIR) if os.path.isfile(os.path.join(THUMBNAIL_DIR, f))])
    
    # Calculate total storage used
    total_size = 0
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            total_size += os.path.getsize(file_path)
    
    storage_type = type(storage).__name__
    
    return {
        "storage_type": storage_type,
        "local_files_count": local_files,
        "thumbnail_files_count": thumbnail_files,
        "total_storage_used": total_size,
        "total_storage_used_mb": round(total_size / (1024 * 1024), 2),
        "upload_directory": UPLOAD_DIR,
        "thumbnail_directory": THUMBNAIL_DIR,
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "max_file_size": MAX_FILE_SIZE,
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "storage_type": type(storage).__name__,
        "upload_directory_exists": os.path.exists(UPLOAD_DIR),
        "thumbnail_directory_exists": os.path.exists(THUMBNAIL_DIR)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)
