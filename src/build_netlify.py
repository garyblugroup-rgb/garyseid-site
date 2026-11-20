import re, json, html, os, shutil

SRC = 'template.html'
OUT = 'netlify/garyseid-site'
BASE = 'https://www.garyseid.com'
shutil.rmtree('netlify', ignore_errors=True)
os.makedirs(OUT + '/images')

t = open(SRC).read()

# ---------- assets ----------
shutil.copy('head1.jpg', OUT + '/images/gary-seid.jpg')
shutil.copy('logo_web.jpg', OUT + '/images/blu-group-logo.jpg')
shutil.copy('apple-touch-icon.png', OUT + '/images/apple-touch-icon.png')
shutil.copy('favicon.png', OUT + '/images/favicon.png')
shutil.copy('hero_web.jpg', OUT + '/images/hero-home.jpg')
shutil.copy('closing_web.jpg', OUT + '/images/closing-day.jpg')
shutil.copy('ranch_web.jpg', OUT + '/images/brick-ranch.jpg')
shutil.copy('door_web.jpg', OUT + '/images/front-door.jpg')
shutil.copy('starter_web.jpg', OUT + '/images/starter-home.jpg')
shutil.copy('celebrate_web.jpg', OUT + '/images/closing-celebration.jpg')
shutil.copy('kw_web.png', OUT + '/images/kw-marquee-logo.png')
t = t.replace('{{HEADSHOT}}', '/images/gary-seid.jpg').replace('{{LOGO}}', '/images/blu-group-logo.jpg').replace('{{HEROBG}}', '/images/hero-home.jpg').replace('{{CLOSING}}', '/images/closing-day.jpg').replace('{{RANCH}}', '/images/brick-ranch.jpg').replace('{{DOOR}}', '/images/front-door.jpg').replace('{{STARTER}}', '/images/starter-home.jpg').replace('{{CELEBRATE}}', '/images/closing-celebration.jpg').replace('{{KWLOGO}}', '/images/kw-marquee-logo.png')

# ---------- pieces ----------
css = t[t.index('<style>') + 7:t.index('</style>')]
css = css.replace('/* views */\nmain > section.view[hidden]{display:none}', '')
css += '\na.contact-links{color:inherit;text-decoration:none}\n.form-ok{font-weight:600}\n'
open(OUT + '/styles.css', 'w').write(css.strip() + '\n')

agent_ld = t[t.index('<script type="application/ld+json">'):t.index('</script>') + 9]
header = t[t.index('<header class="site">'):t.index('</header>') + 9]
footer = t[t.index('<footer class="site">'):t.index('</footer>') + 9]
footer = footer.replace('<li><a href="#contact" data-view="contact">Contact</a></li>', '<li><a href="#contact" data-view="contact">Contact</a></li><li><a href="/privacy/">Privacy Policy</a></li><li><a href="/terms/">Terms</a></li>')
def block(start_marker, end_marker):
    s = t.index(start_marker); e = t.index(end_marker, s)
    return t[s:e]
cta_buyer = block('<div class="cta band" id="cta-buyer">', '<div class="cta band" id="cta-move"').strip()
cta_move = block('<div class="cta band" id="cta-move" hidden>', '<div class="cta band" id="cta-seller"').strip()
cta_seller = t[t.index('<div class="cta band" id="cta-seller" hidden>'):t.index('<div class="follow"')].strip()
cta_seller = cta_seller.replace(' id="cta-seller" hidden', '')
cta_move = cta_move.replace(' id="cta-move" hidden', '')
cta_buyer = cta_buyer.replace(' id="cta-buyer"', '')

def section(name):
    s = t.index(f'data-name="{name}"'); s = t.rfind('<section', 0, s)
    e = t.index('</section>', s) + 10
    sec = t[s:e]
    sec = re.sub(r'<section class="view" id="view-[a-z]+" data-name="[a-z]+"( hidden)?>', '<section>', sec)
    return sec

ROUTES = {'home': '/', 'about': '/about/', 'guide': '/buyer-guide/', 'sellers': '/seller-guide/', 'contact': '/contact/', 'homevalue': '/home-value/', 'storypaige': '/stories/paige/', 'storyangelina': '/stories/angelina/', 'storyshuai': '/stories/shuai/', 'intake': '/intake/', 'careernight': '/career-night/', 'examprep': '/exam-prep/', 'twentyquestions': '/twenty-questions/', 'mortgagecalc': '/mortgage-calculator/', 'netsheet': '/seller-net-sheet/', 'applyloan': '/apply-for-a-loan/', 'prephome': '/preparing-your-home-for-sale/', 'marketing': '/marketing-strategy/', 'storiesindex': '/stories/', 'privacy': '/privacy/', 'terms': '/terms/'}
def fix_links(s):
    s = re.sub(r'href="#[a-z]+" data-view="([a-z]+)" data-anchor="([a-z-]+)"',
               lambda m: f'href="{ROUTES[m.group(1)]}#{m.group(2)}"', s)
    for v, u in ROUTES.items():
        s = s.replace(f'href="#{v}" data-view="{v}"', f'href="{u}"')
    s = re.sub(r' data-view="[a-z]+"', '', s)
    return s

