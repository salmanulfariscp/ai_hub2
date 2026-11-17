/*
 * filters.js - pure functions (no DOM) for searching, filtering, sorting and paging tools.
 * Because it has no DOM code it can be tested in Node:  node tests/test_filters.js
 * Each "tool" is one object from the /api/tools/ JSON (see apps/tools/views.py -> api_tools).
 */
(function (root) {
    'use strict';

    function normalise(text) {
        return String(text || '').toLowerCase().trim();
    }

    /* Text we search in: name, tagline, category and platforms. */
    function haystack(tool) {
        return normalise([tool.name, tool.tagline, tool.category, (tool.platforms || []).join(' ')].join(' '));
    }

    /* filters = { q, category, pricing, openSource }
       pricing: 'any' | 'free-plan' (free or freemium) | 'free' (fully free) | 'paid' (paid only) */
    function filterTools(tools, filters) {
        var words = normalise(filters.q).split(/\s+/).filter(Boolean);
        return tools.filter(function (tool) {
            if (filters.category && tool.category_slug !== filters.category) return false;
            if (filters.openSource && !tool.open_source) return false;
            if (filters.pricing === 'free-plan' && !tool.free_plan) return false;
            if (filters.pricing === 'free' && tool.pricing !== 'free') return false;
            if (filters.pricing === 'paid' && tool.pricing !== 'paid') return false;
            var text = haystack(tool);
            return words.every(function (word) { return text.indexOf(word) !== -1; });
        });
    }

    /* mode: 'featured' | 'name-asc' | 'name-desc' | 'newest' | 'rating' */
    function sortTools(tools, mode) {
        var list = tools.slice(); // never change the original array
        var byName = function (a, b) { return a.name.localeCompare(b.name); };
        if (mode === 'name-desc') {
            list.sort(function (a, b) { return byName(b, a); });
        } else if (mode === 'newest') {
            list.sort(function (a, b) { return (b.added > a.added ? 1 : b.added < a.added ? -1 : 0) || byName(a, b); });
        } else if (mode === 'rating') {
            list.sort(function (a, b) { return ((b.rating || 0) - (a.rating || 0)) || ((b.review_count || 0) - (a.review_count || 0)) || byName(a, b); });
        } else if (mode === 'name-asc') {
            list.sort(byName);
        } else { // 'featured' (default): featured tools first, then A-Z
            list.sort(function (a, b) { return (Number(b.featured) - Number(a.featured)) || byName(a, b); });
        }
        return list;
    }

    function paginate(items, page, perPage) {
        var pages = Math.max(1, Math.ceil(items.length / perPage));
        var current = Math.min(Math.max(1, parseInt(page, 10) || 1), pages);
        return { page: current, pages: pages, total: items.length, items: items.slice((current - 1) * perPage, current * perPage) };
    }

    /* Search suggestions: names that start with the text come first. */
    function suggest(tools, query, limit) {
        var q = normalise(query);
        if (!q) return [];
        var matches = filterTools(tools, { q: q });
        matches.sort(function (a, b) {
            var aStart = normalise(a.name).indexOf(q) === 0 ? 0 : 1;
            var bStart = normalise(b.name).indexOf(q) === 0 ? 0 : 1;
            return (aStart - bStart) || a.name.localeCompare(b.name);
        });
        return matches.slice(0, limit || 6);
    }

    /* Page numbers to show, e.g. [1, '...', 4, 5, 6, '...', 12] */
    function pageWindow(current, total) {
        var pages = [];
        for (var i = 1; i <= total; i++) {
            if (i === 1 || i === total || Math.abs(i - current) <= 1) pages.push(i);
            else if (pages[pages.length - 1] !== '...') pages.push('...');
        }
        return pages;
    }

    var api = { filterTools: filterTools, sortTools: sortTools, paginate: paginate, suggest: suggest, pageWindow: pageWindow };
    if (typeof module !== 'undefined' && module.exports) module.exports = api;
    else root.AIHubFilters = api;
})(typeof window !== 'undefined' ? window : this);
