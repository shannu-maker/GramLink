# AI-Powered Product Search

This Django application now includes advanced AI-powered search functionality for products using image similarity and text recognition.

## 🔍 Features

### 1. **Search by Image Similarity** (FashionSigLIP)
- Upload an image to find visually similar products
- Uses Microsoft's FashionSigLIP model for accurate similarity matching
- Returns products ranked by similarity score
- Fallback to CLIP-ViT-B-32 if FashionSigLIP fails

### 2. **Search by Text Recognition** (TrOCR + EasyOCR)
- Upload an image with handwritten text
- Extracts text using Microsoft TrOCR and EasyOCR
- Searches products by name and description
- Shows extracted text to user

## 🚀 Quick Start

### Installation
1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Installation Script:**
   ```bash
   python install_ai_models.py
   ```

3. **Test Model Status:**
   Visit: `http://localhost:8000/api/debug/models/`

### Usage
1. **Access Search Page:**
   - Go to customer dashboard
   - Click "🔍 Search Products" button
   - Or visit: `http://localhost:8000/search/`

2. **Quick Search from Dashboard:**
   - Click "🖼️ Search by Image" for image similarity
   - Click "📝 Search by Text" for text recognition

## 🛠️ API Endpoints

### Image Similarity Search
```
POST /api/search/image/
Content-Type: multipart/form-data
Body: image file
```

### Text Recognition Search
```
POST /api/search/text-image/
Content-Type: multipart/form-data
Body: image file
```

### Debug Models
```
GET /api/debug/models/
```

## 🔧 Troubleshooting

### Common Issues

1. **"Failed to extract image features"**
   - Check if models are loaded: `/api/debug/models/`
   - Try running: `python test_models.py`
   - Reinstall dependencies: `python install_ai_models.py`

2. **"No text extracted"**
   - Ensure image has clear, visible text
   - Try different image formats (JPG, PNG)
   - Check if EasyOCR is working: `/api/debug/models/`

3. **Models not loading**
   - Check internet connection (models download from Hugging Face)
   - Try: `pip install --upgrade transformers torch`
   - Clear cache: `rm -rf ~/.cache/huggingface/`

### Fallback Behavior
- If AI models fail, the system will show all available products
- This ensures the search functionality always works
- Users will see a message indicating fallback mode

## 📁 File Structure

```
capstone/
├── members/
│   ├── search_views.py          # AI search functionality
│   └── urls.py                   # Search URL patterns
├── templates/customer/
│   ├── search.html              # Search page template
│   └── dashboard.html            # Updated with search buttons
├── requirements.txt              # Updated dependencies
├── test_models.py               # Model testing script
├── install_ai_models.py         # Installation script
└── SEARCH_README.md             # This file
```

## 🎯 Model Details

### FashionSigLIP
- **Purpose**: Image similarity for fashion/clothing items
- **Fallback**: CLIP-ViT-B-32 (general purpose)
- **Input**: Product images
- **Output**: Similarity scores

### TrOCR
- **Purpose**: Handwritten text recognition
- **Fallback**: TrOCR-base-printed (printed text)
- **Input**: Images with text
- **Output**: Extracted text strings

### EasyOCR
- **Purpose**: General text recognition
- **Languages**: English
- **Input**: Images with text
- **Output**: Text with confidence scores

## 🔄 Development

### Testing Models
```bash
python test_models.py
```

### Debugging
- Check model status: `/api/debug/models/`
- View console logs for detailed error messages
- Test individual components in Django shell

### Adding New Models
1. Update `search_views.py` with new model loading function
2. Add fallback handling
3. Update requirements.txt
4. Test with `test_models.py`

## 📊 Performance Notes

- Models are loaded once and cached in memory
- First request may be slower due to model loading
- Subsequent requests are much faster
- Consider using GPU if available for better performance

## 🆘 Support

If you encounter issues:
1. Check the debug endpoint: `/api/debug/models/`
2. Run the test script: `python test_models.py`
3. Check Django logs for detailed error messages
4. Ensure all dependencies are properly installed