def faq_ld(sec_html):
    qa = re.findall(r'<summary>(.*?)</summary><p>(.*?)</p>', sec_html)
    strip = lambda x: html.unescape(re.sub('<[^>]+>', '', x))
    d = {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qa]}
    return '<script type="application/ld+json">\n' + json.dumps(d, indent=1, ensure_ascii=False) + '\n</script>'

# ---------- per-page content fixes ----------
home = section('home')
about = section('about')
guide = section('guide')
sellers = section('sellers')
contact = section('contact')
homevalue = section('homevalue')
storypaige = section('storypaige')
storyangelina = section('storyangelina')
storyshuai = section('storyshuai')
intake = section('intake')
careernight = section('careernight')
examprep = section('examprep')
twentyquestions = section('twentyquestions')
mortgagecalc = section('mortgagecalc')
netsheet = section('netsheet')
applyloan = section('applyloan')
prephome = section('prephome')
marketing = section('marketing')
storiesindex = section('storiesindex')

# lender draft box -> public text
guide = re.sub(r'<div class="draft">.*?</div>\s*</div>',
               '<p class="note">Ask me for lender recommendations. I work with local loan officers who know the first-time buyer and down-payment assistance programs.</p></div>',
               guide, count=1, flags=re.S)
assert 'class="draft"' not in guide

# real contact form for Netlify
fs = contact.index('<form'); fe = contact.index('</form>') + 7
form = '''<form class="lead" name="contact" method="POST" action="/thanks/" data-netlify="true" netlify-honeypot="company">
        <input type="hidden" name="form-name" value="contact">
        <p hidden><label>Leave this empty <input name="company"></label></p>
        <h3>Send Gary a message</h3>
        <div class="two">
          <label for="f-name">Name<input id="f-name" name="name" autocomplete="name" required></label>
          <label for="f-phone">Phone<input id="f-phone" name="phone" type="tel" autocomplete="tel"></label>
        </div>
        <label for="f-email">Email<input id="f-email" name="email" type="email" autocomplete="email" required></label>
        <div class="two">
          <label for="f-goal">I'm looking to<select id="f-goal" name="goal"><option>Buy my first home</option><option>Buy a home</option><option>Sell my home</option><option>Buy and sell</option></select></label>
          <label for="f-state">Where?<select id="f-state" name="state"><option>Missouri</option><option>Illinois</option><option>Not sure yet</option></select></label>
        </div>
        <label for="f-msg">Message<textarea id="f-msg" name="message" rows="4" placeholder="Tell me a little about your plans and timeline."></textarea></label>
        <button class="btn primary" type="submit" style="justify-self:start">Send message</button>
        <p class="note" style="margin:0;font-size:.85rem">I agree to be contacted by Blu Group LLC and Gary Seid via call, email, and text for real estate services. To opt out, you can reply &#39;stop&#39; at any time or reply &#39;help&#39; for assistance. Message and data rates may apply. Message frequency may vary. See the <a href="/privacy/">privacy policy</a>.</p>
      </form>'''
contact = contact[:fs] + form + contact[fe:]
contact = contact.replace("Let's talk about your first home.", "Let's talk about your next move.")
contact = contact.replace('<strong>314-494-6038</strong>', '<strong><a class="contact-links" href="tel:+13144946038">314-494-6038</a></strong>')
contact = contact.replace('<strong>gary@blustl.com</strong>', '<strong><a class="contact-links" href="mailto:gary@blustl.com">gary@blustl.com</a></strong>')
contact = contact.replace('<p class="note" style="font-size:1.05rem">Call or text anytime. I usually reply the same day.</p>',
  '<p class="note" style="font-size:1.05rem">Buying or selling, call or text anytime. I usually reply the same day.</p>')

hv_form = """<form class="lead" name="home-value" method="POST" action="/thanks/" data-netlify="true" netlify-honeypot="company">
        <input type="hidden" name="form-name" value="home-value">
        <p hidden><label>Leave this empty <input name="company"></label></p>
        <h3>Request your free home value analysis</h3>
        <div class="two">
          <label for="hv-name">Name<input id="hv-name" name="name" autocomplete="name" required></label>
          <label for="hv-phone">Phone<input id="hv-phone" name="phone" type="tel" autocomplete="tel"></label>
        </div>
        <label for="hv-email">Email<input id="hv-email" name="email" type="email" autocomplete="email" required></label>
        <label for="hv-address">Property address<input id="hv-address" name="address" autocomplete="street-address" required></label>
        <label for="hv-when">When are you thinking of selling?<select id="hv-when" name="timeframe"><option>In the next 3 months</option><option>3\u20136 months</option><option>6\u201312 months</option><option>Just curious what it's worth</option></select></label>
        <label for="hv-msg">Anything I should know?<textarea id="hv-msg" name="message" rows="3" placeholder="Updates you've made, condition, anything unusual."></textarea></label>
        <button class="btn primary" type="submit" style="justify-self:start">Request my free analysis</button>
        <p class="note" style="margin:0;font-size:.85rem">I agree to be contacted by Blu Group LLC and Gary Seid via call, email, and text for real estate services. To opt out, you can reply &#39;stop&#39; at any time or reply &#39;help&#39; for assistance. Message and data rates may apply. Message frequency may vary. See the <a href="/privacy/">privacy policy</a>.</p>
      </form>"""
