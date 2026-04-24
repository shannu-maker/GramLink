# 🤗 Hugging Face Token Setup Guide

This guide will help you set up your Hugging Face token for the AI search functionality.

## 🔑 Getting Your Hugging Face Token

1. **Visit Hugging Face**: Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. **Sign Up/Login**: Create an account or log in to your existing account
3. **Create Token**: 
   - Click "New token"
   - Give it a name (e.g., "Django App Token")
   - Select "Read" access
   - Click "Generate token"
4. **Copy Token**: Copy the token (it starts with `hf_...`)

## 🔧 Setting Up the Token

### Method 1: Environment Variable (Recommended)

#### Windows (Command Prompt)
```cmd
set HUGGINGFACE_TOKEN=your_token_here
python manage.py runserver
```

#### Windows (PowerShell)
```powershell
$env:HUGGINGFACE_TOKEN="your_token_here"
python manage.py runserver
```

#### Linux/Mac
```bash
export HUGGINGFACE_TOKEN="your_token_here"
python manage.py runserver
```

### Method 2: Direct in settings.py

Edit `capstone/mysite/settings.py` and change this line:
```python
# From:
HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_TOKEN', '')

# To:
HUGGINGFACE_TOKEN = 'your_actual_token_here'
```

### Method 3: Using the Setup Script

Run the automated setup script:
```bash
python setup_huggingface_token.py
```

## 🧪 Testing Your Setup

1. **Start the server**:
   ```bash
   python manage.py runserver
   ```

2. **Check model status**: Visit `http://localhost:8000/api/debug/models/`

3. **Test search functionality**: Go to `http://localhost:8000/search/`

## 🔍 Troubleshooting

### Common Issues

1. **"No token found"**
   - Make sure you've set the environment variable correctly
   - Check that the token is valid and starts with `hf_`

2. **"Model download failed"**
   - Check your internet connection
   - Verify the token has read access
   - Try running: `python test_models.py`

3. **"Authentication failed"**
   - Double-check your token
   - Make sure you copied the entire token
   - Try generating a new token

### Debug Commands

```bash
# Test model loading
python test_models.py

# Check Django configuration
python manage.py check

# View detailed logs
python manage.py runserver --verbosity=2
```

## 📝 Token Security

- **Never commit tokens to version control**
- **Use environment variables in production**
- **Rotate tokens regularly**
- **Use read-only tokens for this application**

## 🚀 Next Steps

Once your token is set up:

1. **Test the search functionality**
2. **Upload some product images**
3. **Try the image similarity search**
4. **Test text recognition with handwritten notes**

## 📞 Support

If you encounter issues:

1. Check the debug endpoint: `/api/debug/models/`
2. Run the test script: `python test_models.py`
3. Check Django logs for detailed error messages
4. Verify your token at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

