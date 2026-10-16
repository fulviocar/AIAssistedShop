const loginSection =
    document.getElementById("login-section");

const registerSection =
    document.getElementById("register-section");

const accountSection =
    document.getElementById("account-section");

const productsSection =
    document.getElementById("products-section");

const productDetailSection =
    document.getElementById("product-detail-section");

const cartSection =
    document.getElementById("cart-section");

const ordersSection =
    document.getElementById("orders-section");

const orderSection =
    document.getElementById("order-section");

const navigation =
    document.getElementById("navigation");

const productsContainer =
    document.getElementById("products-container");

const productDetailContainer =
    document.getElementById("product-detail-container");

const cartContainer =
    document.getElementById("cart-container");

const ordersContainer =
    document.getElementById("orders-container");

const orderContainer =
    document.getElementById("order-container");

const cartCount =
    document.getElementById("cart-count");

const loginError =
    document.getElementById("login-error");

const registerError =
    document.getElementById("register-error");

const accountContainer =
    document.getElementById("account-container");

const productSearch =
    document.getElementById("product-search");


/* ============================================================
   Authentication
   ============================================================ */

function getToken() {

    return localStorage.getItem("access_token");
}


function getRefreshToken() {

    return localStorage.getItem("refresh_token");
}


function isAuthenticated() {

    return getToken() !== null;
}


function logout() {

    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    showLogin();
}


/* ============================================================
   API
   ============================================================ */

async function refreshAccessToken() {

    const refreshToken = getRefreshToken();

    if (!refreshToken) {
        return false;
    }

    const response = await fetch(
        "/api/auth/refresh",
        {
            method: "POST",
            headers: {
                Authorization: `Bearer ${refreshToken}`
            }
        }
    );

    if (!response.ok) {
        return false;
    }

    const data = await response.json();
    localStorage.setItem("access_token", data.access_token);
    return true;
}


async function apiRequest(url, options = {}) {

    const sendRequest = () => {
        const headers = {
            ...(options.headers || {})
        };
        const token = getToken();

        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }

        return fetch(url, {
            ...options,
            headers
        });
    };

    let response = await sendRequest();

    if (response.status === 401) {
        const refreshed = await refreshAccessToken();

        if (refreshed) {
            response = await sendRequest();
        }

        if (response.status === 401) {
            logout();
            throw new Error("Authentication required");
        }
    }

    const contentType =
        response.headers.get("content-type");

    let data = null;

    if (
        contentType &&
        contentType.includes("application/json")
    ) {

        data = await response.json();
    }

    if (!response.ok) {

        throw new Error(
            data?.error ||
            "Request failed"
        );
    }

    return data;
}


/* ============================================================
   Login
   ============================================================ */

document
    .getElementById("login-form")
    .addEventListener(
        "submit",
        login
    );


async function login(event) {

    event.preventDefault();

    loginError.classList.add("hidden");

    const email =
        document
            .getElementById("email")
            .value;

    const password =
        document
            .getElementById("password")
            .value;

    try {

        const response =
            await fetch(
                "/api/auth/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        email,
                        password
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Login failed"
            );
        }

        localStorage.setItem(
            "access_token",
            data.access_token
        );
        localStorage.setItem(
            "refresh_token",
            data.refresh_token
        );

        showApplication();

    } catch (error) {

        loginError.textContent =
            error.message;

        loginError.classList.remove(
            "hidden"
        );
    }
}


/* ============================================================
   Register
   ============================================================ */

document
    .getElementById("show-register-button")
    .addEventListener(
        "click",
        showRegister
    );


document
    .getElementById("show-login-button")
    .addEventListener(
        "click",
        showLogin
    );


document
    .getElementById("register-form")
    .addEventListener(
        "submit",
        register
    );


