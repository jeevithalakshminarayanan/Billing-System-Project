document.addEventListener('DOMContentLoaded', function() {
    // Load products when the page loads
    if (document.getElementById('productList')) {
        loadProducts();
    }

    // Add event listeners
    const addProductBtn = document.getElementById('addProduct');
    if (addProductBtn) {
        addProductBtn.addEventListener('click', addProductField);
    }

    const generateBillBtn = document.getElementById('generateBill');
    if (generateBillBtn) {
        generateBillBtn.addEventListener('click', generateBill);
    }

    const viewPreviousBtn = document.getElementById('viewPrevious');
    if (viewPreviousBtn) {
        viewPreviousBtn.addEventListener('click', viewPreviousBills);
    }
});

async function loadProducts() {
    try {
        const response = await fetch('/api/products/');
        const products = await response.json();

        // Update all product select dropdowns
        const productSelects = document.querySelectorAll('.product-select');
        productSelects.forEach(select => {
            select.innerHTML = '<option value="">Select Product</option>';
            products.forEach(product => {
                // product object uses product_id as the key in mock data
                const pid = product.product_id || product.productId || product.id;
                const stock = product.available_stock ?? product.availableStock ?? '';
                const price = product.price ?? product.unit_price ?? '';
                select.innerHTML += `
                    <option value="${pid}">
                        ${product.name} - ₹${price} (Stock: ${stock})
                    </option>`;
            });
        });
    } catch (error) {
        console.error('Error loading products:', error);
    }
}

function addProductField() {
    const productList = document.getElementById('productList');
    const productItem = document.createElement('div');
    productItem.className = 'product-item';
    productItem.innerHTML = `
        <select class="product-select">
            <option value="">Select Product</option>
        </select>
        <input type="number" class="quantity-input" min="1" value="1">
        <button class="remove-product">Remove</button>
    `;

    // Add remove event listener
    const removeBtn = productItem.querySelector('.remove-product');
    removeBtn.addEventListener('click', () => productItem.remove());

    productList.appendChild(productItem);
    loadProducts();  // Reload products for the new select
}

async function generateBill() {
    const customerEmail = document.getElementById('customerEmail').value;
    if (!customerEmail) {
        alert('Please enter customer email');
        return;
    }

    const items = [];
    const productItems = document.querySelectorAll('.product-item');
    
    productItems.forEach(item => {
        const productId = item.querySelector('.product-select').value;
        const quantity = item.querySelector('.quantity-input').value;
        
        if (productId && quantity) {
            items.push({
                product_id: productId.toString(),
                quantity: parseInt(quantity)
            });
        }
    });

    if (items.length === 0) {
        alert('Please add at least one product');
        return;
    }

    try {
        // collect denominations BEFORE posting
        const denominationInputs = document.querySelectorAll('.denomination-item input');
        let totalPaid = 0;
        const denominationBreakdown = {};
        denominationInputs.forEach(input => {
            const value = parseInt(input.dataset.value);
            const count = parseInt(input.value) || 0;
            if (count > 0) {
                denominationBreakdown[value] = count;
                totalPaid += value * count;
            }
        });

        const response = await fetch('/api/bills/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                customer_email: customerEmail,
                items: items,
                denominations: denominationBreakdown
            })
        });

        if (response.ok) {
            const bill = await response.json();
            // Store bill data and denomination breakdown in sessionStorage
            sessionStorage.setItem('currentBill', JSON.stringify(bill));
            sessionStorage.setItem('denominationBreakdown', JSON.stringify({
                breakdown: denominationBreakdown,
                totalPaid: totalPaid
            }));

            // Redirect to bill page
            window.location.href = '/bill';
        } else {
            const error = await response.json();
            alert(error.detail || 'Error generating bill');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating bill');
    }
}

async function viewPreviousBills() {
    const customerEmail = document.getElementById('customerEmail').value;
    if (!customerEmail) {
        alert('Please enter customer email to view previous bills');
        return;
    }

    try {
        const response = await fetch(`/api/bills/${encodeURIComponent(customerEmail)}`);
        const bills = await response.json();
        
        if (bills.length === 0) {
            alert('No previous bills found for this customer');
            return;
        }

        // Display bills in a modal or new window
        const billsWindow = window.open('', 'Previous Bills', 'width=800,height=600');
        billsWindow.document.write(`
            <html>
                <head>
                    <title>Previous Bills</title>
                    <link href="/static/css/styles.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container">
                        <h1>Previous Bills for ${customerEmail}</h1>
                        ${bills.map(bill => `
                            <div class="bill-details" style="margin-bottom: 20px;">
                                <p>Date: ${new Date(bill.created_at).toLocaleString()}</p>
                                <p>Total Amount: ₹${bill.total_amount}</p>
                                <p>Tax Amount: ₹${bill.tax_amount}</p>
                                <p>Final Amount: ₹${bill.final_amount}</p>
                            </div>
                        `).join('')}
                    </div>
                </body>
            </html>
        `);
    } catch (error) {
        console.error('Error:', error);
        alert('Error fetching previous bills');
    }
}

// For bill.html page
if (window.location.pathname === '/bill') {
    const bill = JSON.parse(sessionStorage.getItem('currentBill'));
    const denominationData = JSON.parse(sessionStorage.getItem('denominationBreakdown'));

    if (bill) {
        document.getElementById('customerEmail').textContent = bill.customer_email;
        document.getElementById('billDate').textContent = new Date(bill.created_at).toLocaleString();
        document.getElementById('totalAmount').textContent = `₹${bill.total_amount}`;
        document.getElementById('taxAmount').textContent = `₹${bill.tax_amount}`;
        document.getElementById('finalAmount').textContent = `₹${bill.final_amount}`;

        // Populate bill items
        const billItemsTable = document.getElementById('billItems');
        bill.items.forEach(item => {
            const row = billItemsTable.insertRow();
            row.innerHTML = `
                <td>${item.product_id}</td>
                <td>${item.name}</td>
                <td>${item.quantity}</td>
                <td>₹${item.unit_price}</td>
                <td>₹${item.tax_amount}</td>
                <td>₹${item.total}</td>
            `;
        });

        // Show denomination breakdown
        const denominationBreakdown = document.getElementById('denominationBreakdown');
        if (denominationData) {
            let breakdownHtml = '<table class="denomination-breakdown">';
            breakdownHtml += '<tr><th>Denomination</th><th>Count</th><th>Total</th></tr>';
            
            Object.entries(denominationData.breakdown).forEach(([value, count]) => {
                breakdownHtml += `
                    <tr>
                        <td>₹${value}</td>
                        <td>${count}</td>
                        <td>₹${value * count}</td>
                    </tr>
                `;
            });
            
            breakdownHtml += '</table>';
            denominationBreakdown.innerHTML = breakdownHtml;

            // Calculate and show balance
            const balance = denominationData.totalPaid - bill.final_amount;
            document.getElementById('balanceAmount').textContent = 
                balance >= 0 ? `₹${balance} (Change)` : `₹${Math.abs(balance)} (Due)`;
        }
    } else {
        window.location.href = '/';  // Redirect to home if no bill data
    }
}