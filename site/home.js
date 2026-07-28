
(function(){
  var c=document.getElementById('scene'); if(!c) return;
  var g=c.getContext('2d'), dpr=Math.min(devicePixelRatio||1,2);
  var W,H,rx,ry,RS,wide, t=0, pulse=0;
  var parX=0,parY=0,tpX=0,tpY=0;
  var still=matchMedia('(prefers-reduced-motion:reduce)').matches;

  var PASS=[95,199,155], WARN=[220,174,74], CRIT=[240,130,122],
      IDLE=[136,164,208], CORE=[168,199,250];
  function rgba(q,a){ return 'rgba('+q[0]+','+q[1]+','+q[2]+','+a+')'; }

  // 機器人素材:黑底圖,以 screen 混合繪製(黑=透明),與整個首屏
  // 「加色混合、光是主體」同一套物理,也免去去背的白邊。
  var img=new Image(), imgOk=false, imgA=0;
  img.onload=function(){ imgOk=true; if(still) settle(); };
  img.src='robot.webp';
  // 素材內的錨點(翻轉後、相對中心、單位 RS):鏡頭、判定點、待複核環。
  // 判定點貼著前爪、隊伍往左下斜排——首屏左上是標題的領土,
  // 封包流走對角線才不會埋在字底下。
  var LENS={x:0.006,y:-0.067}, JPT={x:-0.42,y:0.10}, RING={x:-0.28,y:0.20};

  var dust=[], pk=[], queue=[], scanning=null, scanT=0, cool=26, ringN=0;
  var RING_MAX=6;

  function size(){
    W=c.clientWidth; H=c.clientHeight;
    c.width=W*dpr; c.height=H*dpr; g.setTransform(dpr,0,0,dpr,0,0);
    // 寬螢幕機器人讓到右側,標題才不會壓在它身上;窄螢幕置中偏下。
    wide=W>860;
    rx=wide?W*0.70:W*0.56; ry=wide?H*0.48:H*0.68;
    RS=Math.min(W,H)*(wide?0.66:0.80);
  }
  // 機器人錨點:含滑鼠視差與慢速浮動。所有局部座標經同一組旋轉,
  // 光束的出發點才會黏在鏡頭上,不因浮動而脫節。
  function ax(){ return rx+parX*10; }
  function ay(){ return ry+parY*8+Math.sin(t*0.9)*RS*0.012; }
  function pt(p){ var r=Math.sin(t*0.63)*0.022, ca=Math.cos(r), sa=Math.sin(r),
                  x=p.x*RS, y=p.y*RS;
                  return {x:ax()+x*ca-y*sa, y:ay()+x*sa+y*ca}; }

  // 比例貼著真實稽核結果:絕大多數通過,三成需人工複核,
  // 嚴重問題罕見——罕見不代表不存在,那正是這個工具的用途。
  function verdict(){ var r=Math.random();
    return r>0.97?'crit':(r>0.66?'warn':'pass'); }

  function spawn(){
    var j=pt(JPT);
    return {st:'in', v:verdict(),
            x:-W*0.06+Math.random()*W*0.12,
            y:j.y+(Math.random()*0.55-0.08)*H,
            vx:0, vy:0, u:0, a:0, fl:0, ph:Math.random()*6.283,
            sz:3.2+Math.random()*2.2, col:IDLE, dead:0};
  }

  function init(){
    pk=[]; queue=[]; scanning=null; scanT=0; cool=26; ringN=0;
    for(var i=0;i<8;i++){ var p=spawn(); p.x=Math.random()*W*0.42; pk.push(p); }
    dust=[];
    for(var j=0;j<110;j++)
      dust.push({x:Math.random(), y:Math.random(), s:0.4+Math.random()*1.1,
                 tw:Math.random()*6.283, ly:0.25+Math.random()*0.75});
  }

  // 排隊位:判定點往左下斜排。「排隊、逐一」是這個畫面的重點,
  // 所以封包不是各自亂飛,而是進隊等待被叫號。
  function slot(i){ var j=pt(JPT);
    return {x:j.x-(i+1)*RS*0.075+Math.sin(t*1.1+i*2.3)*2,
            y:j.y+(i+1)*RS*0.048+Math.sin(t*1.3+i*1.7)*3}; }

  function step(p){
    var j, k;
    if(p.st==='in'){
      k=queue.indexOf(p); if(k<0){ queue.push(p); k=queue.length-1; }
      j=slot(k);
      p.x+=(j.x-p.x)*0.045; p.y+=(j.y-p.y)*0.045;
      if(Math.abs(j.x-p.x)+Math.abs(j.y-p.y)<7) p.st='queue';
      p.a=Math.min(1,p.a+0.02);
    } else if(p.st==='queue'){
      k=queue.indexOf(p); j=slot(k);
      p.x+=(j.x-p.x)*0.10; p.y+=(j.y-p.y)*0.10; p.a=Math.min(1,p.a+0.02);
    } else if(p.st==='scan'){
      j=pt(JPT);
      p.x+=(j.x-p.x)*0.16; p.y+=(j.y-p.y)*0.16;
    } else if(p.st==='pass'){
      // 通過:收進機器人下方的綠色流,再流出畫面右緣——「收集」的意象
      p.u+=0.006+p.u*0.004;
      var a0=pt(JPT), a1={x:ax(), y:ay()+RS*0.44}, a2={x:W+80, y:ay()+RS*0.55},
          s2=1-p.u, b=2*s2*p.u, c2=p.u*p.u;
      p.x=a0.x*s2*s2+a1.x*b+a2.x*c2; p.y=a0.y*s2*s2+a1.y*b+a2.y*c2;
      if(p.u>=1) p.dead=1;
    } else if(p.st==='warn'){
      p.ph+=0.016; j=pt(RING);
      p.x+=(j.x+Math.cos(p.ph)*RS*0.155-p.x)*0.08;
      p.y+=(j.y+Math.sin(p.ph)*RS*0.052-p.y)*0.08;
      // 偶爾放行一顆:待複核是狀態不是終點,環也不該無限累積
      if(Math.random()<0.0016){ p.st='pass'; p.u=0; ringN--; }
    } else if(p.st==='crit'){
      p.x+=p.vx; p.y+=p.vy; p.vx*=1.012;
      p.a-=0.011; if(p.a<=0||p.x<-60) p.dead=1;
    }
  }

  function judge(){
    var p=scanning; if(!p) return;
    p.col=p.v==='crit'?CRIT:p.v==='warn'?WARN:PASS;
    pulse=1; p.fl=1;                       // 判定瞬間:封包上的擴散環
    if(p.v==='pass'){ p.st='pass'; p.u=0; }
    else if(p.v==='warn'){
      if(ringN>=RING_MAX){ p.st='pass'; p.u=0; }   // 環滿了就先放行離場
      else { var rc=pt(RING); p.st='warn'; ringN++;
             p.ph=Math.atan2(p.y-rc.y, p.x-rc.x); }
    } else { p.st='crit'; p.vx=-(2.6+Math.random()*1.6);
             p.vy=(Math.random()-0.5)*1.6; }
    scanning=null; cool=12+Math.random()*22;
  }

  function draw(){
    t+=0.0165; pulse*=0.94;
    parX+=(tpX-parX)*0.05; parY+=(tpY-parY)*0.05;
    if(imgOk) imgA=Math.min(1,imgA+0.03);
    // 鋪不透明的深空底色,不能只 clear:透明底上 screen 混合會把
    // 素材的黑當成實色蓋掉頁面背景,方形邊界就浮出來了。
    g.fillStyle='#07090E'; g.fillRect(0,0,W,H);

    // 星塵:視差層,給出「這是一個空間」的底
    g.globalCompositeOperation='lighter';
    for(var i=0;i<dust.length;i++){
      var u=dust[i],
          x=u.x*W-parX*22*u.ly, y=u.y*H-parY*16*u.ly,
          tw=0.24+Math.sin(t*1.7+u.tw)*0.14;
      g.fillStyle=rgba(IDLE, tw*u.ly*0.55);
      g.beginPath(); g.arc(x,y,u.s*u.ly*1.5,0,6.283); g.fill();
    }
    g.globalCompositeOperation='source-over';

    // 排程:一次只檢查一顆——「逐一評估」就是這個狀態機本身
    if(scanning){ scanT--; if(scanT<=0) judge(); }
    else if(cool>0){ cool--; }
    else if(queue.length){ scanning=queue.shift(); scanning.st='scan'; scanT=40; }
    if(pk.length<18&&Math.random()<0.05) pk.push(spawn());

    // 待複核環的軌道:極淡,只是暗示那裡有一個「等待區」
    var rc=pt(RING);
    g.strokeStyle=rgba(WARN,0.10); g.lineWidth=1;
    g.beginPath();
    g.ellipse(rc.x,rc.y,RS*0.155,RS*0.052,0,0,6.283); g.stroke();

    drawRobot();

    for(var n=pk.length-1;n>=0;n--){
      var p=pk[n]; step(p);
      if(p.dead){ pk.splice(n,1); var q=queue.indexOf(p);
                  if(q>-1) queue.splice(q,1); continue; }
      drawPk(p);
    }

    if(scanning) drawBeam(scanning);
  }

  function drawRobot(){
    if(!imgOk||imgA<=0) return;
    var r=Math.sin(t*0.63)*0.022;
    g.save();
    g.translate(ax(),ay()); g.rotate(r); g.scale(-1,1);   // 面朝左,迎向封包
    g.globalCompositeOperation='screen'; g.globalAlpha=imgA;
    g.drawImage(img,-RS/2,-RS/2,RS,RS);
    // 再疊一層低透明度的加色:screen 保形,lighter 補亮——
    // 深色機身在深空背景上需要這半檔的提亮才站得出來。
    g.globalCompositeOperation='lighter'; g.globalAlpha=imgA*0.22;
    g.drawImage(img,-RS/2,-RS/2,RS,RS);
    g.restore();
    // 鏡頭的呼吸與判定脈衝:光疊在素材上,加色
    var L=pt(LENS), ph=0.5+Math.sin(t*2.2)*0.5,
        rr=RS*(0.055+ph*0.008+pulse*0.05);
    g.globalCompositeOperation='lighter';
    var lg=g.createRadialGradient(L.x,L.y,0,L.x,L.y,rr*3.4);
    lg.addColorStop(0,rgba(CORE,(0.30+ph*0.08+pulse*0.45)*imgA));
    lg.addColorStop(0.3,rgba(CORE,0.10*imgA));
    lg.addColorStop(1,rgba(CORE,0));
    g.fillStyle=lg; g.beginPath(); g.arc(L.x,L.y,rr*3.4,0,6.283); g.fill();
    g.globalCompositeOperation='source-over';
  }

  function drawBeam(p){
    var L=pt(LENS), k=scanT>26?(34-scanT)/8:scanT<8?scanT/8:1;
    g.globalCompositeOperation='lighter';
    var bg=g.createLinearGradient(L.x,L.y,p.x,p.y);
    bg.addColorStop(0,rgba(CORE,0.80*k)); bg.addColorStop(1,rgba(CORE,0.18*k));
    g.strokeStyle=bg; g.lineWidth=2;
    g.beginPath(); g.moveTo(L.x,L.y); g.lineTo(p.x,p.y); g.stroke();
    // 掃描口徑:在封包上收攏成一個檢查圈
    g.strokeStyle=rgba(CORE,0.5*k); g.lineWidth=1;
    g.beginPath(); g.arc(p.x,p.y,p.sz+5+(1-k)*3,0,6.283); g.stroke();
    g.globalCompositeOperation='source-over';
  }

  function drawPk(p){
    var col=p.col, a=p.a, rad=p.sz;
    if(p.st==='scan'){ a=1; rad=p.sz+1.4; }
    if(p.st==='warn') a*=0.75;
    g.globalCompositeOperation='lighter';
    if(p.st==='crit'){                       // 拒絕:紅色拖尾,彈回深空
      g.strokeStyle=rgba(col,0.30*a); g.lineWidth=1.2;
      g.beginPath(); g.moveTo(p.x,p.y); g.lineTo(p.x-p.vx*7,p.y-p.vy*7);
      g.stroke();
    }
    if(p.st==='pass'&&p.u>0){                // 通過:綠色的流
      g.strokeStyle=rgba(col,0.22*a); g.lineWidth=1.1;
      g.beginPath(); g.moveTo(p.x,p.y); g.lineTo(p.x-8,p.y-2); g.stroke();
    }
    g.fillStyle=rgba(col,0.16*a);
    g.beginPath(); g.arc(p.x,p.y,rad*2.8,0,6.283); g.fill();
    g.fillStyle=rgba(col,0.92*a);
    g.beginPath(); g.arc(p.x,p.y,rad,0,6.283); g.fill();
    if(p.fl>0.08){                           // 判定閃光:一圈往外散的環
      g.strokeStyle=rgba(col,p.fl*0.55); g.lineWidth=1.2;
      g.beginPath(); g.arc(p.x,p.y,rad+4+(1-p.fl)*26,0,6.283); g.stroke();
      p.fl*=0.94;
    }
    g.globalCompositeOperation='source-over';
  }

  function loop(){ draw(); requestAnimationFrame(loop); }
  // 不播動畫時仍跑滿一段,讓畫面停在「已經運作一陣子」的狀態,
  // 然後再走到「光束正在檢查一顆封包」的瞬間才停——靜態讀者
  // (reduce-motion、OG 截圖)看到的必須是產品隱喻最強的那一格。
  function settle(){
    var i;
    for(i=0;i<560;i++) draw();
    for(i=0;i<600&&!(scanning&&scanT<30&&scanT>16);i++) draw();
  }
  addEventListener('resize',function(){ size(); init(); if(still) settle(); });
  addEventListener('pointermove',function(e){
    if(e.clientY>innerHeight*1.15) return;
    tpX=(e.clientX/innerWidth-0.5)*2; tpY=(e.clientY/innerHeight-0.5)*2;
  },{passive:true});

  size(); init();
  if(still) settle(); else loop();
})();


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
