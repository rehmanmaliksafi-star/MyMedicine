/* ================================================================
   MyMedicine — Main JavaScript
   Animations · Scroll Reveal · Counter · Parallax · Chatbot · Cart
   ================================================================ */
'use strict';

/* ── Theme ─────────────────────────────────────────────────── */
const Theme = {
  KEY: 'mm-theme',
  init() {
    const saved = localStorage.getItem(this.KEY) || 'light';
    this.apply(saved, false);
  },
  apply(theme, animate = true) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(this.KEY, theme);
    const icon = document.getElementById('themeIcon');
    if (icon) icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    if (animate) {
      document.documentElement.style.transition = 'background .4s, color .4s';
      setTimeout(() => document.documentElement.style.transition = '', 500);
    }
  },
  toggle() {
    const cur = document.documentElement.getAttribute('data-theme') || 'light';
    this.apply(cur === 'dark' ? 'light' : 'dark');
  }
};

/* ── Toast ─────────────────────────────────────────────────── */
const Toast = {
  container: null,
  init() {
    this.container = document.getElementById('toastContainer');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toastContainer';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  show(message, type = 'success', duration = 3800) {
    const ICONS = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
    const COLORS = { success: '#4caf50', error: '#f44336', warning: '#ff9800', info: '#1565c0' };
    const t = document.createElement('div');
    t.className = `sp-toast ${type}`;
    t.innerHTML = `<i class="fas ${ICONS[type] || ICONS.info}" style="color:${COLORS[type]};font-size:1.15rem;flex-shrink:0"></i><span>${message}</span><button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--text-muted);cursor:pointer;margin-left:auto;font-size:.9rem;padding:0 0 0 .5rem;">&#x2715;</button>`;
    this.container.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(110%)'; setTimeout(() => t.remove(), 320); }, duration);
  }
};

/* ── Scroll Reveal ─────────────────────────────────────────── */
const ScrollReveal = {
  observer: null,
  init() {
    const options = { threshold: 0.12, rootMargin: '0px 0px -40px 0px' };
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          this.observer.unobserve(entry.target);
        }
      });
    }, options);
    document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale').forEach(el => {
      this.observer.observe(el);
    });
  },
  refresh() {
    document.querySelectorAll('.reveal:not(.visible), .reveal-left:not(.visible), .reveal-right:not(.visible), .reveal-scale:not(.visible)').forEach(el => {
      this.observer.observe(el);
    });
  }
};

/* ── Counter Animation ─────────────────────────────────────── */
const Counter = {
  init() {
    const counters = document.querySelectorAll('[data-count]');
    if (!counters.length) return;
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseInt(el.dataset.count);
        const suffix = el.dataset.suffix || '';
        const duration = parseInt(el.dataset.duration || 1800);
        const start = performance.now();
        const update = (now) => {
          const elapsed = Math.min((now - start) / duration, 1);
          const ease = 1 - Math.pow(1 - elapsed, 3); // ease-out-cubic
          el.textContent = Math.round(target * ease).toLocaleString() + suffix;
          if (elapsed < 1) requestAnimationFrame(update);
        };
        requestAnimationFrame(update);
        obs.unobserve(el);
      });
    }, { threshold: 0.5 });
    counters.forEach(el => obs.observe(el));
  }
};

/* ── Typing Effect ─────────────────────────────────────────── */
const Typer = {
  init() {
    const el = document.getElementById('typingText');
    if (!el) return;
    const words = (el.dataset.words || '').split('|').filter(Boolean);
    if (!words.length) return;
    let wIdx = 0, cIdx = 0, deleting = false;
    const speed = { type: 90, delete: 45, pause: 1800 };
    const tick = () => {
      const word = words[wIdx];
      if (deleting) {
        el.textContent = word.slice(0, --cIdx);
        if (cIdx === 0) { deleting = false; wIdx = (wIdx + 1) % words.length; setTimeout(tick, 400); return; }
        setTimeout(tick, speed.delete);
      } else {
        el.textContent = word.slice(0, ++cIdx);
        if (cIdx === word.length) { deleting = true; setTimeout(tick, speed.pause); return; }
        setTimeout(tick, speed.type);
      }
    };
    tick();
  }
};

/* ── Parallax ──────────────────────────────────────────────── */
const Parallax = {
  init() {
    const el = document.querySelector('.hero-bg-parallax');
    if (!el || window.innerWidth < 768) return;
    window.addEventListener('scroll', () => {
      const scroll = window.pageYOffset;
      el.style.transform = `translateY(${scroll * 0.3}px)`;
    }, { passive: true });
  }
};

/* ── Navbar Scroll Effect ──────────────────────────────────── */
const NavbarFX = {
  init() {
    const nav = document.querySelector('.navbar');
    if (!nav) return;
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 50);
    }, { passive: true });
  }
};

/* ── Ripple Buttons ────────────────────────────────────────── */
const Ripple = {
  init() {
    document.querySelectorAll('.btn').forEach(btn => {
      btn.addEventListener('click', function(e) {
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const span = document.createElement('span');
        span.className = 'ripple-effect';
        span.style.cssText = `width:${size}px;height:${size}px;top:${e.clientY - rect.top - size/2}px;left:${e.clientX - rect.left - size/2}px;`;
        this.appendChild(span);
        setTimeout(() => span.remove(), 700);
      });
    });
  }
};