homevalue = re.sub(r'<form class="lead" id="hv-form".*?</form>', lambda m: hv_form, homevalue, count=1, flags=re.S)
assert 'data-netlify' in homevalue

intake_form = """<form class="lead" name="intake" method="POST" action="/thanks/" data-netlify="true" netlify-honeypot="company">
        <input type="hidden" name="form-name" value="intake">
        <p hidden><label>Leave this empty <input name="company"></label></p>
        <h3>Your information</h3>
        <div class="two">
          <label for="in-first">First name<input id="in-first" name="first_name" autocomplete="given-name" required></label>
          <label for="in-last">Last name<input id="in-last" name="last_name" autocomplete="family-name" required></label>
        </div>
        <div class="two">
          <label for="in-dob">Birth date<input id="in-dob" name="birth_date" type="date" autocomplete="bday" required></label>
          <label for="in-phone">Phone number<input id="in-phone" name="phone" type="tel" autocomplete="tel" required></label>
        </div>
        <label for="in-addr">Street address<input id="in-addr" name="address" autocomplete="address-line1" required></label>
        <div class="two">
          <label for="in-city">City<input id="in-city" name="city" autocomplete="address-level2" required></label>
          <label for="in-state">State<select id="in-state" name="state" autocomplete="address-level1" required><option>Missouri</option><option>Illinois</option><option>Other</option></select></label>
        </div>
        <div class="two">
          <label for="in-zip">ZIP<input id="in-zip" name="zip" autocomplete="postal-code" inputmode="numeric" required></label>
          <label for="in-email">Email address<input id="in-email" name="email" type="email" autocomplete="email" required></label>
        </div>
        <label class="choice" style="font-size:.85rem;font-weight:400"><input type="checkbox" name="sms_consent" value="yes"><span>I agree to be contacted by Blu Group LLC and Gary Seid via call, email, and text for real estate services. To opt out, you can reply &#39;stop&#39; at any time or reply &#39;help&#39; for assistance. Message and data rates may apply. Message frequency may vary. See the <a href="/privacy/">privacy policy</a>.</span></label>
        <button class="btn primary" type="submit" style="justify-self:start">Send to Gary</button>
      </form>"""
intake = re.sub(r'<form class="lead" id="intake-form".*?</form>', lambda m: intake_form, intake, count=1, flags=re.S)
assert 'data-netlify' in intake

careernight = careernight.replace(
    '<form class="lead" id="career-form" novalidate>',
    '<form class="lead" name="career-night" method="POST" action="/thanks/" data-netlify="true" netlify-honeypot="company">\n        <input type="hidden" name="form-name" value="career-night">\n        <p hidden><label>Leave this empty <input name="company"></label></p>')
careernight = re.sub(r'\s*<p class="notice form-note" hidden>.*?</p>', '', careernight, count=1, flags=re.S)
careernight = careernight.replace('<button class="btn primary" type="submit" style="justify-self:start">Send it in</button>', '<label class="choice" style="font-size:.85rem;font-weight:400"><input type="checkbox" name="sms_consent" value="yes"><span>I agree to be contacted by Blu Group LLC and Gary Seid via call, email, and text about career opportunities in real estate. To opt out, you can reply &#39;stop&#39; at any time or reply &#39;help&#39; for assistance. Message and data rates may apply. Message frequency may vary. See the <a href="/privacy/">privacy policy</a>.</span></label>\n        <button class="btn primary" type="submit" style="justify-self:start">Send it in</button>')
assert 'data-netlify' in careernight and 'form-note' not in careernight


