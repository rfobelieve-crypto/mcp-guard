
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
