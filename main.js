/* ═══════════════════════════════════════════════════════════
   VIT Bhopal Lost & Found — Client-side JavaScript
   ═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss flash messages ────────────────────────────
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .5s, transform .5s';
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(-8px)';
      setTimeout(() => el.remove(), 500);
    }, 4500);
  });

  // ── Image file preview ─────────────────────────────────────
  document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', () => {
      const file    = input.files[0];
      const preview = input.closest('.form-group')?.querySelector('.file-preview');
      const img     = preview?.querySelector('img');
      const label   = input.closest('.form-group')?.querySelector('.file-upload-label');

      if (!file || !preview || !img) return;

      const reader  = new FileReader();
      reader.onload = e => {
        img.src           = e.target.result;
        preview.style.display = 'block';
        if (label) {
          label.querySelector('.upload-title').textContent = file.name;
          label.querySelector('.upload-sub').textContent   =
            (file.size / 1024).toFixed(1) + ' KB';
        }
      };
      reader.readAsDataURL(file);
    });
  });

  // ── Reveal Contact (AJAX) ──────────────────────────────────
  document.querySelectorAll('.btn-reveal').forEach(btn => {
    btn.addEventListener('click', async () => {
      const itemId = btn.dataset.itemId;
      const panel  = document.getElementById(`contact-${itemId}`);

      if (!panel) return;

      if (panel.classList.contains('show')) {
        panel.classList.remove('show');
        btn.textContent = '📋 Reveal Contact';
        return;
      }

      // Already loaded
      if (panel.dataset.loaded === '1') {
        panel.classList.add('show');
        btn.textContent = '🔒 Hide Contact';
        return;
      }

      btn.disabled    = true;
      btn.textContent = '⏳ Loading…';

      try {
        const res  = await fetch(`/reveal-contact/${itemId}`);
        const data = await res.json();

        if (data.error) {
          panel.innerHTML = `<strong>Error</strong>${data.error}`;
        } else {
          panel.innerHTML = `
            <strong>Contact for "${data.item_name}"</strong>
            ${escapeHtml(data.contact)}
          `;
          panel.dataset.loaded = '1';
        }

        panel.classList.add('show');
        btn.textContent = '🔒 Hide Contact';
      } catch (err) {
        panel.innerHTML = '<strong>Error</strong>Could not load contact info.';
        panel.classList.add('show');
        btn.textContent = '📋 Reveal Contact';
      } finally {
        btn.disabled = false;
      }
    });
  });

  // ── Claim item ─────────────────────────────────────────────
  document.querySelectorAll('.btn-claim').forEach(btn => {
    btn.addEventListener('click', async () => {
      const itemId = btn.dataset.itemId;
      const card   = btn.closest('.item-card');

      if (!confirm('Mark this item as CLAIMED?')) return;

      btn.disabled = true;
      try {
        const res  = await fetch(`/claim/${itemId}`, { method: 'POST' });
        const data = await res.json();

        if (data.status === 'CLAIMED') {
          const badge = card.querySelector('.status-badge');
          if (badge) {
            badge.textContent = 'Claimed';
            badge.classList.remove('unclaimed');
            badge.classList.add('claimed');
          }
          btn.remove();
        }
      } catch (err) {
        console.error(err);
        btn.disabled = false;
      }
    });
  });

  // ── Email domain live validation ───────────────────────────
  const emailInput = document.getElementById('email-input');
  if (emailInput) {
    const allowed = emailInput.dataset.allowedDomain || 'vitbhopal.ac.in';
    const hint    = document.getElementById('email-hint');

    emailInput.addEventListener('input', () => {
      const val = emailInput.value.trim().toLowerCase();
      if (!hint) return;

      if (val.length === 0) {
        hint.textContent = '';
        hint.style.color = '';
      } else if (val.endsWith(`@${allowed}`)) {
        hint.textContent = '✓ Valid institutional email';
        hint.style.color = 'var(--success)';
      } else if (val.includes('@')) {
        hint.textContent = `✗ Must be @${allowed}`;
        hint.style.color = 'var(--error)';
      } else {
        hint.textContent = `Enter your @${allowed} address`;
        hint.style.color = 'var(--text-muted)';
      }
    });
  }

  // ── OTP digit formatting ───────────────────────────────────
  const otpInput = document.getElementById('otp-input');
  if (otpInput) {
    otpInput.addEventListener('input', () => {
      otpInput.value = otpInput.value.replace(/\D/g, '').slice(0, 6);
    });
  }

  // ── Submit button loading state ────────────────────────────
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('button[type="submit"]');
      if (btn && !btn.classList.contains('no-loading')) {
        btn.classList.add('loading');
        btn.disabled = true;
        // Re-enable after 8s fallback
        setTimeout(() => {
          btn.classList.remove('loading');
          btn.disabled = false;
        }, 8000);
      }
    });
  });

  // ── Catalog search debounce ────────────────────────────────
  const searchInput = document.getElementById('catalog-search');
  if (searchInput) {
    let debounce;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        const q = searchInput.value.trim();
        const url = new URL(window.location.href);
        if (q) {
          url.searchParams.set('q', q);
        } else {
          url.searchParams.delete('q');
        }
        window.location.href = url.toString();
      }, 600);
    });
  }

  // ── Helper: HTML escape ─────────────────────────────────────
  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
      .replace(/\n/g, '<br>');
  }

});
