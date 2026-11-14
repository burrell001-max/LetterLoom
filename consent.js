/* LetterLoom consent banner (draft).
   - Shows once; remembers the choice in localStorage.
   - Ads/analytics must only be loaded inside loadAds() after consent.
   - Add <script src="consent.js" defer></script> to every page.
   - IMPORTANT: once you serve AdSense to EEA/UK/Swiss visitors, Google requires a
     certified consent platform (CMP). Use Google's free "Privacy & messaging" tool in
     AdSense and replace this banner with it. This file is a placeholder until then. */
(function () {
  var KEY = 'll_consent';
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function loadAds() {
    if (window.__adsLoaded) return;
    window.__adsLoaded = true;
    // After you are approved, paste your AdSense loader here, e.g.:
    // var s = document.createElement('script'); s.async = true;
    // s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX';
    // s.crossOrigin = 'anonymous'; document.head.appendChild(s);
    // For non-personalized ads on "Reject", set (window.adsbygoogle = window.adsbygoogle || []).requestNonPersonalizedAds = 1 first.
  }

  function close() { var b = document.getElementById('cc-bar'); if (b) b.remove(); }

  function choose(v) {
    set(v); close();
    if (v === 'accept') loadAds();
  }

  function show() {
    if (document.getElementById('cc-bar')) return;
    var b = document.createElement('div');
    b.id = 'cc-bar';
    b.setAttribute('role', 'dialog');
    b.setAttribute('aria-label', 'Cookie consent');
    b.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:9999;padding:.75rem;';
    b.innerHTML =
      '<div style="max-width:42rem;margin:0 auto;background:var(--card,#fff);color:var(--fg,#12202b);border:1px solid var(--line,#cfdae0);border-radius:14px;padding:1rem;box-shadow:0 10px 30px rgba(0,0,0,.25);font:inherit;line-height:1.5">' +
      '<p style="margin:0 0 .75rem">We and our advertising partners may use cookies to show and measure ads. Accept to allow personalized ads, or reject to keep them non-personalized. See the <a href="privacy.html" style="color:var(--acc,#0e7c86);text-decoration:underline">Privacy Policy</a>.</p>' +
      '<div style="display:flex;gap:.5rem;flex-wrap:wrap">' +
      '<button id="cc-accept" style="background:var(--acc,#0e7c86);color:var(--bg,#fff);border:0;border-radius:8px;padding:.5rem 1rem;font-weight:700;cursor:pointer">Accept</button>' +
      '<button id="cc-reject" style="background:transparent;color:inherit;border:1px solid var(--line,#cfdae0);border-radius:8px;padding:.5rem 1rem;font-weight:700;cursor:pointer">Reject</button>' +
      '</div></div>';
    document.body.appendChild(b);
    document.getElementById('cc-accept').onclick = function () { choose('accept'); };
    document.getElementById('cc-reject').onclick = function () { choose('reject'); };
  }

  document.addEventListener('click', function (e) {
    if (e.target && e.target.id === 'cc-reopen') show();
  });

  var saved = get();
  if (saved === 'accept') loadAds();
  else if (!saved) show();
})();
