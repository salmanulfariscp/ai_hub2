/*
 * recommendations.js - the step-by-step quiz on the Recommendations page.
 * It only controls which step is visible. When the last step is submitted the browser sends the answers
 * as a GET request and Django (apps/tools/recommender.py) ranks the tools.
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var quiz = document.getElementById('quiz');
        if (!quiz) return;
        var steps = Array.prototype.slice.call(quiz.querySelectorAll('.quiz-step'));
        var bar = document.getElementById('quiz-bar');
        var label = document.getElementById('quiz-step-label');
        var back = document.getElementById('quiz-back');
        var next = document.getElementById('quiz-next');
        var submit = document.getElementById('quiz-submit');
        var error = document.getElementById('quiz-error');
        var current = 0;

        function show(index) {
            current = index;
            steps.forEach(function (step, i) { step.classList.toggle('d-none', i !== index); });
            bar.style.width = ((index + 1) / steps.length * 100) + '%';
            label.textContent = 'Question ' + (index + 1) + ' of ' + steps.length;
            back.disabled = index === 0;
            var last = index === steps.length - 1;
            next.classList.toggle('d-none', last);
            submit.classList.toggle('d-none', !last);
            error.classList.add('d-none');
        }

        function stepIsValid() {
            var step = steps[current];
            if (step.dataset.optional === 'true') return true;
            return !!step.querySelector('input[type="radio"]:checked');
        }

        function goNext() {
            if (!stepIsValid()) { error.classList.remove('d-none'); return; }
            if (current < steps.length - 1) show(current + 1);
        }

        next.addEventListener('click', goNext);
        back.addEventListener('click', function () { if (current > 0) show(current - 1); });
        quiz.addEventListener('submit', function (event) {
            if (!stepIsValid()) { event.preventDefault(); error.classList.remove('d-none'); }
        });
        // Pressing Enter in the free-text box should not submit early
        quiz.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' && event.target.tagName === 'INPUT' && event.target.type === 'text') {
                event.preventDefault();
                if (current < steps.length - 1) goNext(); else quiz.requestSubmit ? quiz.requestSubmit() : quiz.submit();
            }
        });
        // Choosing an option clears the error
        quiz.addEventListener('change', function () { error.classList.add('d-none'); });

        // "Retake quiz" button on the results view
        var retake = document.getElementById('retake-quiz');
        if (retake) {
            retake.addEventListener('click', function () {
                document.getElementById('quiz-wrap').classList.remove('d-none');
                document.getElementById('quiz-results').classList.add('d-none');
                show(0);
                document.getElementById('quiz-wrap').scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        }
        show(0);
    });
})();
