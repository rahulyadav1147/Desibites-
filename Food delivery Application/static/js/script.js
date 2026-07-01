const products = [
  { id: 1, name: 'Margherita Pizza', price: 89, cat: 'pizza', img: '/static/images/Margherita Pizza Recipe 3.jpeg', desc: 'Classic tomato & cheese' },
  { id: 2, name: 'Pepperoni Pizza', price: 339, cat: 'pizza', img: '/static/images/Yummy pepperoni pizza cheese pizza food pizza on….jpeg', desc: 'Spicy pepperoni slices' },
  { id: 3, name: 'Cheeseburger', price: 100, cat: 'burger', img: 'https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&s=9a1b0b2c4d5e6f7a8b9c0d1e2f3a4b5c', desc: 'Juicy beef patty with cheese' },
  { id: 4, name: 'Veggie Burger', price: 109, cat: 'burger', img: '/static/images/Photo of a vibrant vegetarian burger featuring a….jpeg', desc: 'Fresh veggies & sauce' },
  { id: 5, name: 'Salmon Sushi', price: 375, cat: 'sushi', img: 'https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&s=112233aabbccddeeff', desc: 'Fresh salmon rolls' },
  { id: 6, name: 'Chocolate Cake', price: 200, cat: 'dessert', img: '/static/images/Dark Chocolate Cake   Ingredients 🎉  For the….jpeg', desc: 'Rich and moist' }
];

let cart = {};

function $(sel){ return document.querySelector(sel); }
function $$(sel){ return document.querySelectorAll(sel); }

function formatPrice(value){
  // prices stored as paise-like integer (e.g., 899 -> ₹8.99)
  const rupees = value;
  return rupees.toLocaleString('en-IN', { style: 'currency', currency: 'INR' });
}

function renderProducts(list = products){
  const container = $('#products');
  container.innerHTML = '';
  list.forEach(p=>{
    const card = document.createElement('div'); card.className='product-card';
    card.innerHTML = `
      <img src="${p.img}" alt="${p.name}">
      <div class="product-title">${p.name}</div>
      <div class="product-desc">${p.desc}</div>
      <div class="product-bottom">
        <div>${formatPrice(p.price)}</div>
        <button class="primary" data-id="${p.id}">Add</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function updateCartCount(){
  const count = Object.values(cart).reduce((s,i)=>s+i.qty,0);
  $('#cartCount').textContent = count;
}

function addToCart(id){
  const p = products.find(x=>x.id==id);
  if(!p) return;
  if(!cart[id]) cart[id] = { ...p, qty:1 };
  else cart[id].qty += 1;
  updateCartCount();
  renderCartItems();
}

function renderCartItems(){
  const el = $('#cartItems'); el.innerHTML = '';
  const items = Object.values(cart);
  items.forEach(it=>{
    const row = document.createElement('div'); row.className='cart-item';
    row.innerHTML = `
      <img src="${it.img}" alt="${it.name}">
      <div style="flex:1">
        <div style="font-weight:700">${it.name}</div>
        <div style="color:#666">${formatPrice(it.price)}</div>
      </div>
      <div class="qty">
        <button class="dec" data-id="${it.id}">-</button>
        <div>${it.qty}</div>
        <button class="inc" data-id="${it.id}">+</button>
      </div>
    `;
    el.appendChild(row);
  });
  const total = items.reduce((s,i)=>s + i.price * i.qty, 0);
  $('#cartTotal').textContent = formatPrice(total);
}

// Events
window.addEventListener('click', (e)=>{
  if(e.target.matches('.primary[data-id]')){
    addToCart(Number(e.target.dataset.id));
  }
  if(e.target.matches('.inc')){ const id=Number(e.target.dataset.id); cart[id].qty+=1; renderCartItems(); updateCartCount(); }
  if(e.target.matches('.dec')){ const id=Number(e.target.dataset.id); cart[id].qty-=1; if(cart[id].qty<=0) delete cart[id]; renderCartItems(); updateCartCount(); }
});

$('#openCart').addEventListener('click', ()=>{ $('#cartDrawer').scrollIntoView({behavior:'smooth'}); $('#cartDrawer').style.boxShadow='0 8px 24px rgba(0,0,0,0.12)'; });
$('#closeCart').addEventListener('click', ()=>{ $('#cartDrawer').style.boxShadow='none'; });

$('#search').addEventListener('input', (e)=>{
  const q = e.target.value.toLowerCase().trim();
  renderProducts(products.filter(p=> p.name.toLowerCase().includes(q) || p.desc.toLowerCase().includes(q)));
});

document.querySelectorAll('.cat-btn').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    document.querySelectorAll('.cat-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    const cat = btn.dataset.cat;
    if(cat==='all') renderProducts(products);
    else renderProducts(products.filter(p=>p.cat===cat));
  });
});

// initial
renderProducts();
renderCartItems();
updateCartCount();
