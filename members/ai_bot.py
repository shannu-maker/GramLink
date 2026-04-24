import os
import threading
from typing import List, Optional

# Lazy state
_model_lock = threading.Lock()
_model = None
_default_gen_model = os.environ.get('AI_TEXT_GEN_MODEL', 'distilgpt2')


def _load_pipeline_optional():
	"""Try to load a local transformers pipeline if libs are installed; otherwise None."""
	global _model
	with _model_lock:
		if _model is not None:
			return _model
		try:
			from transformers import pipeline  # type: ignore
			_model = pipeline('text-generation', model=_default_gen_model, device=-1)
			return _model
		except Exception:
			_model = None
			return None


def _hf_generate(prompt: str) -> Optional[str]:
	"""Call Hugging Face Inference API if HF_API_TOKEN is set. Returns text or None."""
	hf_token = os.environ.get('HF_API_TOKEN') or os.environ.get('HUGGINGFACEHUB_API_TOKEN')
	if not hf_token:
		return None
	model_id = os.environ.get('HF_MODEL_ID', 'google/gemma-2-2b-it')
	api_url = f"https://api-inference.huggingface.co/models/{model_id}"
	payload = {
		"inputs": prompt,
		"parameters": {"max_new_tokens": 120, "temperature": 0.7, "top_p": 0.9},
	}
	try:
		import requests  # type: ignore
		headers = {"Authorization": f"Bearer {hf_token}", "Accept": "application/json"}
		resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
		resp.raise_for_status()
		data = resp.json()
		if isinstance(data, list) and data and isinstance(data[0], dict):
			gen = data[0].get('generated_text')
			if isinstance(gen, str) and gen:
				return gen[len(prompt):].strip() or gen.strip()
			for key in ('summary_text', 'text'):
				if key in data[0] and isinstance(data[0][key], str):
					return data[0][key].strip()
		elif isinstance(data, dict):
			for key in ('generated_text', 'summary_text', 'text'):
				val = data.get(key)
				if isinstance(val, str) and val:
					return val.strip()
		return None
	except Exception:
		return None


def _intent_reply(prompt: str) -> Optional[str]:
	"""Deterministic, domain-aware replies for common intents like login/register/browse/open dashboard."""
	p = (prompt or '').strip().lower()
	if not p:
		return None

	def _has(*words: str) -> bool:
		return all(w in p for w in words)

	# Role detection
	role = None
	if 'shopkeeper' in p:
		role = 'shopkeeper'
	elif 'delivery' in p:
		role = 'delivery'
	elif 'customer' in p:
		role = 'customer'

	# Login
	if any(w in p for w in ['login', 'log in', 'sign in']):
		if role == 'shopkeeper':
			return "To login as Shopkeeper, click the Shopkeeper button, then Login. I can also start a step-by-step login here: say 'shopkeeper login'."
		if role == 'delivery':
			return "To login as Delivery Partner, click the Delivery button, then Login. I can also start step-by-step login: say 'delivery login'."
		if role == 'customer':
			return "To login as Customer, click the Customer button, then Login. I can also start step-by-step login: say 'customer login'."
		return "Who would you like to login as: Shopkeeper, Customer, or Delivery? You can say 'shopkeeper login', 'customer login', or 'delivery login'."

	# Register
	if any(w in p for w in ['register', 'sign up', 'create account']):
		if role == 'shopkeeper':
			return "To register a Shop, click Shopkeeper → Register. I can also create your account step-by-step: say 'shopkeeper register'."
		if role == 'delivery':
			return "To register as Delivery Partner, click Delivery → Register. I can also create your account step-by-step: say 'delivery register'."
		if role == 'customer':
			return "To register as Customer, click Customer → Register. I can also create your account step-by-step: say 'customer register'."
		return "Who would you like to register as: Shopkeeper, Customer, or Delivery? Say 'shopkeeper register', 'customer register', or 'delivery register'."

	# Open dashboard
	if any(w in p for w in ['dashboard', 'open dashboard', 'my dashboard']):
		if role == 'shopkeeper':
			return "Opening the Shopkeeper dashboard. If it doesn't open automatically, click Shopkeeper → Dashboard. You can also say 'view products' or 'view orders'."
		if role == 'delivery':
			return "Opening the Delivery dashboard. If it doesn't open automatically, click Delivery → Dashboard."
		if role == 'customer':
			return "Opening the Customer dashboard. If it doesn't open automatically, click Customer → Browse Products."
		return "Which dashboard should I open: Shopkeeper, Customer, or Delivery?"

	# Browse products (customer-side discovery)
	if any(_has(w) for w in [('browse', 'products'), ('show', 'products'), ('find', 'products')]) or 'browse products' in p or 'products' in p:
		return "You can browse products from the Customer menu or by saying 'customer dashboard'. I can also list product names — try 'search rice' or 'search oil'."

	# Orders intents
	if 'orders' in p or _has('view', 'orders'):
		if role == 'shopkeeper':
			return "Opening shopkeeper orders. If you are on the dashboard, the bot can open the Orders modal automatically — say 'view orders'."
		if role == 'customer':
			return "You can view your orders at Customer → Orders. Say 'customer orders' to navigate."
		if role == 'delivery':
			return "Go to Delivery → Dashboard to see available/assigned orders."
		return "Do you want Shopkeeper orders or Customer orders?"

	# Fallback for other help requests
	if any(w in p for w in ['help', 'assist', 'support']):
		return "I can help you login/register, open dashboards, browse products, and view orders. Tell me your role (Shopkeeper/Customer/Delivery) and what you want to do."

	return None


