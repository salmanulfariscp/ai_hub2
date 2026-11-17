/*
 * main.js - loaded on every page. Creates the shared window.AIHub object used by the other scripts:
 * theme switching, toasts, localStorage helpers, the tools API loader, form validation, recently viewed.
 */
(function () {
    'use strict';

    var KEYS = { theme: 'aihub_theme', favorites: 'aihub_favorites', compare: 'aihub_compare', recent: 'aihub_recent' };

    /* ---- localStorage helpers (wrapped in try/catch: storage can be blocked in private mode) */
    function readList(key) {
        try {
            var value = JSON.parse(localStorage.getItem(key) || '[]');
            return Array.isArray(value) ? value : [];
        } catch (e) { return []; }
    }
    function writeList(key, list) {
        try { localStorage.setItem(key, JSON.stringify(list)); } catch (e) { /* ignore */ }
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value).replace(/[&<>"']/g, function (ch) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
        });
    }

    function debounce(fn, wait) {
        var timer;
        return function () {
            var args = arguments, self = this;
            clearTimeout(timer);
            timer = setTimeout(function () { fn.apply(self, args); }, wait);
        };
    }

    /* ---- Toast notifications (Bootstrap toasts). level: success | danger | warning | info */
    function showToast(message, level) {
        level = level || 'info';
        var container = document.getElementById('toast-container');
        if (!container || !window.bootstrap) return;
        var el = document.createElement('div');
        el.className = 'toast aihub-toast align-items-center t-' + level;
        el.setAttribute('role', level === 'danger' ? 'alert' : 'status');
        el.setAttribute('aria-live', level === 'danger' ? 'assertive' : 'polite');
        el.innerHTML = '<div class="d-flex"><div class="toast-body">' + escapeHtml(message) +
            '</div><button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>';
        container.appendChild(el);
        el.addEventListener('hidden.bs.toast', function () { el.remove(); });
        new bootstrap.Toast(el, { delay: 4500 }).show();
    }

    /* Django messages (rendered in base.html) become toasts */
    function showDjangoMessages() {
        var box = document.getElementById('django-messages');
        if (!box) return;
        var map = { error: 'danger', success: 'success', warning: 'warning', info: 'info', debug: 'info' };
        box.querySelectorAll('[data-level]').forEach(function (item) {
            showToast(item.textContent.trim(), map[item.dataset.level] || 'info');
        });
    }

    /* ---- Server calls */
    function getCsrfToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.content : '';
    }
    function postJSON(url, data) {
        return fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken(), 'Accept': 'application/json' },
            body: JSON.stringify(data)
        }).then(function (response) {
            if (!response.ok) throw new Error('HTTP ' + response.status);
            return response.json();
        });
    }

    var toolsPromise = null;
    /* Loads every approved tool once per page and remembers the result. */
    function loadTools() {
        if (!toolsPromise) {
            toolsPromise = fetch(document.body.dataset.apiTools, { headers: { 'Accept': 'application/json' } })
                .then(function (response) {
                    if (!response.ok) throw new Error('HTTP ' + response.status);
                    return response.json();
                })
                .then(function (data) { return data.tools; });
            toolsPromise.catch(function () { toolsPromise = null; }); // allow a retry after a failure
        }
        return toolsPromise;
    }

    /* ---- Theme (dark / light) */
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        var icon = document.querySelector('#theme-toggle i');
        if (icon) icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
        var button = document.getElementById('theme-toggle');
        if (button) button.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    }
    function initTheme() {
        applyTheme(document.documentElement.getAttribute('data-bs-theme') || 'dark');
        var button = document.getElementById('theme-toggle');
        if (!button) return;
        button.addEventListener('click', function () {
            var next = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            try { localStorage.setItem(KEYS.theme, next); } catch (e) { /* ignore */ }
            applyTheme(next);
        });
    }

    /* ---- Form validation: forms with class "needs-validation" use the browser's checks + Bootstrap styles */
    function initFormValidation() {
        document.querySelectorAll('form.needs-validation').forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    var firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) firstInvalid.focus();
                }
                form.classList.add('was-validated');
            });
        });
    }

    /* ---- Recently viewed (guests): detail pages set <body data-tool-slug="...">
          Logged-in users are also tracked in the database (apps/tools/views.py). */
    function trackRecentlyViewed() {
        var slug = document.body.dataset.toolSlug;
        if (!slug) return;
        var list = readList(KEYS.recent).filter(function (s) { return s !== slug; });
        list.unshift(slug);
        writeList(KEYS.recent, list.slice(0, 8));
    }

    /* ---- Confirmation for dangerous actions: <form data-confirm="Are you sure?"> */
    function initConfirmForms() {
        document.querySelectorAll('form[data-confirm]').forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!window.confirm(form.dataset.confirm)) event.preventDefault();
            });
        });
    }

    window.AIHub = {
        KEYS: KEYS, readList: readList, writeList: writeList, escapeHtml: escapeHtml, debounce: debounce,
        showToast: showToast, postJSON: postJSON, loadTools: loadTools,
        isAuthenticated: function () { return document.body.dataset.auth === '1'; }
    };

    document.addEventListener('DOMContentLoaded', function () {
        initTheme();
        initFormValidation();
        initConfirmForms();
        showDjangoMessages();
        trackRecentlyViewed();
    });
})();
