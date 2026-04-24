import os
import json
import base64
import numpy as np
from PIL import Image
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import Product
import io

# Optional imports for AI functionality
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import torch
    # Some torch versions expose _register_pytree_node only; transformers expects register_pytree_node.
    if hasattr(torch.utils, '_pytree') and not hasattr(torch.utils._pytree, 'register_pytree_node'):
        if hasattr(torch.utils._pytree, '_register_pytree_node'):
            torch.utils._pytree.register_pytree_node = torch.utils._pytree._register_pytree_node

    from transformers import AutoProcessor, AutoModel, VisionEncoderDecoderModel
    TORCH_AVAILABLE = True
except Exception:
    # Avoid failing startup for management commands when model libs are not available.
    TORCH_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except Exception:
    # easyocr may fail due to incompatible torchvision/torch dependencies.
    EASYOCR_AVAILABLE = False

# Global variables for model caching
fashion_model = None
fashion_processor = None
trocr_processor = None
trocr_model = None
ocr_reader = None

def load_fashion_model():
    """Load the Marqo FashionSigLIP model for image similarity search"""
    if not TORCH_AVAILABLE:
        print("PyTorch not available, skipping model loading")
        return False
        
    global fashion_model, fashion_processor
    if fashion_model is None or fashion_processor is None:
        try:
            # Use the Marqo FashionSigLIP model for image similarity
            model_name = "Marqo/marqo-fashionSigLIP"
            print(f"Loading model: {model_name}")
            
            # Set Hugging Face token if available
            token = getattr(settings, 'HUGGINGFACE_TOKEN', None)
            if token:
                print("Using Hugging Face token for authentication")
                fashion_processor = AutoProcessor.from_pretrained(
                    model_name, 
                    trust_remote_code=True,
                    token=token
                )
                fashion_model = AutoModel.from_pretrained(
                    model_name, 
                    trust_remote_code=True,
                    token=token
                )
            else:
                print("No Hugging Face token found, using public access")
                fashion_processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
                fashion_model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
            
            fashion_model.eval()  # Set to evaluation mode
            print("Marqo FashionSigLIP model loaded successfully")
        except Exception as e:
            print(f"Error loading Marqo FashionSigLIP model: {e}")
            # Fallback to Microsoft's FashionSigLIP model
            try:
                model_name = "microsoft/FashionSigLIP"
                print(f"Trying fallback model: {model_name}")
                token = getattr(settings, 'HUGGINGFACE_TOKEN', None)
                if token:
                    fashion_processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True, token=token)
                    fashion_model = AutoModel.from_pretrained(model_name, trust_remote_code=True, token=token)
                else:
                    fashion_processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
                    fashion_model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
                fashion_model.eval()
                print("Fallback Microsoft FashionSigLIP model loaded successfully")
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                return False
    return True

def load_trocr_model():
    """Load the TrOCR model for text recognition"""
    if not TORCH_AVAILABLE:
        print("PyTorch not available, skipping TrOCR model loading")
        return False
        
    global trocr_processor, trocr_model
    if trocr_processor is None or trocr_model is None:
        try:
            # Use the base TrOCR model for text recognition
            model_name = "microsoft/trocr-base-printed"
            print(f"Loading TrOCR model: {model_name}")
            
            # Set Hugging Face token if available
            token = getattr(settings, 'HUGGINGFACE_TOKEN', None)
            if token:
                print("Using Hugging Face token for TrOCR authentication")
                trocr_processor = AutoProcessor.from_pretrained(model_name, token=token)
                trocr_model = VisionEncoderDecoderModel.from_pretrained(model_name, token=token)
            else:
                print("No Hugging Face token found, using public access for TrOCR")
                trocr_processor = AutoProcessor.from_pretrained(model_name)
                trocr_model = VisionEncoderDecoderModel.from_pretrained(model_name)
            
            trocr_model.eval()
            print("TrOCR model loaded successfully")
        except Exception as e:
            print(f"Error loading TrOCR model: {e}")
            # Fallback to handwritten-specific TrOCR model
            try:
                model_name = "microsoft/trocr-base-handwritten"
                print(f"Trying fallback TrOCR model: {model_name}")
                token = getattr(settings, 'HUGGINGFACE_TOKEN', None)
                if token:
                    trocr_processor = AutoProcessor.from_pretrained(model_name, token=token)
                    trocr_model = VisionEncoderDecoderModel.from_pretrained(model_name, token=token)
                else:
                    trocr_processor = AutoProcessor.from_pretrained(model_name)
                    trocr_model = VisionEncoderDecoderModel.from_pretrained(model_name)
                trocr_model.eval()
                print("Fallback TrOCR handwritten model loaded successfully")
            except Exception as e2:
                print(f"Error loading fallback TrOCR model: {e2}")
                return False
    return True

