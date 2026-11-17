/*
 * search.js - two features:
 *   1. Live search suggestions for any ".search-box" (homepage hero)
 *   2. The Explore / Category page explorer (#explorer): real-time search, filters, sorting, pagination
 * The filtering rules themselves live in filters.js.
 */
(function () {
    'use strict';
    var esc = function (v) { return AIHub.escapeHtml(v); };

    /* ============================================================ 1. Suggestions */
    function initSuggestions(box) {
        var input = box.querySelector('input[type="search"]');
        var list = box.querySelector('.suggest-list');
        if (!input || !list) return;
        var exploreUrl = document.body.dataset.exploreUrl;
        var active = -1;

        function close() { list.hidden = true; input.setAttribute('aria-expanded', 'false'); active = -1; }
        function items() { return Array.prototype.slice.call(list.querySelectorAll('a')); }
        function highlight(index) {
            var links = items();
            if (!links.length) return;
            active = (index + links.length) % links.length;
            links.forEach(function (a, i) { a.classList.toggle('is-active', i === active); });
        }

        function show(query) {
            AIHub.loadTools().then(function (tools) {
                var matches = AIHubFilters.suggest(tools, query, 6);
                var html = matches.map(function (t) {
                    return '<li role="option"><a href="' + esc(t.url) + '">' + AIHub.logoHtml(t) +
                        '<span><strong>' + esc(t.name) + '</strong><small>' + esc(t.category) + ' &middot; ' + esc(t.pricing_label) + '</small></span></a></li>';
                }).join('');
                if (!matches.length) html = '<li class="suggest-empty">No tools match "' + esc(query) + '" yet.</li>';
                else html += '<li><a href="' + esc(exploreUrl) + '?q=' + encodeURIComponent(query) + '"><i class="bi bi-search"></i> See all results for "' + esc(query) + '"</a></li>';
                list.innerHTML = html;
                list.hidden = false;
                input.setAttribute('aria-expanded', 'true');
                active = -1;
            }).catch(close);
        }

        input.addEventListener('input', AIHub.debounce(function () {
            var query = input.value.trim();
            if (query.length < 1) { close(); return; }
            show(query);
        }, 150));
        input.addEventListener('keydown', function (event) {
            if (event.key === 'ArrowDown') { event.preventDefault(); highlight(active + 1); }
            else if (event.key === 'ArrowUp') { event.preventDefault(); highlight(active - 1); }
            else if (event.key === 'Escape') { close(); }
            else if (event.key === 'Enter' && active >= 0) { event.preventDefault(); items()[active].click(); }
        });
        document.addEventListener('click', function (event) { if (!box.contains(event.target)) close(); });
    }

    /* ============================================================ 2. Explorer */
    function initExplorer(root) {
        var PER_PAGE = parseInt(root.dataset.perPage, 10) || 12;
        var fixedCategory = root.dataset.category || '';
        var els = {
            q: document.getElementById('q'),
            pills: document.getElementById('category-pills'),
            pricing: document.getElementById('pricing'),
            oss: document.getElementById('open-source'),
            sort: document.getElementById('sort'),
            results: document.getElementById('results'),
            count: document.getElementById('result-count'),
            pagination: document.getElementById('pagination'),
            clear: document.getElementById('clear-filters')
        };
        var allTools = [];
        var params = new URLSearchParams(window.location.search);
        var state = {
            q: params.get('q') || '',
            category: fixedCategory || params.get('category') || '',
            pricing: params.get('pricing') || 'any',
            openSource: params.get('oss') === '1',
            sort: params.get('sort') || 'featured',
            page: parseInt(params.get('page'), 10) || 1
        };

        function writeControls() {
            els.q.value = state.q;
            els.pricing.value = state.pricing;
            els.oss.checked = state.openSource;
            els.sort.value = state.sort;
            if (els.pills) {
                els.pills.querySelectorAll('[data-cat]').forEach(function (btn) {
                    var on = btn.dataset.cat === state.category;
                    btn.classList.toggle('active', on);
                    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
                });
            }
        }

        function updateUrl() {
            var p = new URLSearchParams();
            if (state.q) p.set('q', state.q);
            if (!fixedCategory && state.category) p.set('category', state.category);
            if (state.pricing !== 'any') p.set('pricing', state.pricing);
            if (state.openSource) p.set('oss', '1');
            if (state.sort !== 'featured') p.set('sort', state.sort);
            if (state.page > 1) p.set('page', state.page);
            var query = p.toString();
            try { history.replaceState(null, '', window.location.pathname + (query ? '?' + query : '')); } catch (e) { /* ignore */ }
        }

        function paginationHtml(info) {
            if (info.pages <= 1) return '';
            var html = '<nav aria-label="Tool pages"><ul class="pagination justify-content-center flex-wrap mb-0">';
            html += '<li class="page-item' + (info.page === 1 ? ' disabled' : '') + '"><button class="page-link" data-page="' + (info.page - 1) + '" aria-label="Previous page">&laquo;</button></li>';
            AIHubFilters.pageWindow(info.page, info.pages).forEach(function (p) {
                if (p === '...') html += '<li class="page-item disabled"><span class="page-link">&hellip;</span></li>';
                else html += '<li class="page-item' + (p === info.page ? ' active' : '') + '"><button class="page-link" data-page="' + p + '"' + (p === info.page ? ' aria-current="page"' : '') + '>' + p + '</button></li>';
            });
            html += '<li class="page-item' + (info.page === info.pages ? ' disabled' : '') + '"><button class="page-link" data-page="' + (info.page + 1) + '" aria-label="Next page">&raquo;</button></li></ul></nav>';
            return html;
        }

        function render() {
            var filtered = AIHubFilters.sortTools(AIHubFilters.filterTools(allTools, state), state.sort);
            var info = AIHubFilters.paginate(filtered, state.page, PER_PAGE);
            state.page = info.page;
            if (!info.total) {
                els.results.innerHTML = '<div class="col-12">' + AIHub.emptyStateHtml('bi-search', 'No tools found',
                    'Nothing matches your search and filters. Try a different word or clear the filters.',
                    '<button type="button" class="btn btn-brand btn-sm" data-clear-filters>Clear filters</button>') + '</div>';
            } else {
                AIHub.renderCards(els.results, info.items);
            }
            els.count.textContent = info.total + (info.total === 1 ? ' tool' : ' tools') + ' found';
            els.pagination.innerHTML = paginationHtml(info);
            updateUrl();
        }

        function reset() {
            state.q = ''; state.pricing = 'any'; state.openSource = false; state.sort = 'featured'; state.page = 1;
            if (!fixedCategory) state.category = '';
            writeControls();
            render();
        }

        els.q.addEventListener('input', AIHub.debounce(function () { state.q = els.q.value; state.page = 1; render(); }, 150));
        els.pricing.addEventListener('change', function () { state.pricing = els.pricing.value; state.page = 1; render(); });
        els.oss.addEventListener('change', function () { state.openSource = els.oss.checked; state.page = 1; render(); });
        els.sort.addEventListener('change', function () { state.sort = els.sort.value; state.page = 1; render(); });
        if (els.pills) {
            els.pills.addEventListener('click', function (event) {
                var btn = event.target.closest('[data-cat]');
                if (!btn) return;
                state.category = btn.dataset.cat;
                state.page = 1;
                writeControls();
                render();
            });
        }
        els.pagination.addEventListener('click', function (event) {
            var btn = event.target.closest('[data-page]');
            if (!btn || btn.closest('.disabled')) return;
            state.page = parseInt(btn.dataset.page, 10);
            render();
            root.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
        els.clear.addEventListener('click', reset);
        root.addEventListener('click', function (event) { if (event.target.closest('[data-clear-filters]')) reset(); });
        document.addEventListener('aihub:favorites-changed', function () { AIHub.syncButtons(els.results); });

        writeControls();
        AIHub.skeletonCards(els.results, 6);
        AIHub.loadTools().then(function (tools) {
            allTools = tools;
            render();
        }).catch(function () {
            els.results.innerHTML = '<div class="col-12">' + AIHub.emptyStateHtml('bi-wifi-off', 'Could not load tools',
                'Something went wrong while loading the directory. Reload the page to try again.') + '</div>';
            els.count.textContent = '';
            AIHub.showToast('Could not load the tool list.', 'danger');
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.search-box').forEach(initSuggestions);
        var explorer = document.getElementById('explorer');
        if (explorer) initExplorer(explorer);
    });
})();
