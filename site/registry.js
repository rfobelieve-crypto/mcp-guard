
(function(){
  var els=[].slice.call(document.querySelectorAll('.rv'));
  if(!('IntersectionObserver' in window)||
     matchMedia('(prefers-reduced-motion:reduce)').matches){
    els.forEach(function(e){e.classList.add('in');}); return;
  }
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
    });
  },{rootMargin:'0px 0px -12% 0px'});
  els.forEach(function(e,i){ e.style.transitionDelay=(Math.min(i,6)*55)+'ms';
                             io.observe(e); });
})();


(function(){
  var rows=[].slice.call(document.querySelectorAll('details.row'));
  var chips=[].slice.call(document.querySelectorAll('.chip'));
  var cats=[].slice.call(document.querySelectorAll('.cat-chip'));
  var q=document.getElementById('q'), empty=document.getElementById('empty');
  var count=document.getElementById('count');
  // 兩個獨立維度：結論（安不安全）與用途（是幹嘛的）。
  // 使用者的問題通常是「我要找瀏覽器工具，而且要能裝的」——兩者要能疊加。
  var filter='all', cat='all', dom='all';
  var domBar=document.getElementById('dombar');

  // 收藏：存在使用者自己的瀏覽器（localStorage），不上傳。
  // 我們拿不到的資料，就不必解釋怎麼保管。
  var FKEY='mg_favs', favs=[];
  try{ favs=JSON.parse(localStorage.getItem(FKEY))||[]; }catch(e){}
  function saveF(){ try{ localStorage.setItem(FKEY,JSON.stringify(favs)); }catch(e){} }
  var favChip=document.querySelector('.chip[data-f="fav"]');
  function favCount(){ if(favChip) favChip.querySelector('b').textContent=favs.length; }
  [].slice.call(document.querySelectorAll('.fav')).forEach(function(b){
    var s=b.dataset.s;
    if(favs.indexOf(s)>-1){ b.setAttribute('aria-pressed','true'); b.textContent='★'; }
    b.addEventListener('click',function(e){
      e.preventDefault(); e.stopPropagation();     // 別觸發 summary 的展開
      var i=favs.indexOf(s);
      if(i>-1){ favs.splice(i,1); b.setAttribute('aria-pressed','false'); b.textContent='☆'; }
      else{ favs.push(s); b.setAttribute('aria-pressed','true'); b.textContent='★'; }
      saveF(); favCount(); if(filter==='fav') apply();
    });
  });
  favCount();

  function apply(){
    var t=(q.value||'').toLowerCase().trim(), shown=0;
    rows.forEach(function(r){
      var vis=(filter==='all'||(filter==='fav'
                ? favs.indexOf(r.dataset.s)>-1
                : r.dataset.v===filter)) &&
              (cat==='all'||r.dataset.c===cat) &&
              (dom==='all'||r.dataset.d===dom) &&
              (!t||r.dataset.search.indexOf(t)>-1);
      r.hidden=!vis; if(vis) shown++;
    });
    empty.hidden=shown>0;
    if(count) count.textContent=shown;
  }
  chips.forEach(function(c){ c.addEventListener('click',function(){
    chips.forEach(function(o){o.setAttribute('aria-pressed',o===c);});
    filter=c.dataset.f; apply(); }); });
  cats.forEach(function(c){ c.addEventListener('click',function(){
    cats.forEach(function(o){o.setAttribute('aria-pressed',o===c);});
    cat=c.dataset.c; apply(); }); });
  q.addEventListener('input',apply);

  // 從網址帶入篩選：?c=browser（能力）或 ?d=finance（領域）。
  // 「該裝哪個」那一頁靠這個把讀者送過來。領域不做成第三排 chips——
  // 三排按鈕會把這頁變成控制面板，改用一條可以關掉的提示列。
  var qs=new URLSearchParams(location.search);
  var wantC=qs.get('c'), wantD=qs.get('d');
  if(wantC){
    var hit=cats.filter(function(c){return c.dataset.c===wantC;})[0];
    if(hit) hit.click();
  }
  if(wantD && domBar){
    var row=rows.filter(function(r){return r.dataset.d===wantD;})[0];
    if(row){
      dom=wantD;
      domBar.hidden=false;
      domBar.querySelector('b').textContent=row.dataset.dz||wantD;
      domBar.querySelector('button').addEventListener('click',function(){
        dom='all'; domBar.hidden=true; apply();
      });
      apply();
    }
  }
})();