linksadmin = """<section><div class="band"><div class="wrap stack" style="gap:20px;max-width:760px">
  <div class="stack" style="gap:8px">
    <span class="eyebrow">Gary's tools</span>
    <h1 style="font-size:clamp(1.9rem,4.2vw,2.9rem)">Short link maker</h1>
    <p class="note">Paste a long link (Zillow, anything), give it a short name, and get a garyseid.com/s/ link to text out. Links work instantly \u2014 no redeploy.</p>
  </div>
  <form class="lead" id="mk" onsubmit="return false">
    <label>Passphrase<input id="k" type="password" autocomplete="off"></label>
    <label>Destination URL (the long link)<input id="u" type="url" placeholder="https://www.zillow.com/homedetails/..."></label>
    <label>Short name<input id="n" placeholder="123-main-st"></label>
    <button class="btn primary" id="go" type="button" style="justify-self:start">Create short link</button>
    <p class="note" id="msg" style="margin:0" hidden></p>
    <div id="result" hidden style="gap:10px;align-items:center;flex-wrap:wrap">
      <code id="shorturl" style="font-size:1.05rem;background:var(--bg);padding:8px 12px;border-radius:8px;border:1px solid var(--line)"></code>
      <button class="btn ghost" id="cp" type="button">Copy</button>
    </div>
  </form>
  <div class="stack" style="gap:10px">
    <div class="row"><button class="btn ghost" id="load" type="button">Show my existing links</button></div>
    <div id="list"></div>
  </div>
</div></div></section>
<script>
(function(){
  var $=function(id){return document.getElementById(id)};
  try{ $('k').value = localStorage.getItem('lk')||''; }catch(_){ }
  function msg(t,ok){ var m=$('msg'); m.hidden=false; m.textContent=t; m.style.color=ok?'':'#b4232a'; }
  function suggest(u){ try{ var p=new URL(u), segs=p.pathname.split('/').filter(Boolean), best='';
    for(var i=0;i<segs.length;i++){ var c=segs[i].toLowerCase().replace(/_zpid$/,'').replace(/[^a-z0-9-]+/g,'-').replace(/^-+|-+$/g,'');
      if(/[a-z]/.test(c)&&c.length>best.length) best=c; }
    return best.slice(0,40); }catch(_){ return ''; } }
  $('u').addEventListener('change',function(){ if(!$('n').value) $('n').value=suggest($('u').value); });
  var overwrite=false;
  $('go').addEventListener('click',function(){
    var k=$('k').value.trim(); if(!k){msg('Enter the passphrase.');return;}
    try{ localStorage.setItem('lk',k); }catch(_){ }
    $('go').disabled=true; msg('Creating\u2026',true);
    fetch('/api/links',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({action:'create',key:k,url:$('u').value.trim(),slug:$('n').value.trim(),overwrite:overwrite})})
    .then(function(r){return r.json().then(function(j){return {s:r.status,j:j}})})
    .then(function(x){ $('go').disabled=false; overwrite=false; $('go').textContent='Create short link';
      if(x.j&&x.j.ok){ msg('Done. Your short link:',true); $('result').hidden=false; $('result').style.display='flex'; $('shorturl').textContent=x.j.short; }
      else if(x.s===409){ overwrite=true; $('go').textContent='Yes, replace it'; msg('That name is already used (\u2192 '+(x.j.existing||'')+'). Click again to replace it, or change the name.'); }
      else msg((x.j&&x.j.error)||'Something went wrong.'); })
    .catch(function(){ $('go').disabled=false; msg('Could not reach the link service.'); });
  });
  $('cp').addEventListener('click',function(){ var d=function(){$('cp').textContent='Copied';setTimeout(function(){$('cp').textContent='Copy'},1500)};
    try{ navigator.clipboard.writeText($('shorturl').textContent).then(d,d); }catch(_){ d(); } });
  $('load').addEventListener('click',function(){
    var k=$('k').value.trim(); if(!k){msg('Enter the passphrase first.');return;}
    fetch('/api/links',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({action:'list',key:k})})
    .then(function(r){return r.json()})
    .then(function(j){ if(!j.items){ msg(j.error||'Could not load links.'); return; }
      var h='<table style="width:100%;border-collapse:collapse;font-size:.92rem">';
      if(!j.items.length) h+='<tr><td>No links yet.</td></tr>';
      for(var i=0;i<j.items.length;i++){ var it=j.items[i];
        h+='<tr style="border-top:1px solid var(--line)"><td style="padding:8px 6px;white-space:nowrap"><b>/s/'+it.slug+'</b></td><td style="padding:8px 6px;word-break:break-all;color:var(--muted)">'+it.url.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</td><td style="padding:8px 6px"><button class="btn ghost del" data-slug="'+it.slug+'" style="padding:4px 10px;font-size:.85rem">Delete</button></td></tr>'; }
      $('list').innerHTML=h+'</table>';
      var ds=$('list').querySelectorAll('button.del');
      for(var d2=0;d2<ds.length;d2++){ ds[d2].addEventListener('click',function(){ delLink(this.getAttribute('data-slug')); }); } })
    .catch(function(){ msg('Could not reach the link service.'); });
  });
  window.delLink=function(slug){
    var k=$('k').value.trim();
    fetch('/api/links',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({action:'delete',key:k,slug:slug})})
    .then(function(){ $('load').click(); });
  };
})();
</script>"""

