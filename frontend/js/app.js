/* ================================================================
   RentBike — Shared JS (app.js) — Enhanced Edition
================================================================ */
const API = "https://bike-rent-tchw.onrender.com/api";

const api = {
  async req(method, path, body = null, isForm = false) {
    const tok = localStorage.getItem('access_token');
    const headers = {};

    if (!isForm) headers['Content-Type'] = 'application/json';
    if (tok) headers['Authorization'] = `Bearer ${tok}`;

    const opts = { method, headers };
    if (body) opts.body = isForm ? body : JSON.stringify(body);

    const res = await fetch(API + path, opts);
    const json = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(json.error || json.message || `Server error ${res.status}`);
    }

    return json;
  },

  get: (p) => api.req('GET', p),
  post: (p, b, f) => api.req('POST', p, b, f),
  put: (p, b) => api.req('PUT', p, b),
  del: (p) => api.req('DELETE', p),

  logout() {
    ['access_token', 'refresh_token', 'user'].forEach(k => localStorage.removeItem(k));
    window.location.href = 'login.html';
  }
};

const auth = {
  isLoggedIn: () => !!localStorage.getItem('access_token'),
  user:       () => JSON.parse(localStorage.getItem('user') || 'null'),
  role:       () => auth.user()?.role || null,
  isDemoMode: () => (localStorage.getItem('access_token') || '').startsWith('demo_'),
  requireAuth(to = 'login.html') { if (!auth.isLoggedIn()) { window.location.href = to; return false; } return true; }
};

function demoLogin(role) {
  const MAP = {
    admin:  { _id:'demo_admin',  name:'Admin User',   email:'admin@rentbike.in',  role:'admin',  phone:'9999999999', kyc_status:'approved', is_active:true },
    vendor: { _id:'demo_vendor', name:'Raj Vendor',   email:'vendor@rentbike.in', role:'vendor', phone:'9888888888', kyc_status:'approved', is_active:true },
    user:   { _id:'demo_user',   name:'Rohan Sharma', email:'rohan@example.com',  role:'user',   phone:'9777777777', kyc_status:'approved', is_active:true },
  };
  const u = MAP[role] || MAP.user;
  localStorage.setItem('access_token',  'demo_' + role);
  localStorage.setItem('refresh_token', 'demo_refresh_' + role);
  localStorage.setItem('user', JSON.stringify(u));
  return u;
}

function toast(msg, type = 'info', ms = 4000) {
  const bg = { success:'#10b981', error:'#ef4444', info:'#f59e0b', warning:'#f97316' };
  const ic = { success:'✓', error:'✕', info:'ℹ', warning:'⚠' };
  const el = document.createElement('div');
  el.innerHTML = `<span style="font-size:1.1em;flex-shrink:0">${ic[type]||'ℹ'}</span><span>${msg}</span>`;
  Object.assign(el.style, { position:'fixed', top:'18px', right:'18px', zIndex:99999, display:'flex', alignItems:'center', gap:'10px', padding:'13px 20px', borderRadius:'12px', color:'#fff', fontFamily:"'DM Sans', sans-serif", fontWeight:'500', fontSize:'14px', background:bg[type]||bg.info, maxWidth:'360px', boxShadow:'0 8px 32px rgba(0,0,0,0.4)', transform:'translateX(130%)', transition:'transform .3s ease' });
  document.body.appendChild(el);
  requestAnimationFrame(() => { el.style.transform = 'translateX(0)'; });
  setTimeout(() => { el.style.transform = 'translateX(130%)'; setTimeout(() => el.remove(), 300); }, ms);
}

const fmt = {
  money: n  => `₹${parseFloat(n||0).toLocaleString('en-IN')}`,
  date:  d  => d ? new Date(d).toLocaleDateString('en-IN', {day:'numeric',month:'short',year:'numeric'}) : '—',
  dt:    d  => d ? new Date(d).toLocaleString('en-IN',    {day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}) : '—',
  stars: r  => { const f=Math.floor(r||0),h=(r%1)>=0.5; return '★'.repeat(f)+(h?'½':'')+'☆'.repeat(5-f-(h?1:0)); },
};

