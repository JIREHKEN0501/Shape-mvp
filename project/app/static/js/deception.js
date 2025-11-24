// small deception helpers used by decoy pages
(function(){
  function sendSnare(data){
    fetch('/snare', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(data)
    }).catch(()=>{});
  }

  // Add jitter to forms to detect bots that fill & submit immediately
  document.addEventListener('DOMContentLoaded', function(){
    var f = document.getElementById('decoy-form');
    if(!f) return;
    // If the form is submitted too fast, send snare
    var start = Date.now();
    f.addEventListener('submit', function(e){
      var elapsed = Date.now() - start;
      var data = {ts: Date.now(), elapsed_ms: elapsed, ua: navigator.userAgent};
      sendSnare(data);
      // allow normal submit
    });

    // small random CSS jitter (only visual)
    var box = document.querySelector('.box');
    if(box){
      var dx = (Math.random()-0.5)*6;
      box.style.transform = 'translateX('+dx+'px)';
    }
  });
})();