/* ── Cart ──────────────────────────────────────────────────── */
const Cart = {
  init() {
    this.updateBadge();
    document.querySelectorAll('.btn-add-cart[data-product-id]').forEach(btn => {
      btn.addEventListener('click', e => this.add(e, btn));
    });
  },
  updateBadge(count) {
    document.querySelectorAll('.cart-badge, #cartCount').forEach(b => {
      if (count !== undefined) b.textContent = count;
      const c = parseInt(b.textContent) || 0;
      b.style.display = c > 0 ? 'flex' : 'none';
    });
  },
  async add(e, btn) {
    e.preventDefault();
    if (btn.dataset.needsRx === 'true') {
      window.location.href = `/upload-prescription/?product_id=${btn.dataset.productId}`;
      return;
    }
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    btn.disabled = true;
    try {
      const res = await fetch('/cart/add/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': getCookie('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' },
        body: `product_id=${btn.dataset.productId}&quantity=1`
      });
      const data = await res.json();
      if (data.status === 'success') {
        this.updateBadge(data.cart_count);
        Toast.show(data.message || 'Added to cart!', 'success');
        btn.innerHTML = '<i class="fas fa-check"></i> Added!';
        setTimeout(() => { btn.innerHTML = orig; btn.disabled = false; }, 1800);
      } else if (data.status === 'prescription_required') {
        Toast.show('Prescription required — redirecting…', 'warning');
        setTimeout(() => window.location.href = data.redirect_url, 1000);
        btn.innerHTML = orig; btn.disabled = false;
      } else {
        Toast.show(data.message || 'Error.', 'error');
        btn.innerHTML = orig; btn.disabled = false;
      }
    } catch { Toast.show('Network error. Please try again.', 'error'); btn.innerHTML = orig; btn.disabled = false; }
  }
};

/* ── Cart Qty Controls ─────────────────────────────────────── */
const CartQty = {
  init() {
    document.querySelectorAll('.qty-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const input = btn.closest('.qty-control').querySelector('.qty-input');
        const val = Math.max(1, (parseInt(input.value) || 1) + (btn.dataset.action === 'inc' ? 1 : -1));
        input.value = val;
        input.dispatchEvent(new Event('change'));
      });
    });
    document.querySelectorAll('.qty-input[data-item-id]').forEach(input => {
      input.addEventListener('change', async () => {
        const qty = parseInt(input.value);
        try {
          const res = await fetch('/cart/update/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ item_id: input.dataset.itemId, quantity: qty })
          });
          const data = await res.json();
          if (data.status === 'success') {
            Cart.updateBadge(data.cart_count);
            const tot = document.getElementById('cartTotal');
            if (tot) tot.textContent = `Rs. ${Number(data.cart_total).toLocaleString()}`;
            const rowTot = document.getElementById(`item-total-${input.dataset.itemId}`);
            if (rowTot) rowTot.textContent = `Rs. ${(parseFloat(input.dataset.price || 0) * qty).toLocaleString()}`;
          } else { Toast.show(data.message || 'Update failed.', 'error'); }
        } catch { Toast.show('Network error.', 'error'); }
      });
    });
  }
};