(function(){
  var el=document.getElementById('auth');
  if(!el||!window.fetch) return;
  fetch('/api/me',{credentials:'same-origin'}).then(function(r){
    if(r.status===401) return null;
    if(!r.ok) throw 0;
    return r.json();
  }).then(function(u){
    if(u&&u.login){
      var img=new Image(); img.alt=''; img.referrerPolicy='no-referrer';
      img.src=u.avatar;
      var s=document.createElement('span'); s.className='u';
      s.textContent=u.login;
      var a=document.createElement('a'); a.href='/api/auth/logout';
      a.textContent='登出';
      el.append(img,s,a);
      document.documentElement.dataset.user=u.login;
    }else{
      var a2=document.createElement('a'); a2.className='signin';
      a2.href='/api/auth/login'; a2.title='以 GitHub 帳號登入';
      a2.textContent=el.dataset.signin||'登入';
      el.append(a2);
    }
  }).catch(function(){});
})();


(function(){
  var dlg=document.getElementById('subDlg');
  if(!dlg||!window.fetch||!dlg.showModal) return;
  var kind='scan';
  var repo=document.getElementById('subRepo'),
      note=document.getElementById('subNote'),
      go=document.getElementById('subGo'),
      msg=document.getElementById('subMsg'),
      ttl=document.getElementById('subTitle'),
      hint=document.getElementById('subHint');
  function signed(){ return !!document.documentElement.dataset.user; }
  [].slice.call(document.querySelectorAll('[data-submit]')).forEach(function(b){
    b.addEventListener('click',function(){
      kind=b.dataset.submit;
      ttl.textContent=kind==='scan'?'提交掃描請求':'回報誤判';
      hint.textContent=kind==='scan'
        ?'告訴我們該掃哪個專案。請求會成為公開的 GitHub issue，掃描完成後列入總表。'
        :'指出哪份報告的哪個結論有誤。經確認的誤報會立即修正，並收進回歸測試確保不再重犯。';
      if(b.dataset.repo) repo.value=b.dataset.repo;
      go.textContent=signed()?'送出':'用 GitHub 登入後送出';
      msg.textContent='';
      dlg.showModal();
    });
  });
  document.getElementById('subCancel').addEventListener('click',function(e){
    e.preventDefault(); dlg.close();
  });
  go.addEventListener('click',function(e){
    e.preventDefault();
    if(!signed()){ location.href='/api/auth/login'; return; }
    var r=(repo.value||'').trim()
          .replace(/^https?:\/\/github\.com\//,'').replace(/\/+$/,'');
    if(!/^[\w.-]+\/[\w.-]+$/.test(r)){
      msg.textContent='請輸入 owner/repo 格式（或貼 GitHub 網址）'; return;
    }
    go.disabled=true; msg.textContent='送出中…';
    fetch('/api/submit',{method:'POST',credentials:'same-origin',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({type:kind,repo:r,note:(note.value||'').trim()})
    }).then(function(x){
      return x.json().then(function(j){ return {ok:x.ok,j:j}; });
    }).then(function(o){
      go.disabled=false;
      if(o.ok&&o.j.url){
        msg.textContent='';
        var a=document.createElement('a');
        a.href=o.j.url; a.target='_blank'; a.rel='noopener';
        a.textContent=o.j.existing?'已有相同的請求，進度看這裡 ↗':'已建立，追蹤進度 ↗';
        msg.append(a);
      }else msg.textContent=(o.j&&o.j.hint)||'送出失敗，請稍後再試';
    }).catch(function(){ go.disabled=false; msg.textContent='網路錯誤，請稍後再試'; });
  });
})();