privacy = """<section><div class="band"><div class="wrap stack prose" style="gap:22px;max-width:760px">
  <div class="stack" style="gap:10px">
    <span class="eyebrow">Privacy Policy</span>
    <h1 style="font-size:clamp(2rem,4.6vw,3.3rem)">Privacy policy</h1>
    <p class="note">Last updated: November 19, 2026 &middot; Gary Seid, REALTOR&reg; &middot; The Blu Group Real Estate, powered by Keller Williams Marquee</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">Information I collect</h2>
    <p>When you fill out a form on this site, I collect the information you provide: your name, phone number, email address, and any property details or messages you include. The site also uses standard analytics and tracking tools (including a Follow Up Boss website tracker) that record pages visited and basic technical information such as browser type, in order to understand how visitors use the site and to serve you better when you reach out.</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">How I use it</h2>
    <p>Your information is used to respond to your inquiry, provide real estate services you request, and follow up about your home search or sale. It is stored in the customer relationship tools I use to run my business.</p>
    <p><b>Data will not be shared with third parties for marketing or promotional purposes.</b> I do not sell your personal information. Information is shared only with service providers that help me operate my business (such as my CRM and website host), or as required to complete a transaction you are part of, or as required by law.</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">Calls and text messages</h2>
    <p>By submitting a form with your phone number, you consent to receive calls and text messages from Gary Seid (Blu Group LLC) about your inquiry. Message frequency varies and message and data rates may apply. You can opt out of text messages at any time by replying STOP, or reply HELP for help. Consent to receive texts is not a condition of purchasing any property or service.</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">SMS Terms and Conditions</h2>
    <ol style="margin:0;padding-left:20px;display:grid;gap:10px">
      <li>We use SMS to confirm appointments, send reminders, and notify clients of schedule updates or important changes.</li>
      <li>You can cancel the SMS service at any time. Just text "STOP". After you send the SMS message "STOP" to us, we will send you an SMS message to confirm that you have been unsubscribed. After this, you will no longer receive SMS messages from us. If you want to join again, just sign up as you did the first time, and we will start sending SMS messages to you again.</li>
      <li>If you are experiencing issues with the messaging program, you can reply with the keyword "HELP" for more assistance, or you can get help directly at <a href="mailto:gary@blustl.com">gary@blustl.com</a>.</li>
      <li>Carriers are not liable for delayed or undelivered messages.</li>
      <li>As always, message and data rates may apply for any messages sent to you from us and to us from you. Message frequency may vary. If you have any questions about your text plan or data plan, it is best to contact your wireless provider.</li>
      <li>If you have any questions regarding privacy, please read our privacy policy: <a href="https://garyseid.com/privacy/">https://garyseid.com/privacy/</a></li>
    </ol>
    <p>Phone numbers and mobile opt-in information collected for text messaging are not shared with third parties or affiliates for marketing or promotional purposes.</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">Your choices</h2>
    <p>You may ask me at any time to update or delete the information you have submitted, or to stop contacting you. Call or text 314-494-6038 or email <a href="mailto:gary@blustl.com">gary@blustl.com</a>.</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">Questions</h2>
    <p>Gary Seid &middot; The Blu Group Real Estate, powered by Keller Williams Marquee &middot; 1254 University Dr, Ste 200, Edwardsville, IL 62025 &middot; 314-494-6038 &middot; gary@blustl.com</p>
  </div>
</div></div></section>"""

terms = """<section><div class="band"><div class="wrap stack prose" style="gap:22px;max-width:760px">
  <div class="stack" style="gap:10px">
    <span class="eyebrow">Terms &amp; Conditions</span>
    <h1 style="font-size:clamp(2rem,4.6vw,3.3rem)">Terms and conditions</h1>
    <p class="note">Last updated: November 19, 2026 &middot; Gary Seid, REALTOR&reg; &middot; The Blu Group Real Estate, powered by Keller Williams Marquee</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">Text messaging terms</h2>
    <p>When you provide your phone number through a form on this site or otherwise opt in, you agree to receive informational text messages from Gary Seid (Blu Group LLC) about your real estate inquiry, such as responses to your questions, appointment and showing updates, and follow-up about your home search or sale.</p>
    <ul>
      <li>Message frequency varies based on your inquiry and transaction.</li>
      <li>Message and data rates may apply, depending on your mobile carrier and plan.</li>
      <li>Reply <b>STOP</b> at any time to cancel and stop receiving messages.</li>
      <li>Reply <b>HELP</b> for help, or contact me directly at 314-494-6038 or <a href="mailto:gary@blustl.com">gary@blustl.com</a>.</li>
      <li>Consent to receive text messages is not a condition of purchasing any property or service.</li>
      <li>Mobile carriers are not liable for delayed or undelivered messages.</li>
    </ul>
    <p>How your information is handled is described in the <a href="/privacy/">privacy policy</a>. Your mobile information will not be shared with third parties for marketing or promotional purposes.</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">Use of this website</h2>
    <p>The content on garyseid.com is provided for general informational purposes about buying and selling real estate in the St. Louis, Missouri and Metro East, Illinois area. It is not legal, tax, or financial advice. While I work to keep information current and accurate, programs, rates, taxes, and local requirements change, and information is deemed reliable but not guaranteed. Calculators on this site produce estimates only, not quotes or commitments.</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">Brokerage</h2>
    <p>Gary Seid is a REALTOR&reg; and broker associate with The Blu Group Real Estate, powered by Keller Williams Marquee, 1254 University Dr, Ste 200, Edwardsville, IL 62025. Licensed in Illinois (471.022801) and Missouri (2018043269). Each Keller Williams office is independently owned and operated. Equal Housing Opportunity.</p>
  </div>
  <div class="stack" style="gap:8px"><h2 style="font-size:1.3rem">Questions</h2>
    <p>Call or text 314-494-6038 or email <a href="mailto:gary@blustl.com">gary@blustl.com</a>.</p>
  </div>
</div></div></section>"""

