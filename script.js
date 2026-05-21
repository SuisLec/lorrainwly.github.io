'use strict';

// Navbar scroll effect
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

// Mobile menu
const navToggle = document.getElementById('navToggle');
const mobileMenu = document.getElementById('mobileMenu');
const mobileClose = document.getElementById('mobileClose');

function openMenu() {
  mobileMenu.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeMenu() {
  mobileMenu.classList.remove('open');
  document.body.style.overflow = '';
}

navToggle.addEventListener('click', openMenu);
mobileClose.addEventListener('click', closeMenu);
document.querySelectorAll('.mobile-link').forEach(l => l.addEventListener('click', closeMenu));

// Smooth scroll for anchors
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// Fade-up scroll animation
const fadeEls = document.querySelectorAll(
  '.research-item, .project-card, .about-right, .contact-container'
);
fadeEls.forEach(el => el.classList.add('fade-up'));

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

fadeEls.forEach(el => observer.observe(el));

// Dynamic Handwriting Signature Tracer
window.addEventListener('DOMContentLoaded', () => {
  const brand = document.querySelector('.nav-brand');
  if (!brand) return;

  const img = new Image();
  img.src = 'signature.png';
  img.onload = () => {
    try {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      
      // Downscale to 48px height to smooth out noise and speed up tracing
      const targetH = 48;
      const aspect = img.width / img.height;
      const targetW = Math.round(targetH * aspect);
      
      canvas.width = targetW;
      canvas.height = targetH;
      ctx.drawImage(img, 0, 0, targetW, targetH);

      const imgData = ctx.getImageData(0, 0, targetW, targetH);
      const data = imgData.data;
      const threshold = 150; // Dark ink on light background

      // 1. Find bounding box of active pixels (dark handwriting)
      let minX = targetW, minY = targetH, maxX = 0, maxY = 0;
      for (let y = 0; y < targetH; y++) {
        for (let x = 0; x < targetW; x++) {
          const idx = (y * targetW + x) * 4;
          const r = data[idx];
          const g = data[idx+1];
          const b = data[idx+2];
          const a = data[idx+3];
          const gray = 0.299 * r + 0.587 * g + 0.114 * b;
          
          // Pixel is active if it's opaque enough and dark enough
          const isActive = (a > 30) && (gray < threshold);
          if (isActive) {
            if (x < minX) minX = x;
            if (y < minY) minY = y;
            if (x > maxX) maxX = x;
            if (y > maxY) maxY = y;
          }
        }
      }

      if (maxX < minX || maxY < minY) return;

      const cropW = maxX - minX + 1;
      const cropH = maxY - minY + 1;

      // 2. Extract horizontal spans and offset to (0, 0)
      const pathSegments = [];
      for (let y = minY; y <= maxY; y++) {
        let inSpan = false;
        let startX = 0;
        for (let x = minX; x <= maxX + 1; x++) {
          let isActive = false;
          if (x <= maxX) {
            const idx = (y * targetW + x) * 4;
            const r = data[idx];
            const g = data[idx+1];
            const b = data[idx+2];
            const a = data[idx+3];
            const gray = 0.299 * r + 0.587 * g + 0.114 * b;
            isActive = (a > 30) && (gray < threshold);
          }
          if (isActive) {
            if (!inSpan) {
              inSpan = true;
              startX = x;
            }
          } else {
            if (inSpan) {
              inSpan = false;
              const w = x - startX;
              pathSegments.push(`M ${startX - minX} ${y - minY} h ${w}`);
            }
          }
        }
      }

      const pathD = pathSegments.join(' ');
      brand.innerHTML = `
        <svg viewBox="0 0 ${cropW} ${cropH}" class="nav-signature-svg" aria-label="Lorrain Wei Signature">
          <path d="${pathD}" />
        </svg>
      `;
    } catch (e) {
      console.warn("Signature trace skipped (CORS/local file restriction). Using high-fidelity default vector SVG.");
    }
  };
});

// Console signature
console.log('%c lorrainwly.com ', 'background:#111;color:#fff;padding:4px 10px;border-radius:4px;font-family:serif;font-size:13px');
