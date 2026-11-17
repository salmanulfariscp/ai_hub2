/*
 * favorites.js - bookmarks.
 *   Guests:         saved in localStorage (key aihub_favorites)
 *   Logged-in users: saved in the database through /favorites/toggle/ ; any bookmarks made as a guest
 *                    are copied to the database once (/favorites/sync/).
 * Any element with [data-fav-btn][data-slug] works as a bookmark button (event delegation).
 */
(function () {
    'use strict';
    var body = document.body;
    var authed = AIHub.isAuthenticated();
    var KEY = AIHub.KEYS.favorites;

    var serverEl = document.getElementById('favorite-slugs');
    var serverSlugs = [];
    try { serverSlugs = serverEl ? JSON.parse(serverEl.textContent) : []; } catch (e) { serverSlugs = []; }
    var saved = new Set(authed ? serverSlugs : AIHub.readList(KEY));

    function persistLocal() { if (!authed) AIHub.writeList(KEY, Array.from(saved)); }

    /* Update every bookmark / compare button inside `scope` to match the stored state */
    function syncButtons(scope) {
        (scope || document).querySelectorAll('[data-fav-btn]').forEach(function (btn) {
            var on = saved.has(btn.dataset.slug);
            btn.setAttribute('aria-pressed', on ? 'true' : 'false');
            var icon = btn.querySelector('i');
            if (icon) icon.className = on ? 'bi bi-heart-fill' : 'bi bi-heart';
        });
        if (AIHub.syncCompareButtons) AIHub.syncCompareButtons(scope);
    }

    function toggle(slug) {
        var finish = function (adding) {
            if (adding) saved.add(slug); else saved.delete(slug);
            persistLocal();
            syncButtons();
            AIHub.showToast(adding ? 'Saved to your favourites.' : 'Removed from your favourites.', adding ? 'success' : 'info');
            document.dispatchEvent(new CustomEvent('aihub:favorites-changed', { detail: { slug: slug, saved: adding } }));
        };
        if (authed) {
            AIHub.postJSON(body.dataset.favToggleUrl, { slug: slug })
                .then(function (result) { finish(result.favorited); })
                .catch(function () { AIHub.showToast('Could not update favourites. Please try again.', 'danger'); });
        } else {
            finish(!saved.has(slug));
        }
    }

    document.addEventListener('click', function (event) {
        var btn = event.target.closest('[data-fav-btn]');
        if (!btn) return;
        event.preventDefault();
        toggle(btn.dataset.slug);
    });

    /* After login: move guest bookmarks into the database one time */
    if (authed) {
        var local = AIHub.readList(KEY);
        if (local.length) {
            AIHub.postJSON(body.dataset.favSyncUrl, { slugs: local }).then(function (result) {
                saved = new Set(result.slugs);
                AIHub.writeList(KEY, []);
                syncButtons();
                document.dispatchEvent(new CustomEvent('aihub:favorites-changed', { detail: {} }));
                AIHub.showToast('Your saved tools were added to your account.', 'success');
            }).catch(function () { /* keep local copy and try again next page */ });
        }
    }

    AIHub.favorites = { has: function (slug) { return saved.has(slug); }, list: function () { return Array.from(saved); }, toggle: toggle };
    AIHub.syncButtons = syncButtons;
    document.addEventListener('DOMContentLoaded', function () { syncButtons(); });
})();