function bikeCard(b) {
  const img = b.image || `https://placehold.co/500x280/1a1a2e/f59e0b?text=${encodeURIComponent(b.name||'Bike')}`;
  const badgeColors = { mountain:'#22c55e', road:'#3b82f6', electric:'#a855f7', city:'#f97316', hybrid:'#14b8a6', bmx:'#ec4899', gravel:'#84cc16' };
  const badgeColor = badgeColors[b.type] || '#f59e0b';
  return `
  <div onclick="location.href='bike-detail.html?id=${b._id}'"
    style="background:#16162a;border:1px solid rgba(255,255,255,0.08);border-radius:18px;overflow:hidden;cursor:pointer;transition:all .35s;box-shadow:0 4px 24px rgba(0,0,0,0.2)"
    onmouseover="this.style.borderColor='rgba(245,158,11,.5)';this.style.transform='translateY(-6px)';this.style.boxShadow='0 16px 48px rgba(0,0,0,0.4)'"
    onmouseout="this.style.borderColor='rgba(255,255,255,0.08)';this.style.transform='none';this.style.boxShadow='0 4px 24px rgba(0,0,0,0.2)'">
    <div style="position:relative;height:200px;overflow:hidden;background:#0d0d1a">
      <img src="${img}" alt="${b.name}" loading="lazy"
           style="width:100%;height:100%;object-fit:cover;transition:transform .6s"
           onerror="this.src='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500&q=80'">
      <div style="position:absolute;inset:0;background:linear-gradient(to top,rgba(22,22,42,0.7) 0%,transparent 60%)"></div>
      <span style="position:absolute;top:12px;left:12px;background:${badgeColor};color:#fff;font-size:10px;font-weight:800;padding:4px 12px;border-radius:999px;text-transform:uppercase;letter-spacing:.05em">${b.type}</span>
      <span style="position:absolute;top:12px;right:12px;font-size:10px;font-weight:700;padding:4px 12px;border-radius:999px;${b.is_available?'background:rgba(16,185,129,.9);color:#fff':'background:rgba(239,68,68,.9);color:#fff'}">${b.is_available?'● Available':'✕ Booked'}</span>
      ${b.badge?`<span style="position:absolute;bottom:12px;left:12px;background:rgba(245,158,11,0.95);color:#0f0f1a;font-size:10px;font-weight:800;padding:3px 10px;border-radius:999px">${b.badge}</span>`:''}
    </div>
    <div style="padding:16px">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
        <div style="flex:1;min-width:0">
          <div style="font-weight:800;color:#fff;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:-.2px">${b.name}</div>
          <div style="color:#6b7280;font-size:12px;margin-top:1px">${b.brand} · ${b.year}</div>
        </div>
        <div style="text-align:right;flex-shrink:0;margin-left:12px">
          <div style="color:#f59e0b;font-weight:900;font-size:20px;letter-spacing:-.5px">${fmt.money(b.price_per_hour)}</div>
          <div style="color:#6b7280;font-size:10px">/hour</div>
        </div>
      </div>
      ${b.features?`<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px">${b.features.slice(0,3).map(f=>`<span style="background:rgba(255,255,255,.05);color:#9ca3af;font-size:10px;padding:2px 8px;border-radius:6px;border:1px solid rgba(255,255,255,.06)">${f}</span>`).join('')}</div>`:''}
      <div style="display:flex;justify-content:space-between;align-items:center;padding-top:10px;border-top:1px solid rgba(255,255,255,0.06);font-size:12px">
        <span style="color:#f59e0b;font-weight:600">${fmt.stars(b.rating||0)} <span style="color:#6b7280;font-weight:400">(${b.total_reviews||0})</span></span>
        <span style="color:#6b7280">📍 ${b.location}</span>
      </div>
    </div>
  </div>`;
}

function renderNav() {
  const el = document.getElementById('navbar');
  if (!el) return;
  const u = auth.user();
  const roleColor = { admin:'#f87171', vendor:'#60a5fa', user:'#f59e0b' };
  el.innerHTML = `
  <nav style="background:rgba(11,11,20,0.97);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.07);position:sticky;top:0;z-index:100;font-family:'DM Sans',sans-serif">
    <div style="max-width:1280px;margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:64px">
      <a href="index.html" style="display:flex;align-items:center;gap:10px;text-decoration:none;flex-shrink:0">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#f59e0b,#d97706);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px">🏍️</div>
        <span style="font-weight:900;color:#fff;font-size:20px;letter-spacing:-1px;font-family:'Syne',sans-serif">Rent<span style="color:#f59e0b">Bike</span></span>
      </a>
      <div style="display:flex;align-items:center;gap:2px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:5px">
        <a href="bike-list.html?type=mountain" style="color:#9ca3af;text-decoration:none;font-size:13px;font-weight:500;padding:6px 12px;border-radius:8px;transition:all .2s" onmouseover="this.style.background='rgba(255,255,255,.07)';this.style.color='#fff'" onmouseout="this.style.background='transparent';this.style.color='#9ca3af'">⛰️ Mountain</a>
        <a href="bike-list.html?type=road" style="color:#9ca3af;text-decoration:none;font-size:13px;font-weight:500;padding:6px 12px;border-radius:8px;transition:all .2s" onmouseover="this.style.background='rgba(255,255,255,.07)';this.style.color='#fff'" onmouseout="this.style.background='transparent';this.style.color='#9ca3af'">🚵 Road</a>
        <a href="bike-list.html?type=electric" style="color:#9ca3af;text-decoration:none;font-size:13px;font-weight:500;padding:6px 12px;border-radius:8px;transition:all .2s" onmouseover="this.style.background='rgba(255,255,255,.07)';this.style.color='#fff'" onmouseout="this.style.background='transparent';this.style.color='#9ca3af'">⚡ Electric</a>
        <a href="bike-list.html?type=city" style="color:#9ca3af;text-decoration:none;font-size:13px;font-weight:500;padding:6px 12px;border-radius:8px;transition:all .2s" onmouseover="this.style.background='rgba(255,255,255,.07)';this.style.color='#fff'" onmouseout="this.style.background='transparent';this.style.color='#9ca3af'">🏙️ City</a>
        <a href="bike-list.html?type=hybrid" style="color:#9ca3af;text-decoration:none;font-size:13px;font-weight:500;padding:6px 12px;border-radius:8px;transition:all .2s" onmouseover="this.style.background='rgba(255,255,255,.07)';this.style.color='#fff'" onmouseout="this.style.background='transparent';this.style.color='#9ca3af'">🌿 Hybrid</a>
        <a href="bike-list.html" style="color:#f59e0b;text-decoration:none;font-size:13px;font-weight:700;padding:6px 12px;border-radius:8px;background:rgba(245,158,11,.1)">All Bikes</a>
      </div>
      <div style="display:flex;align-items:center;gap:12px">
        ${u ? `
          <a href="dashboard.html" style="color:#9ca3af;text-decoration:none;font-size:14px;font-weight:500" onmouseover="this.style.color='#f59e0b'" onmouseout="this.style.color='#9ca3af'">Dashboard</a>
          <a href="bookings.html" style="color:#9ca3af;text-decoration:none;font-size:14px;font-weight:500" onmouseover="this.style.color='#f59e0b'" onmouseout="this.style.color='#9ca3af'">My Bookings</a>
          <div style="position:relative" id="user-menu-wrap">
            <button id="user-menu-btn" style="display:flex;align-items:center;gap:8px;background:#1f2937;border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:7px 14px;cursor:pointer;color:#fff;font-size:13px;font-weight:600">
              <span style="background:linear-gradient(135deg,#f59e0b,#d97706);color:#0f0f1a;border-radius:8px;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:12px;flex-shrink:0">${(u.name?.charAt(0)||'U').toUpperCase()}</span>
              <span style="max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${u.name?.split(' ')[0]||'User'}</span>
              <span style="color:${roleColor[u.role]||'#f59e0b'};font-size:10px;background:${roleColor[u.role]||'#f59e0b'}22;padding:2px 7px;border-radius:999px;flex-shrink:0">${u.role}</span>
              <span style="color:#6b7280;flex-shrink:0;font-size:11px">▾</span>
            </button>
            <div id="user-dd" style="display:none;position:absolute;right:0;top:calc(100% + 8px);background:#1f2937;border:1px solid rgba(255,255,255,.1);border-radius:16px;min-width:200px;box-shadow:0 24px 48px rgba(0,0,0,.6);z-index:9999;overflow:hidden">
              <div style="padding:12px 16px;border-bottom:1px solid rgba(255,255,255,.07)">
                <div style="color:#fff;font-weight:700;font-size:14px">${u.name}</div>
                <div style="color:#6b7280;font-size:12px">${u.email}</div>
              </div>
              <a href="profile.html" style="display:block;padding:10px 16px;color:#d1d5db;text-decoration:none;font-size:13px" onmouseover="this.style.background='rgba(255,255,255,.05)'" onmouseout="this.style.background='none'">👤 My Profile</a>
              ${u.role==='vendor'||u.role==='admin'?`<a href="vendor.html" style="display:block;padding:10px 16px;color:#d1d5db;text-decoration:none;font-size:13px" onmouseover="this.style.background='rgba(255,255,255,.05)'" onmouseout="this.style.background='none'">🏪 Vendor Panel</a>`:''}
              ${u.role==='admin'?`<a href="admin.html" style="display:block;padding:10px 16px;color:#d1d5db;text-decoration:none;font-size:13px" onmouseover="this.style.background='rgba(255,255,255,.05)'" onmouseout="this.style.background='none'">⚙️ Admin Panel</a>`:''}
              <div style="border-top:1px solid rgba(255,255,255,.07);margin:4px 0"></div>
              <button onclick="api.logout()" style="width:100%;text-align:left;padding:10px 16px;color:#f87171;background:none;border:none;cursor:pointer;font-size:13px" onmouseover="this.style.background='rgba(255,255,255,.05)'" onmouseout="this.style.background='none'">🚪 Logout</button>
            </div>
          </div>` : `
          <a href="login.html" style="color:#9ca3af;text-decoration:none;font-size:14px;font-weight:500;padding:8px 16px;border-radius:10px;border:1px solid rgba(255,255,255,.1);transition:all .2s" onmouseover="this.style.borderColor='rgba(255,255,255,.3)';this.style.color='#fff'" onmouseout="this.style.borderColor='rgba(255,255,255,.1)';this.style.color='#9ca3af'">Login</a>
          <a href="login.html?tab=register" style="background:linear-gradient(135deg,#f59e0b,#d97706);color:#0f0f1a;text-decoration:none;font-size:13px;font-weight:800;padding:9px 18px;border-radius:10px">Get Started</a>`}
      </div>
    </div>
  </nav>`;
  const btn = document.getElementById('user-menu-btn');
  const dd  = document.getElementById('user-dd');
  const wrap= document.getElementById('user-menu-wrap');
  if (btn && dd) {
    btn.addEventListener('click', e => { e.stopPropagation(); dd.style.display = dd.style.display==='block'?'none':'block'; });
    document.addEventListener('click', e => { if (wrap && !wrap.contains(e.target)) dd.style.display='none'; });
  }
}

/* ── 30 Demo Bikes with real Unsplash photos ─────────────────── */
function demoBikes() {
  return [
    // ─────────────────────────────────────────
    // MOUNTAIN
    // ─────────────────────────────────────────
    { _id:'m1', name:'Royal Enfield Himalayan 450',           type:'mountain', brand:'Trek',         year:2024, price_per_hour:140, price_per_day:900,  location:'Hyderabad', rating:4.9, total_reviews:87,  is_available:true,  badge:'Top Pick',     image:'https://images.openai.com/static-rsc-4/H4C9y-DhLqPU4tofUbGdQTROwlS5wkbDs9Mb3mUS7MlFEUEx15d5MfWj7DQPuNcrcOH3AGy7cnfe_qKC4yrwUKDT9QmeDGXoGto3_IJkOHM4DpINJ6JAqhohp3x0uPLvn3vzSli44_Q-xUgrT7OxeZBLBFbQyg47KfM9p3yCShkXkjYuAsMxHRtORxlwW8X5?purpose=fullsize',  description:'29" hardtail MTB with Fox fork, Shimano SLX 12-speed drivetrain and hydraulic disc brakes. Dominates any trail.', features:['29" Fox Fork','Shimano SLX 12sp','Hydraulic Disc','Tubeless Ready'] },
    { _id:'m2', name:'KTM 390 Adventure',          type:'mountain', brand:'Scott',        year:2024, price_per_hour:220, price_per_day:1400, location:'Bangalore', rating:4.8, total_reviews:54,  is_available:true,  badge:'New',          image:'https://cdn.bajajauto.com/-/media/ktm/ktm-faq/new/new-ktmadv390-5pm.webp',  description:'Full-suspension carbon XC race machine. Traction Control System adapts to any terrain automatically.', features:['Full-Suspension','Carbon Frame','Shimano XTR','TCS Fork'] },
    { _id:'m3', name:'Hero Xpulse 200 4V',           type:'mountain', brand:'Giant',        year:2023, price_per_hour:180, price_per_day:1100, location:'Pune',      rating:4.7, total_reviews:41,  is_available:true,  image:'https://images.openai.com/static-rsc-4/MXCPH2Bh_MTJtOf8I_MKGAjdyMQRIIDd937aKVhITPqk19MeBkr5Q0igTGEuF9LF6-Ob7sDus0eQDLxB6M7sHhQRb0mTgcmuiwnz7qYLVev5u0vzWGXOBxcPM3M_Dp3fXLJskzFNoum8Rqh3oUQkC4PpW8Nj0Gr1VRGUG_D1f-TG6B_EMUTSW5izUZm6-wM8?purpose=fullsize',  description:'Trail enduro beast with 140mm travel. Maestro suspension eats roots and rocks for breakfast.', features:['140mm Travel','Maestro Suspension','29" Wheels','Dropper Post'] },
    { _id:'m4', name:'BMW G 310 GS',         type:'mountain', brand:'Merida',       year:2023, price_per_hour:110, price_per_day:700,  location:'Hyderabad', rating:4.5, total_reviews:33,  is_available:true,  image:'https://images.financialexpressdigital.com/2022/07/2022-BMW-G-310-GS-Launched-2.jpg',  description:'Versatile 29er hardtail with quality Shimano Deore components. Great for beginners and intermediates.', features:['29" Wheels','Shimano Deore','SR Suntour Fork','Disc Brakes'] },
    { _id:'m5', name:'Yezdi Adventure',     type:'mountain', brand:'Specialized',  year:2023, price_per_hour:200, price_per_day:1200, location:'Delhi',     rating:4.8, total_reviews:62,  is_available:false, image:'https://imgd.aeplcdn.com/1280x720/n/cw/ec/1/versions/yezdi-adventure-forest-green-white1749039950945.jpg',  description:'Iconic trail bike. 140mm SWAT-equipped travel handles everything from XC to technical descents.', features:['140mm Travel','SWAT Door','RockShox Pike','SRAM GX Eagle'] },
    { _id:'m6', name:'Suzuki V-Strom SX',          type:'mountain', brand:'Cannondale',   year:2022, price_per_hour:130, price_per_day:820,  location:'Chennai',   rating:4.4, total_reviews:28,  is_available:true,  image:'https://imgd.aeplcdn.com/1280x720/n/cw/ec/125103/v-strom-sx-right-side-view-4.png?isig=0',  description:'Lefty-forked trail bike with efficient Proportional Response geometry. Climbs and descends equally well.', features:['Lefty Fork','Proportional Geo','29" Wheels','Shimano Deore'] },
    { _id:'m7', name:'Royal Enfield Scram 411',     type:'mountain', brand:'Hero',         year:2024, price_per_hour:80,  price_per_day:500,  location:'Hyderabad', rating:4.3, total_reviews:44,  is_available:true,  badge:'Made in India', image:'https://images.openai.com/static-rsc-4/jfj76pKgR8on0mskwO-jGSEffYGWhpSeKig82KL2LSU99uBpye2FnhhZ0EDi-nOQo9bhcyNqIz2UW1yDDi5MrD--cLwQ4mFIL9wsgWa14mqe_l_0-5Ntw-bVoxF9pNunpoRVKy2tbzRGrMhxYA9HlsYBpWiNGcXQAZFFMIucjYBHeJ673eulDc-mEVWGQ-YI?purpose=fullsize',  description:'Rugged Indian MTB with 27.5" wheels, 21-speed Shimano gears, and front suspension fork. Built for Indian trails and rocky terrain.', features:['27.5" Wheels','21-Speed Shimano','Front Suspension','Alloy Frame'] },
    { _id:'m8', name:'KTM 250 Adventure', type:'mountain', brand:'Hercules',     year:2023, price_per_hour:65,  price_per_day:400,  location:'Chennai',   rating:4.1, total_reviews:58,  is_available:true,  image:'https://cdn.bajajauto.com/-/media/images/ktm/ktm-bikes/travel/2025-ktm-250-adv/cards/rally-3/ktm-250-adventure_featues_desktop_590-x-490_bodywork.webp',  description:'India\'s favourite entry-level MTB. 27T wheels, 21-speed gearing, and dual disc brakes make it ideal for weekend trail warriors.', features:['27T Wheels','21-Speed','Dual Disc Brakes','SR Suntour Fork'] },
    { _id:'m9', name:'Honda CB200X',      type:'mountain', brand:'Firefox',      year:2023, price_per_hour:90,  price_per_day:560,  location:'Delhi',     rating:4.4, total_reviews:31,  is_available:true,  image:'https://images.openai.com/static-rsc-4/GcLl3jKIsRhn8w_R08H8MvkBEWrPC-MvV8d-ERzAY1wXIXnl3dir9_UsilQ9eNdc7KvQdZAKTIceg3ceA3aAsIFHHhYy2KxYqPwL25ZL_skfWEzA8TnstEree6vRbfc_h8SbJq7oQwhwDZqaefwpd9JfzH9eptabB5Y5whUGy6X4fjd-pb8HjQbuj3xJcPiD?purpose=fullsize',  description:'Premium Indian 29er hardtail MTB with hydraulic disc brakes and 24-speed Shimano Acera. Performance meets affordability.', features:['29" Wheels','24-Speed Acera','Hydraulic Disc','Lockout Fork'] },
    { _id:'m10',name:'Benelli TRK 502X',      type:'mountain', brand:'Schnell',      year:2024, price_per_hour:75,  price_per_day:470,  location:'Pune',      rating:4.2, total_reviews:22,  is_available:true,  badge:'Budget Pick',  image:'https://cdn.bikedekho.com/processedimages/benelli/benelli-trk-502/source/benelli-trk-5026936828dac483.jpg?imwidth=400&impolicy=resize',  description:'Value Indian MTB brand with sturdy 6061 alloy frame, 21-speed drivetrain, and mechanical disc brakes. Great for beginner trail riders.', features:['6061 Alloy','21-Speed','Mechanical Disc','Ergonomic Saddle'] },

    // ─────────────────────────────────────────
    // ROAD
    // ─────────────────────────────────────────
    
    { _id:'r1', name:'Hero HF Deluxe',         type:'road',     brand:'Trek',        year:2024, price_per_hour:170, price_per_day:1050, location:'Bangalore', rating:4.8, total_reviews:49,  is_available:true,  badge:'Best Value',   image:'https://imgd.aeplcdn.com/664x374/n/bw/models/colors/hero-select-model-blue-black-1707131824745.png?q=80',  description:'Featherlight OCLV carbon road bike. Shimano 105 Di2 electronic groupset for effortless shifting.', features:['OCLV Carbon','Shimano 105 Di2','Carbon Fork','Disc Brakes'] },
    { _id:'r2', name:'Bajaj CT 100',    type:'road',     brand:'Cannondale',  year:2023, price_per_hour:150, price_per_day:920,  location:'Hyderabad', rating:4.7, total_reviews:38,  is_available:true,  image:'https://imgd.aeplcdn.com/664x374/n/bw/models/colors/undefined-gloss-ebony-black-with-blue-decals-1587632761911.jpg?q=80',  description:'Best aluminum road bike ever made. Racing geometry, Shimano 105, and hydraulic disc brakes.', features:['Alloy Frame','Shimano 105','Carbon Fork','Hydraulic Disc'] },
    { _id:'r3', name:'Hero Splendor Plus',  type:'road',     brand:'BMC',         year:2023, price_per_hour:190, price_per_day:1150, location:'Mumbai',    rating:4.9, total_reviews:71,  is_available:true,  badge:'Premium',      image:'https://imgd.aeplcdn.com/664x374/n/b35v6hb_1880993.jpg?q=80',  description:'Swiss precision engineering. Tour de France DNA in an accessible alloy package with Shimano Ultegra.', features:['Swiss Engineering','Shimano Ultegra','Aero Geometry','Integrated Cockpit'] },
    { _id:'r4', name:'TVS Radeon',    type:'road',     brand:'Giant',       year:2024, price_per_hour:160, price_per_day:980,  location:'Pune',      rating:4.6, total_reviews:29,  is_available:true,  image:'https://www.tvsmotor.com/-/media/sept_2024/Radeon-110.jpg',  description:'Endurance road geometry absorbs vibration. D-Fuse carbon seatpost and handlebar for all-day comfort.', features:['Advanced Carbon','D-Fuse Comfort','Shimano 105','Disc Brakes'] },
    { _id:'r5', name:'Honda Shine 125',     type:'road',     brand:'Merida',      year:2022, price_per_hour:145, price_per_day:880,  location:'Delhi',     rating:4.5, total_reviews:22,  is_available:true,  image:'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBETKwcbfufv_4v7iRIc-2wqnc05vPNBNFvw&s',  description:'CF3 carbon frame with aggressive race geometry. Shimano Ultegra groupset is unbeatable value.', features:['CF3 Carbon','Shimano Ultegra','Aero Frame','Disc Brakes'] },
    { _id:'r6', name:'Hero Passion Plus',       type:'road',     brand:'Pinarello',   year:2023, price_per_hour:250, price_per_day:1500, location:'Bangalore', rating:5.0, total_reviews:18,  is_available:true,  badge:'Luxury',       image:'https://5.imimg.com/data5/SELLER/Default/2023/8/336052023/YD/ZB/VL/5590721/hero-passion-plus-bike-500x500.jpg',  description:'Italian masterpiece. Onda fork and TORAYCA carbon for a ride unlike any other.', features:['TORAYCA Carbon','Onda Fork','Campagnolo Chorus','Italian Made'] },
    
    // ─────────────────────────────────────────
    // ELECTRIC
    // ─────────────────────────────────────────
  { _id:'e1', name:'Ultraviolette F77', type:'electric', brand:'Specialized', year:2024, price_per_hour:220, price_per_day:1300, location:'Hyderabad', rating:4.9, total_reviews:103, is_available:true, badge:'Most Rented', image:'https://images.openai.com/static-rsc-4/qSu6heJzzwC3eOP58a_A1Pn6fP_tKseBbfI4VtGC7JzAZNleHwX-vRBc11u8fnUMMFrJSYDyC4v7wdZaV0ialLVgILci9t9T2jk-c0Gx-M8FfDdqNxk7tKYH4W8YhhjzSqMC3LRlQ97hU6-rJ3_eOtubbCY-UEX84G0Cx1wlNnswY3pZYnSwttA4GHqUmkeX?purpose=fullsize', description:'320Wh battery, 80km real-world range. SL 1.1 motor adds power without bulk. Feels like a normal bike.', features:['320Wh Battery','80km Range','SL Motor','Carbon Belt'] },

  { _id:'e2', name:'Revolt RV400', type:'electric', brand:'Trek', year:2024, price_per_hour:200, price_per_day:1200, location:'Mumbai', rating:4.8, total_reviews:67, is_available:true, image:'https://images.openai.com/static-rsc-4/cDl-nOlt0Zu740-Y4yEYsBBhBxNX-Xa1QUbg_Xj1Jp3AekEjwTYnP_gQBSuM6B6RxqydVhe059jl9CUPT042sYE35b_dTKK4KSvM9MZAoy7_RjIY2kmzqbgAjPZRzRvkquw5FTcsP5XSlIZEOOb5ZzuuYHPLKXVW9rPfuxg0iBJlFQFHr7u_J8M7Q1igTugq?purpose=fullsize', description:'Bosch Performance Speed motor. 85Nm torque, 28mph assist. Integrated lights, rack, and fenders.', features:['Bosch Performance','500Wh Battery','85Nm Torque','Integrated Rack'] },

  { _id:'e3', name:'Oben Rorr', type:'electric', brand:'Giant', year:2023, price_per_hour:175, price_per_day:1050, location:'Bangalore', rating:4.7, total_reviews:44, is_available:true, image:'https://images.openai.com/static-rsc-4/_FjLrZ8i6B-MfRrmzGy88wdXnU9RSCaeCbVSpH0BYPee0Iyfwwx3pe_ATf11kvXzko24BX0WScZ2mjuvPfzuk_Sbt0jj3V9zrRxYFi-k5rFA4nYLblhMP1uQ0XVj6AULaJcsjO30SMDSkdr3Ws1-eof61eXa0yi9Eo6FIRXS2wmmOUF6n9ukU405AHM6dzY2?purpose=fullsize', description:'SyncDrive Pro motor with ALUXX SL aluminum frame. Smart Assist adapts power output to your needs.', features:['SyncDrive Pro','500Wh Battery','Smart Assist','Auto Lights'] },

  { _id:'e4', name:'Komaki Ranger', type:'electric', brand:'Cannondale', year:2023, price_per_hour:190, price_per_day:1150, location:'Delhi', rating:4.6, total_reviews:31, is_available:false, image:'https://m.media-amazon.com/images/I/51z6to83OzL._AC_UF1000%2C1000_QL80_.jpg', description:'Urban e-bike with Mahle ebikemotion X35 hub drive. Near-silent, lightweight, and premium quality.', features:['Mahle Hub Drive','250Wh Battery','Lightweight','Urban Design'] },

  { _id:'e5', name:'Hop Oxo', type:'electric', brand:'Hero', year:2023, price_per_hour:90, price_per_day:580, location:'Hyderabad', rating:4.2, total_reviews:56, is_available:true, image:'https://imgd.aeplcdn.com/1280x720/n/cw/ec/130955/oxo-right-front-three-quarter-3.jpeg?isig=0', description:'Made-in-India e-bike with 250W motor, 36V battery, and 7-speed Shimano gears. Great city commuter.', features:['250W Motor','36V Battery','7-Speed Shimano','USB Charging'] },

  { _id:'e6', name:'Ather Rizta S Electric Scooter', type:'electric', brand:'Raleigh', year:2022, price_per_hour:150, price_per_day:920, location:'Chennai', rating:4.5, total_reviews:27, is_available:true, badge:'Popular', image:'https://images.openai.com/thumbnails/url/h3hKGnicDcnbCoIwAADQL8pLXsogYkKpOQRdKvkibc4Lmi63WPZV_U5_U-f1fD-tEIzvVJWOZF6YoNVK4NFQGi5uoiMKme4qbyfGurE5PPb_24GocjySHGG4tfseSrwxNV5TS4u5pBT5ntXU2Apd_zRIeDGSyzudZochULII9sR-jrUMsDtkuQkCCFKBU37SQKyLuaykxdZ6kKDjs5quCHWunw1xkeXLOdGGIn-BH3nXPlY', description:'British heritage meets modern tech. Shimano Steps E6100 motor with 418Wh battery for long commutes.', features:['Shimano Steps','418Wh Battery','Hydraulic Disc','Integrated Lights'] },

  { _id:'e7', name:'Komaki X-One Electric Scooter', type:'electric', brand:'Stryder', year:2024, price_per_hour:100, price_per_day:620, location:'Hyderabad', rating:4.3, total_reviews:72, is_available:true, badge:'Made in India', image:'https://images.openai.com/thumbnails/url/FtTlonicDclJDoIwAADAFwlWUZbEGEABpSGAgQoXI3srlq0q-Cj_4290rvP9VIy1g8LzOU37qWV5NmMJXXLlwK4Mp1za3PmhatoW03Lbbf6nqE4mm6lPvHpvAdsq4_fAwnoVnNSX7aEJEr07ZL5j4NywqekSogkPsAY0aXqxAMgTwfkmz33YP4ucHV0YoCbcvXASuL5kjXBEpnvBRJIne4Fj2YiQUeqBEIVJpxU_J5I9ug', description:'Tata-backed electric cycle with 250W motor, 36V lithium battery, and 40km range. Stylish, silent, and made for Indian cities.', features:['250W Motor','36V Li-Ion','40km Range','LED Display'] },

  { _id:'e8', name:'Green Invicta Electric Scooter', type:'electric', brand:'Hero', year:2023, price_per_hour:110, price_per_day:680, location:'Delhi', rating:4.4, total_reviews:48, is_available:true, image:'https://images.openai.com/thumbnails/url/2_gGanicDclJDoIwAADAFwGiIktiDFsQBRSKQbkYoOxaqq0p-Cq_4290rvP9NJRioglCiYrnhGkJOZojka8JzWhb8MVwF0gzYNyievNY_0_TA6g6RWTmes7KRtQTLuzCWIkzxnp482yE6wB2gL16w_CaM7FwtcMqAgaw_QHO0vkwEhL2S7aMV6ejoowLibhJlQLXkUfrINpqaM391tzKfXbxAsm5yiDbT7vkHcGu_gG8xj5M', description:'Premium Hero electric cycle with 250W rear hub motor, 48V battery, and 50km range. Smart app connectivity and regenerative braking.', features:['250W Hub Motor','48V Battery','50km Range','App Connected'] },

  { _id:'e9', name:'Yakuza Viraj Electric Scooter', type:'electric', brand:'Motovolt', year:2024, price_per_hour:130, price_per_day:800, location:'Bangalore', rating:4.5, total_reviews:33, is_available:true, badge:'Startup', image:'https://images.openai.com/thumbnails/url/bkZ-6HicDcnbCoIwAADQL_KWUSlESImuvFUKzpfQOdwc6mxLsb_qc_qbOq_n-yFScmFrGu7Rc-ES14qselNthCwlRSoaOk2QgXPaN4dx_z_biWrLQ2nY3q-GGVzi9sGjhp-TQKZzXkHUhGyNT_7RU0L63BDd7QBxw1vB_IsR72DKQb3C7G693pbjFnM_YmUQy2gaN8evAysjI4RKUMQlo2CLMqhPkZkkOQBs4iQXP7sVPp0', description:'Indian startup e-bike with 350W motor, swappable battery, and bold urban design. Auto-pedal assist adjusts to your speed automatically.', features:['350W Motor','Swappable Battery','Auto Assist','Bold Design'] },

  { _id:'e10', name:'Matter Aera', type:'electric', brand:'EMotorad', year:2024, price_per_hour:120, price_per_day:750, location:'Pune', rating:4.4, total_reviews:41, is_available:true, image:'https://imgd.aeplcdn.com/1056x594/n/bw/models/colors/matter-select-model-cosmic-blue-1688737115666.png?q=80', description:'Indian fat-tyre e-bike with 250W motor and 7-speed Shimano gears. Conquers sand, mud, and city potholes alike.', features:['Fat Tyres','250W Motor','7-Speed','48V Battery'] },


    // ─────────────────────────────────────────
    // CITY
    // ─────────────────────────────────────────
  { _id:'c1', name:'Hero Splendor Plus', type:'city', brand:'Hero', year:2024, price_per_hour:60, price_per_day:380, location:'Hyderabad', rating:4.3, total_reviews:110, is_available:true, badge:'Most Popular', image:'https://images.openai.com/static-rsc-4/5HvjVM2uS6CNACU0_Z3KRhm-hgPld5_KHvHK4PqiDBbc0BNZTJmamjeEInTJ2D1T-xpr-TdMgQW9WxYmWMA2MEzggNjLO8Hg7MPZGUz4TMN_Mhq8eFO7c0G0xMQwZtROUxZgwFhSfmtA0Y5fJoLpRJ-zBv38IolQlihVGJf2X9qZQq2j6_07xP_parXreULv?purpose=fullsize', description:'Popular Indian city bike with 18-speed gears, dual suspension, and stylish frame. Ideal for daily commuting.', features:['18-Speed Gear','Dual Suspension','Alloy Frame','Disc Brakes'] },

  { _id:'c2', name:'Honda Shine', type:'city', brand:'Firefox', year:2024, price_per_hour:80, price_per_day:500, location:'Bangalore', rating:4.5, total_reviews:72, is_available:true, image:'https://cdn.bikedekho.com/processedimages/honda/shine-bs6/640X309/shine-bs6697b0541ef23f.jpg', description:'Urban commuter bike with 700C wheels and 21-speed Shimano gears. Lightweight and efficient for city rides.', features:['700C Wheels','21-Speed Shimano','Alloy Frame','Caliper Brakes'] },

  { _id:'c3', name:'Bajaj Pulsar 125', type:'city', brand:'Btwin', year:2023, price_per_hour:70, price_per_day:450, location:'Mumbai', rating:4.4, total_reviews:58, is_available:true, image:'https://cdn.bikedekho.com/processedimages/bajaj/pulsar-125/source/pulsar-12569b91c3b7d5f9.jpg', description:'Decathlon’s comfortable hybrid bike with upright posture and smooth ride for urban commuting.', features:['Comfort Geometry','Hybrid Design','Single Speed','Light Frame'] },

  { _id:'c4', name:'TVS Radeon', type:'city', brand:'Montra', year:2024, price_per_hour:85, price_per_day:520, location:'Pune', rating:4.6, total_reviews:49, is_available:true, image:'https://images.openai.com/static-rsc-4/nmBkBV3VMjMFbigv1vC5oCbiTmP8tflBTypRYCWzhqMYRfdNaPFFBvosL5PUuwbvqcyqMMJ1NrUKgU6maTWdtOA8FvgyowD42-hqgDbHnajzrfNHpJBC95sofC3ce8ZMbxrE9M3UVmLEcjId9_GlhZPHfXQO2nzSuRyosKutwsOC01BQGjS2R7G1oCpKgQxp?purpose=fullsize', description:'Premium Indian hybrid city bike with alloy frame and fast-rolling 700C tyres.', features:['700C Tyres','Alloy Frame','21-Speed','Disc Brakes'] },

  { _id:'c5', name:'Hero HF Deluxe', type:'city', brand:'Hero', year:2023, price_per_hour:55, price_per_day:340, location:'Hyderabad', rating:4.2, total_reviews:90, is_available:true, image:'https://images.openai.com/static-rsc-4/hFPfpuZ_RbHbSrXhtgEGSt1fKwyLFkHGJJBdMUVyfwO5JmMCd2RxYvKG13r8Qd6MEIm4DJLgt3ajs_peJOWXFn8aMHhRCna_xy46zEQM63exLhgwsAYH1m8LAdccklAoZocS-0fxUNXzdcW0m6DvcFz2acTEbFAqLSJS8XN4StFk6alR7etTziOccBknOOTR?purpose=fullsize', description:'Budget-friendly city bicycle with 21-speed gears and strong frame for Indian roads.', features:['21-Speed','Dual Disc','Alloy Frame','26T Wheels'] },

  { _id:'c6', name:'TVS Star City Plus', type:'city', brand:'Mach City', year:2023, price_per_hour:65, price_per_day:400, location:'Delhi', rating:4.3, total_reviews:64, is_available:true, badge:'Popular', image:'https://imgd.aeplcdn.com/1280x720/n/cw/ec/211699/star-city-right-front-three-quarter.jpeg?isig=0', description:'Designed for Indian cities with upright seating, 7-speed gears, and puncture-resistant tyres.', features:['7-Speed','Comfort Seat','Puncture Resistant','Carrier'] },

  { _id:'c7', name:'Bajaj CT 110', type:'city', brand:'Hercules', year:2024, price_per_hour:50, price_per_day:300, location:'Hyderabad', rating:4.2, total_reviews:130, is_available:true, badge:'Most Affordable', image:'https://imgd.aeplcdn.com/664x374/n/wg0nigb_1845510.jpg?q=80', description:'Durable Indian bike with sporty design, 21-speed gears, and front suspension.', features:['27.5T Wheels','21-Speed','Front Suspension','Steel Frame'] },

  { _id:'c8', name:'Honda SP 125', type:'city', brand:'BSA', year:2023, price_per_hour:45, price_per_day:280, location:'Chennai', rating:4.1, total_reviews:105, is_available:true, badge:'Icon', image:'https://images.openai.com/static-rsc-4/t7-zoiPLjNSo4JZZOmlSMVbh6Ee9yWXMxOFTZcFPzGZvtEh2lcHXYIPBlIoAKkjNdLec3ED-aPXbhmoOVwsFnxXu3ErWt3OV5rROyePWmQLnrT1cJATuXuR4EffzMwnK4McWU5V2kq7FHSgRsQpcR7oaP5B8JXtOdzozmhuFPrEmWGmA5KuKwl_7DJylYKgW?purpose=fullsize', description:'Classic Indian bicycle with step-through frame, basket, and comfortable ride.', features:['Step-Through Frame','Front Basket','26T Wheels','Comfort Saddle'] },

  { _id:'c9', name:'TVS Apache RTR 160', type:'city', brand:'Atlas', year:2023, price_per_hour:50, price_per_day:320, location:'Delhi', rating:4.0, total_reviews:80, is_available:true, image:'https://images.openai.com/static-rsc-4/jvAoszcR5NqsJh-_DbWZ_LyFcheCvMPF-OcLm2UEsCmI0XhkFVxNn8sQlVMPu39mgHFa_Y6mPpAoO3cI4qBjsDudmooP4JgzbU4lB-JH6x6-og6h1AC7yIOfCHr03z-HzWDxpkNWz2UikkGdFzvm3CYnjjV9ze4NfMY8h8e1p94TlhMTiOrdYNqFjktj-gst?purpose=fullsize', description:'Reliable Indian city bike with sturdy steel frame and simple design for daily use.', features:['Steel Frame','Single Speed','Carrier','Mudguards'] },

  { _id:'c10', name:'Yamaha FZ-S FI', type:'city', brand:'Cradiac', year:2024, price_per_hour:75, price_per_day:460, location:'Bangalore', rating:4.4, total_reviews:55, is_available:true, image:'https://images.openai.com/static-rsc-4/NpoaqhP3F00g38UZG-gKm_sURy3PDtZ5HyVXDpxrgOsY0DProcucSliEh8WmAqLpcC91jz4wl9-THWZDuR9ixJYciNhpK2JwbHwPX0h_vhgJUNibXOgpGJUs1mwOSJugqdeaAGt6kqBbA3HHR7343_HCnkXPKSc653d_ea29ovGUy-2tVA4AGsl0179MQ2lW?purpose=fullsize', description:'Modern hybrid bike with alloy frame, disc brakes, and smooth gear shifting for urban commuters.', features:['21-Speed','Disc Brakes','Alloy Frame','Hybrid Design'] },

    // ─────────────────────────────────────────
    // HYBRID
    // ─────────────────────────────────────────

  // HYBRID
    { _id:'h1', name:'Yamaha FZ-S Fi Hybrid',         type:'hybrid',   brand:'Yamaha Motor',        year:2024, price_per_hour:100, price_per_day:650,  location:'Hyderabad', rating:4.7, total_reviews:63,  is_available:true,  badge:'Great Value',  image:'https://images.openai.com/static-rsc-4/G5Z96Cnaw8YtBwjY0OIu_VjbAiPircSL978FkpiRjoyOiICoSDg6bMmq7A4QE9Duqu9qeogmyHNbSKCsNBYLzB93R_DTq2U2JqWXUXozN8eV4RMcoeNbKnNQYvbn4wYYVCn1813N7cOTGeUnMz33R91sSpAHGFbtz8yK65Zk1g9DlRUMO_ccSzrULZEbZbmX?purpose=fullsize',  description:'Goes anywhere hybrid with RockShox fork and 700c tires. Eats roads and trails equally well.', features:['RockShox Recon','700c Tires','8-Speed Shimano','Disc Brakes'] },
    { _id:'h2', name:'TVS Raider 125',       type:'hybrid',   brand:'TVS Motor',       year:2023, price_per_hour:80,  price_per_day:500,  location:'Chennai',   rating:4.4, total_reviews:29,  is_available:true,  image:'https://imgd.aeplcdn.com/1056x594/n/cw/ec/103183/raider-125-left-side-view-8.jpeg?isig=0&q=80',  description:'Gravel-capable hybrid for roads and light trails. Wide 40mm tires and 21-speed drivetrain.', features:['40mm Gravel Tires','21-Speed','Disc Brakes','Mudguard Ready'] },
    { _id:'h3', name:'Honda SP160',       type:'hybrid',   brand:'Honda',       year:2023, price_per_hour:90,  price_per_day:570,  location:'Bangalore', rating:4.6, total_reviews:47,  is_available:true,  image:'https://imgd.aeplcdn.com/1280x720/n/cw/ec/154781/sp160-right-side-view-11.png?isig=0',  description:'Sport hybrid with ALUXX aluminum frame and 21-speed Shimano. Disc brakes for all-weather confidence.', features:['ALUXX Aluminum','21-Speed','Disc Brakes','Sport Geometry'] },
    { _id:'h4', name:'Bajaj Pulsar N160',       type:'hybrid',   brand:'Bajaj motor',      year:2022, price_per_hour:75,  price_per_day:480,  location:'Delhi',     rating:4.3, total_reviews:22,  is_available:false, image:'https://images.openai.com/static-rsc-4/J2h066HcwTA2Xfq45J0oGqnT4WKyWRQDh4M3eCn42sAJezk8Q7oS8b7QYLTtLVyEiHjFUr8YUYWMkhaQBW6Ek3Tyju73Of5Ak-xdAB2sQ0fpEaWSp1MLlVzJ2s1DJMBMlVqAh49Ar5fctFhWTlB-tbS0zFDm-NqzuERzGUwGgokvfg-KV6h5snzZTZRq-fe5?purpose=fullsize',  description:'Trekking hybrid with SR Suntour Mobie-25 suspension fork and 21-speed Shimano Tourney.', features:['SR Suntour Fork','21-Speed','Reflectors','Kickstand'] },
    { _id:'h5', name:'Hero Splendor Plus XTEC',   type:'hybrid',   brand:'Hero motor',  year:2023, price_per_hour:95,  price_per_day:600,  location:'Pune',      rating:4.5, total_reviews:36,  is_available:true,  image:'https://images.openai.com/static-rsc-4/JVdcNuWBtb7X96LZiYeuMnAPwaOedRdw-c2UEAppTUHfGAN2_dLdd_26neS73I2BOdSXmjaO_Yz_SEIN47kH6066UTW9uGHTVMS4-2NIMs5V1nLi9mlqMXa8I3FCU2brxRXer3NWvmiI5P9eCHzWnITbSTqXBWuBhfPfIVGSpr2S6RmBQ-jxthVH6a87Ph9U?purpose=fullsize',  description:'All-around hybrid with SmartForm C2 alloy and smooth 8-speed Shimano Acera shifting.', features:['SmartForm C2','8-Speed Acera','Disc Brakes','Ergon Grips'] },
    { _id:'h6', name:'TVS Apache RTR 160 4V',        type:'hybrid',   brand:'TVS Motor',     year:2023, price_per_hour:65,  price_per_day:420,  location:'Hyderabad', rating:4.2, total_reviews:51,  is_available:true,  image:'https://images.openai.com/static-rsc-4/2ehOvsHrdcN58BYf8GM9OMtDuLr9cX5Acf1iKtOm6I1mPRnHnjWXIJHbpSEjMofZH-GylDzV9-wdmrHv8dB5QymzKxvL_AfCuHFCb0Px-S5dK49OTVbnAMR6mjQmRBsigMlBoXMSDV0xqPh988stC0icjNyDhuO6YJheaXueE8a4RigtAxv58cUGALLwjPI-?purpose=fullsize',  description:'Indian-made hybrid with 27.5" wheels, 21-speed Shimano, and front suspension. Practical and affordable.', features:['27.5" Wheels','21-Speed Shimano','Front Suspension','Alloy Frame'] },
  ];
}

function demoBookings() {
  const n = Date.now();
  return [
    { _id:'bk1', bike_id:'m1', bike_name:'Trek X-Caliber 9',        bike_brand:'Trek',        bike_type:'mountain', status:'completed', start_time:new Date(n-864e5*5).toISOString(),  end_time:new Date(n-864e5*5+288e5).toISOString(), total_amount:1120,  total_hours:8,  payment_status:'paid',    pickup_location:'Hyderabad Central' },
    { _id:'bk2', bike_id:'c1', bike_name:'Giant Escape 3 City',      bike_brand:'Giant',       bike_type:'city',     status:'confirmed', start_time:new Date(n+864e5*2).toISOString(),  end_time:new Date(n+864e5*3).toISOString(),       total_amount:450,   total_hours:24, payment_status:'paid',    pickup_location:'Banjara Hills' },
    { _id:'bk3', bike_id:'e1', bike_name:'Specialized Vado SL 5.0',  bike_brand:'Specialized', bike_type:'electric', status:'pending',   start_time:new Date(n+864e5*7).toISOString(),  end_time:new Date(n+864e5*7+108e5).toISOString(),total_amount:660,   total_hours:3,  payment_status:'unpaid',  pickup_location:'Jubilee Hills' },
    { _id:'bk4', bike_id:'r1', bike_name:'Trek Émonda SL 6',         bike_brand:'Trek',        bike_type:'road',     status:'active',    start_time:new Date(n-3600e3).toISOString(),   end_time:new Date(n+18e6).toISOString(),          total_amount:850,   total_hours:5,  payment_status:'paid',    pickup_location:'Gachibowli' },
    { _id:'bk5', bike_id:'h1', bike_name:'Trek Dual Sport 3',         bike_brand:'Trek',        bike_type:'hybrid',   status:'cancelled', start_time:new Date(n-864e5*2).toISOString(),  end_time:new Date(n-864e5*1).toISOString(),       total_amount:300,   total_hours:3,  payment_status:'refunded',pickup_location:'Madhapur' },
  ];
}

function demoUsers() {
  return [
    { _id:'u1', name:'Rohan Sharma',   email:'rohan@example.com',   role:'user',   kyc_status:'approved', is_active:true,  phone:'9777777777', created_at:new Date(Date.now()-864e5*30).toISOString() },
    { _id:'u2', name:'Priya Nair',     email:'priya@example.com',   role:'user',   kyc_status:'pending',  is_active:true,  phone:'9666666666', created_at:new Date(Date.now()-864e5*15).toISOString() },
    { _id:'u3', name:'Admin User',     email:'admin@rentbike.in',   role:'admin',  kyc_status:'approved', is_active:true,  phone:'9999999999', created_at:new Date(Date.now()-864e5*60).toISOString() },
    { _id:'u4', name:'Raj Vendor',     email:'vendor@rentbike.in',  role:'vendor', kyc_status:'approved', is_active:true,  phone:'9888888888', created_at:new Date(Date.now()-864e5*45).toISOString() },
    { _id:'u5', name:'Arjun Patel',    email:'arjun@example.com',   role:'user',   kyc_status:'rejected', is_active:false, phone:'9555555555', created_at:new Date(Date.now()-864e5*5).toISOString() },
    { _id:'u6', name:'Sneha Rao',      email:'sneha@example.com',   role:'vendor', kyc_status:'pending',  is_active:true,  phone:'9444444444', created_at:new Date(Date.now()-864e5*2).toISOString() },
    { _id:'u7', name:'Kiran Reddy',    email:'kiran@example.com',   role:'user',   kyc_status:'approved', is_active:true,  phone:'9333333333', created_at:new Date(Date.now()-864e5*20).toISOString() },
    { _id:'u8', name:'Deepika Singh',  email:'deepika@example.com', role:'user',   kyc_status:'approved', is_active:true,  phone:'9222222222', created_at:new Date(Date.now()-864e5*12).toISOString() },
  ];
}
