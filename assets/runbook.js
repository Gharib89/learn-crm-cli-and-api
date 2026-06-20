/* runbook component — tick steps off as you complete them (M12 capstone).
   Each .runbook has .rb-step rows with a .rb-check toggle; foot shows count. */
(function () {
  function wire(rb) {
    var steps = rb.querySelectorAll('.rb-step');
    var foot = rb.querySelector('.rb-foot');
    var total = steps.length;
    function refresh() {
      var done = rb.querySelectorAll('.rb-step.done').length;
      if (foot) {
        foot.textContent = '▸ ' + done + '/' + total + ' steps checked'
          + (done === total ? '   ✓ layer complete' : '');
      }
    }
    steps.forEach(function (step) {
      var btn = step.querySelector('.rb-check');
      if (!btn) return;
      btn.addEventListener('click', function () {
        step.classList.toggle('done');
        refresh();
      });
    });
    refresh();
  }
  function init() { document.querySelectorAll('.runbook').forEach(wire); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
