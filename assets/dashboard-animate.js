/* Dashboard chart animation — driven by clientside callback on tab switch */
(function () {
    'use strict';

    /* ── Trend chart: SVG stroke-dashoffset draw-on ─────────────────────── */
    function animateTrendLines() {
        var gd = document.getElementById('dash-trend-chart');
        if (!gd || !gd._fullLayout) { return; }

        var paths = gd.querySelectorAll('.scatterlayer .trace .lines .js-line');
        if (!paths.length) { return; }

        paths.forEach(function (path, i) {
            var len = path.getTotalLength();
            if (!len) { return; }

            /* Reset — no transition yet */
            path.style.transition      = 'none';
            path.style.strokeDasharray = len + 'px';
            path.style.strokeDashoffset = len + 'px';

            /* Force reflow so the browser registers the reset */
            void path.getBoundingClientRect();

            /* Stagger each trace by 80 ms, ease-out-quart feel */
            var delay = i * 80;
            path.style.transition = [
                'stroke-dashoffset 1.1s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
                delay + 'ms'
            ].join(' ');
            path.style.strokeDashoffset = '0';
        });
    }

    /* ── Category bar chart: Plotly data animation with stagger ─────────── */
    function animateCategoryBars() {
        var gd = document.getElementById('dash-category-chart');
        if (!gd || !gd.data || !gd.data.length) { return; }

        var traces = gd.data;
        var origY  = traces.map(function (t) { return Array.from(t.y); });
        var zeros  = traces.map(function ()  { return [0]; });

        /* Zero all bars in a single restyle call */
        Plotly.restyle(gd, { y: zeros }).then(function () {
            /* Stagger each bar growing back to its value */
            origY.forEach(function (yArr, i) {
                setTimeout(function () {
                    Plotly.animate(
                        gd,
                        [{ data: [{ y: yArr }], traces: [i] }],
                        {
                            transition: { duration: 460, easing: 'cubic-in-out' },
                            frame:      { duration: 460, redraw: false }
                        }
                    );
                }, i * 110);
            });
        });
    }

    /* ── Public entry point, called by clientside callback ──────────────── */
    window.dashboardAnimate = function () {
        animateTrendLines();
        /* Start bar animation after the trend lines are well underway */
        setTimeout(animateCategoryBars, 420);
    };
}());
