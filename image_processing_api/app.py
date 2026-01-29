from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import os
import uuid
import asyncio
from datetime import datetime
import json
import base64
import io
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import numpy as np
import cv2

app = FastAPI(
    title="Image Processing API",
    description="Advanced image processing service with filters, transformations, and AI-powered features",
    version="1.0.0"
)

# Enums
class ImageFormat(str, Enum):
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    BMP = "bmp"
    TIFF = "tiff"
    GIF = "gif"

class FilterType(str, Enum):
    BLUR = "blur"
    SHARPEN = "sharpen"
    EDGE_DETECT = "edge_detect"
    EMBOSS = "emboss"
    CONTOUR = "contour"
    SMOOTH = "smooth"
    DETAIL = "detail"
    FIND_EDGES = "find_edges"

class AdjustmentType(str, Enum):
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"
    HUE = "hue"
    SHARPNESS = "sharpness"
    GAMMA = "gamma"

class ResizeMethod(str, Enum):
    NEAREST = "nearest"
    BILINEAR = "bilinear"
    BICUBIC = "bicubic"
    LANCZOS = "lanczos"

# Data Models
class ImageFilterRequest(BaseModel):
    filter_type: FilterType
    intensity: float = 1.0
    parameters: Optional[Dict[str, Any]] = {}

class ImageAdjustmentRequest(BaseModel):
    adjustment_type: AdjustmentType
    value: float
    parameters: Optional[Dict[str, Any]] = {}