/* ── Chatbot ───────────────────────────────────────────────── */
const Chatbot = {
  open: false,
  typing: false,
  init() {
    const toggle = document.getElementById('chatbotToggle');
    const win = document.getElementById('chatbotWindow');
    const form = document.getElementById('chatbotForm');
    const input = document.getElementById('chatInput');
    if (!toggle || !win) return;

    toggle.addEventListener('click', () => {
      this.open = !this.open;
      win.classList.toggle('hidden', !this.open);
      toggle.querySelector('i').className = this.open ? 'fas fa-times' : 'fas fa-comment-medical';
      if (this.open && input) setTimeout(() => input.focus(), 100);
    });

    form?.addEventListener('submit', async e => {
      e.preventDefault();
      if (this.typing) return;
      const msg = input.value.trim();
      if (!msg) return;
      this.addBubble(msg, 'user');
      input.value = '';
      const typingBubble = this.addTyping();
      this.typing = true;
      try {
        const res = await fetch('/chatbot/api/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
          body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        typingBubble.remove();
        this.addBubble(data.response || 'Sorry, I could not understand that.', 'bot');
      } catch {
        typingBubble.remove();
        this.addBubble('Connection error. Please try again.', 'bot');
      }
      this.typing = false;
    });

    setTimeout(() => {
      if (!this.open) {
        const msgs = document.getElementById('chatMessages');
        if (msgs && msgs.children.length === 0)
          this.addBubble('👋 Hi! I\'m MediBot from MyMedicine. Ask me anything about medicines, orders, or prescriptions!', 'bot');
      }
    }, 1000);
  },
  addBubble(text, role) {
    const msgs = document.getElementById('chatMessages');
    const b = document.createElement('div');
    b.className = `chat-bubble ${role}`;
    b.textContent = text;
    msgs.appendChild(b);
    msgs.scrollTop = msgs.scrollHeight;
    return b;
  },
  addTyping() {
    const msgs = document.getElementById('chatMessages');
    const b = document.createElement('div');
    b.className = 'chat-bubble bot';
    b.innerHTML = '<span style="display:flex;gap:4px;align-items:center"><span style="width:7px;height:7px;background:var(--text-muted);border-radius:50%;animation:pulse-glow .8s ease infinite;animation-delay:0s"></span><span style="width:7px;height:7px;background:var(--text-muted);border-radius:50%;animation:pulse-glow .8s ease infinite;animation-delay:.2s"></span><span style="width:7px;height:7px;background:var(--text-muted);border-radius:50%;animation:pulse-glow .8s ease infinite;animation-delay:.4s"></span></span>';
    msgs.appendChild(b);
    msgs.scrollTop = msgs.scrollHeight;
    return b;
  }
};

/* ── Page Loader ───────────────────────────────────────────── */
const Loader = {
  init() {
    const loader = document.getElementById('pageLoader');
    if (!loader) return;
    window.addEventListener('load', () => {
      loader.style.opacity = '0';
      setTimeout(() => loader.remove(), 500);
    });
    setTimeout(() => { loader.style.opacity = '0'; setTimeout(() => loader.remove(), 500); }, 3000);
  }
};

/* ── Back to Top ───────────────────────────────────────────── */
const BackTop = {
  init() {
    const btn = document.getElementById('backTop');
    if (!btn) return;
    window.addEventListener('scroll', () => btn.classList.toggle('visible', window.scrollY > 400), { passive: true });
    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }
};

/* ── Django Messages → Toasts ──────────────────────────────── */
const DjangoMessages = {
  init() {
    document.querySelectorAll('[data-django-message]').forEach(el => {
      const map = { success: 'success', error: 'error', warning: 'warning', info: 'info', debug: 'info' };
      setTimeout(() => Toast.show(el.dataset.djangoMessage, map[el.dataset.djangoMessageType] || 'info'), 200);
      el.remove();
    });
  }
};

/* ── File Upload Preview ───────────────────────────────────── */
const FilePreview = {
  init() {
    document.querySelectorAll('input[type="file"][data-preview]').forEach(input => {
      input.addEventListener('change', () => {
        const file = input.files[0];
        const preview = document.getElementById(input.dataset.preview);
        if (file && preview) {
          if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = e => { preview.src = e.target.result; preview.style.display = 'block'; };
            reader.readAsDataURL(file);
          } else {
            preview.style.display = 'none';
          }
        }
        const label = document.getElementById(input.dataset.label);
        if (label) label.textContent = `${file.name} (${(file.size/1024).toFixed(1)} KB)`;
      });
    });

    document.querySelectorAll('.upload-zone').forEach(zone => {
      const input = zone.querySelector('input[type="file"]');
      ['dragenter','dragover'].forEach(ev => zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.add('dragover'); }));
      ['dragleave','drop'].forEach(ev => zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.remove('dragover'); }));
      zone.addEventListener('drop', e => {
        if (input && e.dataTransfer.files.length) { input.files = e.dataTransfer.files; input.dispatchEvent(new Event('change')); }
      });
      zone.addEventListener('click', () => input?.click());
    });
  }
};

/* ── Confirm Dialogs ───────────────────────────────────────── */
const Confirm = {
  init() {
    document.querySelectorAll('[data-confirm]').forEach(el => {
      el.addEventListener('click', e => { if (!confirm(el.dataset.confirm)) e.preventDefault(); });
    });
  }
};

/* ── Promo Banner Slider (optional auto-scroll) ────────────── */
const PromoSlider = {
  init() {
    const track = document.getElementById('promoSliderTrack');
    if (!track) return;
    let idx = 0;
    const items = track.querySelectorAll('.promo-slide-item');
    if (items.length <= 1) return;
    setInterval(() => {
      idx = (idx + 1) % items.length;
      track.style.transform = `translateX(-${idx * 100}%)`;
    }, 5000);
  }
};

/* ── Bootstrap Tooltips ────────────────────────────────────── */
function initBootstrap() {
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el, { trigger: 'hover' }));
  document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => new bootstrap.Popover(el));
}

/* ── Utility ───────────────────────────────────────────────── */
function getCookie(name) {
  return document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith(name + '='))?.split('=')[1] ?? '';
}

/* ── Boot ──────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  Theme.init();
  Toast.init();
  Loader.init();
  NavbarFX.init();
  ScrollReveal.init();
  Counter.init();
  Typer.init();
  Parallax.init();
  Ripple.init();
  Cart.init();
  CartQty.init();
  Chatbot.init();
  BackTop.init();
  DjangoMessages.init();
  FilePreview.init();
  Confirm.init();
  PromoSlider.init();
  initBootstrap();
});

/* ── Globals ───────────────────────────────────────────────── */
window.toggleTheme = () => Theme.toggle();
window.showToast   = (m, t) => Toast.show(m, t);
