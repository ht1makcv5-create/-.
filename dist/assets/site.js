'use strict';
(() => {
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const config = JSON.parse($('#site-config').textContent);
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let toastTimer;
  function toast(message) {
    const el = $('#toast');
    el.textContent = message;
    el.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('visible'), 3200);
  }

  // Native dialogs provide focus trapping, return focus and Escape handling.
  const menu = $('#mobile-menu');
  const menuToggle = $('[data-open-menu]');
  const closeMenu = () => menu.close();
  menuToggle?.addEventListener('click', () => {
    menu.showModal();
    document.body.classList.add('menu-open');
    menuToggle.setAttribute('aria-expanded', 'true');
  });
  $('[data-close-menu]')?.addEventListener('click', closeMenu);
  menu.addEventListener('close', () => {
    document.body.classList.remove('menu-open');
    menuToggle.setAttribute('aria-expanded', 'false');
  });
  menu.addEventListener('click', (event) => {
    if (event.target === menu || event.target.closest('nav a')) closeMenu();
  });

  const fallback = $('#copy-fallback');
  $('[data-close-copy]').addEventListener('click', () => fallback.close());
  fallback.addEventListener('click', (event) => {
    if (event.target === fallback) {
      const rect = fallback.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) fallback.close();
    }
  });
  async function copyText(value) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(value);
      return true;
    } catch {
      const input = document.createElement('textarea');
      input.value = value;
      input.setAttribute('readonly', '');
      input.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0';
      // Keep the legacy fallback within the active modal's focus boundary.
      (menu.open ? menu : document.body).append(input);
      input.select();
      let copied = false;
      try { copied = document.execCommand('copy'); } catch { /* Manual path below. */ }
      input.remove();
      return copied;
    }
  }
  $$('[data-copy]').forEach((button) => button.addEventListener('click', async () => {
    const value = button.dataset.copy;
    if (await copyText(value)) {
      toast(value === config.ip ? 'IP скопійовано. Побачимось у грі!' : 'Команду скопійовано');
      button.classList.add('copied');
      setTimeout(() => button.classList.remove('copied'), 900);
      button.focus({preventScroll:true});
    } else {
      if (menu.open) closeMenu();
      $('#copy-value').value = value;
      fallback.showModal();
      $('#copy-value').focus();
      $('#copy-value').select();
    }
  }));

  // Links remain usable without JavaScript; with it they become keyboard tabs.
  const editionLinks = $$('[data-edition]');
  const guidePanels = $$('[data-guide]');
  if (editionLinks.length) {
    editionLinks[0].parentElement.setAttribute('role', 'tablist');
    function chooseEdition(id, focus = false) {
      editionLinks.forEach((a) => {
        const active = a.dataset.edition === id;
        a.setAttribute('aria-selected', String(active));
        a.tabIndex = active ? 0 : -1;
        if (active && focus) a.focus();
      });
      guidePanels.forEach((panel) => { panel.hidden = panel.dataset.guide !== id; });
    }
    editionLinks.forEach((a, index) => {
      a.id = 'tab-' + a.dataset.edition;
      a.setAttribute('role', 'tab');
      a.setAttribute('aria-controls', 'guide-' + a.dataset.edition);
      a.addEventListener('click', (event) => { event.preventDefault(); chooseEdition(a.dataset.edition); });
      a.addEventListener('keydown', (event) => {
        if (['ArrowLeft', 'ArrowRight', 'Home', 'End', ' '].includes(event.key)) {
          event.preventDefault();
          const next = event.key === 'Home' ? 0 : event.key === 'End' ? editionLinks.length - 1 : event.key === ' ' ? index : (index + 1) % editionLinks.length;
          chooseEdition(editionLinks[next].dataset.edition, true);
        }
      });
    });
    guidePanels.forEach((p) => {
      p.setAttribute('role', 'tabpanel');
      p.setAttribute('aria-labelledby', 'tab-' + p.dataset.guide);
      p.tabIndex = 0;
    });
    chooseEdition('java');
  }

  const search = $('#command-search');
  if (search) {
    const rows = $$('[data-command]');
    let category = 'Усі';
    const norm = (s) => s.toLocaleLowerCase('uk-UA').trim();
    function filterCommands() {
      const term = norm(search.value);
      let count = 0;
      rows.forEach((row) => {
        const matches = (category === 'Усі' || row.dataset.categoryName === category) && norm(row.textContent).includes(term);
        row.hidden = !matches;
        if (matches) count++;
      });
      $('#command-count').textContent = 'Знайдено команд: ' + count;
      $('#command-empty').hidden = count > 0;
      $('.table-scroll').hidden = count === 0;
    }
    search.addEventListener('input', filterCommands);
    $$('[data-category]').forEach((button) => button.addEventListener('click', () => {
      category = button.dataset.category;
      $$('[data-category]').forEach((b) => b.setAttribute('aria-pressed', String(b === button)));
      filterCommands();
    }));
    $('[data-reset-search]').addEventListener('click', () => {
      search.value = '';
      category = 'Усі';
      $$('[data-category]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.category === category)));
      filterCommands();
      search.focus();
    });
  }

  // Status is the network entrypoint, never invented per-mode player counts.
  const badges = $$('[data-status]');
  const statusButtons = $$('[data-refresh-status]');
  let requestRunning = false;
  let lastCheck = 0;
  const statusCacheKey = 'minecrafter-status-v1:' + config.ip;
  function paintStatus(state, label, timeText = '') {
    badges.forEach((badge) => {
      badge.dataset.state = state;
      $('[data-status-label]', badge).textContent = label;
      badge.title = timeText;
    });
    $$('[data-status-time]').forEach((el) => { el.textContent = timeText; });
  }
  function showServerResult(data, timestamp) {
    const count = Number.isInteger(data.players?.online) && data.players.online >= 0 ? data.players.online : null;
    const time = new Date(timestamp).toLocaleTimeString('uk-UA', {hour:'2-digit',minute:'2-digit'});
    paintStatus(data.online ? 'online' : 'offline', data.online ? (count === null ? 'Сервер відповідає' : `Гравців у мережі: ${count}`) : 'Сервер не відповів на перевірку', `Дані mcsrvstat.us на ${time}. Кеш до 5 хвилин.`);
  }
  async function checkStatus(force = false) {
    if (!badges.length || requestRunning) return;
    if (!config.status.enabled) { paintStatus('unknown', 'Приєднуйся до спільноти'); return; }
    if (!force) {
      try {
        const cache = JSON.parse(sessionStorage.getItem(statusCacheKey));
        if (cache && Date.now() - cache.timestamp < config.status.refreshMs && typeof cache.data.online === 'boolean') {
          showServerResult(cache.data, cache.timestamp);
          lastCheck = cache.timestamp;
          return;
        }
      } catch { /* Storage may be disabled. Continue without caching. */ }
    }
    requestRunning = true;
    statusButtons.forEach((b) => { b.disabled = true; });
    paintStatus('loading', 'Перевіряємо сервер…');
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.status.timeoutMs);
    try {
      const response = await fetch(config.status.endpoint + encodeURIComponent(config.ip), {signal:controller.signal, credentials:'omit'});
      if (!response.ok) throw new Error('Status response failed');
      const result = await response.json();
      if (typeof result.online !== 'boolean') throw new Error('Invalid status payload');
      const data = {online:result.online, players:{online:result.players?.online}};
      // Use provider cache time when available instead of presenting old data as new.
      const cachetime = result.debug?.cachetime;
      const timestamp = Number.isFinite(cachetime) && cachetime > 0 && cachetime * 1000 <= Date.now() ? cachetime * 1000 : Date.now();
      if (Date.now() - timestamp > config.status.refreshMs * 2) throw new Error('Stale status');
      showServerResult(data, timestamp);
      lastCheck = Date.now();
      try { sessionStorage.setItem(statusCacheKey, JSON.stringify({timestamp,data})); } catch { /* Optional cache. */ }
    } catch {
      paintStatus('unknown', 'Статус зараз недоступний', 'Сервіс перевірки не відповів. Спробуй зайти через Minecraft або перевір оголошення у Discord.');
      lastCheck = Date.now();
    } finally {
      clearTimeout(timeout);
      requestRunning = false;
      statusButtons.forEach((b) => { b.disabled = false; });
    }
  }
  statusButtons.forEach((button) => button.addEventListener('click', () => checkStatus(true)));
  checkStatus();
  if (badges.length) {
    setInterval(() => { if (!document.hidden && Date.now() - lastCheck >= config.status.refreshMs) checkStatus(); }, config.status.refreshMs);
    document.addEventListener('visibilitychange', () => { if (!document.hidden && Date.now() - lastCheck >= config.status.refreshMs) checkStatus(); });
  }

  // Content is visible by default, including when JS or the observer is unavailable.
  if ('IntersectionObserver' in window && !motion.matches) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.remove('is-waiting');
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, {threshold:.07});
    $$('.reveal').forEach((el) => {
      if (el.getBoundingClientRect().top > window.innerHeight) el.classList.add('is-waiting');
      observer.observe(el);
    });
    motion.addEventListener('change', () => {
      if (motion.matches) { $$('.is-waiting').forEach((el) => el.classList.remove('is-waiting')); observer.disconnect(); }
    });
  }
  let scrollFrame = 0;
  const heroArt = $('.hero-art');
  const finePointer = window.matchMedia('(hover:hover) and (pointer:fine)');
  function paintScroll() {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    $('.scroll-progress').style.transform = `scaleX(${scrollable > 0 ? Math.min(1,window.scrollY / scrollable) : 0})`;
    if (heroArt && !motion.matches && finePointer.matches) heroArt.style.transform = `translateY(${Math.min(window.scrollY * .04, 18)}px)`;
    scrollFrame = 0;
  }
  window.addEventListener('scroll', () => { if (!scrollFrame) scrollFrame = requestAnimationFrame(paintScroll); }, {passive:true});
  window.addEventListener('resize', () => { if (!scrollFrame) scrollFrame = requestAnimationFrame(paintScroll); });
  if (finePointer.matches) $$('[data-tilt]').forEach((card) => {
    let frame = 0;
    card.addEventListener('pointermove', (event) => {
      if (motion.matches || frame) return;
      frame = requestAnimationFrame(() => {
        const box = card.getBoundingClientRect();
        card.style.setProperty('--tilt-y', ((event.clientX - box.left) / box.width - .5) * 2 + 'deg');
        card.style.setProperty('--tilt-x', ((event.clientY - box.top) / box.height - .5) * -2 + 'deg');
        frame = 0;
      });
    });
    card.addEventListener('pointerleave', () => {
      cancelAnimationFrame(frame); frame = 0;
      card.style.removeProperty('--tilt-x'); card.style.removeProperty('--tilt-y');
    });
  });
  $$('img').forEach((img) => {
    const failed = () => { img.classList.add('image-failed'); };
    img.addEventListener('error', failed);
    if (img.complete && !img.naturalWidth) failed();
  });
})();
