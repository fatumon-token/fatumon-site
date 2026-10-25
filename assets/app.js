/* Fatumon — витрина. Без сборки, без зависимостей. */
(function () {
  'use strict';

  var ROOT = new URL('..', document.currentScript.src);
  var html = document.documentElement;
  var REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var DICT = {};
  var LANG = 'ru';
  var updatedAt = null;

  /* ---------- i18n ---------- */
  function detectLang() {
    var q = new URLSearchParams(location.search).get('lang');
    if (q === 'ru' || q === 'en') {
      try { localStorage.setItem('lang', q); } catch (e) {}
      return q;
    }
    try {
      var s = localStorage.getItem('lang');
      if (s === 'ru' || s === 'en') return s;
    } catch (e) {}
    var n = (navigator.language || '').toLowerCase();
    if (!n) return 'ru';
    return n.indexOf('ru') === 0 ? 'ru' : 'en';
  }

  function t(key) {
    return Object.prototype.hasOwnProperty.call(DICT, key) ? DICT[key] : null;
  }

  function applyDict() {
    html.setAttribute('lang', LANG);
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var v = t(el.getAttribute('data-i18n'));
      if (v != null) el.textContent = v;
    });
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var v = t(el.getAttribute('data-i18n-html'));
      if (v != null) el.innerHTML = v;
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
      el.getAttribute('data-i18n-attr').split(';').forEach(function (pair) {
        var i = pair.indexOf(':');
        if (i < 0) return;
        var attr = pair.slice(0, i).trim();
        var v = t(pair.slice(i + 1).trim());
        if (v != null) el.setAttribute(attr, v);
      });
    });
    document.querySelectorAll('[data-lang]').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-lang') === LANG ? 'true' : 'false');
    });
    renderUpdated();
  }

  function loadLang(lang) {
    LANG = lang;
    var url = new URL('i18n/' + lang + '.json', ROOT);
    return fetch(url.href, { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error(String(r.status)); return r.json(); })
      .then(function (d) { DICT = d; })
      .catch(function () { DICT = {}; })
      .then(function () {
        applyDict();
        html.classList.remove('i18n-loading');
      });
  }

  function initLang() {
    loadLang(detectLang());
    // в любом случае показать текст не позже чем через 300 мс
    setTimeout(function () { html.classList.remove('i18n-loading'); }, 300);

    document.querySelectorAll('[data-lang]').forEach(function (b) {
      b.addEventListener('click', function () {
        var lang = b.getAttribute('data-lang');
        if (lang !== 'ru' && lang !== 'en') return;
        try { localStorage.setItem('lang', lang); } catch (e) {}
        // убрать ?lang из адреса, чтобы выбор не перебивался при перезагрузке
        if (new URLSearchParams(location.search).has('lang')) {
          var u = new URL(location.href);
          u.searchParams.delete('lang');
          history.replaceState(null, '', u.pathname + (u.search || '') + u.hash);
        }
        loadLang(lang);
      });
    });
  }

  /* ---------- навигация ---------- */
  function initNav() {
    var page = document.body.getAttribute('data-page');
    document.querySelectorAll('[data-nav]').forEach(function (a) {
      if (a.getAttribute('data-nav') === page) a.setAttribute('aria-current', 'page');
    });

    var burger = document.querySelector('.burger');
    var nav = document.getElementById('nav');
    if (!burger || !nav) return;

    function setOpen(open) {
      nav.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    }
    burger.addEventListener('click', function () {
      setOpen(!nav.classList.contains('open'));
    });
    document.addEventListener('click', function (e) {
      if (!nav.classList.contains('open')) return;
      if (nav.contains(e.target) || burger.contains(e.target)) return;
      setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') setOpen(false);
    });
    window.matchMedia('(min-width: 821px)').addEventListener('change', function (m) {
      if (m.matches) setOpen(false);
    });
  }

  /* ---------- звёзды ---------- */
  function initStars() {
    var canvas = document.getElementById('stars');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var N = 70;
    var W, H, CX, CY, R;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var stars = [];
    var raf = 0;
    var pausedAt = 0;

    function resize() {
      W = window.innerWidth; H = window.innerHeight;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      CX = W / 2; CY = H / 2;
      R = Math.hypot(CX, CY) + 24;
    }

    function spawn(s, now, initial) {
      s.a = Math.random() * Math.PI * 2;
      s.d = 2500 + Math.random() * 4500;           // полёт 2.5–7 с
      s.t0 = now - (initial ? Math.random() * s.d : 0);
      s.sz = 2 + Math.random();                      // 2–3 px
    }

    function drawStatic() {
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = '#DCE7FF';
      for (var i = 0; i < N; i++) {
        var a = Math.random() * Math.PI * 2;
        var r = Math.sqrt(Math.random()) * R * 0.95;
        ctx.globalAlpha = 0.35 + Math.random() * 0.55;
        ctx.beginPath();
        ctx.arc(CX + Math.cos(a) * r, CY + Math.sin(a) * r, (2 + Math.random()) / 2, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    }

    function frame(now) {
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = '#DCE7FF';
      for (var i = 0; i < N; i++) {
        var s = stars[i];
        var p = (now - s.t0) / s.d;
        if (p >= 1) { spawn(s, now, false); p = 0; }
        var e = 0.03 + p * p * 0.97;                 // ускорение к краю
        var x = CX + Math.cos(s.a) * e * R;
        var y = CY + Math.sin(s.a) * e * R;
        var scale = 0.6 + p * 1.0;                   // .6 → 1.6
        ctx.globalAlpha = Math.min(1, p / 0.18);     // появление из прозрачности
        ctx.beginPath();
        ctx.arc(x, y, s.sz * scale / 2, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      raf = requestAnimationFrame(frame);
    }

    resize();
    window.addEventListener('resize', function () {
      resize();
      if (REDUCED) drawStatic();
    });

    if (REDUCED) { drawStatic(); return; }

    var now0 = performance.now();
    for (var i = 0; i < N; i++) { var s = {}; spawn(s, now0, true); stars.push(s); }
    raf = requestAnimationFrame(frame);

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        cancelAnimationFrame(raf); raf = 0;
        pausedAt = performance.now();
      } else if (!raf) {
        var shift = performance.now() - pausedAt;
        stars.forEach(function (s) { s.t0 += shift; });
        raf = requestAnimationFrame(frame);
      }
    });
  }

  /* ---------- счётчики (пиксельные экранчики) ---------- */
  function pad2(n) { return (n < 10 ? '0' : '') + n; }

  function renderUpdated() {
    var el = document.querySelector('[data-stats-updated]');
    if (!el || !updatedAt) return;
    var d = new Date(updatedAt);
    if (isNaN(d.getTime())) return;
    el.textContent = 'updated ' + pad2(d.getUTCHours()) + ':' + pad2(d.getUTCMinutes()) + ' UTC';
  }

  function initStats() {
    var els = document.querySelectorAll('[data-stat]');
    if (!els.length) return;
    var current = {};   // текущее показанное значение по ключу
    var timers = {};    // идущие анимации по ключу
    var started = false;

    els.forEach(function (el) {
      current[el.getAttribute('data-stat')] = 0;
      el.textContent = '0';
    });

    function fetchStats() {
      var stamp = Math.floor(Date.now() / 3600000);
      return fetch(new URL('stats.json?t=' + stamp, ROOT).href, { cache: 'no-cache' })
        .then(function (r) { if (!r.ok) throw new Error(String(r.status)); return r.json(); })
        .then(function (d) {
          if (d && d.updated_at) { updatedAt = d.updated_at; renderUpdated(); }
          return d;
        })
        .catch(function () { return null; });
    }

    // «пробег» табло: дискретные шаги, ~24 обновления в секунду
    function runTo(el, key, target) {
      if (timers[key]) { cancelAnimationFrame(timers[key]); timers[key] = 0; }
      var from = current[key] || 0;
      if (REDUCED || from === target) {
        current[key] = target; el.textContent = String(target); return;
      }
      var dur = Math.min(2000, 900 + Math.abs(target - from) * 2);
      var t0 = 0, lastShown = null;
      function step(now) {
        if (!t0) t0 = now;
        var p = Math.min(1, (now - t0) / dur);
        var e = 1 - Math.pow(1 - p, 2.2);
        var frames = Math.floor(p * dur / 42);          // дискретный шаг ~42 мс
        var v = Math.round(from + (target - from) * e);
        if (frames !== lastShown || p >= 1) {
          el.textContent = String(p >= 1 ? target : v);
          lastShown = frames;
        }
        if (p < 1) timers[key] = requestAnimationFrame(step);
        else { timers[key] = 0; current[key] = target; }
      }
      timers[key] = requestAnimationFrame(step);
    }

    function applyData(data) {
      els.forEach(function (el) {
        var key = el.getAttribute('data-stat');
        var fallback = parseInt(el.getAttribute('data-fallback') || '0', 10) || 0;
        var v = data && typeof data[key] === 'number' ? Math.round(data[key]) : fallback;
        runTo(el, key, v);
      });
    }

    function start() {
      if (started) return;
      started = true;
      Promise.race([fetchStats(), new Promise(function (res) { setTimeout(function () { res(null); }, 1500); })])
        .then(applyData);
    }

    function refresh() {
      if (!started || document.hidden) return;
      fetchStats().then(function (d) { if (d) applyData(d); });
    }

    var box = document.querySelector('.stats') || els[0];
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries.some(function (e) { return e.isIntersecting; })) { io.disconnect(); start(); }
      }, { threshold: 0.2 });
      io.observe(box);
    } else {
      start();
    }

    // раз в час и при возврате на вкладку — подхватить новый stats.json без перезагрузки
    setInterval(refresh, 60 * 60 * 1000);
    document.addEventListener('visibilitychange', function () { if (!document.hidden) refresh(); });
  }

  /* ---------- маскот ---------- */
  function initMascot() {
    var svg = document.getElementById('mascot');
    if (!svg) return;
    var pupils = svg.querySelectorAll('.pupil');
    if (!pupils.length) return;
    var EYE_R = 10;
    var MAX = EYE_R * 0.45;
    var touch = window.matchMedia('(hover: none)').matches;
    var cur = { x: 0, y: 0 }, target = { x: 0, y: 0 };
    var raf = 0;

    function setPupils(x, y) {
      var tr = 'translate(' + x.toFixed(2) + ' ' + y.toFixed(2) + ')';
      pupils.forEach(function (p) { p.setAttribute('transform', tr); });
    }

    function tick() {
      cur.x += (target.x - cur.x) * 0.18;
      cur.y += (target.y - cur.y) * 0.18;
      setPupils(cur.x, cur.y);
      if (Math.abs(target.x - cur.x) > 0.02 || Math.abs(target.y - cur.y) > 0.02) {
        raf = requestAnimationFrame(tick);
      } else { raf = 0; }
    }
    function schedule() { if (!raf) raf = requestAnimationFrame(tick); }

    if (REDUCED) return;

    if (!touch) {
      window.addEventListener('pointermove', function (e) {
        var r = svg.getBoundingClientRect();
        var cx = r.left + r.width / 2, cy = r.top + r.height * 0.47;
        var dx = e.clientX - cx, dy = e.clientY - cy;
        var dist = Math.hypot(dx, dy) || 1;
        var f = Math.min(1, dist / 260);
        target.x = dx / dist * MAX * f;
        target.y = dy / dist * MAX * f;
        schedule();
      }, { passive: true });
    } else {
      // «оглядывается»: раз в 1.6–3 с смотрит в случайную сторону
      (function look() {
        var a = Math.random() * Math.PI * 2;
        var m = (0.4 + Math.random() * 0.6) * MAX;
        target.x = Math.cos(a) * m; target.y = Math.sin(a) * m * 0.8;
        schedule();
        setTimeout(look, 1600 + Math.random() * 1400);
      })();
    }

    // моргание каждые ~4 с
    var wrap = svg.closest('.mascot') || svg;
    (function blink() {
      setTimeout(function () {
        wrap.classList.add('blink');
        setTimeout(function () { wrap.classList.remove('blink'); }, 130);
        blink();
      }, 3400 + Math.random() * 1200);
    })();
  }

  /* ---------- старт ---------- */
  function init() {
    initNav();
    initLang();
    initStars();
    initStats();
    initMascot();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
