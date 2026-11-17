/*
 * cards.js - builds tool-card HTML in JavaScript (used by Explore, Favorites, Compare and search).
 * The markup matches templates/partials/_tool_card.html, which the server uses on the homepage.
 */
(function () {
    'use strict';
    var esc = function (v) { return AIHub.escapeHtml(v); };

    function logoHtml(tool, large) {
        var src = 'https://www.google.com/s2/favicons?domain=' + encodeURIComponent(tool.domain) + '&sz=64';
        return '<span class="tool-logo tone-' + esc(tool.category_order) + (large ? ' lg' : '') + '" aria-hidden="true">' +
            '<span>' + esc(tool.name.charAt(0).toUpperCase()) + '</span>' +
            '<img src="' + esc(src) + '" alt="" loading="lazy" onerror="this.remove()"></span>';
    }

    function badgesHtml(tool) {
        var html = '<span class="badge-price price-' + esc(tool.pricing) + '">' + esc(tool.pricing_label) + '</span>';
        if (tool.open_source) html += '<span class="badge-oss">Open source</span>';
        if (tool.rating) html += '<span class="rating-chip"><i class="bi bi-star-fill"></i> ' + esc(tool.rating.toFixed(1)) + '</span>';
        return html;
    }

    function cardHtml(tool) {
        return '<article class="tool-card" data-slug="' + esc(tool.slug) + '">' +
            '<div class="tool-card-head">' + logoHtml(tool) +
            '<div class="min-w-0"><h3 class="tool-card-title"><a href="' + esc(tool.url) + '">' + esc(tool.name) + '</a></h3>' +
            '<span class="tool-card-cat">' + esc(tool.category) + '</span></div>' +
            '<button type="button" class="icon-btn ms-auto" data-fav-btn data-slug="' + esc(tool.slug) + '" aria-pressed="false" ' +
            'aria-label="Save ' + esc(tool.name) + ' to favourites"><i class="bi bi-heart"></i></button></div>' +
            '<p class="tool-card-text">' + esc(tool.tagline) + '</p>' +
            '<div class="tool-card-badges">' + badgesHtml(tool) + '</div>' +
            '<div class="tool-card-actions"><a class="btn btn-sm btn-ghost" href="' + esc(tool.url) + '">View details</a>' +
            '<button type="button" class="btn btn-sm btn-ghost" data-compare-btn data-slug="' + esc(tool.slug) + '" aria-pressed="false">' +
            '<i class="bi bi-columns-gap"></i> <span class="label">Compare</span></button></div></article>';
    }

    /* Draw many cards into a Bootstrap grid. `container` is a .row element. */
    function renderCards(container, tools) {
        container.innerHTML = tools.map(function (tool) {
            return '<div class="col-md-6 col-xl-4">' + cardHtml(tool) + '</div>';
        }).join('');
        if (AIHub.syncButtons) AIHub.syncButtons(container);
    }

    function skeletonCards(container, count) {
        var html = '';
        for (var i = 0; i < count; i++) html += '<div class="col-md-6 col-xl-4"><div class="skeleton" aria-hidden="true"></div></div>';
        container.innerHTML = html;
    }

    function emptyStateHtml(icon, title, text, actionHtml) {
        return '<div class="empty-state"><i class="bi ' + esc(icon) + '"></i><h3>' + esc(title) + '</h3><p>' + esc(text) + '</p>' + (actionHtml || '') + '</div>';
    }

    AIHub.logoHtml = logoHtml;
    AIHub.cardHtml = cardHtml;
    AIHub.renderCards = renderCards;
    AIHub.skeletonCards = skeletonCards;
    AIHub.emptyStateHtml = emptyStateHtml;
})();
