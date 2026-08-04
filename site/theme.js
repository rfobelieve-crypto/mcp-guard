
(function(){
  var KEY='mg_theme';

  function sync(){
    var on=document.documentElement.getAttribute('data-theme')==='light';
    var btns=document.querySelectorAll('.theme-toggle');
    for(var i=0;i<btns.length;i++){
      btns[i].setAttribute('aria-pressed', String(on));
    }
  }

  if(!window.__mgThemeInit){
    window.__mgThemeInit=true;
    document.documentElement.classList.add('js');
    try{
      if(localStorage.getItem(KEY)==='light'){
        document.documentElement.setAttribute('data-theme','light');
      }
    }catch(e){}

    document.addEventListener('click', function(e){
      var btn=e.target.closest&&e.target.closest('.theme-toggle');
      if(!btn) return;
      var wasLight=document.documentElement.getAttribute('data-theme')==='light';
      if(wasLight){
        document.documentElement.removeAttribute('data-theme');
        try{ localStorage.removeItem(KEY); }catch(e){}
      }else{
        document.documentElement.setAttribute('data-theme','light');
        try{ localStorage.setItem(KEY,'light'); }catch(e){}
      }
      sync();
    });

    document.addEventListener('DOMContentLoaded', sync);
  }

  sync();
})();
