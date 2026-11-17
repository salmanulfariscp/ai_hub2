/*
 * compare.js - choose up to 3 tools to compare.
 *   * Any [data-compare-btn][data-slug] toggles a tool in the selection (stored in localStorage)
 *   * A floating tray shows how many are selected
 *   * On the Compare page (#compare-app) it also draws the picker and the comparison table
 */
(function () {
    'use strict';
    var KEY = AIHub.KEYS.compare;
    var MAX = 3;
    var selected = AIHub.readList(KEY).slice(0, MAX);
    var esc = function (v) { return AIHub.escapeHtml(v); };

    function save() { AIHub.writeList(KEY, selected); }

    function syncCompareButtons(scope) {
        (scope || document).querySelectorAll('[data-compare-btn]').forEach(function (btn) {
            var on = selected.indexOf(btn.dataset.slug) !== -1;
            btn.setAttribute('aria-pressed', on ? 'true' : 'false');
            btn.classList.toggle('active', on);
            var label = btn.querySelector('.label');
            if (label) label.textContent = on ? 'Added' : 'Compare';
        });
    }

    function updateTray() {
        var tray = document.getElementById('compare-tray');
        if (!tray) return;
        var onComparePage = !!document.getElementById('compare-app');
        tray.hidden = selected.length === 0 || onComparePage;
        var count = document.getElementById('compare-count');
        if (count) count.textContent = selected.length + (selected.length === 1 ? ' tool selected' : ' tools selected');
    }

    function changed() {
        save();
        syncCompareButtons();
        updateTray();
        document.dispatchEvent(new CustomEvent('aihub:compare-changed'));
    }

    function add(slug) {
        if (selected.indexOf(slug) !== -1) return true;
        if (selected.length >= MAX) {
            AIHub.showToast('You can compare up to ' + MAX + ' tools. Remove one first.', 'warning');
            return false;
        }
        selected.push(slug);
        changed();
        return true;
    }
    function remove(slug) {
        selected = selected.filter(function (s) { return s !== slug; });
        changed();
    }
    function toggle(slug) {
        if (selected.indexOf(slug) !== -1) { remove(slug); AIHub.showToast('Removed from comparison.', 'info'); }
        else if (add(slug)) { AIHub.showToast('Added to comparison.', 'success'); }
    }

    document.addEventListener('click', function (event) {
        var btn = event.target.closest('[data-compare-btn]');
        if (btn) { event.preventDefault(); toggle(btn.dataset.slug); return; }
        if (event.target.closest('#compare-clear')) { selected = []; changed(); }
    });

    AIHub.compare = { list: function () { return selected.slice(); }, add: add, remove: remove, toggle: toggle };
    AIHub.syncCompareButtons = syncCompareButtons;

    /* ------------------------------------------------ Compare page */
    var app = document.getElementById('compare-app');

    function listHtml(items) {
        if (!items || !items.length) return '<span class="text-muted">Not listed</span>';
        return '<ul>' + items.map(function (i) { return '<li>' + esc(i) + '</li>'; }).join('') + '</ul>';
    }

    function tableHtml(tools) {
        var head = '<tr><th class="row-label" scope="row">Tool</th>' + tools.map(function (t) {
            return '<td><div class="d-flex align-items-center gap-2 mb-2">' + AIHub.logoHtml(t) +
                '<div><a class="fw-semibold" href="' + esc(t.url) + '">' + esc(t.name) + '</a></div></div>' +
                '<button type="button" class="btn btn-sm btn-ghost" data-remove-compare="' + esc(t.slug) + '"><i class="bi bi-x-lg"></i> Remove</button></td>';
        }).join('') + '</tr>';
        var rows = [
            ['Category', function (t) { return esc(t.category); }],
            ['Pricing', function (t) { return '<span class="badge-price price-' + esc(t.pricing) + '">' + esc(t.pricing_label) + '</span>'; }],
            ['Free plan', function (t) { return t.free_plan ? '<i class="bi bi-check-circle-fill text-success"></i> Yes' : '<i class="bi bi-x-circle-fill text-danger"></i> No'; }],
            ['Open source', function (t) { return t.open_source ? 'Yes' : 'No'; }],
            ['Platforms', function (t) { return listHtml(t.platforms); }],
            ['Main capabilities', function (t) { return listHtml(t.features); }],
            ['Best for', function (t) { return listHtml(t.use_cases); }],
            ['Advantages', function (t) { return listHtml(t.pros); }],
            ['Disadvantages', function (t) { return listHtml(t.cons); }],
            ['Official website', function (t) { return '<a href="' + esc(t.website) + '" target="_blank" rel="noopener noreferrer nofollow">' + esc(t.domain) + ' <i class="bi bi-box-arrow-up-right"></i></a>'; }]
        ];
        return '<div class="compare-table-wrap"><table class="compare-table"><caption class="visually-hidden">Tool comparison</caption><tbody>' + head +
            rows.map(function (row) {
                return '<tr><th class="row-label" scope="row">' + row[0] + '</th>' +
                    tools.map(function (t) { return '<td>' + row[1](t) + '</td>'; }).join('') + '</tr>';
            }).join('') + '</tbody></table></div>';
    }

    function initComparePage() {
        var results = document.getElementById('compare-results');
        var slots = document.getElementById('compare-slots');
        var input = document.getElementById('picker-input');
        var pickerList = document.getElementById('picker-results');
        var allTools = [];

        function bySlug(slug) { return allTools.filter(function (t) { return t.slug === slug; })[0]; }

        function renderSlots() {
            var html = '';
            for (var i = 0; i < MAX; i++) {
                var tool = bySlug(selected[i]);
                html += '<div class="col-md-4"><div class="compare-slot' + (tool ? ' filled' : '') + '">' +
                    (tool ? AIHub.logoHtml(tool) + '<div class="min-w-0"><strong>' + esc(tool.name) + '</strong><div class="small text-muted">' + esc(tool.category) + '</div></div>' +
                        '<button type="button" class="icon-btn ms-auto" data-remove-compare="' + esc(tool.slug) + '" aria-label="Remove ' + esc(tool.name) + '"><i class="bi bi-x-lg"></i></button>'
                        : '<span class="text-muted"><i class="bi bi-plus-circle"></i> Slot ' + (i + 1) + (i < 2 ? '' : ' (optional)') + '</span>') +
                    '</div></div>';
            }
            slots.innerHTML = html;
        }

        function renderResults() {
            var tools = selected.map(bySlug).filter(Boolean);
            if (tools.length < 2) {
                results.innerHTML = AIHub.emptyStateHtml('bi-columns-gap', 'Pick at least two tools',
                    'Search below or use the Compare button on any tool card. You can compare up to three tools side by side.');
            } else {
                results.innerHTML = tableHtml(tools);
            }
        }

        function renderPicker() {
            var q = input.value;
            var matches = AIHubFilters.filterTools(allTools, { q: q }).slice(0, 8);
            if (!matches.length) {
                pickerList.innerHTML = '<div class="p-3 text-muted">No tools match "' + esc(q) + '".</div>';
                return;
            }
            pickerList.innerHTML = matches.map(function (t) {
                var picked = selected.indexOf(t.slug) !== -1;
                return '<button type="button" class="picker-item" data-pick="' + esc(t.slug) + '"' + (picked ? ' disabled' : '') + '>' +
                    AIHub.logoHtml(t) + '<span class="min-w-0"><strong>' + esc(t.name) + '</strong><small class="d-block text-muted">' + esc(t.category) + '</small></span>' +
                    '<span class="ms-auto small">' + (picked ? 'Selected' : '<i class="bi bi-plus-lg"></i> Add') + '</span></button>';
            }).join('');
        }

        function refresh() { renderSlots(); renderResults(); renderPicker(); }

        AIHub.skeletonCards(results, 3);
        AIHub.loadTools().then(function (tools) {
            allTools = tools;
            // Support shared links such as /compare/?tools=chatgpt,claude
            var fromUrl = new URLSearchParams(window.location.search).get('tools');
            if (fromUrl) {
                selected = fromUrl.split(',').map(function (s) { return s.trim(); })
                    .filter(function (s) { return bySlug(s); }).slice(0, MAX);
                save();
            }
            selected = selected.filter(function (s) { return bySlug(s); });
            save();
            refresh();
        }).catch(function () {
            results.innerHTML = AIHub.emptyStateHtml('bi-wifi-off', 'Could not load tools', 'Check your connection and reload the page.');
        });

        input.addEventListener('input', AIHub.debounce(renderPicker, 120));
        document.addEventListener('aihub:compare-changed', refresh);
        app.addEventListener('click', function (event) {
            var pick = event.target.closest('[data-pick]');
            if (pick) { add(pick.dataset.pick); return; }
            var rm = event.target.closest('[data-remove-compare]');
            if (rm) remove(rm.dataset.removeCompare);
        });
        document.getElementById('compare-share').addEventListener('click', function () {
            if (!selected.length) { AIHub.showToast('Select some tools first.', 'warning'); return; }
            var link = window.location.origin + window.location.pathname + '?tools=' + selected.join(',');
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(link).then(function () { AIHub.showToast('Comparison link copied.', 'success'); },
                    function () { AIHub.showToast(link, 'info'); });
            } else { AIHub.showToast(link, 'info'); }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        syncCompareButtons();
        updateTray();
        if (app) initComparePage();
    });
})();