def generate_ai_reply(messages: List[dict]) -> str:
	"""Generate a reply given a chat history. Prefers local pipeline; falls back to HF API; then rules.
	Also includes deterministic intent handling so common UX requests are always answered well."""
	user_texts = [m['content'] for m in messages if m.get('role') == 'user']
	prompt = user_texts[-1] if user_texts else ''

	# 0) Intent handler first – ensures consistent UX answers
	intent_text = _intent_reply(prompt)
	if intent_text:
		return intent_text

	# 1) Try local transformers pipeline if available
	pipe = _load_pipeline_optional()
	if pipe is not None and prompt:
		try:
			out = pipe(prompt, max_new_tokens=100, do_sample=True, top_p=0.9, temperature=0.7, num_return_sequences=1)
			text = out[0].get('generated_text', '') if isinstance(out, list) else ''
			return (text[len(prompt):].strip() or text.strip() or _rule_fallback(prompt))
		except Exception:
			pass

	# 2) Try hosted Hugging Face Inference API if token present
	if prompt:
		gen = _hf_generate(prompt)
		if gen:
			return gen

	# 3) Rule-based fallback
	return _rule_fallback(prompt)


def _rule_fallback(prompt: str) -> str:
	if not prompt:
		return "Hi! I'm your AI assistant for Gram Connect. I can help you with shopping, managing your shop, delivery, orders, payments, and much more. What would you like to know?"
	
	lower = prompt.lower()
	
	# Project-specific knowledge and context
	if any(k in lower for k in ['what is gram connect', 'about gram connect', 'tell me about this platform']):
		return """Gram Connect is a comprehensive e-commerce platform that connects three key stakeholders:

🛒 **Customers**: Browse and purchase products from local shops
🏪 **Shopkeepers**: Manage their inventory, track orders, and grow their business  
🚚 **Delivery Partners**: Pick up and deliver orders to customers

**Key Features:**
• Real-time order tracking
• Price history analysis for smart shopping
• Multi-role dashboard system
• Secure payment processing
• AI-powered shopping assistance

I'm here to help you navigate and make the most of our platform! What specific aspect interests you?"""

	# Shopping and product queries
	if any(k in lower for k in ['shop', 'buy', 'purchase', 'product', 'item']):
		if 'price' in lower or 'cost' in lower:
			return """Great question about pricing! Here's what you should know:

💰 **Pricing Features:**
• Real-time price tracking
• Price history analysis (click the 📊 button on any product)
• Smart buying recommendations
• Compare prices across different shops

💡 **Pro Tips:**
• Use the price history feature to see if it's a good time to buy
• Check multiple shops for the best deals
• Look for products trending down in price

Would you like me to help you find specific products or explain how price tracking works?"""
		else:
			return """Shopping on Gram Connect is easy and smart! Here's how:

🛍️ **How to Shop:**
1. Go to Customer Dashboard
2. Browse products by category or search
3. Use the price history feature (📊) to check if it's a good deal
4. Add to cart and checkout
5. Track your order in real-time

🔍 **Smart Features:**
• Search by product name or shop
• View shop-wise or all products
• Price comparison and history
• AI recommendations

What type of products are you looking for? I can help you find the best deals!"""

	# Order tracking and management
	if any(k in lower for k in ['order','track','delivery','shipping', 'status']):
		return """I can help you with orders! Here's everything about order management:

📦 **For Customers:**
• View all your orders in Customer Dashboard → Orders
• Real-time status updates (Pending → Confirmed → Ready → Out for Delivery → Delivered)
• Track delivery progress
• Contact support for order issues

🏪 **For Shopkeepers:**
• Manage incoming orders in your dashboard
• Update order status
• View order details and customer info
• Print order summaries

🚚 **For Delivery Partners:**
• See available orders to accept
• Update delivery status
• Navigate to delivery locations

**Order Status Flow:**
Pending → Confirmed → Ready → Assigned → Out for Delivery → Delivered

Need help with a specific order? Tell me your role and I'll guide you!"""

	# Payment and billing
	if any(k in lower for k in ['pay','payment','card','upi','wallet', 'billing', 'cost']):
		return """Payment options on Gram Connect are flexible and secure:

💳 **Payment Methods:**
• **Cash on Delivery (COD)** - Pay when you receive your order
• **Online Payment** - Secure card/UPI payments
• **Digital Wallets** - Quick and easy payments

🔒 **Security Features:**
• Encrypted payment processing
• Secure checkout process
• Payment verification
• Fraud protection

💰 **Pricing Transparency:**
• No hidden fees
• Clear order breakdown
• Real-time price updates
• Price history tracking

**Pro Tip:** Use the price history feature to ensure you're getting the best deal before checkout!

Need help with a specific payment issue or want to know about pricing strategies?"""

	# Returns and support
	if any(k in lower for k in ['return','refund','exchange', 'problem', 'issue', 'help']):
		return """I'm here to help resolve any issues! Here's our support system:

🔄 **Returns & Refunds:**
• 7-14 day return window for most items
• Easy return process through your order history
• Full refund for defective items
• Exchange options available

🛠️ **Getting Help:**
• **AI Assistant** (that's me!) - Available 24/7
• **Order Support** - Contact through order details
• **Technical Issues** - Use the debug modal in your dashboard
• **General Questions** - Just ask me anything!

📞 **Support Channels:**
• In-app chat (this conversation)
• Order-specific support
• Technical assistance
• Feature explanations

**What I can help with:**
• Navigation and features
• Order tracking
• Payment issues
• Account management
• Platform guidance

What specific issue are you facing? I'll provide step-by-step help!"""

	# Technical and platform questions
	if any(k in lower for k in ['how to', 'how do i', 'tutorial', 'guide', 'learn']):
		return """I'd love to teach you how to use Gram Connect effectively! Here are some popular guides:

🎯 **Quick Start Guides:**
• **New Customer?** → Register → Browse Products → Add to Cart → Checkout
• **New Shopkeeper?** → Register → Add Products → Manage Orders → Track Sales
• **New Delivery Partner?** → Register → Accept Orders → Update Status → Earn Money

📚 **Feature Tutorials:**
• **Price History** - Click 📊 on any product to see price trends and get buying recommendations
• **Smart Shopping** - Use search filters and compare prices across shops
• **Order Management** - Track orders from placement to delivery
• **Dashboard Navigation** - Access all features from your role-specific dashboard

🔧 **Advanced Features:**
• **AI Shopping Assistant** - Get personalized recommendations
• **Voice Commands** - Use voice input for hands-free interaction
• **Real-time Updates** - Get instant notifications on order status

**Which role are you and what would you like to learn?** I can provide detailed, step-by-step instructions!"""

	# General conversation and greetings
	if any(k in lower for k in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
		import datetime
		hour = datetime.datetime.now().hour
		greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
		return f"""{greeting}! I'm your AI assistant for Gram Connect. 

I'm here to help you with:
🛒 Shopping and product discovery
📦 Order tracking and management  
💳 Payment and billing questions
🏪 Shop management (for shopkeepers)
🚚 Delivery coordination (for delivery partners)
📊 Price analysis and recommendations
🔧 Technical support and guidance

What can I help you with today? Feel free to ask me anything about our platform!"""

	# Default intelligent response
	return f"""I understand you're asking about "{prompt}". Let me help you with that!

As your AI assistant for Gram Connect, I can help with:

🎯 **Specific Help:**
• Shopping guidance and product recommendations
• Order tracking and management
• Payment and billing support
• Platform navigation and features
• Technical troubleshooting

💡 **Smart Features I Can Explain:**
• Price history analysis and buying recommendations
• Multi-role dashboard functionality
• Real-time order tracking
• AI-powered shopping assistance
• Voice commands and accessibility

**To give you the best help, could you tell me:**
1. What's your role? (Customer/Shopkeeper/Delivery Partner)
2. What specific task are you trying to accomplish?
3. Are you experiencing any issues?

I'm here to provide personalized, step-by-step assistance!"""
