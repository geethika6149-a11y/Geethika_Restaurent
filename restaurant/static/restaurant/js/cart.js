/**
 * GourmetOS Restaurant - Dynamic Shopping Cart & UI Controller
 * Manages localStorage, Django Session Cart sync, and dynamic UI updates.
 */

class RestaurantCart {
    constructor() {
        this.storageKey = 'gourmet_cart_v1';
        this.cart = this.loadCart();
        this.taxRate = 0.05; // 5%
        this.init();
    }

    loadCart() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : {};
        } catch (e) {
            console.error("Error loading cart from localStorage", e);
            return {};
        }
    }

    saveCart() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.cart));
        } catch (e) {
            console.error("Error saving cart to localStorage", e);
        }
    }

    init() {
        this.bindEvents();
        this.updateUI();
        this.syncWithServer();
    }

    bindEvents() {
        // Event delegation for "Add to Cart" and Quantity steppers
        document.addEventListener('click', (e) => {
            const addBtn = e.target.closest('.btn-add-to-cart');
            if (addBtn) {
                const itemId = addBtn.dataset.itemId;
                const name = addBtn.dataset.name;
                const price = parseFloat(addBtn.dataset.price);
                const image = addBtn.dataset.image;
                const qtyInput = document.getElementById(`qty-input-${itemId}`);
                const qty = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;
                this.addItem(itemId, name, price, image, qty);
                return;
            }

            const stepBtn = e.target.closest('.qty-step-btn');
            if (stepBtn) {
                const itemId = stepBtn.dataset.itemId;
                const action = stepBtn.dataset.action;
                const input = document.getElementById(`qty-input-${itemId}`);
                if (input) {
                    let cur = parseInt(input.value, 10) || 1;
                    if (action === 'plus') cur++;
                    if (action === 'minus' && cur > 1) cur--;
                    input.value = cur;
                }
            }

            const drawerRemoveBtn = e.target.closest('.btn-drawer-remove');
            if (drawerRemoveBtn) {
                const itemId = drawerRemoveBtn.dataset.itemId;
                this.removeItem(itemId);
            }

            const drawerStepBtn = e.target.closest('.drawer-qty-btn');
            if (drawerStepBtn) {
                const itemId = drawerStepBtn.dataset.itemId;
                const action = drawerStepBtn.dataset.action;
                this.changeQuantity(itemId, action === 'plus' ? 1 : -1);
            }
        });
    }

    addItem(id, name, price, image, quantity = 1) {
        if (!this.cart[id]) {
            this.cart[id] = {
                id: id,
                name: name,
                price: price,
                image: image,
                quantity: 0
            };
        }
        this.cart[id].quantity += quantity;
        this.saveCart();
        this.updateUI();
        this.showToast(`Added ${quantity}x "${name}" to your order!`);
        this.syncItemToServer(id, 'add', quantity);
    }

    changeQuantity(id, delta) {
        if (!this.cart[id]) return;
        this.cart[id].quantity += delta;
        if (this.cart[id].quantity <= 0) {
            delete this.cart[id];
            this.syncItemToServer(id, 'remove', 0);
        } else {
            this.syncItemToServer(id, 'set', this.cart[id].quantity);
        }
        this.saveCart();
        this.updateUI();
    }

    removeItem(id) {
        if (this.cart[id]) {
            const name = this.cart[id].name;
            delete this.cart[id];
            this.saveCart();
            this.updateUI();
            this.showToast(`Removed "${name}" from order.`);
            this.syncItemToServer(id, 'remove', 0);
        }
    }

    clearCart() {
        this.cart = {};
        this.saveCart();
        this.updateUI();
    }

    calculateTotals() {
        let subtotal = 0;
        let count = 0;
        for (const id in this.cart) {
            const item = this.cart[id];
            subtotal += item.price * item.quantity;
            count += item.quantity;
        }
        const tax = Math.round(subtotal * this.taxRate * 100) / 100;
        const total = subtotal + tax;

        return {
            count,
            subtotal: subtotal.toFixed(2),
            tax: tax.toFixed(2),
            total: total.toFixed(2)
        };
    }

    updateUI() {
        const totals = this.calculateTotals();

        // Update badge counters
        const globalBadges = document.querySelectorAll('#globalCartBadge, .cart-count-badge');
        globalBadges.forEach(b => {
            b.textContent = totals.count;
            if (totals.count > 0) {
                b.classList.add('bg-white', 'text-dark');
                b.classList.remove('bg-secondary');
            } else {
                b.classList.remove('bg-white', 'text-dark');
                b.classList.add('bg-secondary');
            }
        });

        // Update Offcanvas Drawer
        const itemsContainer = document.getElementById('drawerCartItems');
        const emptyState = document.getElementById('drawerCartEmpty');
        const subtotalEl = document.getElementById('drawerSubtotal');
        const taxEl = document.getElementById('drawerTax');
        const totalEl = document.getElementById('drawerGrandTotal');
        const checkoutBtn = document.getElementById('drawerBtnCheckout');

        if (subtotalEl) subtotalEl.textContent = `$${totals.subtotal}`;
        if (taxEl) taxEl.textContent = `$${totals.tax}`;
        if (totalEl) totalEl.textContent = `$${totals.total}`;

        if (totals.count === 0) {
            if (emptyState) emptyState.classList.remove('d-none');
            if (itemsContainer) itemsContainer.innerHTML = '';
            if (checkoutBtn) checkoutBtn.classList.add('disabled');
        } else {
            if (emptyState) emptyState.classList.add('d-none');
            if (checkoutBtn) checkoutBtn.classList.remove('disabled');

            if (itemsContainer) {
                let html = '';
                for (const id in this.cart) {
                    const item = this.cart[id];
                    const itemTotal = (item.price * item.quantity).toFixed(2);
                    html += `
                        <div class="card mb-2 border-0 bg-light p-2 rounded-3 shadow-none">
                            <div class="d-flex align-items-center gap-2">
                                <img src="${item.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=150&q=80'}" alt="${item.name}" class="rounded-2" style="width: 50px; height: 50px; object-fit: cover;">
                                <div class="flex-grow-1 min-w-0">
                                    <div class="fw-bold text-truncate small">${item.name}</div>
                                    <div class="text-muted small">$${item.price.toFixed(2)} each</div>
                                </div>
                                <div class="d-flex flex-column align-items-end">
                                    <span class="fw-bold text-dark small mb-1">$${itemTotal}</span>
                                    <div class="d-flex align-items-center gap-1">
                                        <button class="btn btn-sm btn-white border px-1 py-0 drawer-qty-btn" data-item-id="${item.id}" data-action="minus"><i class="bi bi-dash"></i></button>
                                        <span class="px-2 small fw-bold">${item.quantity}</span>
                                        <button class="btn btn-sm btn-white border px-1 py-0 drawer-qty-btn" data-item-id="${item.id}" data-action="plus"><i class="bi bi-plus"></i></button>
                                        <button class="btn btn-sm btn-link text-danger p-0 ms-1 btn-drawer-remove" data-item-id="${item.id}" title="Remove"><i class="bi bi-trash"></i></button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }
                itemsContainer.innerHTML = html;
            }
        }
    }

    async syncItemToServer(itemId, action, quantity) {
        if (!window.CART_UPDATE_URL) return;
        try {
            await fetch(window.CART_UPDATE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.CSRF_TOKEN || ''
                },
                body: JSON.stringify({ item_id: itemId, action: action, quantity: quantity })
            });
        } catch (e) {
            console.warn("Could not sync item with server session", e);
        }
    }

    async syncWithServer() {
        if (!window.CART_SYNC_URL) return;
        // Build map of item_id -> quantity
        const cartPayload = {};
        for (const id in this.cart) {
            cartPayload[id] = this.cart[id].quantity;
        }

        try {
            const resp = await fetch(window.CART_SYNC_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.CSRF_TOKEN || ''
                },
                body: JSON.stringify({ cart: cartPayload })
            });
            if (resp.ok) {
                const data = await resp.json();
                console.log("Cart synchronized with Django session:", data);
            }
        } catch (e) {
            console.warn("Could not sync cart with server session", e);
        }
    }

    showToast(message) {
        const toastEl = document.getElementById('liveAlertToast');
        const msgEl = document.getElementById('toastMessage');
        if (toastEl && msgEl) {
            msgEl.innerHTML = `<i class="bi bi-check2-circle text-mint fs-5"></i> <span>${message}</span>`;
            const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 2800 });
            toast.show();
        }
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.gourmetCart = new RestaurantCart();
});