async function register(event) {

    event.preventDefault();

    registerError.classList.add("hidden");

    const name =
        document
            .getElementById("register-name")
            .value
            .trim();

    const email =
        document
            .getElementById("register-email")
            .value
            .trim();

    const password =
        document
            .getElementById("register-password")
            .value;

    try {

        const response =
            await fetch(
                "/api/auth/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        name,
                        email,
                        password
                    })
                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Registration failed"
            );
        }

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        document
            .getElementById("register-form")
            .reset();

        showApplication();

    } catch (error) {

        registerError.textContent =
            error.message;

        registerError.classList.remove(
            "hidden"
        );
    }
}


/* ============================================================
   Navigation
   ============================================================ */

document
    .getElementById("products-link")
    .addEventListener(
        "click",
        showProducts
    );


document
    .getElementById("cart-link")
    .addEventListener(
        "click",
        showCart
    );


document
    .getElementById("orders-link")
    .addEventListener(
        "click",
        showOrders
    );


document
    .getElementById("account-link")
    .addEventListener(
        "click",
        showAccount
    );


document
    .getElementById("logout-button")
    .addEventListener(
        "click",
        logout
    );


document
    .getElementById("search-button")
    .addEventListener(
        "click",
        searchProducts
    );


document
    .getElementById("back-to-products")
    .addEventListener(
        "click",
        showProducts
    );


document
    .getElementById("checkout-button")
    .addEventListener(
        "click",
        checkout
    );


document
    .getElementById("clear-cart-button")
    .addEventListener(
        "click",
        clearCart
    );


/* ============================================================
   Section navigation
   ============================================================ */

function hideAllSections() {

    loginSection.classList.add("hidden");

    registerSection.classList.add("hidden");

    productsSection.classList.add("hidden");

    productDetailSection.classList.add("hidden");

    cartSection.classList.add("hidden");

    ordersSection.classList.add("hidden");

    orderSection.classList.add("hidden");

    accountSection.classList.add("hidden");
}


function showLogin() {

    hideAllSections();

    loginSection.classList.remove("hidden");

    navigation.classList.add("hidden");
}


function showRegister() {

    hideAllSections();

    registerSection.classList.remove("hidden");

    navigation.classList.add("hidden");

    registerError.classList.add("hidden");
}


function showApplication() {

    loginSection.classList.add("hidden");

    registerSection.classList.add("hidden");

    navigation.classList.remove("hidden");

    showProducts();
}


/* ============================================================
   Products
   ============================================================ */

async function showProducts() {

    hideAllSections();

    productsSection.classList.remove("hidden");

    await loadProducts(
        productSearch.value.trim()
    );
}


async function searchProducts() {

    await loadProducts(
        productSearch.value.trim()
    );
}


async function loadProducts(search = "") {

    try {

        let url = "/api/products";

        if (search) {

            url +=
                `?search=${encodeURIComponent(search)}`;
        }

        const products =
            await apiRequest(url);

        productsContainer.innerHTML = "";

        if (products.length === 0) {

            productsContainer.innerHTML =
                "<p>No products found.</p>";

            return;
        }

        for (const product of products) {

            const card =
                document.createElement("div");

            card.className =
                "product-card";

            card.innerHTML = `
                <h2>
                    ${product.name}
                </h2>

                <p>
                    ${product.description}
                </p>

                <div class="product-price">
                    €${product.price}
                </div>

                <div class="product-stock">
                    Stock:
                    ${product.stock_quantity}
                </div>

                <button
                    class="view-product"
                    data-product-id="${product.id}"
                >
                    View Details
                </button>

                <button
                    class="add-to-cart"
                    data-product-id="${product.id}"
                >
                    Add to Cart
                </button>
            `;

            card
                .querySelector(".view-product")
                .addEventListener(
                    "click",
                    () => showProduct(product.id)
                );

            card
                .querySelector(".add-to-cart")
                .addEventListener(
                    "click",
                    () => addToCart(product.id)
                );

            productsContainer.appendChild(card);
        }

    } catch (error) {

        productsContainer.innerHTML = `
            <div class="error">
                ${error.message}
            </div>
        `;
    }
}