class ImageResizeRequest(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
    maintain_aspect_ratio: bool = True
    resize_method: ResizeMethod = ResizeMethod.LANCZOS
    quality: int = 95

class ImageTransformRequest(BaseModel):
    rotation: Optional[float] = None
    flip_horizontal: bool = False
    flip_vertical: bool = False
    crop: Optional[Dict[str, int]] = None  # {x, y, width, height}
    resize: Optional[ImageResizeRequest] = None

class BatchProcessRequest(BaseModel):
    operations: List[Dict[str, Any]]
    output_format: Optional[ImageFormat] = None
    quality: int = 95
    preserve_metadata: bool = True

class ImageAnalysisRequest(BaseModel):
    analyze_colors: bool = True
    analyze_faces: bool = False
    analyze_objects: bool = False
    analyze_text: bool = False
    analyze_quality: bool = True

# Storage (in production, use proper storage)
processed_images = {}
processing_jobs = {}

@app.get("/")
async def root():
    return {"message": "Image Processing API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Image Upload and Processing
@app.post("/api/image/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image for processing"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        
        # Generate unique ID
        image_id = str(uuid.uuid4())
        
        # Create upload directory
        upload_dir = Path("./uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = upload_dir / f"{image_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Open image with PIL
        image = Image.open(file_path)
        
        # Get image info
        image_info = {
            "id": image_id,
            "filename": file.filename,
            "original_path": str(file_path),
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "file_size": len(content),
            "uploaded_at": datetime.now().isoformat()
        }
        
        processed_images[image_id] = image_info
        
        return {
            "success": True,
            "message": "Image uploaded successfully",
            "image_id": image_id,
            "image_info": image_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@app.post("/api/image/{image_id}/filter")
async def apply_filter(image_id: str, filter_request: ImageFilterRequest):
    """Apply filter to uploaded image"""
    try:
        if image_id not in processed_images:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image_info = processed_images[image_id]
        image_path = image_info["original_path"]
        
        # Open image
        image = Image.open(image_path)
        
        # Apply filter based on type
        if filter_request.filter_type == FilterType.BLUR:
            filtered_image = image.filter(ImageFilter.GaussianBlur(radius=filter_request.intensity * 5))
        elif filter_request.filter_type == FilterType.SHARPEN:
            filtered_image = image.filter(ImageFilter.SHARPEN)
        elif filter_request.filter_type == FilterType.EDGE_DETECT:
            filtered_image = image.filter(ImageFilter.FIND_EDGES)
        elif filter_request.filter_type == FilterType.EMBOSS:
            filtered_image = image.filter(ImageFilter.EMBOSS)
        elif filter_request.filter_type == FilterType.CONTOUR:
            filtered_image = image.filter(ImageFilter.CONTOUR)
        elif filter_request.filter_type == FilterType.SMOOTH:
            filtered_image = image.filter(ImageFilter.SMOOTH)
        elif filter_request.filter_type == FilterType.DETAIL:
            filtered_image = image.filter(ImageFilter.DETAIL)
        elif filter_request.filter_type == FilterType.FIND_EDGES:
            filtered_image = image.filter(ImageFilter.FIND_EDGES)
        else:
            filtered_image = image
        
        # Save processed image
        processed_dir = Path("./processed")
        processed_dir.mkdir(exist_ok=True)
        
        processed_filename = f"{image_id}_filtered_{filter_request.filter_type.value}.png"
        processed_path = processed_dir / processed_filename
        filtered_image.save(processed_path)
        
        return {
            "success": True,
            "message": f"Filter {filter_request.filter_type.value} applied successfully",
            "processed_image_id": f"{image_id}_filtered",
            "processed_filename": processed_filename,
            "processed_path": str(processed_path),
            "filter_applied": filter_request.filter_type.value,
            "intensity": filter_request.intensity
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply filter: {str(e)}")

@app.post("/api/image/{image_id}/adjust")
async def adjust_image(image_id: str, adjustment_request: ImageAdjustmentRequest):
    """Adjust image properties (brightness, contrast, etc.)"""
    try:
        if image_id not in processed_images:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image_info = processed_images[image_id]
        image_path = image_info["original_path"]
        
        # Open image
        image = Image.open(image_path)
        
        # Apply adjustment based on type
        if adjustment_request.adjustment_type == AdjustmentType.BRIGHTNESS:
            enhancer = ImageEnhance.Brightness(image)
            adjusted_image = enhancer.enhance(adjustment_request.value)
        elif adjustment_request.adjustment_type == AdjustmentType.CONTRAST:
            enhancer = ImageEnhance.Contrast(image)
            adjusted_image = enhancer.enhance(adjustment_request.value)
        elif adjustment_request.adjustment_type == AdjustmentType.SATURATION:
            enhancer = ImageEnhance.Color(image)
            adjusted_image = enhancer.enhance(adjustment_request.value)
        elif adjustment_request.adjustment_type == AdjustmentType.SHARPNESS:
            enhancer = ImageEnhance.Sharpness(image)
            adjusted_image = enhancer.enhance(adjustment_request.value)
        else:
            adjusted_image = image
        
        # Save processed image
        processed_dir = Path("./processed")
        processed_dir.mkdir(exist_ok=True)
        
        processed_filename = f"{image_id}_adjusted_{adjustment_request.adjustment_type.value}.png"
        processed_path = processed_dir / processed_filename
        adjusted_image.save(processed_path)
        
        return {
            "success": True,
            "message": f"Adjustment {adjustment_request.adjustment_type.value} applied successfully",
            "processed_image_id": f"{image_id}_adjusted",
            "processed_filename": processed_filename,
            "processed_path": str(processed_path),
            "adjustment_applied": adjustment_request.adjustment_type.value,
            "value": adjustment_request.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to adjust image: {str(e)}")

@app.post("/api/image/{image_id}/transform")
async def transform_image(image_id: str, transform_request: ImageTransformRequest):
    """Transform image (rotate, flip, crop, resize)"""
    try:
        if image_id not in processed_images:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image_info = processed_images[image_id]
        image_path = image_info["original_path"]
        
        # Open image
        image = Image.open(image_path)
        transformed_image = image
        
        # Apply transformations
        if transform_request.rotation is not None:
            transformed_image = transformed_image.rotate(transform_request.rotation, expand=True)
        
        if transform_request.flip_horizontal:
            transformed_image = transformed_image.transpose(Image.FLIP_LEFT_RIGHT)
        
        if transform_request.flip_vertical:
            transformed_image = transformed_image.transpose(Image.FLIP_TOP_BOTTOM)
        
        if transform_request.crop:
            crop_params = transform_request.crop
            transformed_image = transformed_image.crop((
                crop_params["x"],
                crop_params["y"],
                crop_params["x"] + crop_params["width"],
                crop_params["y"] + crop_params["height"]
            ))
        
        if transform_request.resize:
            resize_params = transform_request.resize
            
            if resize_params.maintain_aspect_ratio:
                # Calculate new size maintaining aspect ratio
                original_width, original_height = transformed_image.size
                if resize_params.width and resize_params.height:
                    # Use the smaller ratio to fit within bounds
                    ratio = min(resize_params.width / original_width, resize_params.height / original_height)
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                elif resize_params.width:
                    ratio = resize_params.width / original_width
                    new_width = resize_params.width
                    new_height = int(original_height * ratio)
                elif resize_params.height:
                    ratio = resize_params.height / original_height
                    new_width = int(original_width * ratio)
                    new_height = resize_params.height
                else:
                    new_width, new_height = transformed_image.size
            else:
                new_width = resize_params.width or transformed_image.size[0]
                new_height = resize_params.height or transformed_image.size[1]
            
            # Map resize method to PIL constant
            resize_methods = {
                ResizeMethod.NEAREST: Image.NEAREST,
                ResizeMethod.BILINEAR: Image.BILINEAR,
                ResizeMethod.BICUBIC: Image.BICUBIC,
                ResizeMethod.LANCZOS: Image.LANCZOS
            }
            
            resample = resize_methods.get(resize_params.resize_method, Image.LANCZOS)
            transformed_image = transformed_image.resize((new_width, new_height), resample)
        
        # Save processed image
        processed_dir = Path("./processed")
        processed_dir.mkdir(exist_ok=True)
        
        processed_filename = f"{image_id}_transformed.png"
        processed_path = processed_dir / processed_filename
        transformed_image.save(processed_path)
        
        return {
            "success": True,
            "message": "Image transformed successfully",
            "processed_image_id": f"{image_id}_transformed",
            "processed_filename": processed_filename,
            "processed_path": str(processed_path),
            "original_size": image.size,
            "new_size": transformed_image.size,
            "transformations_applied": {
                "rotation": transform_request.rotation,
                "flip_horizontal": transform_request.flip_horizontal,
                "flip_vertical": transform_request.flip_vertical,
                "crop": transform_request.crop,
                "resize": {
                    "width": transform_request.resize.width if transform_request.resize else None,
                    "height": transform_request.resize.height if transform_request.resize else None,
                    "method": transform_request.resize.resize_method.value if transform_request.resize else None
                } if transform_request.resize else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transform image: {str(e)}")

@app.post("/api/image/{image_id}/analyze")
async def analyze_image(image_id: str, analysis_request: ImageAnalysisRequest):
    """Analyze image properties and content"""
    try:
        if image_id not in processed_images:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image_info = processed_images[image_id]
        image_path = image_info["original_path"]
        
        # Open image
        image = Image.open(image_path)
        
        analysis_results = {}
        
        # Basic image properties
        analysis_results["basic_properties"] = {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "has_transparency": image.mode in ('RGBA', 'LA') or 'transparency' in image.info
        }
        
        # Color analysis
        if analysis_request.analyze_colors:
            # Convert to RGB if necessary
            rgb_image = image.convert('RGB')
            
            # Get dominant colors using histogram
            histogram = rgb_image.histogram()
            
            # Calculate average color
            width, height = rgb_image.size
            pixels = list(rgb_image.getdata())
            
            if pixels:
                avg_r = sum(p[0] for p in pixels) / len(pixels)
                avg_g = sum(p[1] for p in pixels) / len(pixels)
                avg_b = sum(p[2] for p in pixels) / len(pixels)
                
                analysis_results["color_analysis"] = {
                    "average_color": {
                        "rgb": [int(avg_r), int(avg_g), int(avg_b)],
                        "hex": f"#{int(avg_r):02x}{int(avg_g):02x}{int(avg_b):02x}"
                    },
                    "total_pixels": width * height,
                    "color_channels": {
                        "red": histogram[0:256],
                        "green": histogram[256:512],
                        "blue": histogram[512:768]
                    }
                }
        
        # Quality analysis
        if analysis_request.analyze_quality:
            # Calculate basic quality metrics
            gray_image = image.convert('L')
            gray_array = np.array(gray_image)
            
            # Calculate sharpness (using Laplacian variance)
            laplacian_var = cv2.Laplacian(gray_array, cv2.CV_64F).var()
            
            # Calculate brightness and contrast
            brightness = np.mean(gray_array)
            contrast = np.std(gray_array)
            
            analysis_results["quality_analysis"] = {
                "sharpness": float(laplacian_var),
                "brightness": float(brightness),
                "contrast": float(contrast),
                "quality_score": min(100, max(0, (laplacian_var / 100) * 50 + (contrast / 128) * 50))
            }
        
        # Face detection (placeholder - would need face detection library)
        if analysis_request.analyze_faces:
            analysis_results["face_detection"] = {
                "faces_detected": 0,
                "face_locations": [],
                "note": "Face detection requires additional ML libraries"
            }
        
        # Object detection (placeholder - would need object detection library)
        if analysis_request.analyze_objects:
            analysis_results["object_detection"] = {
                "objects_detected": [],
                "note": "Object detection requires additional ML libraries"
            }
        
        # Text detection (placeholder - would need OCR library)
        if analysis_request.analyze_text:
            analysis_results["text_detection"] = {
                "text_found": "",
                "confidence": 0.0,
                "note": "Text detection requires OCR libraries"
            }
        
        return {
            "success": True,
            "message": "Image analysis completed",
            "image_id": image_id,
            "analysis_results": analysis_results,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze image: {str(e)}")

@app.post("/api/image/{image_id}/batch-process")
async def batch_process_image(image_id: str, batch_request: BatchProcessRequest):
    """Apply multiple operations to an image"""
    try:
        if image_id not in processed_images:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image_info = processed_images[image_id]
        image_path = image_info["original_path"]
        
        # Open image
        image = Image.open(image_path)
        processed_image = image
        
        # Apply operations in sequence
        applied_operations = []
        
        for operation in batch_request.operations:
            op_type = operation.get("type")
            op_params = operation.get("parameters", {})
            
            if op_type == "filter":
                filter_type = FilterType(op_params.get("filter_type"))
                intensity = op_params.get("intensity", 1.0)
                
                if filter_type == FilterType.BLUR:
                    processed_image = processed_image.filter(ImageFilter.GaussianBlur(radius=intensity * 5))
                elif filter_type == FilterType.SHARPEN:
                    processed_image = processed_image.filter(ImageFilter.SHARPEN)
                elif filter_type == FilterType.EDGE_DETECT:
                    processed_image = processed_image.filter(ImageFilter.FIND_EDGES)
                
                applied_operations.append(f"filter_{filter_type.value}")
            
            elif op_type == "adjust":
                adjustment_type = AdjustmentType(op_params.get("adjustment_type"))
                value = op_params.get("value", 1.0)
                
                if adjustment_type == AdjustmentType.BRIGHTNESS:
                    enhancer = ImageEnhance.Brightness(processed_image)
                    processed_image = enhancer.enhance(value)
                elif adjustment_type == AdjustmentType.CONTRAST:
                    enhancer = ImageEnhance.Contrast(processed_image)
                    processed_image = enhancer.enhance(value)
                elif adjustment_type == AdjustmentType.SATURATION:
                    enhancer = ImageEnhance.Color(processed_image)
                    processed_image = enhancer.enhance(value)
                
                applied_operations.append(f"adjust_{adjustment_type.value}")
            
            elif op_type == "resize":
                width = op_params.get("width")
                height = op_params.get("height")
                maintain_aspect = op_params.get("maintain_aspect_ratio", True)
                
                if maintain_aspect:
                    original_width, original_height = processed_image.size
                    if width and height:
                        ratio = min(width / original_width, height / original_height)
                        new_width = int(original_width * ratio)
                        new_height = int(original_height * ratio)
                    elif width:
                        ratio = width / original_width
                        new_width = width
                        new_height = int(original_height * ratio)
                    else:
                        new_width, new_height = processed_image.size
                else:
                    new_width = width or processed_image.size[0]
                    new_height = height or processed_image.size[1]
                
                processed_image = processed_image.resize((new_width, new_height), Image.LANCZOS)
                applied_operations.append(f"resize_{new_width}x{new_height}")
        
        # Save processed image
        processed_dir = Path("./processed")
        processed_dir.mkdir(exist_ok=True)
        
        output_format = batch_request.output_format or ImageFormat.PNG
        processed_filename = f"{image_id}_batch_{'_'.join(applied_operations)}.{output_format.value}"
        processed_path = processed_dir / processed_filename
        
        # Save with quality if JPEG
        if output_format == ImageFormat.JPEG:
            processed_image.save(processed_path, quality=batch_request.quality, optimize=True)
        else:
            processed_image.save(processed_path)
        
        return {
            "success": True,
            "message": "Batch processing completed successfully",
            "processed_image_id": f"{image_id}_batch",
            "processed_filename": processed_filename,
            "processed_path": str(processed_path),
            "operations_applied": applied_operations,
            "output_format": output_format.value,
            "final_size": processed_image.size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to batch process image: {str(e)}")

@app.get("/api/image/{image_id}/download")
async def download_image(image_id: str, processed_type: str = "original"):
    """Download original or processed image"""
    try:
        if processed_type == "original":
            if image_id not in processed_images:
                raise HTTPException(status_code=404, detail="Image not found")
            
            image_path = processed_images[image_id]["original_path"]
            filename = processed_images[image_id]["filename"]
        else:
            # Look for processed image
            processed_dir = Path("./processed")
            processed_files = list(processed_dir.glob(f"{image_id}_{processed_type}*"))
            
            if not processed_files:
                raise HTTPException(status_code=404, detail="Processed image not found")
            
            image_path = processed_files[0]
            filename = processed_files[0].name
        
        return FileResponse(
            path=image_path,
            filename=filename,
            media_type="image/jpeg"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download image: {str(e)}")

@app.get("/api/images")
async def list_images(limit: int = 50, offset: int = 0):
    """List uploaded and processed images"""
    try:
        images = []
        
        for image_id, image_info in processed_images.items():
            # Check for processed images
            processed_dir = Path("./processed")
            processed_files = list(processed_dir.glob(f"{image_id}_*"))
            
            images.append({
                "id": image_id,
                "filename": image_info["filename"],
                "format": image_info["format"],
                "size": image_info["size"],
                "file_size": image_info["file_size"],
                "uploaded_at": image_info["uploaded_at"],
                "processed_count": len(processed_files)
            })
        
        # Apply pagination
        total = len(images)
        paginated_images = images[offset:offset + limit]
        
        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "images": paginated_images
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list images: {str(e)}")

@app.delete("/api/image/{image_id}")
async def delete_image(image_id: str, delete_processed: bool = True):
    """Delete uploaded image and optionally processed versions"""
    try:
        if image_id not in processed_images:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Delete original image
        original_path = processed_images[image_id]["original_path"]
        if os.path.exists(original_path):
            os.remove(original_path)
        
        # Delete processed images if requested
        deleted_processed = []
        if delete_processed:
            processed_dir = Path("./processed")
            processed_files = list(processed_dir.glob(f"{image_id}_*"))
            
            for processed_file in processed_files:
                processed_file.unlink()
                deleted_processed.append(processed_file.name)
        
        # Remove from storage
        del processed_images[image_id]
        
        return {
            "success": True,
            "message": "Image deleted successfully",
            "deleted_original": True,
            "deleted_processed_count": len(deleted_processed),
            "deleted_processed_files": deleted_processed
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
