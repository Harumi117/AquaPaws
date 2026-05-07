/* わたしいぬわたしねこライフ - Theme JS */

(function () {
  'use strict';

  // --- Mobile Menu ---
  const mobileMenuBtn = document.querySelector('.site-header__mobile-menu');
  const mobileNav = document.querySelector('.mobile-nav');

  if (mobileMenuBtn && mobileNav) {
    mobileMenuBtn.addEventListener('click', function () {
      const isOpen = mobileMenuBtn.getAttribute('aria-expanded') === 'true';
      mobileMenuBtn.setAttribute('aria-expanded', String(!isOpen));
      mobileNav.setAttribute('aria-hidden', String(isOpen));
      mobileNav.style.display = isOpen ? 'none' : 'block';
      document.body.style.overflow = isOpen ? '' : 'hidden';
    });
  }

  // --- Cart Drawer ---
  const cartDrawer = document.getElementById('cart-drawer');
  const cartBtns = document.querySelectorAll('.site-header__cart-btn');
  const cartClose = document.querySelector('.cart-drawer__close');
  const cartOverlay = document.querySelector('.cart-drawer__overlay');

  function openCartDrawer() {
    if (!cartDrawer) return;
    cartDrawer.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeCartDrawer() {
    if (!cartDrawer) return;
    cartDrawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  cartBtns.forEach(function (btn) {
    btn.addEventListener('click', openCartDrawer);
  });

  if (cartClose) cartClose.addEventListener('click', closeCartDrawer);
  if (cartOverlay) cartOverlay.addEventListener('click', closeCartDrawer);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeCartDrawer();
  });

  // --- Quick Add to Cart ---
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.product-card__quick-add');
    if (!btn) return;

    const variantId = btn.dataset.productId;
    if (!variantId) return;

    btn.textContent = '追加中...';
    btn.disabled = true;

    fetch('/cart/add.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: variantId, quantity: 1 }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error('Add to cart failed');
        return res.json();
      })
      .then(function () {
        btn.textContent = 'カートに追加しました！';
        updateCartCount();
        setTimeout(function () {
          btn.textContent = 'カートに追加';
          btn.disabled = false;
        }, 2000);
        openCartDrawer();
      })
      .catch(function () {
        btn.textContent = 'エラーが発生しました';
        btn.disabled = false;
      });
  });

  // --- Update Cart Count ---
  function updateCartCount() {
    fetch('/cart.js')
      .then(function (res) { return res.json(); })
      .then(function (cart) {
        const countEls = document.querySelectorAll('.cart-count');
        countEls.forEach(function (el) {
          if (cart.item_count > 0) {
            el.textContent = cart.item_count;
            el.style.display = '';
          } else {
            el.style.display = 'none';
          }
        });
      });
  }

  // --- Sticky Header Shadow ---
  const header = document.querySelector('.site-header');
  if (header) {
    const announcementBar = document.querySelector('.announcement-bar');
    let lastScroll = 0;

    window.addEventListener('scroll', function () {
      const currentScroll = window.scrollY;
      if (currentScroll > 10) {
        header.style.boxShadow = '0 2px 16px rgba(44,24,16,0.12)';
      } else {
        header.style.boxShadow = '';
      }
      lastScroll = currentScroll;
    }, { passive: true });
  }

  // --- Lazy load images polyfill ---
  if ('loading' in HTMLImageElement.prototype === false) {
    const images = document.querySelectorAll('img[loading="lazy"]');
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
          }
          observer.unobserve(img);
        }
      });
    });
    images.forEach(function (img) { observer.observe(img); });
  }

})();