/* ============================================================
   Product detail
   ============================================================ */

async function showProduct(productId) {

    hideAllSections();

    productDetailSection.classList.remove(
        "hidden"
    );

    productDetailContainer.innerHTML =
        "Loading...";

    try {

        const product =
            await apiRequest(
                `/api/products/${productId}`
            );

        productDetailContainer.innerHTML = `
            <div class="product-detail">

                <h1>
                    ${product.name}
                </h1>

                <p class="product-description">
                    ${product.description}
                </p>

                <div class="product-price">
                    €${product.price}
                </div>

                <div class="product-stock">
                    Available:
                    ${product.stock_quantity}
                </div>

                <button
                    id="detail-add-to-cart"
                >
                    Add to Cart
                </button>

            </div>
        `;

        document
            .getElementById(
                "detail-add-to-cart"
            )
            .addEventListener(
                "click",
                async () => {

                    await addToCart(
                        product.id
                    );
                }
            );

    } catch (error) {

        productDetailContainer.innerHTML = `
            <div class="error">
                ${error.message}
            </div>
        `;
    }
}


/* ============================================================
   Cart
   ============================================================ */

async function addToCart(productId) {

    try {

        await apiRequest(
            "/api/customers/me/cart/items",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    product_id: productId,
                    quantity: 1
                })
            }
        );

        await updateCartCount();

    } catch (error) {

        alert(error.message);
    }
}


async function showCart() {

    hideAllSections();

    cartSection.classList.remove(
        "hidden"
    );

    await loadCart();
}


async function loadCart() {

    try {

        const cart =
            await apiRequest(
                "/api/customers/me/cart"
            );

        cartContainer.innerHTML = "";

        if (cart.items.length === 0) {

            cartContainer.innerHTML =
                "<p>Your cart is empty.</p>";

            return;
        }

        for (const item of cart.items) {

            const element =
                document.createElement("div");

            element.className =
                "cart-item";

            element.innerHTML = `
                <div class="cart-item-info">

                    <strong>
                        ${item.product_name}
                    </strong>

                    <div>
                        €${item.unit_price} each
                    </div>

                </div>

                <div class="cart-item-controls">

                    <button
                        class="quantity-button"
                        data-action="decrease"
                    >
                        −
                    </button>

                    <span class="quantity">
                        ${item.quantity}
                    </span>

                    <button
                        class="quantity-button"
                        data-action="increase"
                    >
                        +
                    </button>

                    <strong>
                        €${item.subtotal}
                    </strong>

                    <button
                        class="remove-item"
                    >
                        Remove
                    </button>

                </div>
            `;

            element
                .querySelector(
                    '[data-action="decrease"]'
                )
                .addEventListener(
                    "click",
                    () => updateCartItem(
                        item.id,
                        item.quantity - 1
                    )
                );

            element
                .querySelector(
                    '[data-action="increase"]'
                )
                .addEventListener(
                    "click",
                    () => updateCartItem(
                        item.id,
                        item.quantity + 1
                    )
                );

            element
                .querySelector(
                    ".remove-item"
                )
                .addEventListener(
                    "click",
                    () => removeCartItem(item.id)
                );

            cartContainer.appendChild(element);
        }

        const total =
            document.createElement("div");

        total.className =
            "cart-total";

        total.textContent =
            `Total: €${cart.total}`;

        cartContainer.appendChild(total);

    } catch (error) {

        cartContainer.innerHTML = `
            <div class="error">
                ${error.message}
            </div>
        `;
    }
}


async function updateCartItem(
    itemId,
    quantity
) {

    try {

        if (quantity <= 0) {

            await removeCartItem(itemId);

            return;
        }

        await apiRequest(
            `/api/customers/me/cart/items/${itemId}`,
            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    quantity
                })
            }
        );

        await loadCart();

        await updateCartCount();

    } catch (error) {

        alert(error.message);
    }
}