thanks = '''<section><div class="band"><div class="wrap stack prose">
  <span class="eyebrow">Message sent</span>
  <h1 style="font-size:clamp(2rem,4.6vw,3.3rem)">Thanks! I'll be in touch soon.</h1>
  <p class="note" style="font-size:1.05rem">I usually reply the same day. If it's urgent, call or text me at 314-494-6038.</p>
  <div class="row"><a class="btn dark" href="/buyer-guide/">Read the Buyer Guide</a><a class="btn ghost" href="/seller-guide/">Read the Seller Guide</a></div>
</div></div></section>'''
notfound = '''<section><div class="band"><div class="wrap stack prose">
  <span class="eyebrow">Page not found</span>
  <h1 style="font-size:clamp(2rem,4.6vw,3.3rem)">That page doesn't exist.</h1>
  <p class="note" style="font-size:1.05rem">It may have moved. Try one of these instead.</p>
  <div class="row"><a class="btn dark" href="/">Home</a><a class="btn ghost" href="/buyer-guide/">Buyer Guide</a><a class="btn ghost" href="/seller-guide/">Seller Guide</a></div>
</div></div></section>'''

PAGES = [
 # key, path, title, description, body, cta, faq
 ('home', '/', 'Gary Seid | REALTOR® & Broker | Buy or Sell in St. Louis & Metro East',
  'Gary Seid, REALTOR® and broker with The Blu Group powered by Keller Williams Marquee, helps home sellers and first-time buyers across St. Louis, Missouri and the Metro East, Illinois.', home, cta_move, True),
 ('about', '/about/', 'About Gary Seid | REALTOR® & Real Estate Broker | The Blu Group',
  'Gary Seid is a REALTOR® and real estate broker licensed in Missouri and Illinois, with an MBA from Washington University and 40–50 home sales a year.', about, cta_move, False),
 ('guide', '/buyer-guide/', 'First-Time Homebuyer Guide | St. Louis & Metro East | Gary Seid',
  'A first-time homebuyer guide for St. Louis, Missouri and the Metro East, Illinois: the steps, costs, down-payment programs, Missouri vs. Illinois differences and FAQ.', guide, cta_buyer, True),
 ('sellers', '/seller-guide/', 'Home Seller Guide | St. Louis & Metro East | Gary Seid',
  'How to sell your home in St. Louis, Missouri or the Metro East, Illinois: pricing, preparation, costs, disclosures, occupancy permits and seller FAQ.', sellers, cta_seller, True),
 ('homevalue', '/home-value/', "What's My Home Worth? | Free Home Value Analysis | Gary Seid",
  'Get a free, no-obligation home value analysis from Gary Seid, REALTOR\u00ae \u2014 real comparable sales from the MLS, not an online estimate, for St. Louis, Missouri and Metro East, Illinois homes.', homevalue, cta_seller, False),
 ('storypaige', '/stories/paige/', "Paige's First Home | First-Time Buyer Story | Gary Seid",
  'How a first-time buyer went from homebuyer-seminar confusion to closing on her $340,000 first home in St. Louis in 2023, with Gary Seid, REALTOR\u00ae.', storypaige, cta_buyer, False),
 ('storyangelina', '/stories/angelina/', "Angelina's Forever Home | Missouri to Illinois Buyer Story | Gary Seid",
  'Stuck searching Missouri with an agent licensed in one state, two buyers crossed the river with Gary Seid, REALTOR\u00ae, and closed on their $358,000 forever home in Fairview Heights, Illinois in January 2025.', storyangelina, cta_buyer, False),
 ('storyshuai', '/stories/shuai/', "Shuai and Linwei's First Home | First-Time Buyer Story | Gary Seid",
  'Two medical residents new to the U.S. home-buying process bought their $275,000 first home in St. Louis in December 2022 with Gary Seid, REALTOR\u00ae \u2014 winning a hot market without waiving the contingencies they needed.', storyshuai, cta_buyer, False),
 ('intake', '/intake/', 'Client Intake | Gary Seid',
  'Secure client intake form for Gary Seid, REALTOR\u00ae.', intake, '', False),
 ('careernight', '/career-night/', 'Career Night | Keller Williams Marquee',
  'Career Night follow-up form for Keller Williams Marquee, hosted by Gary Seid.', careernight, '', False),
 ('examprep', '/exam-prep/', 'Exam Prep Checklist | Keller Williams Marquee',
  'Real estate licensing exam prep checklist from Keller Williams Marquee.', examprep, '', False),
 ('twentyquestions', '/twenty-questions/', 'Twenty Questions to Ask | Keller Williams Marquee',
  'Twenty questions to ask about the real estate company you are with or considering joining.', twentyquestions, '', False),
 ('mortgagecalc', '/mortgage-calculator/', 'Mortgage Calculator | St. Louis & Metro East | Gary Seid',
  'Estimate your full monthly payment \u2014 principal, interest, taxes, insurance and PMI \u2014 with Missouri and Illinois property tax differences built in.', mortgagecalc, cta_buyer, False),
 ('netsheet', '/seller-net-sheet/', 'Seller Net Sheet Calculator | Missouri & Illinois | Gary Seid',
  'Estimate what you will walk away with when your St. Louis area home sells \u2014 with Illinois transfer tax and arrears tax proration built in.', netsheet, cta_seller, True),
 ('applyloan', '/apply-for-a-loan/', 'Apply for a Loan | Local St. Louis Lenders | Gary Seid',
  'Apply with two trusted local loan officers \u2014 Jason Jacobs (Guild Mortgage) and Alex Burden (Delmar Mortgage) \u2014 or bring your own lender.', applyloan, cta_buyer, False),
 ('prephome', '/preparing-your-home-for-sale/', 'Preparing Your Home for Sale in St. Louis & the Metro East | Gary Seid',
  'What to fix, clean and skip before listing your St. Louis area home \u2014 the prep checklist Gary Seid, REALTOR\u00ae, walks sellers through.', prephome, cta_seller, True),
 ('marketing', '/marketing-strategy/', 'How I Market Your Home | Gary Seid, REALTOR\u00ae',
  'How Gary Seid markets St. Louis and Metro East homes: research-based pricing, launch-ready listings, both-states MLS exposure and buyer-side insight.', marketing, cta_seller, False),
 ('storiesindex', '/stories/', 'Success Stories | Real Clients, Real Closings | Gary Seid',
  'Real client stories from Gary Seid, REALTOR\u00ae \u2014 real prices, real closings, told with permission, across Missouri and Illinois.', storiesindex, cta_buyer, False),
 ('contact', '/contact/', 'Contact Gary Seid | REALTOR® | 314-494-6038',
  'Book a free consultation with Gary Seid, REALTOR®. Call or text 314-494-6038 or send a message. Office in Edwardsville, IL, serving St. Louis and the Metro East.', contact, cta_move, False),
 ('linksadmin', '/links/', 'Short Links | Gary Seid', 'Short link maker.', linksadmin, '', False),
 ('privacy', '/privacy/', 'Privacy Policy | Gary Seid',
  'Privacy policy for garyseid.com: what information is collected, how it is used, and your choices.', privacy, '', False),
 ('terms', '/terms/', 'Terms and Conditions | Gary Seid',
  'Terms and conditions for garyseid.com, including text messaging terms: message frequency, rates, and how to opt out.', terms, '', False),
 ('thanks', '/thanks/', 'Thank You | Gary Seid', 'Thanks for contacting Gary Seid.', thanks, '', False),
 ('404', '/404.html', 'Page Not Found | Gary Seid', 'Page not found.', notfound, cta_move, False),
]


