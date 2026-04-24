        let users = {
            shopkeepers: [
                { email: "shop1@example.com", password: "shop123", name: "SuperMart", address: "123 Main St" }
            ],
            customers: [
                { email: "customer1@example.com", password: "customer123", name: "John Doe", phone: "9876543210" }
            ],
            delivery: [
                { email: "delivery1@example.com", password: "delivery123", name: "Mike Johnson", vehicle: "bike" }
            ]
        };
        
        let products = [
            { id: 1, shop: "SuperMart", name: "Milk", image: "https://4.imimg.com/data4/JF/JX/MY-9419122/milk-3.jpg", price: 50, quantity: "500ml", description: "Fresh cow milk" },
            { id: 2, shop: "SuperMart", name: "Bread", image: "https://5.imimg.com/data5/TF/EA/MH/SELLER-8764849/fresh-bread-500x500.png", price: 35, quantity: "1 loaf", description: "Whole wheat bread" },
            { id: 3, shop: "SuperMart", name: "Eggs", image: "https://4.imimg.com/data4/IU/DJ/IMOB-16689578/image.jpeg", price: 60, quantity: "12 pieces", description: "Farm fresh eggs" }
        ];
        
        let orders = [];
        let cart = [];
        let currentUser = null;
        let currentRole = null;

        // Removed Dummy location data as it will be fetched from backend
        // const locations = {
        //     "Andhra Pradesh": {
        //         "Guntur": ["Mangalagiri", "Tadepalli", "Guntur East", "Guntur West"],
        //         "Krishna": ["Vijayawada", "Machilipatnam", "Gudivada"]
        //     },
        //     "Telangana": {
        //         "Hyderabad": ["Secunderabad", "Gachibowli", "Jubilee Hills"],
        //         "Warangal": ["Hanamkonda", "Kazipet"]
        //     }
        // };

        // Get references to the HTML elements for homepage location selection
        const stateSelect = document.getElementById('state-select');
        const stateSearch = document.getElementById('state-search');
        const mandalSelect = document.getElementById('mandal-select');
        const mandalSearch = document.getElementById('mandal-search');
        const villageSelect = document.getElementById('village-select');
        const villageSearch = document.getElementById('village-search');

        // Get references to the HTML elements for registration form location selection
        const stateSelectReg = document.getElementById('state-select-reg');
        const stateSearchReg = document.getElementById('state-search-reg');
        const districtSelectReg = document.getElementById('district-select-reg');
        const districtSearchReg = document.getElementById('district-search-reg');
        const mandalSelectReg = document.getElementById('mandal-select-reg');
        const mandalSearchReg = document.getElementById('mandal-search-reg');
        const villageSelectReg = document.getElementById('village-select-reg');
        const villageSearchReg = document.getElementById('village-search-reg');

        // Get references to the new content wrappers
        const locationSelectionWrapper = document.getElementById('location-selection-wrapper');
        const mainContent = document.getElementById('main-content');

        // Function to fetch location data from Django backend
        async function fetchLocationData(type, parentId = null) {
            let url = `/api/${type}/`;
            if (parentId) {
                url += `${parentId}/`;
            }
            console.log(`Attempting to fetch ${type} data from: ${url}`);
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                console.log(`Fetched ${type} data:`, data);
                return data;
            } catch (error) {
                console.error(`Error fetching ${type} data:`, error);
                return [];
            }
        }

        // Function to populate dropdowns (modified to handle objects with id and name)
        function populateDropdown(dropdownElement, data, placeholder) {
            console.log(`Populating dropdown: ${dropdownElement.id} with data:`, data);
            dropdownElement.innerHTML = `<option value="">${placeholder}</option>`;
            if (data.length === 0) {
                console.warn(`No data to populate dropdown: ${dropdownElement.id}`);
                // Removed alert as it can be disruptive
            }
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id;
                option.textContent = item.name;
                dropdownElement.appendChild(option);
            });
        }

        // Function to filter dropdown options based on search input (modified to handle objects)
        function filterDropdown(dropdownElement, searchInputElement, allItems, placeholder) {
            const searchTerm = searchInputElement.value.toLowerCase();
            const filteredItems = allItems.filter(item => 
                item.name.toLowerCase().includes(searchTerm)
            );
            populateDropdown(dropdownElement, filteredItems, placeholder);
            if (searchTerm === '') {
                populateDropdown(dropdownElement, allItems, placeholder);
            }
        }

        // Populate states on page load for homepage location selector (using new fetch function)
        async function initLocationSelectors() {
            console.log('Initializing homepage location selectors...');
            const stateSelect = document.getElementById('state-select');
            if (!stateSelect) {
                console.error('Homepage state dropdown element #state-select not found.');
                return;
            }
            console.log('Homepage state dropdown element found:', stateSelect);

            const states = await fetchLocationData('states');
            populateDropdown(stateSelect, states, 'Select State');
            mandalSelect.disabled = true;
            mandalSearch.disabled = true;
            villageSelect.disabled = true;
            villageSearch.disabled = true;
            locationSelectionWrapper.style.display = 'block'; // Show location selector initially
            mainContent.style.display = 'none'; // Hide main content initially
        }

        // Event listener for state selection (homepage)
        if (stateSelect) stateSelect.addEventListener('change', async () => {
            const selectedStateId = stateSelect.value;
            mandalSelect.innerHTML = '<option value="">Select Mandal</option>';
            mandalSearch.value = '';
            villageSelect.innerHTML = '<option value="">Select Village</option>';
            villageSearch.value = '';

            if (selectedStateId) {
                // Note: The homepage logic currently uses `locations[selectedState]` which is based on dummy data. 
                // This will need to be updated to fetch districts first and then mandals.
                // For now, I'm adapting it to assume a similar structure if it were to fetch districts.
                // This part of the code might need further adjustment once backend API for districts is defined.
                const districts = await fetchLocationData('districts', selectedStateId); 
                // Assuming 'districts' will return data with 'id' and 'name' fields
                populateDropdown(mandalSelect, districts, 'Select Mandal'); // For homepage, treating district as mandal for now.
                mandalSelect.disabled = false;
                mandalSearch.disabled = false;
                villageSelect.disabled = true;
                villageSearch.disabled = true;
            } else {
                mandalSelect.disabled = true;
                mandalSearch.disabled = true;
                villageSelect.disabled = true;
                villageSearch.disabled = true;
            }
        });

        // Event listener for mandal selection (homepage)
        if (mandalSelect) mandalSelect.addEventListener('change', async () => {
            const selectedMandalId = mandalSelect.value;
            villageSelect.innerHTML = '<option value="">Select Village</option>';
            villageSearch.value = '';

            if (selectedMandalId) {
                const villages = await fetchLocationData('villages', selectedMandalId);
                populateDropdown(villageSelect, villages, 'Select Village');
                villageSelect.disabled = false;
                villageSearch.disabled = false;
            } else {
                villageSelect.disabled = true;
                villageSearch.disabled = true;
            }
            mainContent.style.display = 'none';
            locationSelectionWrapper.style.display = 'block';
        });

        // Event listener for village selection (homepage)
        if (villageSelect) villageSelect.addEventListener('change', () => {
            const selectedVillage = villageSelect.value;
            if (selectedVillage) {
                locationSelectionWrapper.style.display = 'none';
                mainContent.style.display = 'block';
            } else {
                locationSelectionWrapper.style.display = 'block';
                mainContent.style.display = 'none';
            }
        });

        // Event listeners for search inputs (homepage)
        if (stateSearch) stateSearch.addEventListener('input', async () => {
            const states = await fetchLocationData('states');
            filterDropdown(stateSelect, stateSearch, states, 'Select State');
        });

        if (mandalSearch) mandalSearch.addEventListener('input', async () => {
            const selectedStateId = stateSelect.value;
            if (selectedStateId) {
                const districts = await fetchLocationData('districts', selectedStateId);
                filterDropdown(mandalSelect, mandalSearch, districts, 'Select Mandal');
            }
        });

        if (villageSearch) villageSearch.addEventListener('input', async () => {
            const selectedMandalId = mandalSelect.value;
            if (selectedMandalId) {
                const villages = await fetchLocationData('villages', selectedMandalId);
                filterDropdown(villageSelect, villageSearch, villages, 'Select Village');
            }
        });

        // --- Registration Form Location Logic ---

        // Populate states on page load for registration form
        async function initRegistrationLocationSelectors() {
            console.log('Initializing registration form location selectors...');
            const stateSelectReg = document.getElementById('state-select-reg');
            if (!stateSelectReg) {
                console.error('Registration state dropdown element #state-select-reg not found.');
                return;
            }
            console.log('Registration state dropdown element found:', stateSelectReg);

            const states = await fetchLocationData('states');
            populateDropdown(stateSelectReg, states, 'Select State');
            districtSelectReg.disabled = true;
            districtSearchReg.disabled = true;
            mandalSelectReg.disabled = true;
            mandalSearchReg.disabled = true;
            villageSelectReg.disabled = true;
            villageSearchReg.disabled = true;
        }

        // Event listener for state selection (registration form)
        if (stateSelectReg) stateSelectReg.addEventListener('change', async () => {
            console.log('State selection changed on registration form.');
            const selectedStateId = stateSelectReg.value;
            districtSelectReg.innerHTML = '<option value="">Select District</option>';
            districtSearchReg.value = '';
            mandalSelectReg.innerHTML = '<option value="">Select Mandal</option>';
            mandalSearchReg.value = '';
            villageSelectReg.innerHTML = '<option value="">Select Village</option>';
            villageSearchReg.value = '';

            if (selectedStateId) {
                const districts = await fetchLocationData('districts', selectedStateId);
                populateDropdown(districtSelectReg, districts, 'Select District');
                districtSelectReg.disabled = false;
                districtSearchReg.disabled = false;
            } else {
                districtSelectReg.disabled = true;
                districtSearchReg.disabled = true;
            }
            mandalSelectReg.disabled = true;
            mandalSearchReg.disabled = true;
            villageSelectReg.disabled = true;
            villageSearchReg.disabled = true;
        });

        // Event listener for district selection (registration form)
        if (districtSelectReg) districtSelectReg.addEventListener('change', async () => {
            const selectedDistrictId = districtSelectReg.value;
            mandalSelectReg.innerHTML = '<option value="">Select Mandal</option>';
            mandalSearchReg.value = '';
            villageSelectReg.innerHTML = '<option value="">Select Village</option>';
            villageSearchReg.value = '';

            if (selectedDistrictId) {
                const mandals = await fetchLocationData('mandals', selectedDistrictId);
                populateDropdown(mandalSelectReg, mandals, 'Select Mandal');
                mandalSelectReg.disabled = false;
                mandalSearchReg.disabled = false;
            } else {
                mandalSelectReg.disabled = true;
                mandalSearchReg.disabled = true;
            }
            villageSelectReg.disabled = true;
            villageSearchReg.disabled = true;
        });

        // Event listener for mandal selection (registration form)
        if (mandalSelectReg) mandalSelectReg.addEventListener('change', async () => {
            const selectedMandalId = mandalSelectReg.value;
            villageSelectReg.innerHTML = '<option value="">Select Village</option>';
            villageSearchReg.value = '';

            if (selectedMandalId) {
                const villages = await fetchLocationData('villages', selectedMandalId);
                populateDropdown(villageSelectReg, villages, 'Select Village');
                villageSelectReg.disabled = false;
                villageSearchReg.disabled = false;
            } else {
                villageSelectReg.disabled = true;
                villageSearchReg.disabled = true;
            }
        });

        // Event listeners for search inputs (registration form)
        if (stateSearchReg) stateSearchReg.addEventListener('input', async () => {
            const states = await fetchLocationData('states');
            filterDropdown(stateSelectReg, stateSearchReg, states, 'Select State');
        });

        if (districtSearchReg) districtSearchReg.addEventListener('input', async () => {
            const selectedStateId = stateSelectReg.value;
            if (selectedStateId) {
                const districts = await fetchLocationData('districts', selectedStateId);
                filterDropdown(districtSelectReg, districtSearchReg, districts, 'Select District');
            }
        });

        if (mandalSearchReg) mandalSearchReg.addEventListener('input', async () => {
            const selectedDistrictId = districtSelectReg.value;
            if (selectedDistrictId) {
                const mandals = await fetchLocationData('mandals', selectedDistrictId);
                filterDropdown(mandalSelectReg, mandalSearchReg, mandals, 'Select Mandal');
            }
        });

        if (villageSearchReg) villageSearchReg.addEventListener('input', async () => {
            const selectedMandalId = mandalSelectReg.value;
            if (selectedMandalId) {
                const villages = await fetchLocationData('villages', selectedMandalId);
                filterDropdown(villageSelectReg, villageSearchReg, villages, 'Select Village');
            }
        });
        
        // Initialize location selectors when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            console.log('DOMContentLoaded event fired.');
            initLocationSelectors(); // For homepage
            initRegistrationLocationSelectors(); // For registration forms
        });
        
        // Function to open login modal
        function openModal(role) {
            document.getElementById(`${role}-modal`).style.display = 'flex';
        }
        
        // Function to open register modal
        function openRegisterModal(role) {
            closeModal(`${role}-modal`);
            document.getElementById(`${role}-register-modal`).style.display = 'flex';
        }
        
        // Function to close modal
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // Close modal when clicking outside of it
        window.onclick = function(event) {
            if (event.target.className === 'login-modal' || event.target.className === 'register-modal') {
                event.target.style.display = 'none';
            }
        }
        
        if (document.getElementById('shopkeeper-register-form')) document.getElementById('shopkeeper-register-form').onsubmit = function(e) {
            // Let the form submit normally to Django backend
            // No need to prevent default or handle client-side
            console.log('Shopkeeper registration form submitting to Django backend');
        };
        
        if (document.getElementById('customer-register-form')) document.getElementById('customer-register-form').onsubmit = function(e) {
            // Let the form submit normally to Django backend
            console.log('Customer registration form submitting to Django backend');
        };
        
        if (document.getElementById('delivery-register-form')) document.getElementById('delivery-register-form').onsubmit = function(e) {
            // Let the form submit normally to Django backend
            console.log('Delivery registration form submitting to Django backend');
        };
        
        // Login form handlers
        if (document.getElementById('shopkeeper-form')) document.getElementById('shopkeeper-form').onsubmit = function(e) {
            e.preventDefault();
            const email = document.getElementById('shopkeeper-email').value;
            const password = document.getElementById('shopkeeper-password').value;
            
            const user = users.shopkeepers.find(u => u.email === email && u.password === password);
            if (user) {
                currentUser = user;
                currentRole = 'shopkeeper';
                showDashboard();
                closeModal('shopkeeper-modal');
                renderShopkeeperDashboard();
            } else {
                alert('Invalid email or password');
            }
        };
        
        if (document.getElementById('customer-form')) document.getElementById('customer-form').onsubmit = function(e) {
            e.preventDefault();
            const email = document.getElementById('customer-email').value;
            const password = document.getElementById('customer-password').value;
            
            const user = users.customers.find(u => u.email === email && u.password === password);
            if (user) {
                currentUser = user;
                currentRole = 'customer';
                showDashboard();
                closeModal('customer-modal');
                renderCustomerDashboard();
            } else {
                alert('Invalid email or password');
            }
        };
        
        if (document.getElementById('delivery-form')) document.getElementById('delivery-form').onsubmit = function(e) {
            e.preventDefault();
            const email = document.getElementById('delivery-email').value;
            const password = document.getElementById('delivery-password').value;
            
            const user = users.delivery.find(u => u.email === email && u.password === password);
            if (user) {
                currentUser = user;
                currentRole = 'delivery';
                showDashboard();
                closeModal('delivery-modal');
                renderDeliveryDashboard();
            } else {
                alert('Invalid email or password');
            }
        };
        function toggleOrders() {
            const ordersSection = document.getElementById('customer-orders-section');
            if (ordersSection.style.display === 'block') {
                ordersSection.style.display = 'none';
            } else {
                ordersSection.style.display = 'block';
                renderCustomerOrders(); // Always refresh orders when shown
            }
        }
        // Show the appropriate dashboard
        function showDashboard() {
            locationSelectionWrapper.style.display = 'none'; // Hide location selector
            mainContent.style.display = 'none'; // Hide main content (role selection)
            document.getElementById(`${currentRole}-dashboard`).style.display = 'block';
        }
        
        // Logout function
        function logout() {
            currentUser = null;
            currentRole = null;
            document.getElementById('main-page').style.display = 'block';
            document.getElementById('shopkeeper-dashboard').style.display = 'none';
            document.getElementById('customer-dashboard').style.display = 'none';
            document.getElementById('delivery-dashboard').style.display = 'none';
        }
        
        // Shopkeeper Dashboard Functions
        function renderShopkeeperDashboard() {
            // Render products
            const productList = document.getElementById('shopkeeper-product-list');
            productList.innerHTML = '';
            
            const shopProducts = products.filter(p => p.shop === currentUser.name);
            if (shopProducts.length === 0) {
                productList.innerHTML = '<p>No products added yet</p>';
            } else {
                shopProducts.forEach(product => {
                    const productCard = document.createElement('div');
                    productCard.className = 'product-card';
                    productCard.innerHTML = `
                        <img src="${product.image}" alt="${product.name}">
                        <h3>${product.name}</h3>
                        <p>₹${product.price}</p>
                        <p>Quantity: ${product.quantity}</p>
                        <p>${product.description}</p>
                    `;
                    productList.appendChild(productCard);
                });
            }
            
            // Render orders
            const orderList = document.getElementById('shopkeeper-order-list');
            orderList.innerHTML = '';

            const shopOrders = orders.filter(o => o.shop === currentUser.name);

            // Active orders (pending or ready)
            const activeOrders = shopOrders.filter(o => o.status === 'pending' || o.status === 'ready');
            if (activeOrders.length === 0) {
                orderList.innerHTML = '<p>No active orders</p>';
            } else {
                activeOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Customer: ${order.customer}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-${order.status}">${order.status}</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                        ${order.status === 'pending' ? `<button class="btn btn-shopkeeper" onclick="updateOrderStatus(${order.id}, 'ready')">Mark as Ready</button>` : ''}
                    `;
                    orderList.appendChild(orderCard);
                });
            }

            // Delivered orders (history)
            const deliveredOrders = shopOrders.filter(o => o.status === 'delivered');
            if (deliveredOrders.length > 0) {
                orderList.innerHTML += '<h3>Delivered Orders</h3>';
                deliveredOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Customer: ${order.customer}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-delivered">delivered</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                    `;
                    orderList.appendChild(orderCard);
                });
            }
        }
                
        // Add product form handler
        if (document.getElementById('add-product-form')) document.getElementById('add-product-form').onsubmit = function(e) {
            e.preventDefault();
            const newProduct = {
                id: products.length + 1,
                shop: currentUser.name,
                name: document.getElementById('product-name').value,
                image: document.getElementById('product-image').value,
                price: parseInt(document.getElementById('product-price').value),
                quantity: parseInt(document.getElementById('product-quantity').value),
                description: document.getElementById('product-description').value
            };
            products.push(newProduct);
            document.getElementById('add-product-form').reset();
            renderShopkeeperDashboard();
            alert('Product added successfully!');
        };

        
        function renderCustomerOrders() {
            const orderList = document.getElementById('customer-order-list');
            orderList.innerHTML = '';

            const customerOrders = orders.filter(o => o.customer === currentUser.name);

            // Active orders (pending or ready)
            const activeOrders = customerOrders.filter(o => o.status === 'pending' || o.status === 'ready');
            if (activeOrders.length === 0) {
                orderList.innerHTML = '<p>No active orders</p>';
            } else {
                activeOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Shop: ${order.shop}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-${order.status}">${order.status}</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                    `;
                    orderList.appendChild(orderCard);
                });
            }

            // Delivered orders (history)
            const deliveredOrders = customerOrders.filter(o => o.status === 'delivered');
            if (deliveredOrders.length > 0) {
                orderList.innerHTML += '<h3>Delivered Orders</h3>';
                deliveredOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Shop: ${order.shop}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-delivered">delivered</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                    `;
                    orderList.appendChild(orderCard);
                });
            }
        }

        // Customer Dashboard Functions
        function renderCustomerDashboard() {
            // Render products
            const productList = document.getElementById('customer-product-list');
            productList.innerHTML = '';
            
            if (products.length === 0) {
                productList.innerHTML = '<p>No products available</p>';
            } else {
                products.forEach(product => {
                    const productCard = document.createElement('div');
                    productCard.className = 'product-card';
                    productCard.innerHTML = `
                        <img src="${product.image}" alt="${product.name}">
                        <h3>${product.name}</h3>
                        <p>₹${product.price}</p>
                        <p>Available: ${product.quantity}</p>
                        <p>${product.description}</p>
                        <button class="btn btn-customer" onclick="addToCart(${product.id})">Add to Cart</button>
                    `;
                    productList.appendChild(productCard);
                });
            }
            
            // Set minimum delivery time (1 hour from now)
            setMinimumDeliveryTime();
            
            // Render cart
            renderCart();
            updateCartCount();
            renderCustomerOrders();
        }
        
        // Add to cart function
        function addToCart(productId) {
            const product = products.find(p => p.id === productId);
            if (!product) {
                alert('Product not found!');
                return;
            }

            const existingItem = cart.find(item => item.id === productId);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                cart.push({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    quantity: 1,  // Starting quantity is 1
                    shop: product.shop,
                    unit: product.quantity, // This is the product's available quantity/unit
                    image: product.image    // Add image for cart display
                });
            }

            updateCartCount();
            renderCart();
            alert(`${product.name} added to cart!`);
        }
        
        // Update cart count in header
        function updateCartCount() {
            const cartCount = document.getElementById('cart-count');
            if (cartCount) {
                const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
                cartCount.textContent = totalItems;
            }
        }
        
        // Toggle cart visibility
        function toggleCart() {
            const cartModal = document.getElementById('cart-modal');
            cartModal.style.display = cartModal.style.display === 'block' ? 'none' : 'block';
        }
        
        // Set minimum delivery time (1 hour from now)
        function setMinimumDeliveryTime() {
            const deliveryTimeInput = document.getElementById('delivery-time');
            if (deliveryTimeInput) {
                const now = new Date();
                const oneHourLater = new Date(now.getTime() + (60 * 60 * 1000)); // Add 1 hour
                
                // Format the datetime for the input field
                const year = oneHourLater.getFullYear();
                const month = String(oneHourLater.getMonth() + 1).padStart(2, '0');
                const day = String(oneHourLater.getDate()).padStart(2, '0');
                const hours = String(oneHourLater.getHours()).padStart(2, '0');
                const minutes = String(oneHourLater.getMinutes()).padStart(2, '0');
                
                const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
                deliveryTimeInput.min = minDateTime;
                deliveryTimeInput.value = minDateTime;
            }
        }
        
        // Remove from cart function
        function removeFromCart(productId) {
            const itemIndex = cart.findIndex(item => item.id === productId);
            if (itemIndex !== -1) {
                cart.splice(itemIndex, 1);
                updateCartCount();
                renderCart();
            }
        }
        
        // Place order form handler (keep only ONE!)
        if (document.getElementById('place-order-form')) document.getElementById('place-order-form').onsubmit = function(e) {
            e.preventDefault();
            if (cart.length === 0) {
                alert('Your cart is empty!');
                return;
            }
            
            const newOrder = {
                id: orders.length + 1,
                customer: currentUser.name,
                shop: cart[0].shop, // Assuming all items are from same shop for simplicity
                items: [...cart],
                deliveryAddress: document.getElementById('delivery-address').value,
                deliveryPhone: document.getElementById('delivery-phone').value,
                deliveryTime: document.getElementById('delivery-time').value,
                status: 'pending',
                date: new Date().toISOString()
            };
            
            orders.push(newOrder);
            cart = [];
            document.getElementById('place-order-form').reset();
            updateCartCount();
            renderCart();
            alert('Order placed successfully!');
            renderCustomerOrders();           // <-- Show in customer dashboard
            renderShopkeeperDashboard();
            if (currentRole === 'delivery') renderDeliveryDashboard();
        };

        // Update order status
        function updateOrderStatus(orderId, status) {
            const orderIndex = orders.findIndex(o => o.id === orderId);
            if (orderIndex !== -1) {
                orders[orderIndex].status = status;
                renderShopkeeperDashboard();
                renderDeliveryDashboard();
                
            }
        }

        // Render cart
        function renderCart() {
            const cartItems = document.getElementById('cart-items');
            const emptyCartMessage = document.getElementById('empty-cart-message');
            const cartTotal = document.getElementById('cart-total');

            // Remove all cart-item elements
            cartItems.querySelectorAll('.cart-item').forEach(el => el.remove());

            if (cart.length === 0) {
                emptyCartMessage.style.display = 'block';
                cartTotal.textContent = '';
            } else {
                emptyCartMessage.style.display = 'none';

                cart.forEach(item => {
                    const cartItem = document.createElement('div');
                    cartItem.className = 'cart-item';
                    cartItem.innerHTML = `
                        <img src="${item.image}" alt="${item.name}">
                        <div class="cart-item-info">
                            <h4>${item.name}</h4>
                            <p>${item.unit}</p>
                            <p>₹${item.price} × ${item.quantity} = ₹${item.price * item.quantity}</p>
                            <button class="remove-item" onclick="removeFromCart(${item.id})">Remove</button>
                        </div>
                    `;
                    cartItems.appendChild(cartItem);
                });

                const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
                cartTotal.textContent = `Total: ₹${total}`;
            }
        }
        

        
        // Place order form handler
        if (document.getElementById('place-order-form')) document.getElementById('place-order-form').onsubmit = function(e) {
            e.preventDefault();
            if (cart.length === 0) {
                alert('Your cart is empty!');
                return;
            }
            
            const newOrder = {
                id: orders.length + 1,
                customer: currentUser.name,
                shop: cart[0].shop, // Assuming all items are from same shop for simplicity
                items: [...cart],
                deliveryAddress: document.getElementById('delivery-address').value,
                deliveryPhone: document.getElementById('delivery-phone').value,
                deliveryTime: document.getElementById('delivery-time').value,
                status: 'pending',
                date: new Date().toISOString()
            };
            
            orders.push(newOrder);
            cart = [];
            document.getElementById('place-order-form').reset();
            updateCartCount();
            renderCart();
            alert('Order placed successfully!');
            renderCustomerOrders();           // Customer dashboard
            renderShopkeeperDashboard();      // Shopkeeper dashboard
            renderDeliveryDashboard();        // Delivery dashboard
        };


        // Delivery Dashboard Functions
        function renderDeliveryDashboard() {
            const orderList = document.getElementById('delivery-order-list');
            orderList.innerHTML = '';

            // Show orders that are pending or ready
            const deliveryOrders = orders.filter(o => o.status === 'pending' || o.status === 'ready');
            if (deliveryOrders.length === 0) {
                orderList.innerHTML = '<p>No orders to deliver</p>';
            } else {
                deliveryOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Shop: ${order.shop}</p>
                        <p>Customer: ${order.customer}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-${order.status}">${order.status}</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                        ${order.status === 'ready' ? `<button class="btn btn-delivery" onclick="updateOrderStatus(${order.id}, 'delivered')">Mark as Delivered</button>` : ''}
                    `;
                    orderList.appendChild(orderCard);
                });
            }

            // Show delivered orders (history)
            const deliveredOrders = orders.filter(o => o.status === 'delivered');
            if (deliveredOrders.length > 0) {
                orderList.innerHTML += '<h3>Delivered Orders</h3>';
                deliveredOrders.forEach(order => {
                    const orderCard = document.createElement('div');
                    orderCard.className = 'order-card';
                    orderCard.innerHTML = `
                        <h3>Order #${order.id}</h3>
                        <p>Shop: ${order.shop}</p>
                        <p>Customer: ${order.customer}</p>
                        <p>Delivery Address: ${order.deliveryAddress}</p>
                        <p>Delivery Time: ${new Date(order.deliveryTime).toLocaleString()}</p>
                        <p>Status: <span class="status-btn status-${order.status}">${order.status}</span></p>
                        <p>Items: ${order.items.map(item => `${item.name} (${item.quantity})`).join(', ')}</p>
                    `;
                    orderList.appendChild(orderCard);
                });
            }
        }
        
        // Product search functionality
        if (document.getElementById('product-search')) document.getElementById('product-search').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const filteredProducts = products.filter(product => 
                product.name.toLowerCase().includes(searchTerm) || 
                product.description.toLowerCase().includes(searchTerm)
            );
            
            const productList = document.getElementById('customer-product-list');
            productList.innerHTML = '';
            
            if (filteredProducts.length === 0) {
                productList.innerHTML = '<p>No products found</p>';
            } else {
                filteredProducts.forEach(product => {
                    const productCard = document.createElement('div');
                    productCard.className = 'product-card';
                    productCard.innerHTML = `
                        <img src="${product.image}" alt="${product.name}">
                        <h3>${product.name}</h3>
                        <p>₹${product.price}</p>
                        <p>Available: ${product.quantity}</p>
                        <p>${product.description}</p>
                        <button class="btn btn-customer" onclick="addToCart(${product.id})">Add to Cart</button>
                    `;
                    productList.appendChild(productCard);
                });
            }
        });