async function removeCartItem(itemId) {

    try {

        await apiRequest(
            `/api/customers/me/cart/items/${itemId}`,
            {
                method: "DELETE"
            }
        );

        await loadCart();

        await updateCartCount();

    } catch (error) {

        alert(error.message);
    }
}


async function updateCartCount() {

    try {

        const cart =
            await apiRequest(
                "/api/customers/me/cart"
            );

        const count =
            cart.items.reduce(
                (total, item) =>
                    total + item.quantity,
                0
            );

        cartCount.textContent = count;

    } catch {

        cartCount.textContent = "0";
    }
}


async function clearCart() {

    try {

        await apiRequest(
            "/api/customers/me/cart",
            {
                method: "DELETE"
            }
        );

        await loadCart();

        await updateCartCount();

    } catch (error) {

        alert(error.message);
    }
}


/* ============================================================
   Checkout
   ============================================================ */

async function checkout() {

    try {

        const order =
            await apiRequest(
                "/api/customers/me/orders/checkout",
                {
                    method: "POST"
                }
            );

        showOrder(order);

        await updateCartCount();

    } catch (error) {

        alert(error.message);
    }
}


/* ============================================================
   Orders
   ============================================================ */

async function showOrders() {

    hideAllSections();

    ordersSection.classList.remove(
        "hidden"
    );

    await loadOrders();
}


async function loadOrders() {

    try {

        const orders =
            await apiRequest(
                "/api/customers/me/orders"
            );

        ordersContainer.innerHTML = "";

        if (orders.length === 0) {

            ordersContainer.innerHTML =
                "<p>No orders yet.</p>";

            return;
        }

        for (const order of orders) {

            const element =
                document.createElement("div");

            element.className =
                "cart-item";

            element.innerHTML = `
                <div>

                    <strong>
                        Order #${order.id}
                    </strong>

                    <div>
                        Status:
                        ${order.status}
                    </div>

                    <div>
                        ${order.created_at}
                    </div>

                </div>

                <div>
                    €${order.total_amount}
                </div>
            `;

            ordersContainer.appendChild(element);
        }

    } catch (error) {

        ordersContainer.innerHTML = `
            <div class="error">
                ${error.message}
            </div>
        `;
    }
}


/* ============================================================
   My Account
   ============================================================ */

async function showAccount() {

    hideAllSections();

    accountSection.classList.remove("hidden");

    accountContainer.textContent =
        "Loading account...";

    try {

        const customer =
            await apiRequest(
                "/api/customers/me"
            );

        accountContainer.innerHTML = `
            <div class="account-details">

                <p>
                    <strong>ID:</strong>
                    ${customer.id}
                </p>

                <p>
                    <strong>Name:</strong>
                    ${customer.name}
                </p>

                <p>
                    <strong>Email:</strong>
                    ${customer.email}
                </p>

                <p>
                    <strong>Created:</strong>
                    ${customer.created_at}
                </p>

            </div>
        `;

    } catch (error) {

        accountContainer.innerHTML = `
            <div class="error">
                ${error.message}
            </div>
        `;
    }
}


/* ============================================================
   Order confirmation
   ============================================================ */

function showOrder(order) {

    hideAllSections();

    orderSection.classList.remove(
        "hidden"
    );

    orderContainer.innerHTML = `
        <p>
            Order:
            <strong>#${order.id}</strong>
        </p>

        <p>
            Status:
            <strong>${order.status}</strong>
        </p>

        <p>
            Total:
            <strong>€${order.total_amount}</strong>
        </p>

        <h2>Items</h2>

        ${order.items.map(item => `
            <div class="cart-item">

                <span>
                    Product #${item.product_id}
                    × ${item.quantity}
                </span>

                <span>
                    €${item.subtotal}
                </span>

            </div>
        `).join("")}
    `;
}


/* ============================================================
   Application initialization
   ============================================================ */

async function initialize() {

    if (isAuthenticated()) {

        showApplication();

    } else {

        showLogin();
    }
}


initialize();