# sticky follow card (per-page, fixed variant)
BOOKING_F = 'https://bookings.cloud.microsoft/bookwithme/user/70c0e465b2d24efdb39ea8a00f0b844b@blustl.com/meetingtype/LzqghpTURUmyhBXWgDE6LA2?anonymous&amp;ismsaljsauthenabled&amp;ep=mcard'
FOLLOW_KINDS = {
 'seller': ('Selling your home?',
            'Get a free written price analysis, net sheet and plan for your sale \u2014 before you commit to anything.',
            'Get my free analysis', '/home-value/', ''),
 'buyer':  ('Buying your first home?',
            'Book a free 30-minute consultation: what you can afford, which programs fit, and your path to keys.',
            'Book my free consultation', BOOKING_F, ' target="_blank" rel="noopener"'),
}
FOLLOW_MAP = {'sellers': 'seller', 'home': 'seller', 'about': 'seller', 'netsheet': 'seller', 'prephome': 'seller', 'marketing': 'seller',
              'guide': 'buyer', 'storypaige': 'buyer', 'storyangelina': 'buyer', 'storyshuai': 'buyer', 'mortgagecalc': 'buyer', 'applyloan': 'buyer', 'storiesindex': 'buyer'}
def follow_for(key):
    kind = FOLLOW_MAP.get(key)
    if not kind:
        return ''
    e, txt, btn, href, extra = FOLLOW_KINDS[kind]
    return f"""<div class="follow" id="follow" hidden>
  <button class="follow-x" id="follow-x" type="button" aria-label="Dismiss">&times;</button>
  <p class="follow-eyebrow">{e}</p>
  <p class="follow-text">{txt}</p>
  <a class="btn primary" href="{href}"{extra} style="width:100%;text-align:center">{btn}</a>
</div>
<script>
(function(){{
  var f=document.getElementById('follow'),d=false;
  try{{d=sessionStorage.getItem('fdis')==='1'}}catch(_){{}}
  window.addEventListener('scroll',function(){{
    if(d) return;
    if(window.scrollY>700){{f.hidden=false;f.classList.add('show');}}
  }},{{passive:true}});
  document.getElementById('follow-x').addEventListener('click',function(){{
    d=true;f.classList.remove('show');
    try{{sessionStorage.setItem('fdis','1')}}catch(_){{}}
  }});
}})();
</script>
"""