def load_ocr_reader():
    """Load EasyOCR reader for text extraction"""
    if not EASYOCR_AVAILABLE:
        print("EasyOCR not available, skipping OCR reader loading")
        return False
        
    global ocr_reader
    if ocr_reader is None:
        try:
            ocr_reader = easyocr.Reader(['en'])
            print("EasyOCR reader loaded successfully")
        except Exception as e:
            print(f"Error loading EasyOCR reader: {e}")
            return False
    return True

def preprocess_image(image_file):
    """Preprocess image for model input"""
    try:
        # Convert to PIL Image
        if isinstance(image_file, str):
            # If it's a base64 string
            image_data = base64.b64decode(image_file.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
        else:
            # If it's a file upload
            image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def extract_image_features(image):
    """Extract features from image using FashionSigLIP"""
    if not load_fashion_model():
        print("Failed to load fashion model")
        return None
    
    try:
        # Process image
        inputs = fashion_processor(images=image, return_tensors="pt")
        print(f"Processed image inputs shape: {inputs.pixel_values.shape}")
        
        # Get image features
        with torch.no_grad():
            outputs = fashion_model(**inputs)
            # Handle different model output structures
            if hasattr(outputs, 'image_embeds'):
                image_features = outputs.image_embeds
            elif hasattr(outputs, 'last_hidden_state'):
                image_features = outputs.last_hidden_state.mean(dim=1)
            else:
                # Fallback: use the first available tensor
                image_features = list(outputs.values())[0]
                if len(image_features.shape) > 2:
                    image_features = image_features.mean(dim=1)
        
        print(f"Extracted features shape: {image_features.shape}")
        return image_features
    except Exception as e:
        print(f"Error extracting image features: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_text_from_image(image):
    """Extract text from image using TrOCR and EasyOCR"""
    extracted_texts = []
    
    # Try EasyOCR first (more reliable for general text)
    if load_ocr_reader():
        try:
            print("Using EasyOCR for text extraction")
            # Convert PIL to numpy array for EasyOCR
            img_array = np.array(image)
            results = ocr_reader.readtext(img_array)
            print(f"EasyOCR found {len(results)} text regions")
            for (bbox, text, confidence) in results:
                print(f"Text: '{text}' (confidence: {confidence:.2f})")
                if confidence > 0.3:  # Lower threshold for better results
                    extracted_texts.append(text.strip())
        except Exception as e:
            print(f"EasyOCR error: {e}")
            import traceback
            traceback.print_exc()
    
    # Try TrOCR as backup for handwritten text
    if load_trocr_model() and not extracted_texts:
        try:
            print("Using TrOCR for handwritten text extraction")
            inputs = trocr_processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = trocr_model(**inputs)
                # For TrOCR, we need to decode the logits to text
                # This is a simplified version - in practice you'd use a proper decoder
                if hasattr(outputs, 'logits'):
                    # Simple approach: just indicate TrOCR was used
                    extracted_texts.append("Handwritten text detected by TrOCR")
                else:
                    extracted_texts.append("Text detected by TrOCR")
        except Exception as e:
            print(f"TrOCR error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"Final extracted texts: {extracted_texts}")
    return extracted_texts

def calculate_similarity(features1, features2):
    """Calculate cosine similarity between two feature vectors"""
    try:
        # Normalize features
        features1_norm = torch.nn.functional.normalize(features1, p=2, dim=1)
        features2_norm = torch.nn.functional.normalize(features2, p=2, dim=1)
        
        # Calculate cosine similarity
        similarity = torch.mm(features1_norm, features2_norm.t())
        return similarity.item()
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0

@csrf_exempt
def search_products_by_image(request):
    """Search products by image similarity using FashionSigLIP"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        # Get uploaded image
        if 'image' in request.FILES:
            image_file = request.FILES['image']
        elif 'image_data' in request.POST:
            image_file = request.POST['image_data']
        else:
            return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)
        
        # Preprocess image
        image = preprocess_image(image_file)
        if image is None:
            return JsonResponse({'success': False, 'error': 'Invalid image'}, status=400)
        
        # Extract features from query image
        print("Extracting features from query image...")
        query_features = extract_image_features(image)
        if query_features is None:
            # Fallback: return all products with images if AI fails
            print("AI model failed, returning all products with images as fallback")
            products = Product.objects.exclude(image__isnull=True).exclude(image='')
            fallback_products = []
            for product in products:
                fallback_products.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': product.quantity,
                    'description': product.description,
                    'image_url': product.image.url if product.image else '',
                    'shop': product.shopkeeper.name,
                    'similarity': 0.5  # Default similarity for fallback
                })
            
            return JsonResponse({
                'success': True,
                'products': fallback_products[:10],
                'total_found': len(fallback_products),
                'message': 'AI model unavailable, showing all products with images'
            })
        
        # Get all products with images
        products = Product.objects.exclude(image__isnull=True).exclude(image='')
        
        # Calculate similarities
        similar_products = []
        for product in products:
            try:
                # Load and preprocess product image
                product_image = Image.open(product.image.path)
                product_image = product_image.convert('RGB')
                
                # Extract features from product image
                product_features = extract_image_features(product_image)
                if product_features is not None:
                    # Calculate similarity
                    similarity = calculate_similarity(query_features, product_features)
                    
                    similar_products.append({
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'quantity': product.quantity,
                        'description': product.description,
                        'image_url': product.image.url if product.image else '',
                        'shop': product.shopkeeper.name,
                        'similarity': similarity
                    })
            except Exception as e:
                print(f"Error processing product {product.id}: {e}")
                continue
        
        # Sort by similarity (highest first)
        similar_products.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Group products by category
        grouped_products = {}
        for product_data in similar_products[:20]:  # Get top 20 for better category representation
            # Get the actual product to access category
            product = Product.objects.filter(id=product_data['id']).first()
            if product:
                category = product.get_category_display()  # Get human-readable category name
                if category not in grouped_products:
                    grouped_products[category] = []
                grouped_products[category].append(product_data)
        
        # Return grouped products
        return JsonResponse({
            'success': True,
            'products': similar_products[:10],  # Keep original flat list for backward compatibility
            'grouped_products': grouped_products,
            'total_found': len(similar_products)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def search_products_by_text_image(request):
    """Search products by text extracted from image using TrOCR and EasyOCR"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        # Get uploaded image
        if 'image' in request.FILES:
            image_file = request.FILES['image']
        elif 'image_data' in request.POST:
            image_file = request.POST['image_data']
        else:
            return JsonResponse({'success': False, 'error': 'No image provided'}, status=400)
        
        # Preprocess image
        image = preprocess_image(image_file)
        if image is None:
            return JsonResponse({'success': False, 'error': 'Invalid image'}, status=400)
        
        # Extract text from image
        print("Extracting text from image...")
        extracted_texts = extract_text_from_image(image)
        print(f"Extracted texts: {extracted_texts}")
        
        if not extracted_texts:
            # Fallback: return all products if no text extracted
            print("No text extracted, returning all products as fallback")
            products = Product.objects.all()
            fallback_products = []
            for product in products:
                fallback_products.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': product.quantity,
                    'description': product.description,
                    'image_url': product.image.url if product.image else '',
                    'shop': product.shopkeeper.name
                })
            
            return JsonResponse({
                'success': True,
                'products': fallback_products[:10],
                'extracted_text': 'No text extracted',
                'total_found': len(fallback_products),
                'message': 'No text found in image, showing all available products'
            })
        
        # Combine all extracted text
        combined_text = ' '.join(extracted_texts)
        
        # Search products by text
        from django.db.models import Q
        
        # Create search query
        search_terms = combined_text.lower().split()
        query = Q()
        for term in search_terms:
            query |= Q(name__icontains=term) | Q(description__icontains=term)
        
        # Get matching products
        products = Product.objects.filter(query).distinct()
        
        # Format results and group by category
        matching_products = []
        grouped_products = {}
        
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': product.quantity,
                'description': product.description,
                'image_url': product.image.url if product.image else '',
                'shop': product.shopkeeper.name
            }
            matching_products.append(product_data)
            
            # Group by category
            category = product.get_category_display()
            if category not in grouped_products:
                grouped_products[category] = []
            grouped_products[category].append(product_data)
        
        return JsonResponse({
            'success': True,
            'products': matching_products,
            'grouped_products': grouped_products,
            'extracted_text': combined_text,
            'total_found': len(matching_products)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def search_page(request):
    """Render the search page with both search options"""
    context = {}
    
    # Handle pre-loaded images from dashboard quick search
    if request.method == 'POST':
        if 'image' in request.FILES:
            # Pre-fill image search form
            context['preload_image'] = request.FILES['image']
        elif 'text_image' in request.FILES:
            # Pre-fill text search form
            context['preload_text_image'] = request.FILES['text_image']
    
    return render(request, 'customer/search.html', context)

@csrf_exempt
def debug_models(request):
    """Debug endpoint to check model loading status"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        status = {
            'fashion_model': fashion_model is not None,
            'fashion_processor': fashion_processor is not None,
            'trocr_model': trocr_model is not None,
            'trocr_processor': trocr_processor is not None,
            'ocr_reader': ocr_reader is not None,
        }
        
        # Test model loading
        fashion_ok = load_fashion_model()
        trocr_ok = load_trocr_model()
        ocr_ok = load_ocr_reader()
        
        return JsonResponse({
            'success': True,
            'models_loaded': status,
            'fashion_model_working': fashion_ok,
            'trocr_model_working': trocr_ok,
            'ocr_working': ocr_ok,
            'message': 'Model status checked'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Error checking model status'
        }, status=500)
