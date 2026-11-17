// Run with:  node tests/test_filters.js   (tests static/js/filters.js - no browser needed)
const assert = require('assert');
const F = require('../static/js/filters.js');

const tools = [
  { name: 'ChatGPT', tagline: 'Assistant', category: 'AI Chatbots', category_slug: 'ai-chatbots', pricing: 'freemium', free_plan: true, open_source: false, featured: true, platforms: ['Web'], added: '2026-01-02', rating: null },
  { name: 'Midjourney', tagline: 'Images', category: 'Image Generation', category_slug: 'image-generation', pricing: 'paid', free_plan: false, open_source: false, featured: false, platforms: ['Discord'], added: '2026-01-03', rating: 4.5, review_count: 2 },
  { name: 'Continue', tagline: 'Open-source coding', category: 'Coding Assistants', category_slug: 'coding-assistants', pricing: 'free', free_plan: true, open_source: true, featured: false, platforms: ['VS Code'], added: '2026-01-01', rating: 5, review_count: 1 },
  { name: 'Claude', tagline: 'Assistant', category: 'AI Chatbots', category_slug: 'ai-chatbots', pricing: 'freemium', free_plan: true, open_source: false, featured: true, platforms: ['Web'], added: '2026-01-04', rating: null },
];
const names = (l) => l.map((t) => t.name);

assert.deepStrictEqual(names(F.filterTools(tools, { q: 'image' })), ['Midjourney']);
assert.deepStrictEqual(names(F.filterTools(tools, { q: 'ai chatbots assistant' })), ['ChatGPT', 'Claude']);
assert.deepStrictEqual(names(F.filterTools(tools, { category: 'coding-assistants' })), ['Continue']);
assert.deepStrictEqual(names(F.filterTools(tools, { pricing: 'free-plan' })), ['ChatGPT', 'Continue', 'Claude']);
assert.deepStrictEqual(names(F.filterTools(tools, { pricing: 'free' })), ['Continue']);
assert.deepStrictEqual(names(F.filterTools(tools, { pricing: 'paid' })), ['Midjourney']);
assert.deepStrictEqual(names(F.filterTools(tools, { openSource: true })), ['Continue']);
assert.deepStrictEqual(names(F.filterTools(tools, { q: 'zzz' })), []);
assert.strictEqual(F.filterTools(tools, {}).length, 4);

assert.deepStrictEqual(names(F.sortTools(tools, 'name-asc')), ['ChatGPT', 'Claude', 'Continue', 'Midjourney']);
assert.deepStrictEqual(names(F.sortTools(tools, 'name-desc')), ['Midjourney', 'Continue', 'Claude', 'ChatGPT']);
assert.deepStrictEqual(names(F.sortTools(tools, 'newest')), ['Claude', 'Midjourney', 'ChatGPT', 'Continue']);
assert.deepStrictEqual(names(F.sortTools(tools, 'rating')), ['Continue', 'Midjourney', 'ChatGPT', 'Claude']);
assert.deepStrictEqual(names(F.sortTools(tools, 'featured')), ['ChatGPT', 'Claude', 'Continue', 'Midjourney']);
assert.strictEqual(tools[0].name, 'ChatGPT', 'sortTools must not mutate the input');

const p = F.paginate([1, 2, 3, 4, 5], 2, 2);
assert.deepStrictEqual(p, { page: 2, pages: 3, total: 5, items: [3, 4] });
assert.strictEqual(F.paginate([1, 2, 3], 99, 2).page, 2);
assert.strictEqual(F.paginate([1, 2, 3], -4, 2).page, 1);
assert.deepStrictEqual(F.paginate([], 1, 12), { page: 1, pages: 1, total: 0, items: [] });

// names starting with the typed text come first, then other matches (here 'Midjourney' matches via its Discord platform)
assert.deepStrictEqual(names(F.suggest(tools, 'c')), ['ChatGPT', 'Claude', 'Continue', 'Midjourney']);
assert.strictEqual(names(F.suggest(tools, 'cl'))[0], 'Claude');
assert.deepStrictEqual(F.suggest(tools, ''), []);
assert.deepStrictEqual(F.pageWindow(1, 3), [1, 2, 3]);
assert.deepStrictEqual(F.pageWindow(6, 12), [1, '...', 5, 6, 7, '...', 12]);
console.log('filters.js: all assertions passed');