SCRIPT = '''<script>
document.addEventListener('click',function(e){
  var b=e.target.closest('.sub-btn');
  if(b){var p=b.parentElement,was=p.classList.contains('open');
    document.querySelectorAll('.has-sub.open').forEach(function(x){x.classList.remove('open');x.querySelector('.sub-btn').setAttribute('aria-expanded','false')});
    if(!was){p.classList.add('open');b.setAttribute('aria-expanded','true');}return;}
  if(!e.target.closest('.has-sub')){
    document.querySelectorAll('.has-sub.open').forEach(function(x){x.classList.remove('open');x.querySelector('.sub-btn').setAttribute('aria-expanded','false')});
  }
  var c=e.target.closest('button.copy'); if(!c) return;
  var done=function(){c.textContent='Copied';setTimeout(function(){c.textContent='Copy'},1500)};
  try{navigator.clipboard.writeText(c.dataset.copy).then(done,done)}catch(_){done()}
});
</script>'''

def nav_for(key):
    h = fix_links(header)
    route = ROUTES.get(key)
    if route:
        h = h.replace(f'<a href="{route}">', f'<a href="{route}" aria-current="page">', 1) if key != 'home' else \
            h.replace('<a href="/">Home</a>', '<a href="/" aria-current="page">Home</a>')
    return h

FUB_PIXEL = """<!-- begin Widget Tracker Code -->
<script>
(function(w,i,d,g,e,t){w["WidgetTrackerObject"]=g;(w[g]=w[g]||function()
{(w[g].q=w[g].q||[]).push(arguments);}),(w[g].ds=1*new Date());(e="script"),
(t=d.createElement(e)),(e=d.getElementsByTagName(e)[0]);t.async=1;t.src=i;
e.parentNode.insertBefore(t,e);})
(window,"https://widgetbe.com/agent",document,"widgetTracker");
window.widgetTracker("create", "WT-YYYBBGFE");
window.widgetTracker("send", "pageview");
</script>
<!-- end Widget Tracker Code -->"""

for key, path, title, desc, body, cta, faq in PAGES:
    url = BASE + (path if path != '/404.html' else '/')
    head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/images/gary-seid.jpg">
<link rel="icon" type="image/png" href="/images/favicon.png">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/styles.css">
{agent_ld}
{faq_ld(body) if faq else ''}
{'<meta name="robots" content="noindex">' if key in ('thanks','404','intake','careernight','examprep','twentyquestions','linksadmin') else ''}
{FUB_PIXEL}
</head>
<body>'''
    page = head + '\n' + nav_for(key) + '\n<main>\n' + fix_links(body) + '\n</main>\n' + fix_links(cta) + '\n' + follow_for(key) + fix_links(footer) + '\n' + SCRIPT + '\n</body>\n</html>\n'
    assert '{{' not in page and 'data-view' not in page, key
    assert not re.search(r'href="#(home|about|guide|sellers|contact|buyers)"', page), key
    if path == '/404.html':
        open(OUT + '/404.html', 'w').write(page)
    else:
        d = OUT + path; os.makedirs(d, exist_ok=True)
        open(d + 'index.html', 'w').write(page)

open(OUT + '/robots.txt', 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n')
urls = ['/', '/about/', '/buyer-guide/', '/seller-guide/', '/home-value/', '/mortgage-calculator/', '/seller-net-sheet/', '/apply-for-a-loan/', '/preparing-your-home-for-sale/', '/marketing-strategy/', '/stories/', '/stories/paige/', '/stories/angelina/', '/stories/shuai/', '/contact/']
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
     ''.join(f'  <url><loc>{BASE}{u}</loc><lastmod>2026-10-20</lastmod></url>\n' for u in urls) + '</urlset>\n'
open(OUT + '/sitemap.xml', 'w').write(sm)
# send non-www to www handled in Netlify domain settings; keep a netlify.toml for clean defaults
open(OUT + '/netlify.toml', 'w').write('[[headers]]\n  for = "/*"\n  [headers.values]\n    X-Content-Type-Options = "nosniff"\n    Referrer-Policy = "strict-origin-when-cross-origin"\n')

# Short links: garyseid.com/go/<name> -> destination (302 so destinations can change later)
SHORTLINKS = {
    'book':   'https://bookings.cloud.microsoft/bookwithme/user/70c0e465b2d24efdb39ea8a00f0b844b@blustl.com/meetingtype/LzqghpTURUmyhBXWgDE6LA2?anonymous&ismsaljsauthenabled&ep=mcard',
    'review': 'https://g.page/r/Cdhu7P9vpvC1EBM/review',
    'search': 'https://garyseid.kw.com/search',
}
short_rules = '/s/* /.netlify/functions/links 200\n/api/links /.netlify/functions/links 200\n' + ''.join(f'/go/{k} {v} 302\n' for k, v in SHORTLINKS.items())

# serverless short-link function (pre-bundled from fnbuild/links.src.mjs)
os.makedirs(OUT + '/netlify/functions', exist_ok=True)
shutil.copy('fnbuild/links.mjs', OUT + '/netlify/functions/links.mjs')

# blustl.com is a domain alias: send it (and any non-canonical host) to the main site
open(OUT + '/_redirects', 'w').write(short_rules + '''https://blustl.com/* https://www.garyseid.com/:splat 301!
https://www.blustl.com/* https://www.garyseid.com/:splat 301!
http://blustl.com/* https://www.garyseid.com/:splat 301!
http://www.blustl.com/* https://www.garyseid.com/:splat 301!
''')
print('ok')
