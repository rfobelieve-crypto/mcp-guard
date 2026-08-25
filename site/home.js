
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

window.__MCPG_INDEX__={"DIALLOUBE-RESEARCH/hypernatt-terminal":{"v":"🔴 不要安裝","t":"倉庫與作者帳號都不存在（DIALLOUBE-RESEARCH/hypernatt-terminal）"},"paperclipai/paperclip":{"v":"🟡 需人工複核","t":"安裝時會自動執行腳本：postinstall","x":1},"mims-harvard/ToolUniverse":{"v":"🟡 需人工複核","t":"指令檔要求下載並直接執行遠端腳本"},"t8y2/dbx":{"v":"🟡 需人工複核","t":"npm 套件標示的倉庫與實際來源不一致","x":1},"Klavis-AI/klavis":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"JerBouma/FinanceToolkit":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"homeassistant-ai/ha-mcp":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"akutishevsky/nutrition-mcp":{"v":"🟡 需人工複核","t":"npm 套件標示的倉庫與實際來源不一致","x":1},"aks129/HealthClawGuardrails":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"iowarp/clio-kit":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"Arjun0606/smolanalytics":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"upstash/context7":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"bytedance/UI-TARS-desktop":{"v":"🟡 需人工複核","t":"npm 套件標示的倉庫與實際來源不一致","x":1},"MervinPraison/PraisonAI":{"v":"🟡 需人工複核","t":"setup.py 覆寫了安裝期指令","x":1},"callstack/agent-device":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"blazickjp/arxiv-mcp-server":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"vmoranv/jshookmcp":{"v":"🟡 需人工複核","t":"安裝時會自動執行腳本：postinstall","x":1},"zereight/gitlab-mcp":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"timescale/pg-aiguide":{"v":"🟡 需人工複核","t":"指令檔要求下載並直接執行遠端腳本"},"dongdongbh/Mindwtr":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"blitzdotdev/blitz-mac":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"svnscha/mcp-windbg":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"8beeeaaat/touchdesigner-mcp":{"v":"🟡 需人工複核","t":"PyPI 套件標示的倉庫與實際來源不一致","x":1},"burningion/video-editing-mcp":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"surendranb/google-analytics-mcp":{"v":"🟡 需人工複核","t":"指令檔要求下載並直接執行遠端腳本"},"ganapativs/microcharts":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"Dave-London/Pare":{"v":"🟡 需人工複核","t":"npm 套件標示的倉庫與實際來源不一致","x":1},"codefuturist/email-mcp":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"waystation-ai/mcp":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"WenyuChiou/research-hub":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"davidmosiah/google-health-mcp":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"umbraco/Umbraco-CMS-MCP-Dev":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"BerkKilicoglu/google-health-fitbit-mcp":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"LaZZy0v0/tijori-finance-mcp":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"davidmosiah/samsung-health-mcp":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"JosueM1109/personal-finance-mcp":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"AlgoVaultLabs/crypto-quant-signal-mcp":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"PhilipAD/health-export-mcp":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"ChromeDevTools/chrome-devtools-mcp":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"HeyPuter/puter":{"v":"🟡 需人工複核","t":"npm 套件標示的倉庫與實際來源不一致"},"amruthpillai/reactive-resume":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"DeusData/codebase-memory-mcp":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"JanDeDobbeleer/oh-my-posh":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"modelscope/FunASR":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"hangwin/mcp-chrome":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"modelcontextprotocol/inspector":{"v":"🟡 需人工複核","t":"安裝時會自動執行腳本：postinstall"},"LaurieWired/GhidraMCP":{"v":"🟡 需人工複核","t":"超過 14 個月沒有更新"},"wonderwhy-er/DesktopCommanderMCP":{"v":"🟡 需人工複核","t":"安裝時會自動執行腳本：postinstall"},"BrowserMCP/mcp":{"v":"🟡 需人工複核","t":"超過 16 個月沒有更新"},"antvis/mcp-server-chart":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"nowork-studio/NotFair":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"Ataraxy-Labs/sem":{"v":"🟡 需人工複核","t":"安裝時會自動執行腳本：postinstall"},"jgravelle/jcodemunch-mcp":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"bergside/typeui":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"winedarksea/AutoTS":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"mbailey/voicemode":{"v":"🟡 需人工複核","t":"指令檔要求下載並直接執行遠端腳本"},"Vrun-design/openflowkit":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"awkoy/notion-mcp-server":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"pulsemcp/mcp-servers":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"freema/mcp-design-system-extractor":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"Kastalien-Research/thoughtbox":{"v":"🟡 需人工複核","t":"指令檔含零寬字元"},"Grey-Iris/easy-notion-mcp":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"n24q02m/better-notion-mcp":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"AION-Analytics/aion-indian-market-intelligence":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"hollaugo/tutorials":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"SidneyBissoli/medical-terminologies-mcp":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"RetrogradeLabs/lune-mcp-server":{"v":"🟡 需人工複核","t":"⚠ 會執行外部指令 / 開子行程（超出宣稱用途）","x":1},"alexalexalex222/frontend-design-loop-mcp":{"v":"🟡 需人工複核","t":"⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）","x":1},"SpikeyCoder/website-auditor-mcp":{"v":"🟡 需人工複核","t":"⚠ 會讀寫本機檔案（超出宣稱用途）","x":1},"modelcontextprotocol/servers":{"v":"🟢 未發現明顯風險","t":"—"},"D4Vinci/Scrapling":{"v":"🟢 未發現明顯風險","t":"—"},"ruvnet/ruflo":{"v":"🟢 未發現明顯風險","t":"—"},"tldraw/tldraw":{"v":"🟢 未發現明顯風險","t":"—"},"PostHog/posthog":{"v":"🟢 未發現明顯風險","t":"—"},"microsoft/playwright-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"github/github-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"PrefectHQ/fastmcp":{"v":"🟢 未發現明顯風險","t":"—"},"agentskills/agentskills":{"v":"🟢 未發現明顯風險","t":"—"},"Skyvern-AI/skyvern":{"v":"🟢 未發現明顯風險","t":"—"},"screenpipe/screenpipe":{"v":"🟢 未發現明顯風險","t":"—"},"googleapis/mcp-toolbox":{"v":"🟢 未發現明顯風險","t":"—"},"GLips/Figma-Context-MCP":{"v":"🟢 未發現明顯風險","t":"—"},"coder/coder":{"v":"🟢 未發現明顯風險","t":"—"},"kubeshark/kubeshark":{"v":"🟢 未發現明顯風險","t":"—"},"BeehiveInnovations/pal-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"awslabs/mcp":{"v":"🟢 未發現明顯風險","t":"—"},"droidrun/mobilerun":{"v":"🟢 未發現明顯風險","t":"—"},"idosal/git-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"MystenLabs/sui":{"v":"🟢 未發現明顯風險","t":"—"},"firecrawl/firecrawl-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"modelcontextprotocol/registry":{"v":"🟢 未發現明顯風險","t":"—"},"CursorTouch/Windows-MCP":{"v":"🟢 未發現明顯風險","t":"—"},"airweave-ai/airweave":{"v":"🟢 未發現明顯風險","t":"—"},"getsentry/XcodeBuildMCP":{"v":"🟢 未發現明顯風險","t":"—"},"repowise-dev/repowise":{"v":"🟢 未發現明顯風險","t":"—"},"mobile-next/mobile-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"mock-server/mockserver-monorepo":{"v":"🟢 未發現明顯風險","t":"—"},"exa-labs/exa-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"apify/apify-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"KnockOutEZ/wigolo":{"v":"🟢 未發現明顯風險","t":"—"},"firebase/firebase-tools":{"v":"🟢 未發現明顯風險","t":"—"},"txn2/kubefwd":{"v":"🟢 未發現明顯風險","t":"—"},"cloudflare/mcp-server-cloudflare":{"v":"🟢 未發現明顯風險","t":"—"},"tolgee/tolgee-platform":{"v":"🟢 未發現明顯風險","t":"—"},"IvanMurzak/Unity-MCP":{"v":"🟢 未發現明顯風險","t":"—"},"basicmachines-co/basic-memory":{"v":"🟢 未發現明顯風險","t":"—"},"revolist/revogrid":{"v":"🟢 未發現明顯風險","t":"—"},"bytebase/dbhub":{"v":"🟢 未發現明顯風險","t":"—"},"giancarloerra/SocratiCode":{"v":"🟢 未發現明顯風險","t":"—"},"codeaashu/claude-code":{"v":"🟢 未發現明顯風險","t":"—"},"signerlabs/ShipSwift":{"v":"🟢 未發現明顯風險","t":"—"},"supabase/mcp":{"v":"🟢 未發現明顯風險","t":"—"},"nteract/semiotic":{"v":"🟢 未發現明顯風險","t":"—"},"medplum/medplum":{"v":"🟢 未發現明顯風險","t":"—"},"dgunning/edgartools":{"v":"🟢 未發現明顯風險","t":"—"},"tavily-ai/tavily-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"llmsresearch/paperbanana":{"v":"🟢 未發現明顯風險","t":"—"},"containers/kubernetes-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"figma/mcp-server-guide":{"v":"🟢 未發現明顯風險","t":"—"},"MicrosoftDocs/mcp":{"v":"🟢 未發現明顯風險","t":"—"},"LetsFG/LetsFG":{"v":"🟢 未發現明顯風險","t":"—"},"stripe/ai":{"v":"🟢 未發現明顯風險","t":"—"},"kubeshop/testkube":{"v":"🟢 未發現明顯風險","t":"—"},"NuGet/Home":{"v":"🟢 未發現明顯風險","t":"—"},"hashicorp/terraform-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"mnemox-ai/tradememory-protocol":{"v":"🟢 未發現明顯風險","t":"—"},"robotmcp/ros-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"nrwl/nx-console":{"v":"🟢 未發現明顯風險","t":"—"},"Intuition-Lab/personal-model":{"v":"🟢 未發現明顯風險","t":"—"},"anypost/emailmd":{"v":"🟢 未發現明顯風險","t":"—"},"BetterDB-inc/monitor":{"v":"🟢 未發現明顯風險","t":"—"},"sceneview/sceneview":{"v":"🟢 未發現明顯風險","t":"—"},"codespar/mcp-dev-latam":{"v":"🟢 未發現明顯風險","t":"—"},"jpicklyk/task-orchestrator":{"v":"🟢 未發現明顯風險","t":"—"},"nirholas/three.ws":{"v":"🟢 未發現明顯風險","t":"—"},"Tapetide-hq/nse-bse-indian-stock-market-data-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"JuzzyDee/audio-analyzer-rs":{"v":"🟢 未發現明顯風險","t":"—"},"norman-finance/norman-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"shibayu36/slack-explorer-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"KyuRish/mcp-dashboards":{"v":"🟢 未發現明顯風險","t":"—"},"counterpoint-studio/audio-file-mcp-app":{"v":"🟢 未發現明顯風險","t":"—"},"truss44/mcp-crypto-price":{"v":"🟢 未發現明顯風險","t":"—"},"debridge-finance/debridge-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"mcparmory/registry":{"v":"🟢 未發現明顯風險","t":"—"},"jtalk22/slack-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"jonradoff/lightcms":{"v":"🟢 未發現明顯風險","t":"—"},"grahammccain/chart-library-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"marlinjai/email-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"danishashko/yahoo-finance-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"coyaSONG/youtube-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"mindstone/mcp-servers":{"v":"🟢 未發現明顯風險","t":"—"},"base76-research-lab/token-compressor":{"v":"🟢 未發現明顯風險","t":"—"},"CryptoCultCurt/appfolio-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"amcharts/amcharts5-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"MidOSresearch/midos":{"v":"🟢 未發現明顯風險","t":"—"},"embeddedlayers/mcp-analytics":{"v":"🟢 未發現明顯風險","t":"—"},"arcadia-finance/mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"thinkchainai/mcpbundles":{"v":"🟢 未發現明顯風險","t":"—"},"chia-health/chia-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"cyanheads/cdc-health-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"clueso-ai/clueso-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"blantian/lanhu-design-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"studiomeyer-io/mcp-video":{"v":"🟢 未發現明顯風險","t":"—"},"friendlygeorge/docker-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"megberts/mcp-websitepublisher-ai":{"v":"🟢 未發現明顯風險","t":"—"},"L337-org/docker-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"gattjoe/ACMS":{"v":"🟢 未發現明顯風險","t":"—"},"alisaitteke/docker-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"ofershap/mcp-server-docker":{"v":"🟢 未發現明顯風險","t":"—"},"webtoolbox/websitetoolbox-mcp":{"v":"🟢 未發現明顯風險","t":"—"},"NomaCMS/nomacms-mcp-server":{"v":"🟢 未發現明顯風險","t":"—"},"pipeworx-io/mcp-cms":{"v":"🟢 未發現明顯風險","t":"—"},"deployment-io/cursor-plugin":{"v":"🟢 未發現明顯風險","t":"—"},"timergy-app/timergy":{"v":"🟢 未發現明顯風險","t":"—"},"rog0x/mcp-docker-tools":{"v":"🟢 未發現明顯風險","t":"—"},"edesent/custom-website-editor":{"v":"🟢 未發現明顯風險","t":"—"},"uptimemonitoring/examples":{"v":"🟢 未發現明顯風險","t":"—"},"AIops-tools/Monitoring-AIops":{"v":"🟢 未發現明顯風險","t":"—"}};

(function(){
  var form=document.getElementById('probe');
  if(!form) return;
  // 漸進增強的第二步:HTML 出貨的是 <input>(沒有 JS 時 Enter 仍能送出
  // 到 /registry/?q=)。有 JS 才換成 textarea,因為設定檔是多行的,
  // 貼進單行輸入框看不到自己貼了什麼。
  var input=document.getElementById('probe-q');
  if(input&&input.tagName==='INPUT'){
    var ta=document.createElement('textarea');
    ta.id=input.id; ta.name=input.name; ta.rows=1;
    ta.placeholder=input.placeholder; ta.spellcheck=false;
    ta.className=input.className;
    var desc=input.getAttribute('aria-describedby');
    if(desc) ta.setAttribute('aria-describedby',desc);
    input.parentNode.replaceChild(ta,input);
    input=ta;
  }
  var btn=document.getElementById('probe-go');
  var box=document.getElementById('probe-res');
  var INDEX=window.__MCPG_INDEX__||{};

  function esc(s){ return String(s==null?'':s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

  // textarea 隨內容長高:單筆查詢時看起來就是一行輸入框,
  // 貼進設定檔才展開——使用者要看得見自己貼了什麼。
  function autogrow(){
    input.style.height='auto';
    input.style.height=Math.min(input.scrollHeight,260)+'px';
  }
  input.addEventListener('input',autogrow);
  // 單行時 Enter 直接送出(維持輸入框的直覺);多行內容按 Enter 是換行,
  // 那時候用按鈕送出。Shift+Enter 一律換行。
  input.addEventListener('keydown',function(e){
    if(e.key==='Enter'&&!e.shiftKey&&input.value.indexOf('\n')<0){
      e.preventDefault();
      form.dispatchEvent(new Event('submit',{cancelable:true}));
    }
  });

  // 使用者手上真正有的是安裝指令或設定檔片段，不是乾淨的 owner/repo。
  // 這裡只做「夠用的」前端比對；權威的正規化在 mcp_guard/userinput.py，
  // 兩邊不一致時以後端為準。
  function guessSlug(raw){
    var s=(raw||'').trim();
    var m=s.match(/github\.com[\/:]([\w.-]+\/[\w.-]+)/);
    if(m) return m[1].replace(/\.git$/,'');
    if(/^[\w.-]+\/[\w.-]+$/.test(s)) return s;
    return '';
  }

  function show(html){ box.innerHTML=html; box.hidden=false; }

  // 結論字串 → 樣式類別。務必比對整個 emoji，不要比對 charAt(0)：
  // 🔴 🟡 🟢 的第一個 UTF-16 單元都是 \ud83d，用單一 code unit 判斷會讓
  // 三種結論全部落進同一類——實際發生過，通過的專案被渲染成紅色警示。
  function seal(v){
    var cls = v.indexOf('🔴')===0 ? 'crit'
            : v.indexOf('🟡')===0 ? 'warn'
            : 'pass';
    return '<span class="seal '+cls+'">'+esc(v.slice(2).trim())+'</span>';
  }

  function renderLocal(slug,rec){
    show('<div class="res-head">'+seal(rec.v)+
      '<span class="res-name">'+esc(slug)+'</span></div>'+
      '<p class="res-why">'+esc(rec.t)+'</p>'+
      '<p class="res-more"><a href="registry/?q='+encodeURIComponent(slug)+
      '">看完整檢查發現與證據 →</a></p>');
  }

  function renderRemote(d){
    var top=(d.findings||[]).filter(function(f){
      return f.severity==='CRITICAL'||f.severity==='HIGH'; }).slice(0,5);
    var items=top.map(function(f){
      return '<li><b>'+esc(f.title)+'</b><br>'+esc(f.detail)+'</li>'; }).join('');
    var notes=(d.notes||[]).map(function(n){
      return '<li>'+esc(n)+'</li>'; }).join('');
    show('<div class="res-head">'+seal(d.verdict)+
      '<span class="res-name">'+esc(d.slug||d.target)+'</span></div>'+
      '<p class="res-why">'+esc(d.why)+
      '　<span style="color:var(--muted)">已掃描 '+(d.files_scanned||0)+
      ' 個檔案</span></p>'+
      (items?'<ul class="res-list">'+items+'</ul>':'')+
      (notes?'<ul class="res-list">'+notes+'</ul>':'')+
      '<p class="res-more">這份結果是<b>現在即時掃的</b>，未收錄在總表中。'+
      '你可以自己複現：<code>mcp-guard '+esc(d.target)+'</code></p>');
  }

  // ── 設定檔健檢 ──────────────────────────────────────────────
  // 解析一律在瀏覽器完成,原始設定檔一個位元組都不送出去。
  // 理由不是潔癖:Claude Desktop 設定檔的 env 區塊裡放的就是使用者的
  // GitHub token、Slack token、資料庫連線字串。一個教人檢查供應鏈風險
  // 的網站,自己變成金鑰外洩管道會非常諷刺。只有萃取出來的套件名會離開
  // 這台裝置。
  var RUNNERS={npx:1,uvx:1,pnpx:1,bunx:1,npm:1,pnpm:1,yarn:1,bun:1,
               pip:1,pip3:1,pipx:1,uv:1,dlx:1,exec:1,install:1,add:1,run:1};
  var FLAGS={'-y':1,'--yes':1,'-q':1,'--quiet':1,'--silent':1,'-f':1,
             '--force':1,'-g':1,'--global':1,'-p':1,'--package':1};

  function stripVer(s){
    if(s.charAt(0)==='@'){
      var i=s.indexOf('/');
      if(i<0) return s;
      return s.slice(0,i+1)+s.slice(i+1).split('@')[0];
    }
    return s.split('@')[0];
  }
  function fromArgs(args){
    for(var i=0;i<args.length;i++){
      var t=String(args[i]||'').trim();
      if(!t||FLAGS[t]||RUNNERS[t.toLowerCase()]) continue;
      if(t.charAt(0)==='-') continue;
      if(/^[\/.~]/.test(t)||/^[A-Za-z]:[\\/]/.test(t)) continue;  // 路徑參數
      if(t.indexOf('=')>-1&&t.charAt(0)!=='@') continue;              // 環境變數
      return stripVer(t);
    }
    return '';
  }
  // 回傳 [{key:設定檔裡的名稱, pkg:套件名}],找不到就跳過那一項。
  function parseConfig(text){
    var obj;
    try{ obj=JSON.parse(text); }catch(err){ return null; }
    var out=[];
    function fromServer(key,s){
      if(!s||typeof s!=='object') return;
      var pkg=Array.isArray(s.args)?fromArgs(s.args):'';
      if(!pkg&&typeof s.command==='string'&&!RUNNERS[s.command.toLowerCase()])
        pkg=stripVer(s.command);
      if(pkg) out.push({key:key,pkg:pkg});
    }
    function walk(o){
      if(!o||typeof o!=='object') return;
      var holder=o.mcpServers||o.servers||o.mcp;
      if(holder&&typeof holder==='object'){
        Object.keys(holder).forEach(function(k){ fromServer(k,holder[k]); });
        return;
      }
      if(o.command||o.args){ fromServer(o.name||'(未命名)',o); return; }
      Object.keys(o).forEach(function(k){ walk(o[k]); });
    }
    walk(obj);
    return out;
  }

  // done  = 拿到結論的
  // failed = 查不動的（限流、連線失敗）
  // settled = 已經有下文的，不論成敗——摘要句要靠它才知道跑完了沒。
  // 只數 done 的話,只要有一筆失敗,摘要就會永遠停在「已檢查 1/2…」,
  // 那個刪節號會讓人一直等一個不會來的結果。
  function tally(rows){
    var t={crit:0,warn:0,pass:0,over:0,done:0,failed:0,settled:0};
    rows.forEach(function(r){
      if(r.err){ t.failed++; t.settled++; return; }
      if(!r.verdict) return;
      t.done++; t.settled++;
      if(r.verdict.indexOf('🔴')===0) t.crit++;
      else if(r.verdict.indexOf('🟡')===0) t.warn++;
      else t.pass++;
      if(r.over) t.over++;
    });
    return t;
  }

  function renderInventory(rows){
    var t=tally(rows);
    // 跑完之後的結論句。三種狀況要講不同的話,尤其是「一筆都沒查成」——
    // 那時候不能講「沒有任何一個超出宣稱用途」,那會把「查不到」講成「查過了沒事」。
    var done;
    if(!t.done){
      done = '<span class="inv-wait">全部都查不動，可能是暫時限流，稍後再試一次。</span>';
    }else{
      done = (t.over
        ? '其中 <b class="warn-n">'+t.over+' 個要求了超出宣稱用途的權限</b>。'
        : '沒有任何一個要求超出宣稱用途的權限。')
        + (t.failed
            ? '<span class="inv-wait">（另有 '+t.failed+' 個查不動，未列入計算）</span>'
            : '');
    }
    var head='<p class="inv-sum">你正在跑 <b>'+rows.length+'</b> 個 MCP。'+
      // 還在跑：用「已檢查 N/M…」表示進度
      (t.settled<rows.length
        ? '<span class="inv-wait">（已檢查 '+t.settled+'/'+rows.length+'…）</span>'
        : done)+'</p>';
    var sum='<p class="inv-tally">'+
      '<span>🔴 '+t.crit+' 不要安裝</span>'+
      '<span>🟡 '+t.warn+' 需複核</span>'+
      '<span>🟢 '+t.pass+' 未發現明顯風險</span>'+
      (t.failed ? '<span>⚠ '+t.failed+' 查不動</span>' : '')+'</p>';
    var items=rows.map(function(r){
      var right = r.verdict
        ? (r.over?'<span class="inv-flag">⚠ 超出宣稱用途</span>':'')
        : (r.err?'<span class="inv-wait">'+esc(r.err)+'</span>'
                :'<span class="inv-wait"><span class="spin"></span>檢查中…</span>');
      var badge=r.verdict?seal(r.verdict):'<span class="seal">—</span>';
      var name=r.slug
        ? '<a href="registry/?q='+encodeURIComponent(r.slug)+'">'+esc(r.slug)+'</a>'
        : esc(r.pkg);
      return '<li class="inv-item">'+badge+
        '<span class="inv-key">'+name+
        '<span class="inv-pkg">設定檔名稱：'+esc(r.key)+'　套件：'+esc(r.pkg)+
        '</span></span>'+right+'</li>';
    }).join('');
    show(head+sum+
      '<p class="inv-priv">設定檔在你的瀏覽器裡解析，<b>原始內容沒有送出</b>——'+
      '裡面的 env 金鑰不會離開這台裝置，只有套件名被拿去查。</p>'+
      '<ul class="inv-list">'+items+'</ul>');
  }

  function runInventory(list){
    var rows=list.map(function(x){
      return {key:x.key,pkg:x.pkg,verdict:'',over:false,slug:'',err:''};
    });
    renderInventory(rows);
    btn.disabled=true;

    var queue=rows.slice(), active=0, MAX=3;
    function next(){
      if(!queue.length&&active===0){ btn.disabled=false; return; }
      while(active<MAX&&queue.length){
        (function(r){
          active++;
          // 已收錄的直接命中索引,不打 API。索引是以 owner/repo 為鍵,
          // 而設定檔給的是 npm 套件名,所以目前多半要走即時掃描——
          // 若日後 data.json 補上 npm 名,這裡多數會變成秒開。
          var hit=INDEX[r.pkg];
          if(hit){
            r.verdict=hit.v; r.over=!!hit.x; r.slug=r.pkg;
            active--; renderInventory(rows); next(); return;
          }
          fetch('/api/scan?target='+encodeURIComponent(r.pkg),
                {credentials:'same-origin'})
            .then(function(res){ return res.json(); })
            .then(function(d){
              if(d&&d.ok){
                r.verdict=d.verdict; r.slug=d.slug||'';
                r.over=(d.findings||[]).some(function(f){
                  return f.title.indexOf('超出宣稱用途')>-1; });
              }else{
                r.err='查不動';
              }
            })
            .catch(function(){ r.err='連線失敗'; })
            .then(function(){ active--; renderInventory(rows); next(); });
        })(queue.shift());
      }
    }
    next();
  }

  form.addEventListener('submit',function(e){
    e.preventDefault();
    var raw=(input.value||'').trim();
    if(!raw) return;

    // 看起來像設定檔就走健檢
    if(raw.charAt(0)==='{'||raw.charAt(0)==='['){
      var list=parseConfig(raw);
      if(list&&list.length){ runInventory(list); return; }
      if(list&&!list.length){
        show('<p class="res-why res-err">這份設定檔裡找不到任何 MCP server。</p>'+
             '<p class="res-more">預期會有 <code>mcpServers</code> 區塊。</p>');
        return;
      }
      // JSON 解析失敗 → 落回單筆流程,交給後端的正規化去處理
    }

    var slug=guessSlug(raw);
    if(slug && INDEX[slug]){ renderLocal(slug,INDEX[slug]); return; }

    btn.disabled=true;
    show('<span class="spin"></span>正在即時稽核，約需數秒…');

    fetch('/api/scan?target='+encodeURIComponent(raw),
          {credentials:'same-origin'})
      .then(function(r){ return r.json().then(function(j){
        return {status:r.status, body:j}; }); })
      .then(function(res){
        if(res.body && res.body.ok){ renderRemote(res.body); return; }
        // 抓取失敗刻意不假裝成結論——沒查到事實就不給答案。
        show('<p class="res-why res-err">'+
          esc((res.body&&res.body.error)||'稽核失敗。')+'</p>'+
          '<p class="res-more">你也可以在本機自己跑：'+
          '<code>mcp-guard '+esc(raw)+'</code></p>');
      })
      .catch(function(){
        show('<p class="res-why res-err">連不上稽核服務。</p>'+
          '<p class="res-more">在本機自己跑一樣能得到結果：'+
          '<code>mcp-guard '+esc(raw)+'</code></p>');
      })
      .then(function(){ btn.disabled=false; });
  });
})();
