/* Terminal typewriter animation for the Home page hero.
 *
 * Walks through TOKENS — each a [text, cssClass] pair — and types
 * characters one-by-one into #terminal-code at a realistic human-variable
 * speed. Respects prefers-reduced-motion by revealing everything instantly.
 *
 * Uses polling to handle Dash's client-side React rendering delay before
 * the DOM element exists.
 */
(function () {
  'use strict';

  // ── Code tokens: [text, cssClass] ─────────────────────────────────────
  // Tells the Bronze → Silver → Gold medallion story in real DLT code.
  var TOKENS = [
    ['# Lakeflow Declarative Pipeline\n',   'tok-comment'],
    ['import ',                              'tok-kw'],
    ['dlt\n',                               'tok-default'],
    ['from ',                               'tok-kw'],
    ['pyspark.sql.functions ',              'tok-default'],
    ['import ',                             'tok-kw'],
    ['col\n\n',                             'tok-default'],

    ['@dlt',                                'tok-decorator'],
    ['.table',                              'tok-default'],
    ['(comment=',                           'tok-default'],
    ['"Bronze: raw ingest"',                'tok-string'],
    [')\n',                                 'tok-default'],
    ['@dlt',                                'tok-decorator'],
    ['.expect',                             'tok-default'],
    ['(',                                   'tok-default'],
    ['"no_nulls"',                          'tok-string'],
    [', ',                                  'tok-default'],
    ['"order_id IS NOT NULL"',              'tok-string'],
    [')\n',                                 'tok-default'],
    ['def ',                                'tok-kw'],
    ['bronze_orders',                       'tok-fn'],
    ['():\n',                               'tok-default'],
    ['  return (\n',                        'tok-default'],
    ['    spark',                           'tok-default'],
    ['.readStream\n',                       'tok-default'],
    ['    .format(',                        'tok-default'],
    ['"cloudFiles"',                        'tok-string'],
    [')\n',                                 'tok-default'],
    ['    .load(',                          'tok-default'],
    ['"/mnt/landing/orders"',              'tok-string'],
    ['))\n\n',                              'tok-default'],

    ['@dlt',                                'tok-decorator'],
    ['.table',                              'tok-default'],
    ['(comment=',                           'tok-default'],
    ['"Silver: curated"',                   'tok-string'],
    [')\n',                                 'tok-default'],
    ['def ',                                'tok-kw'],
    ['silver_orders',                       'tok-fn'],
    ['():\n',                               'tok-default'],
    ['  return (\n',                        'tok-default'],
    ['    dlt',                             'tok-default'],
    ['.read_stream(',                       'tok-default'],
    ['"bronze_orders"',                     'tok-string'],
    [')\n',                                 'tok-default'],
    ['    .filter(col(',                    'tok-default'],
    ['"is_valid"',                          'tok-string'],
    [') == ',                               'tok-default'],
    ['True',                                'tok-kw'],
    [')\n',                                 'tok-default'],
    ['    .select(',                        'tok-default'],
    ['"order_id"',                          'tok-string'],
    [', ',                                  'tok-default'],
    ['"amount"',                            'tok-string'],
    [', ',                                  'tok-default'],
    ['"category"',                          'tok-string'],
    ['))\n\n',                              'tok-default'],

    ['@dlt',                                'tok-decorator'],
    ['.table',                              'tok-default'],
    ['(comment=',                           'tok-default'],
    ['"Gold: aggregated"',                  'tok-string'],
    [')\n',                                 'tok-default'],
    ['def ',                                'tok-kw'],
    ['gold_metrics',                        'tok-fn'],
    ['():\n',                               'tok-default'],
    ['  return (\n',                        'tok-default'],
    ['    dlt',                             'tok-default'],
    ['.read(',                              'tok-default'],
    ['"silver_orders"',                     'tok-string'],
    [')\n',                                 'tok-default'],
    ['    .groupBy(',                       'tok-default'],
    ['"category"',                          'tok-string'],
    [')\n',                                 'tok-default'],
    ['    .agg(sum(',                       'tok-default'],
    ['"amount"',                            'tok-string'],
    [').alias(',                            'tok-default'],
    ['"revenue"',                           'tok-string'],
    ['))',                                  'tok-default'],
  ];

  // ── Timing ───────────────────────────────────────────────────────────
  function delay(ch) {
    if (ch === '\n') return 75 + Math.random() * 40;   // pause at line breaks
    if (ch === '('  || ch === ')') return 18;
    if (ch === '"'  || ch === "'") return 14;
    if (ch === ' ')  return 10;
    return 13 + Math.random() * 14;                    // 13–27 ms per char
  }

  // ── Flatten tokens into a char list ──────────────────────────────────
  function flatten(tokens) {
    var chars = [];
    tokens.forEach(function (tok) {
      var text = tok[0], cls = tok[1];
      for (var i = 0; i < text.length; i++) {
        chars.push({ ch: text[i], cls: cls });
      }
    });
    return chars;
  }

  // ── Render all tokens at once (reduced-motion path) ──────────────────
  function renderImmediate(container) {
    TOKENS.forEach(function (tok) {
      var span = document.createElement('span');
      span.className = tok[1];
      span.textContent = tok[0];
      container.appendChild(span);
    });
  }

  // ── Animated typing ───────────────────────────────────────────────────
  function typeWriter(container) {
    var chars       = flatten(TOKENS);
    var cursor      = document.createElement('span');
    cursor.className = 'term-cursor';
    container.appendChild(cursor);

    var i           = 0;
    var curSpan     = null;
    var curCls      = null;

    function step() {
      if (i >= chars.length) return;   // done — cursor keeps blinking

      var item = chars[i++];

      if (item.cls !== curCls) {
        curSpan = document.createElement('span');
        curSpan.className = item.cls;
        container.insertBefore(curSpan, cursor);
        curCls = item.cls;
      }

      curSpan.textContent += item.ch;
      setTimeout(step, delay(item.ch));
    }

    setTimeout(step, 700);   // brief pause before first keystroke
  }

  // ── Initialise — polls until the React-rendered DOM element appears ───
  function init() {
    var reducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches;

    var attempts = 0;
    var MAX      = 40;   // give up after ~4 s

    function tryAttach() {
      var container = document.getElementById('terminal-code');
      if (container) {
        if (reducedMotion) {
          renderImmediate(container);
        } else {
          typeWriter(container);
        }
        return;
      }
      if (++attempts < MAX) setTimeout(tryAttach, 100);
    }

    tryAttach();
  }

  // Run after the Dash React tree has had a moment to mount
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
