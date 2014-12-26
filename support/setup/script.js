/* Tooltipster v3.0.5 */;(function(e,t,n){function o(t,n){this.bodyOverflowX;this.checkInterval=null;this.content;this.$el=e(t);this.elProxyPosition;this.$elProxy;this.enabled=true;this.options=e.extend({},s,n);this.mouseIsOverProxy=false;this.namespace="tooltipster-"+Math.round(Math.random()*1e5);this.status="hidden";this.timerHide=null;this.timerShow=null;this.$tooltip;this.options.iconTheme=this.options.iconTheme.replace(".","");this.options.theme=this.options.theme.replace(".","");this.init()}function u(t,n){var r=true;e.each(t,function(e,i){if(typeof n[e]==="undefined"||t[e]!==n[e]){r=false;return false}});return r}function l(){return!f&&a}function c(){var e=n.body||n.documentElement,t=e.style,r="transition";if(typeof t[r]=="string"){return true}v=["Moz","Webkit","Khtml","O","ms"],r=r.charAt(0).toUpperCase()+r.substr(1);for(var i=0;i<v.length;i++){if(typeof t[v[i]+r]=="string"){return true}}return false}var r="tooltipster",s={animation:"fade",arrow:true,arrowColor:"",autoClose:true,content:null,contentAsHTML:false,contentCloning:true,delay:200,fixedWidth:0,maxWidth:0,functionInit:function(e,t){},functionBefore:function(e,t){t()},functionReady:function(e,t){},functionAfter:function(e){},icon:"(?)",iconCloning:true,iconDesktop:false,iconTouch:false,iconTheme:"tooltipster-icon",interactive:false,interactiveTolerance:350,offsetX:0,offsetY:0,onlyOne:false,position:"top",positionTracker:false,speed:350,timer:0,theme:"tooltipster-default",touchDevices:true,trigger:"hover",updateAnimation:true};o.prototype={init:function(){var t=this;if(n.querySelector){if(t.options.content!==null){t.setContent(t.options.content)}else{var r=t.$el.attr("title");if(typeof r==="undefined")r=null;t.setContent(r)}var i=t.options.functionInit(t.$el,t.content);if(typeof i!=="undefined")t.setContent(i);t.$el.removeAttr("title").addClass("tooltipstered");if(!a&&t.options.iconDesktop||a&&t.options.iconTouch){if(typeof t.options.icon==="string"){t.$elProxy=e('<span class="'+t.options.iconTheme+'"></span>');t.$elProxy.text(t.options.icon)}else{if(t.options.iconCloning)t.$elProxy=t.options.icon.clone(true);else t.$elProxy=t.options.icon}t.$elProxy.insertAfter(t.$el)}else{t.$elProxy=t.$el}if(t.options.trigger=="hover"){t.$elProxy.on("mouseenter."+t.namespace,function(){if(!l()||t.options.touchDevices){t.mouseIsOverProxy=true;t.showTooltip()}}).on("mouseleave."+t.namespace,function(){if(!l()||t.options.touchDevices){t.mouseIsOverProxy=false}});if(a&&t.options.touchDevices){t.$elProxy.on("touchstart."+t.namespace,function(){t.showTooltipNow()})}}else if(t.options.trigger=="click"){t.$elProxy.on("click."+t.namespace,function(){if(!l()||t.options.touchDevices){t.showTooltip()}})}}},showTooltip:function(){var e=this;if(e.status!="shown"&&e.status!="appearing"){if(e.options.delay){e.timerShow=setTimeout(function(){if(e.options.trigger=="click"||e.options.trigger=="hover"&&e.mouseIsOverProxy){e.showTooltipNow()}},e.options.delay)}else e.showTooltipNow()}},showTooltipNow:function(){var n=this;clearTimeout(n.timerShow);n.timerShow=null;clearTimeout(n.timerHide);n.timerHide=null;if(n.enabled&&n.content!==null){if(n.options.onlyOne){e(".tooltipstered").not(n.$el).each(function(t,n){var i=e(n),s=i[r]("status"),o=i[r]("option","autoClose");if(s!=="hidden"&&s!=="disappearing"&&o){i[r]("hide")}})}n.options.functionBefore(n.$elProxy,function(){if(n.status!=="hidden"){var r=0;if(n.status==="disappearing"){n.status="appearing";if(c()){n.$tooltip.clearQueue().removeClass("tooltipster-dying").addClass("tooltipster-"+n.options.animation+"-show");if(n.options.speed>0)n.$tooltip.delay(n.options.speed);n.$tooltip.queue(function(){n.status="shown"})}else{n.$tooltip.stop().fadeIn(function(){n.status="shown"})}}}else{n.status="appearing";var r=n.options.speed;n.bodyOverflowX=e("body").css("overflow-x");e("body").css("overflow-x","hidden");var i="tooltipster-"+n.options.animation,s="-webkit-transition-duration: "+n.options.speed+"ms; -webkit-animation-duration: "+n.options.speed+"ms; -moz-transition-duration: "+n.options.speed+"ms; -moz-animation-duration: "+n.options.speed+"ms; -o-transition-duration: "+n.options.speed+"ms; -o-animation-duration: "+n.options.speed+"ms; -ms-transition-duration: "+n.options.speed+"ms; -ms-animation-duration: "+n.options.speed+"ms; transition-duration: "+n.options.speed+"ms; animation-duration: "+n.options.speed+"ms;",o=n.options.fixedWidth>0?"width:"+Math.round(n.options.fixedWidth)+"px;":"",u=n.options.maxWidth>0?"max-width:"+Math.round(n.options.maxWidth)+"px;":"",f=n.options.interactive?"pointer-events: auto;":"";n.$tooltip=e('<div class="tooltipster-base '+n.options.theme+'" style="'+o+" "+u+" "+f+" "+s+'"><div class="tooltipster-content"></div></div>');if(c())n.$tooltip.addClass(i);n.insertContent();n.$tooltip.appendTo("body");n.positionTooltip();n.options.functionReady(n.$el,n.$tooltip);if(c()){n.$tooltip.addClass(i+"-show");if(n.options.speed>0)n.$tooltip.delay(n.options.speed);n.$tooltip.queue(function(){n.status="shown"})}else{n.$tooltip.css("display","none").fadeIn(n.options.speed,function(){n.status="shown"})}n.setCheckInterval();e(t).on("scroll."+n.namespace+" resize."+n.namespace,function(){n.positionTooltip()});if(n.options.autoClose){e("body").off("."+n.namespace);if(n.options.trigger=="hover"){if(a){setTimeout(function(){e("body").on("touchstart."+n.namespace,function(){n.hideTooltip()})},0)}if(n.options.interactive){if(a){n.$tooltip.on("touchstart."+n.namespace,function(e){e.stopPropagation()})}var l=null;n.$elProxy.add(n.$tooltip).on("mouseleave."+n.namespace+"-autoClose",function(){clearTimeout(l);l=setTimeout(function(){n.hideTooltip()},n.options.interactiveTolerance)}).on("mouseenter."+n.namespace+"-autoClose",function(){clearTimeout(l)})}else{n.$elProxy.on("mouseleave."+n.namespace+"-autoClose",function(){n.hideTooltip()})}}else if(n.options.trigger=="click"){setTimeout(function(){e("body").on("click."+n.namespace+" touchstart."+n.namespace,function(){n.hideTooltip()})},0);if(n.options.interactive){n.$tooltip.on("click."+n.namespace+" touchstart."+n.namespace,function(e){e.stopPropagation()})}}}}if(n.options.timer>0){n.timerHide=setTimeout(function(){n.timerHide=null;n.hideTooltip()},n.options.timer+r)}})}},setCheckInterval:function(){var t=this;t.checkInterval=setInterval(function(){if(e("body").find(t.$el).length===0||e("body").find(t.$elProxy).length===0||t.status=="hidden"||e("body").find(t.$tooltip).length===0){if(t.status=="shown"||t.status=="appearing")t.hideTooltip();t.cancelCheckInterval()}else{if(t.options.positionTracker){var n=t.positionInfo(t.$elProxy),r=false;if(u(n.dimension,t.elProxyPosition.dimension)){if(t.$elProxy.css("position")==="fixed"){if(u(n.position,t.elProxyPosition.position))r=true}else{if(u(n.offset,t.elProxyPosition.offset))r=true}}if(!r){t.positionTooltip()}}}},200)},cancelCheckInterval:function(){clearInterval(this.checkInterval);this.checkInterval=null},hideTooltip:function(){var n=this;clearTimeout(n.timerShow);n.timerShow=null;clearTimeout(n.timerHide);n.timerHide=null;if(n.status=="shown"||n.status=="appearing"){n.status="disappearing";var r=function(){n.status="hidden";n.$tooltip.remove();n.$tooltip=null;e(t).off("."+n.namespace);e("body").off("."+n.namespace).css("overflow-x",n.bodyOverflowX);n.$elProxy.off("."+n.namespace+"-autoClose");n.options.functionAfter(n.$elProxy)};if(c()){n.$tooltip.clearQueue().removeClass("tooltipster-"+n.options.animation+"-show").addClass("tooltipster-dying");if(n.options.speed>0)n.$tooltip.delay(n.options.speed);n.$tooltip.queue(r)}else{n.$tooltip.stop().fadeOut(n.options.speed,r)}}},setContent:function(e){if(typeof e==="object"&&e!==null&&this.options.contentCloning){e=e.clone(true)}this.content=e},insertContent:function(){var e=this,t=this.$tooltip.find(".tooltipster-content");if(typeof e.content==="string"&&!e.options.contentAsHTML){t.text(e.content)}else{t.empty().append(e.content)}},updateTooltip:function(e){var t=this;t.setContent(e);if(t.content!==null){if(t.status!=="hidden"){t.insertContent();t.positionTooltip();if(t.options.updateAnimation){if(c()){t.$tooltip.css({width:"","-webkit-transition":"all "+t.options.speed+"ms, width 0ms, height 0ms, left 0ms, top 0ms","-moz-transition":"all "+t.options.speed+"ms, width 0ms, height 0ms, left 0ms, top 0ms","-o-transition":"all "+t.options.speed+"ms, width 0ms, height 0ms, left 0ms, top 0ms","-ms-transition":"all "+t.options.speed+"ms, width 0ms, height 0ms, left 0ms, top 0ms",transition:"all "+t.options.speed+"ms, width 0ms, height 0ms, left 0ms, top 0ms"}).addClass("tooltipster-content-changing");setTimeout(function(){if(t.status!="hidden"){t.$tooltip.removeClass("tooltipster-content-changing");setTimeout(function(){if(t.status!=="hidden"){t.$tooltip.css({"-webkit-transition":t.options.speed+"ms","-moz-transition":t.options.speed+"ms","-o-transition":t.options.speed+"ms","-ms-transition":t.options.speed+"ms",transition:t.options.speed+"ms"})}},t.options.speed)}},t.options.speed)}else{t.$tooltip.fadeTo(t.options.speed,.5,function(){if(t.status!="hidden"){t.$tooltip.fadeTo(t.options.speed,1)}})}}}}else{t.hideTooltip()}},positionInfo:function(e){return{dimension:{height:e.outerHeight(false),width:e.outerWidth(false)},offset:e.offset(),position:{left:parseInt(e.css("left")),top:parseInt(e.css("top"))}}},positionTooltip:function(){var n=this;if(e("body").find(n.$tooltip).length!==0){n.$tooltip.css("width","");n.elProxyPosition=n.positionInfo(n.$elProxy);var r=null,s=e(t).width(),o=n.elProxyPosition,u=n.$tooltip.outerWidth(false),a=n.$tooltip.innerWidth()+1,f=n.$tooltip.outerHeight(false),l=null;if(n.$elProxy.is("area")){var c=n.$elProxy.attr("shape"),h=n.$elProxy.parent().attr("name"),p=e('img[usemap="#'+h+'"]'),d=p.offset().left,v=p.offset().top,m=n.$elProxy.attr("coords")!==undefined?n.$elProxy.attr("coords").split(","):undefined;if(c=="circle"){var g=parseInt(m[0]),y=parseInt(m[1]),b=parseInt(m[2]);o.dimension.height=b*2;o.dimension.width=b*2;o.offset.top=v+y-b;o.offset.left=d+g-b}else if(c=="rect"){var g=parseInt(m[0]),y=parseInt(m[1]),w=parseInt(m[2]),E=parseInt(m[3]);o.dimension.height=E-y;o.dimension.width=w-g;o.offset.top=v+y;o.offset.left=d+g}else if(c=="poly"){var S=[],x=[],T=0,N=0,C=0,k=0,L="even";for(i=0;i<m.length;i++){var A=parseInt(m[i]);if(L=="even"){if(A>C){C=A;if(i===0){T=C}}if(A<T){T=A}L="odd"}else{if(A>k){k=A;if(i==1){N=k}}if(A<N){N=A}L="even"}}o.dimension.height=k-N;o.dimension.width=C-T;o.offset.top=v+N;o.offset.left=d+T}else{o.dimension.height=p.outerHeight(false);o.dimension.width=p.outerWidth(false);o.offset.top=v;o.offset.left=d}}if(n.options.fixedWidth===0){n.$tooltip.css({width:Math.round(a)+"px","padding-left":"0px","padding-right":"0px"})}var O=0,M=0,_=0,D=parseInt(n.options.offsetY),P=parseInt(n.options.offsetX),H=n.options.position;function B(){var n=e(t).scrollLeft();if(O-n<0){r=O-n;O=n}if(O+u-n>s){r=O-(s+n-u);O=s+n-u}}function j(n,r){if(o.offset.top-e(t).scrollTop()-f-D-12<0&&r.indexOf("top")>-1){H=n}if(o.offset.top+o.dimension.height+f+12+D>e(t).scrollTop()+e(t).height()&&r.indexOf("bottom")>-1){H=n;_=o.offset.top-f-D-12}}if(H=="top"){var F=o.offset.left+u-(o.offset.left+o.dimension.width);O=o.offset.left+P-F/2;_=o.offset.top-f-D-12;B();j("bottom","top")}if(H=="top-left"){O=o.offset.left+P;_=o.offset.top-f-D-12;B();j("bottom-left","top-left")}if(H=="top-right"){O=o.offset.left+o.dimension.width+P-u;_=o.offset.top-f-D-12;B();j("bottom-right","top-right")}if(H=="bottom"){var F=o.offset.left+u-(o.offset.left+o.dimension.width);O=o.offset.left-F/2+P;_=o.offset.top+o.dimension.height+D+12;B();j("top","bottom")}if(H=="bottom-left"){O=o.offset.left+P;_=o.offset.top+o.dimension.height+D+12;B();j("top-left","bottom-left")}if(H=="bottom-right"){O=o.offset.left+o.dimension.width+P-u;_=o.offset.top+o.dimension.height+D+12;B();j("top-right","bottom-right")}if(H=="left"){O=o.offset.left-P-u-12;M=o.offset.left+P+o.dimension.width+12;var I=o.offset.top+f-(o.offset.top+n.$elProxy.outerHeight(false));_=o.offset.top-I/2-D;if(O<0&&M+u>s){var q=parseFloat(n.$tooltip.css("border-width"))*2,R=u+O-q;n.$tooltip.css("width",R+"px");f=n.$tooltip.outerHeight(false);O=o.offset.left-P-R-12-q;I=o.offset.top+f-(o.offset.top+n.$elProxy.outerHeight(false));_=o.offset.top-I/2-D}else if(O<0){O=o.offset.left+P+o.dimension.width+12;r="left"}}if(H=="right"){O=o.offset.left+P+o.dimension.width+12;M=o.offset.left-P-u-12;var I=o.offset.top+f-(o.offset.top+n.$elProxy.outerHeight(false));_=o.offset.top-I/2-D;if(O+u>s&&M<0){var q=parseFloat(n.$tooltip.css("border-width"))*2,R=s-O-q;n.$tooltip.css("width",R+"px");f=n.$tooltip.outerHeight(false);I=o.offset.top+f-(o.offset.top+n.$elProxy.outerHeight(false));_=o.offset.top-I/2-D}else if(O+u>s){O=o.offset.left-P-u-12;r="right"}}if(n.options.arrow){var U="tooltipster-arrow-"+H;if(n.options.arrowColor.length<1){var z=n.$tooltip.css("background-color")}else{var z=n.options.arrowColor}if(!r){r=""}else if(r=="left"){U="tooltipster-arrow-right";r=""}else if(r=="right"){U="tooltipster-arrow-left";r=""}else{r="left:"+Math.round(r)+"px;"}if(H=="top"||H=="top-left"||H=="top-right"){var W=parseFloat(n.$tooltip.css("border-bottom-width")),X=n.$tooltip.css("border-bottom-color")}else if(H=="bottom"||H=="bottom-left"||H=="bottom-right"){var W=parseFloat(n.$tooltip.css("border-top-width")),X=n.$tooltip.css("border-top-color")}else if(H=="left"){var W=parseFloat(n.$tooltip.css("border-right-width")),X=n.$tooltip.css("border-right-color")}else if(H=="right"){var W=parseFloat(n.$tooltip.css("border-left-width")),X=n.$tooltip.css("border-left-color")}else{var W=parseFloat(n.$tooltip.css("border-bottom-width")),X=n.$tooltip.css("border-bottom-color")}if(W>1){W++}var V="";if(W!==0){var J="",K="border-color: "+X+";";if(U.indexOf("bottom")!==-1){J="margin-top: -"+Math.round(W)+"px;"}else if(U.indexOf("top")!==-1){J="margin-bottom: -"+Math.round(W)+"px;"}else if(U.indexOf("left")!==-1){J="margin-right: -"+Math.round(W)+"px;"}else if(U.indexOf("right")!==-1){J="margin-left: -"+Math.round(W)+"px;"}V='<span class="tooltipster-arrow-border" style="'+J+" "+K+';"></span>'}n.$tooltip.find(".tooltipster-arrow").remove();var Q='<div class="'+U+' tooltipster-arrow" style="'+r+'">'+V+'<span style="border-color:'+z+';"></span></div>';n.$tooltip.append(Q)}n.$tooltip.css({top:Math.round(_)+"px",left:Math.round(O)+"px"})}}};e.fn[r]=function(){var t=arguments;if(this.length===0){if(typeof t[0]==="string"){var n=true;switch(t[0]){case"setDefaults":e.extend(s,t[1]);break;default:n=false;break}if(n)return true;else return this}else{return this}}else{if(typeof t[0]==="string"){var r="#*$~&";this.each(function(){var n=e(this).data("tooltipster");if(n){switch(t[0]){case"content":case"update":if(typeof t[1]==="undefined"){r=n.content;return false}else{n.updateTooltip(t[1]);break};case"destroy":n.hideTooltip();if(n.$el[0]!==n.$elProxy[0])n.$elProxy.remove();var i=typeof n.content==="string"?n.content:e("<div></div>").append(n.content).html();n.$el.removeClass("tooltipstered").attr("title",i).removeData("tooltipster").off("."+n.namespace);break;case"disable":n.hideTooltip();n.enabled=false;break;case"elementIcon":r=n.$el[0]!==n.$elProxy[0]?n.$elProxy[0]:undefined;return false;case"elementTooltip":r=n.$tooltip?n.$tooltip[0]:undefined;return false;case"enable":n.enabled=true;break;case"hide":n.hideTooltip();break;case"option":r=n.options[t[1]];break;case"reposition":n.positionTooltip();break;case"show":n.showTooltipNow();break;case"status":r=n.status;return false;default:throw new Error('Unknown method .tooltipster("'+t[0]+'")');break}}else{throw new Error("You called Tooltipster's \""+t[0]+'" method on an uninitialized element')}});return r!=="#*$~&"?r:this}else{return this.each(function(){if(!e(this).data("tooltipster")){e(this).data("tooltipster",new o(this,t[0]))}})}}};var a=!!("ontouchstart"in t);var f=false;e("body").one("mousemove",function(){f=true})})(jQuery,window,document);
//fgnass.github.com/spin.js#v1.3.3
!function(a,b){"object"==typeof exports?module.exports=b():"function"==typeof define&&define.amd?define(b):a.Spinner=b()}(this,function(){"use strict";function a(a,b){var c,d=document.createElement(a||"div");for(c in b)d[c]=b[c];return d}function b(a){for(var b=1,c=arguments.length;c>b;b++)a.appendChild(arguments[b]);return a}function c(a,b,c,d){var e=["opacity",b,~~(100*a),c,d].join("-"),f=.01+c/d*100,g=Math.max(1-(1-a)/b*(100-f),a),h=k.substring(0,k.indexOf("Animation")).toLowerCase(),i=h&&"-"+h+"-"||"";return m[e]||(n.insertRule("@"+i+"keyframes "+e+"{0%{opacity:"+g+"}"+f+"%{opacity:"+a+"}"+(f+.01)+"%{opacity:1}"+(f+b)%100+"%{opacity:"+a+"}100%{opacity:"+g+"}}",n.cssRules.length),m[e]=1),e}function d(a,b){var c,d,e=a.style;for(b=b.charAt(0).toUpperCase()+b.slice(1),d=0;d<l.length;d++)if(c=l[d]+b,void 0!==e[c])return c;return void 0!==e[b]?b:void 0}function e(a,b){for(var c in b)a.style[d(a,c)||c]=b[c];return a}function f(a){for(var b=1;b<arguments.length;b++){var c=arguments[b];for(var d in c)void 0===a[d]&&(a[d]=c[d])}return a}function g(a){for(var b={x:a.offsetLeft,y:a.offsetTop};a=a.offsetParent;)b.x+=a.offsetLeft,b.y+=a.offsetTop;return b}function h(a,b){return"string"==typeof a?a:a[b%a.length]}function i(a){return"undefined"==typeof this?new i(a):(this.opts=f(a||{},i.defaults,o),void 0)}function j(){function c(b,c){return a("<"+b+' xmlns="urn:schemas-microsoft.com:vml" class="spin-vml">',c)}n.addRule(".spin-vml","behavior:url(#default#VML)"),i.prototype.lines=function(a,d){function f(){return e(c("group",{coordsize:k+" "+k,coordorigin:-j+" "+-j}),{width:k,height:k})}function g(a,g,i){b(m,b(e(f(),{rotation:360/d.lines*a+"deg",left:~~g}),b(e(c("roundrect",{arcsize:d.corners}),{width:j,height:d.width,left:d.radius,top:-d.width>>1,filter:i}),c("fill",{color:h(d.color,a),opacity:d.opacity}),c("stroke",{opacity:0}))))}var i,j=d.length+d.width,k=2*j,l=2*-(d.width+d.length)+"px",m=e(f(),{position:"absolute",top:l,left:l});if(d.shadow)for(i=1;i<=d.lines;i++)g(i,-2,"progid:DXImageTransform.Microsoft.Blur(pixelradius=2,makeshadow=1,shadowopacity=.3)");for(i=1;i<=d.lines;i++)g(i);return b(a,m)},i.prototype.opacity=function(a,b,c,d){var e=a.firstChild;d=d.shadow&&d.lines||0,e&&b+d<e.childNodes.length&&(e=e.childNodes[b+d],e=e&&e.firstChild,e=e&&e.firstChild,e&&(e.opacity=c))}}var k,l=["webkit","Moz","ms","O"],m={},n=function(){var c=a("style",{type:"text/css"});return b(document.getElementsByTagName("head")[0],c),c.sheet||c.styleSheet}(),o={lines:12,length:7,width:5,radius:10,rotate:0,corners:1,color:"#000",direction:1,speed:1,trail:100,opacity:.25,fps:20,zIndex:2e9,className:"spinner",top:"auto",left:"auto",position:"relative"};i.defaults={},f(i.prototype,{spin:function(b){this.stop();var c,d,f=this,h=f.opts,i=f.el=e(a(0,{className:h.className}),{position:h.position,width:0,zIndex:h.zIndex}),j=h.radius+h.length+h.width;if(b&&(b.insertBefore(i,b.firstChild||null),d=g(b),c=g(i),e(i,{left:("auto"==h.left?d.x-c.x+(b.offsetWidth>>1):parseInt(h.left,10)+j)+"px",top:("auto"==h.top?d.y-c.y+(b.offsetHeight>>1):parseInt(h.top,10)+j)+"px"})),i.setAttribute("role","progressbar"),f.lines(i,f.opts),!k){var l,m=0,n=(h.lines-1)*(1-h.direction)/2,o=h.fps,p=o/h.speed,q=(1-h.opacity)/(p*h.trail/100),r=p/h.lines;!function s(){m++;for(var a=0;a<h.lines;a++)l=Math.max(1-(m+(h.lines-a)*r)%p*q,h.opacity),f.opacity(i,a*h.direction+n,l,h);f.timeout=f.el&&setTimeout(s,~~(1e3/o))}()}return f},stop:function(){var a=this.el;return a&&(clearTimeout(this.timeout),a.parentNode&&a.parentNode.removeChild(a),this.el=void 0),this},lines:function(d,f){function g(b,c){return e(a(),{position:"absolute",width:f.length+f.width+"px",height:f.width+"px",background:b,boxShadow:c,transformOrigin:"left",transform:"rotate("+~~(360/f.lines*j+f.rotate)+"deg) translate("+f.radius+"px,0)",borderRadius:(f.corners*f.width>>1)+"px"})}for(var i,j=0,l=(f.lines-1)*(1-f.direction)/2;j<f.lines;j++)i=e(a(),{position:"absolute",top:1+~(f.width/2)+"px",transform:f.hwaccel?"translate3d(0,0,0)":"",opacity:f.opacity,animation:k&&c(f.opacity,f.trail,l+j*f.direction,f.lines)+" "+1/f.speed+"s linear infinite"}),f.shadow&&b(i,e(g("#000","0 0 4px #000"),{top:"2px"})),b(d,b(i,g(h(f.color,j),"0 0 1px rgba(0,0,0,.1)")));return d},opacity:function(a,b,c){b<a.childNodes.length&&(a.childNodes[b].style.opacity=c)}});var p=e(a("group"),{behavior:"url(#default#VML)"});return!d(p,"transform")&&p.adj?j():k=d(p,"animation"),i});

(function(factory) {

  if (typeof exports == 'object') {
    // CommonJS
    factory(require('jquery'), require('spin'))
  }
  else if (typeof define == 'function' && define.amd) {
    // AMD, register as anonymous module
    define(['jquery', 'spin'], factory)
  }
  else {
    // Browser globals
    if (!window.Spinner) throw new Error('Spin.js not present')
    factory(window.jQuery, window.Spinner)
  }

}(function($, Spinner) {

  $.fn.spin = function(opts, color) {

    return this.each(function() {
      var $this = $(this),
        data = $this.data();

      if (data.spinner) {
        data.spinner.stop();
        delete data.spinner;
      }
      if (opts !== false) {
        opts = $.extend(
          { color: color || $this.css('color') },
          $.fn.spin.presets[opts] || opts
        )
        data.spinner = new Spinner(opts).spin(this)
      }
    })
  }

  $.fn.spin.presets = {
    tiny: { lines: 8, length: 2, width: 2, radius: 3 },
    small: { lines: 8, length: 4, width: 3, radius: 5 },
    large: { lines: 10, length: 8, width: 4, radius: 8 },
    plex:{lines: 13, // The number of lines to draw
  length: 6, // The length of each line
  width: 2, // The line thickness
  radius: 3, // The radius of the inner circle
  corners: 0, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  direction: 1, // 1: clockwise, -1: counterclockwise
  color: '#000', // #rgb or #rrggbb or array of colors
  speed: 1.2, // Rounds per second
  trail: 27, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: false, // Whether to use hardware acceleration
  className: 'spinner', // The CSS class to assign to the spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: 'auto', // Top position relative to parent in px
  left: 'auto' // Left position relative to parent in px
  }}

}));
var daemon_installed 
function checkplatform(){
// 0 = remove option to install as daemon
$.get('daemon_support.txt',{ "_": $.now() }).done(function(data){
	if(data.trim()=="0"){
		$(".wizard:eq(3)").remove()
		$("input[name=bootdaemon]").remove()
		$(".bootdaemon").addClass("grey")
		$('.bootdaemon').tooltipster('content', 'Not available.');
	}
	$('.spacing').cycle({ 
    fx:     'fade', 
    prev:   '#wizardprev', 
    next:   '#wizardnext', 
    after:   onAfter, 
    timeout: 0 
});
})
}
$(function(){

if(getCookie("log") == "true")
	{
		$("#showlog").text("HIDE")
		$("#log").show()
	}

	$(".my-grid-form").hide()
	var spinner = new Spinner().spin();
// 		$("#spin").spin('plex')

// $(".restarting").show()

checkplatform()
refreshlog()

	if(getCookie("log") == "true")
	{
		$("#showlog").text("HIDE")
		$("#log").show()
	}

	$.get('plexconnect_status.txt',{ "_": $.now() }).done(function(data){
		
		if(data.indexOf("not")!= -1)
		{
			$("#stop").hide()
			$("#start").show()
		}
		else
		{
			$("#stop").show()
			$("#start").hide()
		}

	})
	
	// load Settings.cfg
	$.get('Settings.cfg',{ "_": $.now() })
		.done(function(data){
			$(".header").show()
			$("#main").show()
			var lines = data.split('\n');
			   
		    if (lines.length>1){
				for(i=1; i<lines.length; i++)
			    {
					// parse lines from settings.cfg
			       	setting = lines[i].split('=')
			       	
			       	if(setting[0].indexOf("#")){
			       		// parse values and set form element values

			       		// checkboxes
			       		if($("form").find("input[name="+ setting[0].trim() +"]").length>0 && (setting[1].trim() == "True" || setting[1].trim() == "False")){
			       			var thecase =setting[0].trim()
					
							switch (thecase)
							{
								case 'enable_plexgdm': 
							  		
							  		if(setting[1].trim()=="False"){
							  			$("input[name=enable_plexgdm]").prop('checked',false);
							  			$(".enable_plexgdm").removeClass("grey")
							  			$("input[name=ip_pms],input[name=port_pms]").prop("disabled",false)
							  		}
							  		else{
							  			$("input[name=enable_plexgdm]").prop('checked',true);
							  			$(".enable_plexgdm").addClass("grey")
							  			$("input[name=ip_pms],input[name=port_pms]").prop("disabled",true)
							  		}
							  		break

							  	case 'enable_plexconnect_autodetect':
							  		if(setting[1].trim()=="False"){

							  			$('input[name=enable_plexconnect_autodetect]').prop('checked',false);
							  			$(".enable_plexconnect_autodetect").removeClass("grey")
							  			$("input[name=ip_plexconnect],input[name=port_webserver]").prop("disabled",false)

							  		}
							  		else{
							  			$('input[name=enable_plexconnect_autodetect]').prop('checked',true);
							  			$(".enable_plexconnect_autodetect").addClass("grey")
							  			$("input[name=ip_plexconnect],input[name=port_webserver]").prop("disabled",true)
							  		}
							  		break

								case 'enable_dnsserver':
							  		if(setting[1].trim()=="False"){
							  			$("input[name='enable_dnsserver']").prop('checked',false);
							  			$(".enable_dnsserver").addClass("grey")
							  			$("input[name=ip_dnsmaster],input[name=port_dnsserver]").prop("disabled",true)
							  		}
							  		else{
							  			$("input[name='enable_dnsserver']").prop('checked',true);
							  			$(".enable_dnsserver").removeClass("grey")
							  			$("input[name=ip_dnsmaster],input[name=port_dnsserver]").prop("disabled",false)
							  		}
							  		break

							  	case 'enable_webserver_ssl':
							  		if(setting[1].trim()=="False"){
							  			$("input[name='enable_webserver_ssl']").trigger("click").prop('checked',false);
							  		}
							  		else{
							  			$("input[name='enable_webserver_ssl']").prop('checked',true);
							  		}
							  		break

							  	case 'prevent_atv_update':
							  		if(setting[1].trim()=="False"){
							  			$("input[name='prevent_atv_update']").prop('checked',false);
							  		}
							  		else{
							  			$("input[name='prevent_atv_update']").prop('checked',true);
							  		}
							  		break
							  	
							} // end switch case

				   		}

				   		// other fields
				   		if(setting[0].trim()=="loglevel"){
				   			if(setting[1].trim()=="Off"){
				   				$("select[name='loglevel']").val("Off")
				   				$("#showlog").hide()
				   			}
				   			if(setting[1].trim()=="High"){
				   				$("select[name='loglevel']").val("High")
				   			}

				   			if(setting[1].trim()=="Normal"){
				   				$("select[name='loglevel']").val("Normal")
				   			}

				   		}
				   		

				   		if(setting[0].trim()=="hosttointercept"){
				   				$("input[name='hosttointercept']").val(setting[1].trim())
				   				if(setting[1].trim()=="trailers.apple.com"){
				   					$(".trailer-cert").trigger("click")
				   				}
				   				if(setting[1].trim()=="www.icloud.com"){
				   					$(".imovie-cert").trigger("click")
				   				}
				   				if(setting[1].trim()=="secure.marketwatch.com"){
				   					$(".wsj-cert").trigger("click")
				   				}
				   		}
				   		if(setting[0].trim()=="certfile"){
				   				
				   				$("input[name='certfile']").val(setting[1].trim())
				   		}
				   		if(setting[0].trim()=="ip_pms"){
				   			$("input[name=ip_pms]").val(setting[1].trim())
				   		}

				   		if(setting[0].trim()=="ip_plexconnect"){
				   			$("input[name=ip_plexconnect]").val(setting[1].trim())
				   		}

				   		if(setting[0].trim()=="ip_dnsmaster"){
				   			$("input[name=ip_dnsmaster]").val(setting[1].trim())
				   		}

				   		if(setting[0].trim()=="port_ssl"){
				   			$("input[name=port_ssl]").val(setting[1].trim())
				   		}

				   		if(setting[0].trim()=="port_webserver"){
				   			$("input[name=port_webserver]").val(setting[1].trim())
				   		}

				   		if(setting[0].trim()=="port_dnsserver"){
				   			$("input[name=port_dnsserver]").val(setting[1].trim())
				   		}

				   		if(setting[0].trim()=="port_pms"){
				   			$("input[name=port_pms]").val(setting[1].trim())
				   		}

			    	}
			    }
			}
	   		$.get('daemon_installed.txt',{ "_": $.now() })
	   		.done(function(data){
	   			if(data.trim()=="1"){
	   				daemon_installed=1
		   			$("input[name=bootdaemon]").prop("checked",true)
		   			$('.bootdaemon').tooltipster('content', 'PlexConnect has been installed as boot-daemon and will automatically restarted after a reboot.<Br/><br/>Uncheck and save to uninstall the daemon.');
	   			}
	   			else{
	   				daemon_installed=0
					$("input[name=bootdaemon]").prop("checked",false)
	   			}
	   		})

		})

		// no settings file found - set default values
		.fail(function(){
			document.cookie="log=; expires=Thu, 18 Dec 1970 12:00:00 GMT";
			$("#log").hide()
			$("#ipaddress").text(window.location.hostname)
			$(".header h1").hide()
			$(".restarting h4").text("INSTALLING...STARTING UP")

			//$(".header").css("padding-top","30%")
			$(".header").show()
			$(".header img").attr("src","support/setup/media/images/plex_large.png").css({"opacity":0})
			.animate({ opacity:1,height:"300px" },800,"easeInOutExpo",function(){})
			.delay(100)
			.animate({ opacity:1,height:"40px" },1000,"easeInOutExpo",function(){
				$(".header h1").fadeIn(500,"easeInOutExpo", function(){
					$("#introduction").fadeIn(1000,"easeInOutExpo", function(){
						$(".wizard:eq(0)").addClass("active").show()
					})
				})
			})
			
			$("input[name=enable_plexgdm]").prop('checked',true);
			$(".enable_plexgdm").addClass("grey")
			$("input[name=ip_pms],input[name=port_pms]").prop("disabled",true)
  			$('input[name=enable_plexconnect_autodetect]').prop('checked',true);
  			$(".enable_plexconnect_autodetect").addClass("grey")
  			$("input[name=ip_plexconnect],input[name=port_webserver]").prop("disabled",true)
  			$("input[name='enable_dnsserver']").prop('checked',true);
  			$("legend:eq(0)").html("Setup<br/><span><strong>*</strong> Settings.cfg not found, using default values</span>")
			$("select[name='loglevel']").val("Normal")

		})


	// toggle states
	$("input[name=enable_plexgdm]").on("click",function(){
		$(".enable_plexgdm").toggleClass("grey")
		
		if($(".enable_plexgdm").hasClass("grey"))
		{
			$("input[name=ip_pms],input[name=port_pms]").prop("disabled",true)	
		}
		else
		{
			$("input[name=ip_pms],input[name=port_pms]").prop("disabled",false)	
		}
	})


	$("#enable_webserver_ssl").click(function(){
		if($("input[name=port_ssl]").prop("disabled")==true)
		{
			$("input[name=port_ssl]").prop("disabled", false)
			$(".usessl").removeClass("grey")
		}
		else
		{
			$("input[name=port_ssl]").prop("disabled", true)
			$(".usessl").addClass("grey")	
		}
	})

	$("input[name=enable_plexconnect_autodetect]").click(function(){
		$(".enable_plexconnect_autodetect").toggleClass("grey")
		
		if($(".enable_plexconnect_autodetect").hasClass("grey"))
		{
			$("input[name=ip_plexconnect],input[name=port_webserver]").prop("disabled",true)	
		}
		else
		{
			$("input[name=ip_plexconnect],input[name=port_webserver]").prop("disabled",false)	
		}
	})

	$("#enable_dnsserver").click(function(){
		if($(".enable_dnsserver input:eq(0)").prop("disabled")==true)
		{
			$(".enable_dnsserver input").prop("disabled", false)
			$(".enable_dnsserver").removeClass("grey")
		}
		else
		{
			$(".enable_dnsserver input").prop("disabled", true)
			$(".enable_dnsserver").addClass("grey")	
		}
	})

	$("#loglevel").on("change",function(){
		if($(this).val()=="Off"){
			$("#showlog,#log").hide()
			$("#showlog").text("SHOW")
			document.cookie="log=; expires=Thu, 18 Dec 1970 12:00:00 GMT";
		}
		else{
			$("#showlog").show()
		}
	})


$("#setupdone").click(function(){
	$("#wizardprev,#wizardnext,#setupdone").hide()
	$('#spin').spin(false);
	$("#spin1").spin('plex')
	$("#main").trigger("submit")
})

	$("#main").submit(function(e) {
		e.preventDefault();

		//$("#main,#log,.info").hide()
		$("#actions").hide()
		$("#spin").spin('plex')
		$(".restarting").show()

		config = "[PlexConnect]\n" 

		// Generate config for Settings.cfg 
		config +=  "enable_plexgdm = " + capitalize(""+$("input[name=enable_plexgdm]").is(":checked")+"")+"\n" 
		config +=  "enable_dnsserver = " + capitalize(""+$("input[name=enable_dnsserver]").is(":checked")+"") +"\n"
		config +=  "enable_plexconnect_autodetect = " + capitalize(""+$("input[name=enable_plexconnect_autodetect]").is(":checked")+"") +"\n"
		config +=  "ip_pms = " + $("input[name=ip_pms]").val()+"\n" 
		config +=  "port_pms = " + $("input[name=port_pms]").val()+"\n" 
		config +=  "ip_plexconnect = " + $("input[name=ip_plexconnect]").val()+"\n" 
		config +=  "port_webserver = " + $("input[name=port_webserver]").val()+"\n" 
		config +=  "port_dnsserver = " + $("input[name=port_dnsserver]").val()+"\n" 
		config +=  "ip_dnsmaster = " + $("input[name=ip_dnsmaster]").val()+"\n" 
		config +=  "hosttointercept = " + $("input[name=hosttointercept]").val()+"\n" 
		config +=  "certfile = " + $("input[name=certfile]").val()+"\n" 
		config +=  "enable_webserver_ssl = " + capitalize(""+$("input[name=enable_webserver_ssl]").is(":checked")+"") +"\n"
		config +=  "port_ssl = " + $("input[name=port_ssl]").val()+"\n" 
		config +=  "prevent_atv_update = " + capitalize(""+$("input[name=prevent_atv_update]").is(":checked")+"")+"\n" 
		config +=  "loglevel = " + $("select[name=loglevel]").val() +"\n"
		config +=  "logpath = .\n"

		if($("input[name=bootdaemon]").prop("checked")==true){
			if(daemon_installed==0){
				$(".restarting h4").text("SAVING AND INSTALLING...")
				$("<input type='hidden' name='boot' value='install' />").appendTo("form")
			}
		}
		if($("input[name=bootdaemon]").prop("checked")==false){
			if(daemon_installed==1){
				$(".restarting h4").text("UNINSTALLING BOOTDAEMON...")
				$("<input type='hidden' name='boot' value='uninstall' />").appendTo("form")
			}
		}		
		$("input[name=config]").val(config)

		$(this).unbind("submit")
		setTimeout('$("#main").trigger("submit")',800)
	//	alert(config)
	});
	$("#save").click(function(){
		$("#main").trigger("submit")
	})
	// start plexconnect
	$("#start").click(function(e){
		e.preventDefault()
		$(".restarting h4").text("STARTING...")
		$("<input type='hidden' name='start' value='start' />").appendTo("form")
		$("#main").trigger("submit")
	})

	// stop plexconnect
	$("#stop").click(function(e){
		e.preventDefault()
		$(".restarting h4").text("STOPPING...")
		$("<input type='hidden' name='stop' value='stop' />").appendTo("form")
		$("#main").trigger("submit")
	})
	// kill gui
	$("#kill").click(function(e){
		e.preventDefault()
		$(".restarting h4").text("STOPPING GUI...")
		$("<input type='hidden' name='kill' value='kill' />").appendTo("form")
		$("<h2 style='margin-top:80px;'>GUI stopped</h2>").appendTo(".header")
		$("#main,#log").hide()
		$("#main").trigger("submit")
	})
	$("#showlog").click(function(){
		$("#log").toggle()
		if($(this).text() =="SHOW")
		{ 
			$(this).text("HIDE") 
			document.cookie="log=true; expires=Thu, 18 Dec 2050 12:00:00 GMT";
		}
		else
		{ 
			$(this).text("SHOW") 
			document.cookie="log=; expires=Thu, 18 Dec 1970 12:00:00 GMT";
		}
	})

	$(".trailer-cert").click(function(){
		$("input[name=hosttointercept]").val("trailers.apple.com")
		$("input[name=certfile]").val("./assets/certificates/trailers.pem")
		$("#setcert").text("http://trailers.apple.com/trailers.cer")
		$("img").removeClass("certselected")
		$(".trailer-cert").addClass("certselected")
		$('.spacing').cycle('next');
	})
	$(".imovie-cert").click(function(){
		$("input[name=hosttointercept]").val("www.icloud.com")
		$("#setcert").text("http://trailers.apple.com/imovie.cer")
		$("input[name=certfile]").val("./assets/certificates/imovie.pem")
		$("img").removeClass("certselected")
		$(".imovie-cert").addClass("certselected")	
		$('.spacing').cycle('next');
	
	})
	$(".wsj-cert").click(function(){
		$("input[name=hosttointercept]").val("secure.marketwatch.com")
		$("input[name=certfile]").val("./assets/certificates/wsj.pem")
		$("#setcert").text("http://trailers.apple.com/wsj.cer")
		$("img").removeClass("certselected")
		$(".wsj-cert").addClass("certselected")
		$('.spacing').cycle('next');
	})
	$("#bootyes").click(function(){
		$("<input type='hidden' name='boot' value='install' />").appendTo("form")
		$('.spacing').cycle('next');
	})
	$("#bootno").click(function(){
		$('.spacing').cycle('next');
		$("input[name=boot]").remove();

	})

	$('.tooltip').tooltipster({
		maxWidth: 400,
		position: 'bottom',
		contentAsHTML: true,
		animation: 'grow',
		
	});
	
$('.custom-tooltip').tooltipster({
		fixedWidth: 700,
		position: 'bottom',
		contentAsHTML: true,
		animation: 'grow',
		theme:'tooltipster-custom'
	})
	
})

var newlog =""

function refreshlog(){
	var newlog =""

	$.get('PlexConnect.log',{ "_": $.now() })
			.done(function(data){

				var lines = data.split('\n');
				 lines.reverse()
					for(i=1; i<lines.length; i++)
				    {
						// parse log from settings.cfg
				       	 	//alert(lines[i])
				       	 	newlog = newlog+lines[i] + "<br/>"
			    	}
			    	$("#log").text("")
			    	$(newlog).appendTo("#log")
			    	setTimeout("refreshlog()",5000)
			})
			
}

function getCookie(cname)
{
var name = cname + "=";
var ca = document.cookie.split(';');
for(var i=0; i<ca.length; i++) 
  {
  var c = ca[i].trim();
  if (c.indexOf(name)==0) return c.substring(name.length,c.length);
  }
return "";
}

function capitalize(s)
{
    return s[0].toUpperCase() + s.slice(1);
}
function onAfter(curr, next, opts) {
    var index = opts.currSlide;
    $('#wizardprev')[index == 0 ? 'hide' : 'show']();
    $('#wizardnext')[index == opts.slideCount - 1 ? 'hide' : 'show']();
}

/*
 * jQuery Easing v1.3 - http://gsgd.co.uk/sandbox/jquery/easing/
 *
 * Uses the built in easing capabilities added In jQuery 1.1
 * to offer multiple easing options
 *
 * TERMS OF USE - jQuery Easing
 * 
 * Open source under the BSD License. 
 * 
 * Copyright Â© 2008 George McGinley Smith
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without modification, 
 * are permitted provided that the following conditions are met:
 * 
 * Redistributions of source code must retain the above copyright notice, this list of 
 * conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list 
 * of conditions and the following disclaimer in the documentation and/or other materials 
 * provided with the distribution.
 * 
 * Neither the name of the author nor the names of contributors may be used to endorse 
 * or promote products derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 *  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 *  GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED 
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 *  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
 * OF THE POSSIBILITY OF SUCH DAMAGE. 
 *
*/

// t: current time, b: begInnIng value, c: change In value, d: duration
jQuery.easing['jswing'] = jQuery.easing['swing'];

jQuery.extend( jQuery.easing,
{
	def: 'easeOutQuad',
	swing: function (x, t, b, c, d) {
		//alert(jQuery.easing.default);
		return jQuery.easing[jQuery.easing.def](x, t, b, c, d);
	},
	easeInQuad: function (x, t, b, c, d) {
		return c*(t/=d)*t + b;
	},
	easeOutQuad: function (x, t, b, c, d) {
		return -c *(t/=d)*(t-2) + b;
	},
	easeInOutQuad: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t + b;
		return -c/2 * ((--t)*(t-2) - 1) + b;
	},
	easeInCubic: function (x, t, b, c, d) {
		return c*(t/=d)*t*t + b;
	},
	easeOutCubic: function (x, t, b, c, d) {
		return c*((t=t/d-1)*t*t + 1) + b;
	},
	easeInOutCubic: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t*t + b;
		return c/2*((t-=2)*t*t + 2) + b;
	},
	easeInQuart: function (x, t, b, c, d) {
		return c*(t/=d)*t*t*t + b;
	},
	easeOutQuart: function (x, t, b, c, d) {
		return -c * ((t=t/d-1)*t*t*t - 1) + b;
	},
	easeInOutQuart: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t*t*t + b;
		return -c/2 * ((t-=2)*t*t*t - 2) + b;
	},
	easeInQuint: function (x, t, b, c, d) {
		return c*(t/=d)*t*t*t*t + b;
	},
	easeOutQuint: function (x, t, b, c, d) {
		return c*((t=t/d-1)*t*t*t*t + 1) + b;
	},
	easeInOutQuint: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t*t*t*t + b;
		return c/2*((t-=2)*t*t*t*t + 2) + b;
	},
	easeInSine: function (x, t, b, c, d) {
		return -c * Math.cos(t/d * (Math.PI/2)) + c + b;
	},
	easeOutSine: function (x, t, b, c, d) {
		return c * Math.sin(t/d * (Math.PI/2)) + b;
	},
	easeInOutSine: function (x, t, b, c, d) {
		return -c/2 * (Math.cos(Math.PI*t/d) - 1) + b;
	},
	easeInExpo: function (x, t, b, c, d) {
		return (t==0) ? b : c * Math.pow(2, 10 * (t/d - 1)) + b;
	},
	easeOutExpo: function (x, t, b, c, d) {
		return (t==d) ? b+c : c * (-Math.pow(2, -10 * t/d) + 1) + b;
	},
	easeInOutExpo: function (x, t, b, c, d) {
		if (t==0) return b;
		if (t==d) return b+c;
		if ((t/=d/2) < 1) return c/2 * Math.pow(2, 10 * (t - 1)) + b;
		return c/2 * (-Math.pow(2, -10 * --t) + 2) + b;
	},
	easeInCirc: function (x, t, b, c, d) {
		return -c * (Math.sqrt(1 - (t/=d)*t) - 1) + b;
	},
	easeOutCirc: function (x, t, b, c, d) {
		return c * Math.sqrt(1 - (t=t/d-1)*t) + b;
	},
	easeInOutCirc: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return -c/2 * (Math.sqrt(1 - t*t) - 1) + b;
		return c/2 * (Math.sqrt(1 - (t-=2)*t) + 1) + b;
	},
	easeInElastic: function (x, t, b, c, d) {
		var s=1.70158;var p=0;var a=c;
		if (t==0) return b;  if ((t/=d)==1) return b+c;  if (!p) p=d*.3;
		if (a < Math.abs(c)) { a=c; var s=p/4; }
		else var s = p/(2*Math.PI) * Math.asin (c/a);
		return -(a*Math.pow(2,10*(t-=1)) * Math.sin( (t*d-s)*(2*Math.PI)/p )) + b;
	},
	easeOutElastic: function (x, t, b, c, d) {
		var s=1.70158;var p=0;var a=c;
		if (t==0) return b;  if ((t/=d)==1) return b+c;  if (!p) p=d*.3;
		if (a < Math.abs(c)) { a=c; var s=p/4; }
		else var s = p/(2*Math.PI) * Math.asin (c/a);
		return a*Math.pow(2,-10*t) * Math.sin( (t*d-s)*(2*Math.PI)/p ) + c + b;
	},
	easeInOutElastic: function (x, t, b, c, d) {
		var s=1.70158;var p=0;var a=c;
		if (t==0) return b;  if ((t/=d/2)==2) return b+c;  if (!p) p=d*(.3*1.5);
		if (a < Math.abs(c)) { a=c; var s=p/4; }
		else var s = p/(2*Math.PI) * Math.asin (c/a);
		if (t < 1) return -.5*(a*Math.pow(2,10*(t-=1)) * Math.sin( (t*d-s)*(2*Math.PI)/p )) + b;
		return a*Math.pow(2,-10*(t-=1)) * Math.sin( (t*d-s)*(2*Math.PI)/p )*.5 + c + b;
	},
	easeInBack: function (x, t, b, c, d, s) {
		if (s == undefined) s = 1.70158;
		return c*(t/=d)*t*((s+1)*t - s) + b;
	},
	easeOutBack: function (x, t, b, c, d, s) {
		if (s == undefined) s = 1.70158;
		return c*((t=t/d-1)*t*((s+1)*t + s) + 1) + b;
	},
	easeInOutBack: function (x, t, b, c, d, s) {
		if (s == undefined) s = 1.70158; 
		if ((t/=d/2) < 1) return c/2*(t*t*(((s*=(1.525))+1)*t - s)) + b;
		return c/2*((t-=2)*t*(((s*=(1.525))+1)*t + s) + 2) + b;
	},
	easeInBounce: function (x, t, b, c, d) {
		return c - jQuery.easing.easeOutBounce (x, d-t, 0, c, d) + b;
	},
	easeOutBounce: function (x, t, b, c, d) {
		if ((t/=d) < (1/2.75)) {
			return c*(7.5625*t*t) + b;
		} else if (t < (2/2.75)) {
			return c*(7.5625*(t-=(1.5/2.75))*t + .75) + b;
		} else if (t < (2.5/2.75)) {
			return c*(7.5625*(t-=(2.25/2.75))*t + .9375) + b;
		} else {
			return c*(7.5625*(t-=(2.625/2.75))*t + .984375) + b;
		}
	},
	easeInOutBounce: function (x, t, b, c, d) {
		if (t < d/2) return jQuery.easing.easeInBounce (x, t*2, 0, c, d) * .5 + b;
		return jQuery.easing.easeOutBounce (x, t*2-d, 0, c, d) * .5 + c*.5 + b;
	}
});

/*
 *
 * TERMS OF USE - EASING EQUATIONS
 * 
 * Open source under the BSD License. 
 * 
 * Copyright Â© 2001 Robert Penner
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without modification, 
 * are permitted provided that the following conditions are met:
 * 
 * Redistributions of source code must retain the above copyright notice, this list of 
 * conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list 
 * of conditions and the following disclaimer in the documentation and/or other materials 
 * provided with the distribution.
 * 
 * Neither the name of the author nor the names of contributors may be used to endorse 
 * or promote products derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 *  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
 *  GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED 
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 *  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
 * OF THE POSSIBILITY OF SUCH DAMAGE. 
 *
 */

/*!
 * jQuery Cycle Plugin (with Transition Definitions)
 * Examples and documentation at: http://jquery.malsup.com/cycle/
 * Copyright (c) 2007-2013 M. Alsup
 * Version: 3.0.3 (11-JUL-2013)
 * Dual licensed under the MIT and GPL licenses.
 * http://jquery.malsup.com/license.html
 * Requires: jQuery v1.7.1 or later
 */
;(function($, undefined) {
"use strict";

var ver = '3.0.3';

function debug(s) {
	if ($.fn.cycle.debug)
		log(s);
}		
function log() {
	/*global console */
	if (window.console && console.log)
		console.log('[cycle] ' + Array.prototype.join.call(arguments,' '));
}
$.expr[':'].paused = function(el) {
	return el.cyclePause;
};


// the options arg can be...
//   a number  - indicates an immediate transition should occur to the given slide index
//   a string  - 'pause', 'resume', 'toggle', 'next', 'prev', 'stop', 'destroy' or the name of a transition effect (ie, 'fade', 'zoom', etc)
//   an object - properties to control the slideshow
//
// the arg2 arg can be...
//   the name of an fx (only used in conjunction with a numeric value for 'options')
//   the value true (only used in first arg == 'resume') and indicates
//	 that the resume should occur immediately (not wait for next timeout)

$.fn.cycle = function(options, arg2) {
	var o = { s: this.selector, c: this.context };

	// in 1.3+ we can fix mistakes with the ready state
	if (this.length === 0 && options != 'stop') {
		if (!$.isReady && o.s) {
			log('DOM not ready, queuing slideshow');
			$(function() {
				$(o.s,o.c).cycle(options,arg2);
			});
			return this;
		}
		// is your DOM ready?  http://docs.jquery.com/Tutorials:Introducing_$(document).ready()
		log('terminating; zero elements found by selector' + ($.isReady ? '' : ' (DOM not ready)'));
		return this;
	}

	// iterate the matched nodeset
	return this.each(function() {
		var opts = handleArguments(this, options, arg2);
		if (opts === false)
			return;

		opts.updateActivePagerLink = opts.updateActivePagerLink || $.fn.cycle.updateActivePagerLink;
		
		// stop existing slideshow for this container (if there is one)
		if (this.cycleTimeout)
			clearTimeout(this.cycleTimeout);
		this.cycleTimeout = this.cyclePause = 0;
		this.cycleStop = 0; // issue #108

		var $cont = $(this);
		var $slides = opts.slideExpr ? $(opts.slideExpr, this) : $cont.children();
		var els = $slides.get();

		if (els.length < 2) {
			log('terminating; too few slides: ' + els.length);
			return;
		}

		var opts2 = buildOptions($cont, $slides, els, opts, o);
		if (opts2 === false)
			return;

		var startTime = opts2.continuous ? 10 : getTimeout(els[opts2.currSlide], els[opts2.nextSlide], opts2, !opts2.backwards);

		// if it's an auto slideshow, kick it off
		if (startTime) {
			startTime += (opts2.delay || 0);
			if (startTime < 10)
				startTime = 10;
			debug('first timeout: ' + startTime);
			this.cycleTimeout = setTimeout(function(){go(els,opts2,0,!opts.backwards);}, startTime);
		}
	});
};

function triggerPause(cont, byHover, onPager) {
	var opts = $(cont).data('cycle.opts');
	if (!opts)
		return;
	var paused = !!cont.cyclePause;
	if (paused && opts.paused)
		opts.paused(cont, opts, byHover, onPager);
	else if (!paused && opts.resumed)
		opts.resumed(cont, opts, byHover, onPager);
}

// process the args that were passed to the plugin fn
function handleArguments(cont, options, arg2) {
	if (cont.cycleStop === undefined)
		cont.cycleStop = 0;
	if (options === undefined || options === null)
		options = {};
	if (options.constructor == String) {
		switch(options) {
		case 'destroy':
		case 'stop':
			var opts = $(cont).data('cycle.opts');
			if (!opts)
				return false;
			cont.cycleStop++; // callbacks look for change
			if (cont.cycleTimeout)
				clearTimeout(cont.cycleTimeout);
			cont.cycleTimeout = 0;
			if (opts.elements)
				$(opts.elements).stop();
			$(cont).removeData('cycle.opts');
			if (options == 'destroy')
				destroy(cont, opts);
			return false;
		case 'toggle':
			cont.cyclePause = (cont.cyclePause === 1) ? 0 : 1;
			checkInstantResume(cont.cyclePause, arg2, cont);
			triggerPause(cont);
			return false;
		case 'pause':
			cont.cyclePause = 1;
			triggerPause(cont);
			return false;
		case 'resume':
			cont.cyclePause = 0;
			checkInstantResume(false, arg2, cont);
			triggerPause(cont);
			return false;
		case 'prev':
		case 'next':
			opts = $(cont).data('cycle.opts');
			if (!opts) {
				log('options not found, "prev/next" ignored');
				return false;
			}
			if (typeof arg2 == 'string') 
				opts.oneTimeFx = arg2;
			$.fn.cycle[options](opts);
			return false;
		default:
			options = { fx: options };
		}
		return options;
	}
	else if (options.constructor == Number) {
		// go to the requested slide
		var num = options;
		options = $(cont).data('cycle.opts');
		if (!options) {
			log('options not found, can not advance slide');
			return false;
		}
		if (num < 0 || num >= options.elements.length) {
			log('invalid slide index: ' + num);
			return false;
		}
		options.nextSlide = num;
		if (cont.cycleTimeout) {
			clearTimeout(cont.cycleTimeout);
			cont.cycleTimeout = 0;
		}
		if (typeof arg2 == 'string')
			options.oneTimeFx = arg2;
		go(options.elements, options, 1, num >= options.currSlide);
		return false;
	}
	return options;
	
	function checkInstantResume(isPaused, arg2, cont) {
		if (!isPaused && arg2 === true) { // resume now!
			var options = $(cont).data('cycle.opts');
			if (!options) {
				log('options not found, can not resume');
				return false;
			}
			if (cont.cycleTimeout) {
				clearTimeout(cont.cycleTimeout);
				cont.cycleTimeout = 0;
			}
			go(options.elements, options, 1, !options.backwards);
		}
	}
}

function removeFilter(el, opts) {
	if (!$.support.opacity && opts.cleartype && el.style.filter) {
		try { el.style.removeAttribute('filter'); }
		catch(smother) {} // handle old opera versions
	}
}

// unbind event handlers
function destroy(cont, opts) {
	if (opts.next)
		$(opts.next).unbind(opts.prevNextEvent);
	if (opts.prev)
		$(opts.prev).unbind(opts.prevNextEvent);
	
	if (opts.pager || opts.pagerAnchorBuilder)
		$.each(opts.pagerAnchors || [], function() {
			this.unbind().remove();
		});
	opts.pagerAnchors = null;
	$(cont).unbind('mouseenter.cycle mouseleave.cycle');
	if (opts.destroy) // callback
		opts.destroy(opts);
}

// one-time initialization
function buildOptions($cont, $slides, els, options, o) {
	var startingSlideSpecified;
	// support metadata plugin (v1.0 and v2.0)
	var opts = $.extend({}, $.fn.cycle.defaults, options || {}, $.metadata ? $cont.metadata() : $.meta ? $cont.data() : {});
	var meta = $.isFunction($cont.data) ? $cont.data(opts.metaAttr) : null;
	if (meta)
		opts = $.extend(opts, meta);
	if (opts.autostop)
		opts.countdown = opts.autostopCount || els.length;

	var cont = $cont[0];
	$cont.data('cycle.opts', opts);
	opts.$cont = $cont;
	opts.stopCount = cont.cycleStop;
	opts.elements = els;
	opts.before = opts.before ? [opts.before] : [];
	opts.after = opts.after ? [opts.after] : [];

	// push some after callbacks
	if (!$.support.opacity && opts.cleartype)
		opts.after.push(function() { removeFilter(this, opts); });
	if (opts.continuous)
		opts.after.push(function() { go(els,opts,0,!opts.backwards); });

	saveOriginalOpts(opts);

	// clearType corrections
	if (!$.support.opacity && opts.cleartype && !opts.cleartypeNoBg)
		clearTypeFix($slides);

	// container requires non-static position so that slides can be position within
	if ($cont.css('position') == 'static')
		$cont.css('position', 'relative');
	if (opts.width)
		$cont.width(opts.width);
	if (opts.height && opts.height != 'auto')
		$cont.height(opts.height);

	if (opts.startingSlide !== undefined) {
		opts.startingSlide = parseInt(opts.startingSlide,10);
		if (opts.startingSlide >= els.length || opts.startSlide < 0)
			opts.startingSlide = 0; // catch bogus input
		else 
			startingSlideSpecified = true;
	}
	else if (opts.backwards)
		opts.startingSlide = els.length - 1;
	else
		opts.startingSlide = 0;

	// if random, mix up the slide array
	if (opts.random) {
		opts.randomMap = [];
		for (var i = 0; i < els.length; i++)
			opts.randomMap.push(i);
		opts.randomMap.sort(function(a,b) {return Math.random() - 0.5;});
		if (startingSlideSpecified) {
			// try to find the specified starting slide and if found set start slide index in the map accordingly
			for ( var cnt = 0; cnt < els.length; cnt++ ) {
				if ( opts.startingSlide == opts.randomMap[cnt] ) {
					opts.randomIndex = cnt;
				}
			}
		}
		else {
			opts.randomIndex = 1;
			opts.startingSlide = opts.randomMap[1];
		}
	}
	else if (opts.startingSlide >= els.length)
		opts.startingSlide = 0; // catch bogus input
	opts.currSlide = opts.startingSlide || 0;
	var first = opts.startingSlide;

	// set position and zIndex on all the slides
	$slides.css({position: 'absolute', top:0, left:0}).hide().each(function(i) {
		var z;
		if (opts.backwards)
			z = first ? i <= first ? els.length + (i-first) : first-i : els.length-i;
		else
			z = first ? i >= first ? els.length - (i-first) : first-i : els.length-i;
		$(this).css('z-index', z);
	});

	// make sure first slide is visible
	$(els[first]).css('opacity',1).show(); // opacity bit needed to handle restart use case
	removeFilter(els[first], opts);

	// stretch slides
	if (opts.fit) {
		if (!opts.aspect) {
	        if (opts.width)
	            $slides.width(opts.width);
	        if (opts.height && opts.height != 'auto')
	            $slides.height(opts.height);
		} else {
			$slides.each(function(){
				var $slide = $(this);
				var ratio = (opts.aspect === true) ? $slide.width()/$slide.height() : opts.aspect;
				if( opts.width && $slide.width() != opts.width ) {
					$slide.width( opts.width );
					$slide.height( opts.width / ratio );
				}

				if( opts.height && $slide.height() < opts.height ) {
					$slide.height( opts.height );
					$slide.width( opts.height * ratio );
				}
			});
		}
	}

	if (opts.center && ((!opts.fit) || opts.aspect)) {
		$slides.each(function(){
			var $slide = $(this);
			$slide.css({
				"margin-left": opts.width ?
					((opts.width - $slide.width()) / 2) + "px" :
					0,
				"margin-top": opts.height ?
					((opts.height - $slide.height()) / 2) + "px" :
					0
			});
		});
	}

	if (opts.center && !opts.fit && !opts.slideResize) {
		$slides.each(function(){
			var $slide = $(this);
			$slide.css({
				"margin-left": opts.width ? ((opts.width - $slide.width()) / 2) + "px" : 0,
				"margin-top": opts.height ? ((opts.height - $slide.height()) / 2) + "px" : 0
			});
		});
	}
		
	// stretch container
	var reshape = (opts.containerResize || opts.containerResizeHeight) && $cont.innerHeight() < 1;
	if (reshape) { // do this only if container has no size http://tinyurl.com/da2oa9
		var maxw = 0, maxh = 0;
		for(var j=0; j < els.length; j++) {
			var $e = $(els[j]), e = $e[0], w = $e.outerWidth(), h = $e.outerHeight();
			if (!w) w = e.offsetWidth || e.width || $e.attr('width');
			if (!h) h = e.offsetHeight || e.height || $e.attr('height');
			maxw = w > maxw ? w : maxw;
			maxh = h > maxh ? h : maxh;
		}
		if (opts.containerResize && maxw > 0 && maxh > 0)
			$cont.css({width:maxw+'px',height:maxh+'px'});
		if (opts.containerResizeHeight && maxh > 0)
			$cont.css({height:maxh+'px'});
	}

	var pauseFlag = false;  // https://github.com/malsup/cycle/issues/44
	if (opts.pause)
		$cont.bind('mouseenter.cycle', function(){
			pauseFlag = true;
			this.cyclePause++;
			triggerPause(cont, true);
		}).bind('mouseleave.cycle', function(){
				if (pauseFlag)
					this.cyclePause--;
				triggerPause(cont, true);
		});

	if (supportMultiTransitions(opts) === false)
		return false;

	// apparently a lot of people use image slideshows without height/width attributes on the images.
	// Cycle 2.50+ requires the sizing info for every slide; this block tries to deal with that.
	var requeue = false;
	options.requeueAttempts = options.requeueAttempts || 0;
	$slides.each(function() {
		// try to get height/width of each slide
		var $el = $(this);
		this.cycleH = (opts.fit && opts.height) ? opts.height : ($el.height() || this.offsetHeight || this.height || $el.attr('height') || 0);
		this.cycleW = (opts.fit && opts.width) ? opts.width : ($el.width() || this.offsetWidth || this.width || $el.attr('width') || 0);

		if ( $el.is('img') ) {
			var loading = (this.cycleH === 0 && this.cycleW === 0 && !this.complete);
			// don't requeue for images that are still loading but have a valid size
			if (loading) {
				if (o.s && opts.requeueOnImageNotLoaded && ++options.requeueAttempts < 100) { // track retry count so we don't loop forever
					log(options.requeueAttempts,' - img slide not loaded, requeuing slideshow: ', this.src, this.cycleW, this.cycleH);
					setTimeout(function() {$(o.s,o.c).cycle(options);}, opts.requeueTimeout);
					requeue = true;
					return false; // break each loop
				}
				else {
					log('could not determine size of image: '+this.src, this.cycleW, this.cycleH);
				}
			}
		}
		return true;
	});

	if (requeue)
		return false;

	opts.cssBefore = opts.cssBefore || {};
	opts.cssAfter = opts.cssAfter || {};
	opts.cssFirst = opts.cssFirst || {};
	opts.animIn = opts.animIn || {};
	opts.animOut = opts.animOut || {};

	$slides.not(':eq('+first+')').css(opts.cssBefore);
	$($slides[first]).css(opts.cssFirst);

	if (opts.timeout) {
		opts.timeout = parseInt(opts.timeout,10);
		// ensure that timeout and speed settings are sane
		if (opts.speed.constructor == String)
			opts.speed = $.fx.speeds[opts.speed] || parseInt(opts.speed,10);
		if (!opts.sync)
			opts.speed = opts.speed / 2;
		
		var buffer = opts.fx == 'none' ? 0 : opts.fx == 'shuffle' ? 500 : 250;
		while((opts.timeout - opts.speed) < buffer) // sanitize timeout
			opts.timeout += opts.speed;
	}
	if (opts.easing)
		opts.easeIn = opts.easeOut = opts.easing;
	if (!opts.speedIn)
		opts.speedIn = opts.speed;
	if (!opts.speedOut)
		opts.speedOut = opts.speed;

	opts.slideCount = els.length;
	opts.currSlide = opts.lastSlide = first;
	if (opts.random) {
		if (++opts.randomIndex == els.length)
			opts.randomIndex = 0;
		opts.nextSlide = opts.randomMap[opts.randomIndex];
	}
	else if (opts.backwards)
		opts.nextSlide = opts.startingSlide === 0 ? (els.length-1) : opts.startingSlide-1;
	else
		opts.nextSlide = opts.startingSlide >= (els.length-1) ? 0 : opts.startingSlide+1;

	// run transition init fn
	if (!opts.multiFx) {
		var init = $.fn.cycle.transitions[opts.fx];
		if ($.isFunction(init))
			init($cont, $slides, opts);
		else if (opts.fx != 'custom' && !opts.multiFx) {
			log('unknown transition: ' + opts.fx,'; slideshow terminating');
			return false;
		}
	}

	// fire artificial events
	var e0 = $slides[first];
	if (!opts.skipInitializationCallbacks) {
		if (opts.before.length)
			opts.before[0].apply(e0, [e0, e0, opts, true]);
		if (opts.after.length)
			opts.after[0].apply(e0, [e0, e0, opts, true]);
	}
	if (opts.next)
		$(opts.next).bind(opts.prevNextEvent,function(){return advance(opts,1);});
	if (opts.prev)
		$(opts.prev).bind(opts.prevNextEvent,function(){return advance(opts,0);});
	if (opts.pager || opts.pagerAnchorBuilder)
		buildPager(els,opts);

	exposeAddSlide(opts, els);

	return opts;
}

// save off original opts so we can restore after clearing state
function saveOriginalOpts(opts) {
	opts.original = { before: [], after: [] };
	opts.original.cssBefore = $.extend({}, opts.cssBefore);
	opts.original.cssAfter  = $.extend({}, opts.cssAfter);
	opts.original.animIn	= $.extend({}, opts.animIn);
	opts.original.animOut   = $.extend({}, opts.animOut);
	$.each(opts.before, function() { opts.original.before.push(this); });
	$.each(opts.after,  function() { opts.original.after.push(this); });
}

function supportMultiTransitions(opts) {
	var i, tx, txs = $.fn.cycle.transitions;
	// look for multiple effects
	if (opts.fx.indexOf(',') > 0) {
		opts.multiFx = true;
		opts.fxs = opts.fx.replace(/\s*/g,'').split(',');
		// discard any bogus effect names
		for (i=0; i < opts.fxs.length; i++) {
			var fx = opts.fxs[i];
			tx = txs[fx];
			if (!tx || !txs.hasOwnProperty(fx) || !$.isFunction(tx)) {
				log('discarding unknown transition: ',fx);
				opts.fxs.splice(i,1);
				i--;
			}
		}
		// if we have an empty list then we threw everything away!
		if (!opts.fxs.length) {
			log('No valid transitions named; slideshow terminating.');
			return false;
		}
	}
	else if (opts.fx == 'all') {  // auto-gen the list of transitions
		opts.multiFx = true;
		opts.fxs = [];
		for (var p in txs) {
			if (txs.hasOwnProperty(p)) {
				tx = txs[p];
				if (txs.hasOwnProperty(p) && $.isFunction(tx))
					opts.fxs.push(p);
			}
		}
	}
	if (opts.multiFx && opts.randomizeEffects) {
		// munge the fxs array to make effect selection random
		var r1 = Math.floor(Math.random() * 20) + 30;
		for (i = 0; i < r1; i++) {
			var r2 = Math.floor(Math.random() * opts.fxs.length);
			opts.fxs.push(opts.fxs.splice(r2,1)[0]);
		}
		debug('randomized fx sequence: ',opts.fxs);
	}
	return true;
}

// provide a mechanism for adding slides after the slideshow has started
function exposeAddSlide(opts, els) {
	opts.addSlide = function(newSlide, prepend) {
		var $s = $(newSlide), s = $s[0];
		if (!opts.autostopCount)
			opts.countdown++;
		els[prepend?'unshift':'push'](s);
		if (opts.els)
			opts.els[prepend?'unshift':'push'](s); // shuffle needs this
		opts.slideCount = els.length;

		// add the slide to the random map and resort
		if (opts.random) {
			opts.randomMap.push(opts.slideCount-1);
			opts.randomMap.sort(function(a,b) {return Math.random() - 0.5;});
		}

		$s.css('position','absolute');
		$s[prepend?'prependTo':'appendTo'](opts.$cont);

		if (prepend) {
			opts.currSlide++;
			opts.nextSlide++;
		}

		if (!$.support.opacity && opts.cleartype && !opts.cleartypeNoBg)
			clearTypeFix($s);

		if (opts.fit && opts.width)
			$s.width(opts.width);
		if (opts.fit && opts.height && opts.height != 'auto')
			$s.height(opts.height);
		s.cycleH = (opts.fit && opts.height) ? opts.height : $s.height();
		s.cycleW = (opts.fit && opts.width) ? opts.width : $s.width();

		$s.css(opts.cssBefore);

		if (opts.pager || opts.pagerAnchorBuilder)
			$.fn.cycle.createPagerAnchor(els.length-1, s, $(opts.pager), els, opts);

		if ($.isFunction(opts.onAddSlide))
			opts.onAddSlide($s);
		else
			$s.hide(); // default behavior
	};
}

// reset internal state; we do this on every pass in order to support multiple effects
$.fn.cycle.resetState = function(opts, fx) {
	fx = fx || opts.fx;
	opts.before = []; opts.after = [];
	opts.cssBefore = $.extend({}, opts.original.cssBefore);
	opts.cssAfter  = $.extend({}, opts.original.cssAfter);
	opts.animIn	= $.extend({}, opts.original.animIn);
	opts.animOut   = $.extend({}, opts.original.animOut);
	opts.fxFn = null;
	$.each(opts.original.before, function() { opts.before.push(this); });
	$.each(opts.original.after,  function() { opts.after.push(this); });

	// re-init
	var init = $.fn.cycle.transitions[fx];
	if ($.isFunction(init))
		init(opts.$cont, $(opts.elements), opts);
};

// this is the main engine fn, it handles the timeouts, callbacks and slide index mgmt
function go(els, opts, manual, fwd) {
	var p = opts.$cont[0], curr = els[opts.currSlide], next = els[opts.nextSlide];

	// opts.busy is true if we're in the middle of an animation
	if (manual && opts.busy && opts.manualTrump) {
		// let manual transitions requests trump active ones
		debug('manualTrump in go(), stopping active transition');
		$(els).stop(true,true);
		opts.busy = 0;
		clearTimeout(p.cycleTimeout);
	}

	// don't begin another timeout-based transition if there is one active
	if (opts.busy) {
		debug('transition active, ignoring new tx request');
		return;
	}


	// stop cycling if we have an outstanding stop request
	if (p.cycleStop != opts.stopCount || p.cycleTimeout === 0 && !manual)
		return;

	// check to see if we should stop cycling based on autostop options
	if (!manual && !p.cyclePause && !opts.bounce &&
		((opts.autostop && (--opts.countdown <= 0)) ||
		(opts.nowrap && !opts.random && opts.nextSlide < opts.currSlide))) {
		if (opts.end)
			opts.end(opts);
		return;
	}

	// if slideshow is paused, only transition on a manual trigger
	var changed = false;
	if ((manual || !p.cyclePause) && (opts.nextSlide != opts.currSlide)) {
		changed = true;
		var fx = opts.fx;
		// keep trying to get the slide size if we don't have it yet
		curr.cycleH = curr.cycleH || $(curr).height();
		curr.cycleW = curr.cycleW || $(curr).width();
		next.cycleH = next.cycleH || $(next).height();
		next.cycleW = next.cycleW || $(next).width();

		// support multiple transition types
		if (opts.multiFx) {
			if (fwd && (opts.lastFx === undefined || ++opts.lastFx >= opts.fxs.length))
				opts.lastFx = 0;
			else if (!fwd && (opts.lastFx === undefined || --opts.lastFx < 0))
				opts.lastFx = opts.fxs.length - 1;
			fx = opts.fxs[opts.lastFx];
		}

		// one-time fx overrides apply to:  $('div').cycle(3,'zoom');
		if (opts.oneTimeFx) {
			fx = opts.oneTimeFx;
			opts.oneTimeFx = null;
		}

		$.fn.cycle.resetState(opts, fx);

		// run the before callbacks
		if (opts.before.length)
			$.each(opts.before, function(i,o) {
				if (p.cycleStop != opts.stopCount) return;
				o.apply(next, [curr, next, opts, fwd]);
			});

		// stage the after callacks
		var after = function() {
			opts.busy = 0;
			$.each(opts.after, function(i,o) {
				if (p.cycleStop != opts.stopCount) return;
				o.apply(next, [curr, next, opts, fwd]);
			});
			if (!p.cycleStop) {
				// queue next transition
				queueNext();
			}
		};

		debug('tx firing('+fx+'); currSlide: ' + opts.currSlide + '; nextSlide: ' + opts.nextSlide);
		
		// get ready to perform the transition
		opts.busy = 1;
		if (opts.fxFn) // fx function provided?
			opts.fxFn(curr, next, opts, after, fwd, manual && opts.fastOnEvent);
		else if ($.isFunction($.fn.cycle[opts.fx])) // fx plugin ?
			$.fn.cycle[opts.fx](curr, next, opts, after, fwd, manual && opts.fastOnEvent);
		else
			$.fn.cycle.custom(curr, next, opts, after, fwd, manual && opts.fastOnEvent);
	}
	else {
		queueNext();
	}

	if (changed || opts.nextSlide == opts.currSlide) {
		// calculate the next slide
		var roll;
		opts.lastSlide = opts.currSlide;
		if (opts.random) {
			opts.currSlide = opts.nextSlide;
			if (++opts.randomIndex == els.length) {
				opts.randomIndex = 0;
				opts.randomMap.sort(function(a,b) {return Math.random() - 0.5;});
			}
			opts.nextSlide = opts.randomMap[opts.randomIndex];
			if (opts.nextSlide == opts.currSlide)
				opts.nextSlide = (opts.currSlide == opts.slideCount - 1) ? 0 : opts.currSlide + 1;
		}
		else if (opts.backwards) {
			roll = (opts.nextSlide - 1) < 0;
			if (roll && opts.bounce) {
				opts.backwards = !opts.backwards;
				opts.nextSlide = 1;
				opts.currSlide = 0;
			}
			else {
				opts.nextSlide = roll ? (els.length-1) : opts.nextSlide-1;
				opts.currSlide = roll ? 0 : opts.nextSlide+1;
			}
		}
		else { // sequence
			roll = (opts.nextSlide + 1) == els.length;
			if (roll && opts.bounce) {
				opts.backwards = !opts.backwards;
				opts.nextSlide = els.length-2;
				opts.currSlide = els.length-1;
			}
			else {
				opts.nextSlide = roll ? 0 : opts.nextSlide+1;
				opts.currSlide = roll ? els.length-1 : opts.nextSlide-1;
			}
		}
	}
	if (changed && opts.pager)
		opts.updateActivePagerLink(opts.pager, opts.currSlide, opts.activePagerClass);
	
	function queueNext() {
		// stage the next transition
		var ms = 0, timeout = opts.timeout;
		if (opts.timeout && !opts.continuous) {
			ms = getTimeout(els[opts.currSlide], els[opts.nextSlide], opts, fwd);
         if (opts.fx == 'shuffle')
            ms -= opts.speedOut;
      }
		else if (opts.continuous && p.cyclePause) // continuous shows work off an after callback, not this timer logic
			ms = 10;
		if (ms > 0)
			p.cycleTimeout = setTimeout(function(){ go(els, opts, 0, !opts.backwards); }, ms);
	}
}

// invoked after transition
$.fn.cycle.updateActivePagerLink = function(pager, currSlide, clsName) {
   $(pager).each(function() {
       $(this).children().removeClass(clsName).eq(currSlide).addClass(clsName);
   });
};

// calculate timeout value for current transition
function getTimeout(curr, next, opts, fwd) {
	if (opts.timeoutFn) {
		// call user provided calc fn
		var t = opts.timeoutFn.call(curr,curr,next,opts,fwd);
		while (opts.fx != 'none' && (t - opts.speed) < 250) // sanitize timeout
			t += opts.speed;
		debug('calculated timeout: ' + t + '; speed: ' + opts.speed);
		if (t !== false)
			return t;
	}
	return opts.timeout;
}

// expose next/prev function, caller must pass in state
$.fn.cycle.next = function(opts) { advance(opts,1); };
$.fn.cycle.prev = function(opts) { advance(opts,0);};

// advance slide forward or back
function advance(opts, moveForward) {
	var val = moveForward ? 1 : -1;
	var els = opts.elements;
	var p = opts.$cont[0], timeout = p.cycleTimeout;
	if (timeout) {
		clearTimeout(timeout);
		p.cycleTimeout = 0;
	}
	if (opts.random && val < 0) {
		// move back to the previously display slide
		opts.randomIndex--;
		if (--opts.randomIndex == -2)
			opts.randomIndex = els.length-2;
		else if (opts.randomIndex == -1)
			opts.randomIndex = els.length-1;
		opts.nextSlide = opts.randomMap[opts.randomIndex];
	}
	else if (opts.random) {
		opts.nextSlide = opts.randomMap[opts.randomIndex];
	}
	else {
		opts.nextSlide = opts.currSlide + val;
		if (opts.nextSlide < 0) {
			if (opts.nowrap) return false;
			opts.nextSlide = els.length - 1;
		}
		else if (opts.nextSlide >= els.length) {
			if (opts.nowrap) return false;
			opts.nextSlide = 0;
		}
	}

	var cb = opts.onPrevNextEvent || opts.prevNextClick; // prevNextClick is deprecated
	if ($.isFunction(cb))
		cb(val > 0, opts.nextSlide, els[opts.nextSlide]);
	go(els, opts, 1, moveForward);
	return false;
}

function buildPager(els, opts) {
	var $p = $(opts.pager);
	$.each(els, function(i,o) {
		$.fn.cycle.createPagerAnchor(i,o,$p,els,opts);
	});
	opts.updateActivePagerLink(opts.pager, opts.startingSlide, opts.activePagerClass);
}

$.fn.cycle.createPagerAnchor = function(i, el, $p, els, opts) {
	var a;
	if ($.isFunction(opts.pagerAnchorBuilder)) {
		a = opts.pagerAnchorBuilder(i,el);
		debug('pagerAnchorBuilder('+i+', el) returned: ' + a);
	}
	else
		a = '<a href="#">'+(i+1)+'</a>';
		
	if (!a)
		return;
	var $a = $(a);
	// don't reparent if anchor is in the dom
	if ($a.parents('body').length === 0) {
		var arr = [];
		if ($p.length > 1) {
			$p.each(function() {
				var $clone = $a.clone(true);
				$(this).append($clone);
				arr.push($clone[0]);
			});
			$a = $(arr);
		}
		else {
			$a.appendTo($p);
		}
	}

	opts.pagerAnchors =  opts.pagerAnchors || [];
	opts.pagerAnchors.push($a);
	
	var pagerFn = function(e) {
		e.preventDefault();
		opts.nextSlide = i;
		var p = opts.$cont[0], timeout = p.cycleTimeout;
		if (timeout) {
			clearTimeout(timeout);
			p.cycleTimeout = 0;
		}
		var cb = opts.onPagerEvent || opts.pagerClick; // pagerClick is deprecated
		if ($.isFunction(cb))
			cb(opts.nextSlide, els[opts.nextSlide]);
		go(els,opts,1,opts.currSlide < i); // trigger the trans
//		return false; // <== allow bubble
	};
	
	if ( /mouseenter|mouseover/i.test(opts.pagerEvent) ) {
		$a.hover(pagerFn, function(){/* no-op */} );
	}
	else {
		$a.bind(opts.pagerEvent, pagerFn);
	}
	
	if ( ! /^click/.test(opts.pagerEvent) && !opts.allowPagerClickBubble)
		$a.bind('click.cycle', function(){return false;}); // suppress click
	
	var cont = opts.$cont[0];
	var pauseFlag = false; // https://github.com/malsup/cycle/issues/44
	if (opts.pauseOnPagerHover) {
		$a.hover(
			function() { 
				pauseFlag = true;
				cont.cyclePause++; 
				triggerPause(cont,true,true);
			}, function() { 
				if (pauseFlag)
					cont.cyclePause--; 
				triggerPause(cont,true,true);
			} 
		);
	}
};

// helper fn to calculate the number of slides between the current and the next
$.fn.cycle.hopsFromLast = function(opts, fwd) {
	var hops, l = opts.lastSlide, c = opts.currSlide;
	if (fwd)
		hops = c > l ? c - l : opts.slideCount - l;
	else
		hops = c < l ? l - c : l + opts.slideCount - c;
	return hops;
};

// fix clearType problems in ie6 by setting an explicit bg color
// (otherwise text slides look horrible during a fade transition)
function clearTypeFix($slides) {
	debug('applying clearType background-color hack');
	function hex(s) {
		s = parseInt(s,10).toString(16);
		return s.length < 2 ? '0'+s : s;
	}
	function getBg(e) {
		for ( ; e && e.nodeName.toLowerCase() != 'html'; e = e.parentNode) {
			var v = $.css(e,'background-color');
			if (v && v.indexOf('rgb') >= 0 ) {
				var rgb = v.match(/\d+/g);
				return '#'+ hex(rgb[0]) + hex(rgb[1]) + hex(rgb[2]);
			}
			if (v && v != 'transparent')
				return v;
		}
		return '#ffffff';
	}
	$slides.each(function() { $(this).css('background-color', getBg(this)); });
}

// reset common props before the next transition
$.fn.cycle.commonReset = function(curr,next,opts,w,h,rev) {
	$(opts.elements).not(curr).hide();
	if (typeof opts.cssBefore.opacity == 'undefined')
		opts.cssBefore.opacity = 1;
	opts.cssBefore.display = 'block';
	if (opts.slideResize && w !== false && next.cycleW > 0)
		opts.cssBefore.width = next.cycleW;
	if (opts.slideResize && h !== false && next.cycleH > 0)
		opts.cssBefore.height = next.cycleH;
	opts.cssAfter = opts.cssAfter || {};
	opts.cssAfter.display = 'none';
	$(curr).css('zIndex',opts.slideCount + (rev === true ? 1 : 0));
	$(next).css('zIndex',opts.slideCount + (rev === true ? 0 : 1));
};

// the actual fn for effecting a transition
$.fn.cycle.custom = function(curr, next, opts, cb, fwd, speedOverride) {
	var $l = $(curr), $n = $(next);
	var speedIn = opts.speedIn, speedOut = opts.speedOut, easeIn = opts.easeIn, easeOut = opts.easeOut, animInDelay = opts.animInDelay, animOutDelay = opts.animOutDelay;
	$n.css(opts.cssBefore);
	if (speedOverride) {
		if (typeof speedOverride == 'number')
			speedIn = speedOut = speedOverride;
		else
			speedIn = speedOut = 1;
		easeIn = easeOut = null;
	}
	var fn = function() {
		$n.delay(animInDelay).animate(opts.animIn, speedIn, easeIn, function() {
			cb();
		});
	};
	$l.delay(animOutDelay).animate(opts.animOut, speedOut, easeOut, function() {
		$l.css(opts.cssAfter);
		if (!opts.sync) 
			fn();
	});
	if (opts.sync) fn();
};

// transition definitions - only fade is defined here, transition pack defines the rest
$.fn.cycle.transitions = {
	fade: function($cont, $slides, opts) {
		$slides.not(':eq('+opts.currSlide+')').css('opacity',0);
		opts.before.push(function(curr,next,opts) {
			$.fn.cycle.commonReset(curr,next,opts);
			opts.cssBefore.opacity = 0;
		});
		opts.animIn	   = { opacity: 1 };
		opts.animOut   = { opacity: 0 };
		opts.cssBefore = { top: 0, left: 0 };
	}
};

$.fn.cycle.ver = function() { return ver; };

// override these globally if you like (they are all optional)
$.fn.cycle.defaults = {
    activePagerClass: 'activeSlide', // class name used for the active pager link
    after:            null,     // transition callback (scope set to element that was shown):  function(currSlideElement, nextSlideElement, options, forwardFlag)
    allowPagerClickBubble: false, // allows or prevents click event on pager anchors from bubbling
    animIn:           null,     // properties that define how the slide animates in
    animInDelay:      0,        // allows delay before next slide transitions in	
    animOut:          null,     // properties that define how the slide animates out
    animOutDelay:     0,        // allows delay before current slide transitions out
    aspect:           false,    // preserve aspect ratio during fit resizing, cropping if necessary (must be used with fit option)
    autostop:         0,        // true to end slideshow after X transitions (where X == slide count)
    autostopCount:    0,        // number of transitions (optionally used with autostop to define X)
    backwards:        false,    // true to start slideshow at last slide and move backwards through the stack
    before:           null,     // transition callback (scope set to element to be shown):     function(currSlideElement, nextSlideElement, options, forwardFlag)
    center:           null,     // set to true to have cycle add top/left margin to each slide (use with width and height options)
    cleartype:        !$.support.opacity,  // true if clearType corrections should be applied (for IE)
    cleartypeNoBg:    false,    // set to true to disable extra cleartype fixing (leave false to force background color setting on slides)
    containerResize:  1,        // resize container to fit largest slide
    containerResizeHeight:  0,  // resize containers height to fit the largest slide but leave the width dynamic
    continuous:       0,        // true to start next transition immediately after current one completes
    cssAfter:         null,     // properties that defined the state of the slide after transitioning out
    cssBefore:        null,     // properties that define the initial state of the slide before transitioning in
    delay:            0,        // additional delay (in ms) for first transition (hint: can be negative)
    easeIn:           null,     // easing for "in" transition
    easeOut:          null,     // easing for "out" transition
    easing:           null,     // easing method for both in and out transitions
    end:              null,     // callback invoked when the slideshow terminates (use with autostop or nowrap options): function(options)
    fastOnEvent:      0,        // force fast transitions when triggered manually (via pager or prev/next); value == time in ms
    fit:              0,        // force slides to fit container
    fx:               'fade',   // name of transition effect (or comma separated names, ex: 'fade,scrollUp,shuffle')
    fxFn:             null,     // function used to control the transition: function(currSlideElement, nextSlideElement, options, afterCalback, forwardFlag)
    height:           'auto',   // container height (if the 'fit' option is true, the slides will be set to this height as well)
    manualTrump:      true,     // causes manual transition to stop an active transition instead of being ignored
    metaAttr:         'cycle',  // data- attribute that holds the option data for the slideshow
    next:             null,     // element, jQuery object, or jQuery selector string for the element to use as event trigger for next slide
    nowrap:           0,        // true to prevent slideshow from wrapping
    onPagerEvent:     null,     // callback fn for pager events: function(zeroBasedSlideIndex, slideElement)
    onPrevNextEvent:  null,     // callback fn for prev/next events: function(isNext, zeroBasedSlideIndex, slideElement)
    pager:            null,     // element, jQuery object, or jQuery selector string for the element to use as pager container
    pagerAnchorBuilder: null,   // callback fn for building anchor links:  function(index, DOMelement)
    pagerEvent:       'click.cycle', // name of event which drives the pager navigation
    pause:            0,        // true to enable "pause on hover"
    pauseOnPagerHover: 0,       // true to pause when hovering over pager link
    prev:             null,     // element, jQuery object, or jQuery selector string for the element to use as event trigger for previous slide
    prevNextEvent:    'click.cycle',// event which drives the manual transition to the previous or next slide
    random:           0,        // true for random, false for sequence (not applicable to shuffle fx)
    randomizeEffects: 1,        // valid when multiple effects are used; true to make the effect sequence random
    requeueOnImageNotLoaded: true, // requeue the slideshow if any image slides are not yet loaded
    requeueTimeout:   250,      // ms delay for requeue
    rev:              0,        // causes animations to transition in reverse (for effects that support it such as scrollHorz/scrollVert/shuffle)
    shuffle:          null,     // coords for shuffle animation, ex: { top:15, left: 200 }
    skipInitializationCallbacks: false, // set to true to disable the first before/after callback that occurs prior to any transition
    slideExpr:        null,     // expression for selecting slides (if something other than all children is required)
    slideResize:      1,        // force slide width/height to fixed size before every transition
    speed:            1000,     // speed of the transition (any valid fx speed value)
    speedIn:          null,     // speed of the 'in' transition
    speedOut:         null,     // speed of the 'out' transition
    startingSlide:    undefined,// zero-based index of the first slide to be displayed
    sync:             1,        // true if in/out transitions should occur simultaneously
    timeout:          4000,     // milliseconds between slide transitions (0 to disable auto advance)
    timeoutFn:        null,     // callback for determining per-slide timeout value:  function(currSlideElement, nextSlideElement, options, forwardFlag)
    updateActivePagerLink: null,// callback fn invoked to update the active pager link (adds/removes activePagerClass style)
    width:            null      // container width (if the 'fit' option is true, the slides will be set to this width as well)
};

})(jQuery);


/*!
 * jQuery Cycle Plugin Transition Definitions
 * This script is a plugin for the jQuery Cycle Plugin
 * Examples and documentation at: http://malsup.com/jquery/cycle/
 * Copyright (c) 2007-2010 M. Alsup
 * Version:	 2.73
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 */
(function($) {
"use strict";

//
// These functions define slide initialization and properties for the named
// transitions. To save file size feel free to remove any of these that you
// don't need.
//
$.fn.cycle.transitions.none = function($cont, $slides, opts) {
	opts.fxFn = function(curr,next,opts,after){
		$(next).show();
		$(curr).hide();
		after();
	};
};

// not a cross-fade, fadeout only fades out the top slide
$.fn.cycle.transitions.fadeout = function($cont, $slides, opts) {
	$slides.not(':eq('+opts.currSlide+')').css({ display: 'block', 'opacity': 1 });
	opts.before.push(function(curr,next,opts,w,h,rev) {
		$(curr).css('zIndex',opts.slideCount + (rev !== true ? 1 : 0));
		$(next).css('zIndex',opts.slideCount + (rev !== true ? 0 : 1));
	});
	opts.animIn.opacity = 1;
	opts.animOut.opacity = 0;
	opts.cssBefore.opacity = 1;
	opts.cssBefore.display = 'block';
	opts.cssAfter.zIndex = 0;
};

// scrollUp/Down/Left/Right
$.fn.cycle.transitions.scrollUp = function($cont, $slides, opts) {
	$cont.css('overflow','hidden');
	opts.before.push($.fn.cycle.commonReset);
	var h = $cont.height();
	opts.cssBefore.top = h;
	opts.cssBefore.left = 0;
	opts.cssFirst.top = 0;
	opts.animIn.top = 0;
	opts.animOut.top = -h;
};
$.fn.cycle.transitions.scrollDown = function($cont, $slides, opts) {
	$cont.css('overflow','hidden');
	opts.before.push($.fn.cycle.commonReset);
	var h = $cont.height();
	opts.cssFirst.top = 0;
	opts.cssBefore.top = -h;
	opts.cssBefore.left = 0;
	opts.animIn.top = 0;
	opts.animOut.top = h;
};
$.fn.cycle.transitions.scrollLeft = function($cont, $slides, opts) {
	$cont.css('overflow','hidden');
	opts.before.push($.fn.cycle.commonReset);
	var w = $cont.width();
	opts.cssFirst.left = 0;
	opts.cssBefore.left = w;
	opts.cssBefore.top = 0;
	opts.animIn.left = 0;
	opts.animOut.left = 0-w;
};
$.fn.cycle.transitions.scrollRight = function($cont, $slides, opts) {
	$cont.css('overflow','hidden');
	opts.before.push($.fn.cycle.commonReset);
	var w = $cont.width();
	opts.cssFirst.left = 0;
	opts.cssBefore.left = -w;
	opts.cssBefore.top = 0;
	opts.animIn.left = 0;
	opts.animOut.left = w;
};
$.fn.cycle.transitions.scrollHorz = function($cont, $slides, opts) {
	$cont.css('overflow','hidden').width();
	opts.before.push(function(curr, next, opts, fwd) {
		if (opts.rev)
			fwd = !fwd;
		$.fn.cycle.commonReset(curr,next,opts);
		opts.cssBefore.left = fwd ? (next.cycleW-1) : (1-next.cycleW);
		opts.animOut.left = fwd ? -curr.cycleW : curr.cycleW;
	});
	opts.cssFirst.left = 0;
	opts.cssBefore.top = 0;
	opts.animIn.left = 0;
	opts.animOut.top = 0;
};
$.fn.cycle.transitions.scrollVert = function($cont, $slides, opts) {
	$cont.css('overflow','hidden');
	opts.before.push(function(curr, next, opts, fwd) {
		if (opts.rev)
			fwd = !fwd;
		$.fn.cycle.commonReset(curr,next,opts);
		opts.cssBefore.top = fwd ? (1-next.cycleH) : (next.cycleH-1);
		opts.animOut.top = fwd ? curr.cycleH : -curr.cycleH;
	});
	opts.cssFirst.top = 0;
	opts.cssBefore.left = 0;
	opts.animIn.top = 0;
	opts.animOut.left = 0;
};

// slideX/slideY
$.fn.cycle.transitions.slideX = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$(opts.elements).not(curr).hide();
		$.fn.cycle.commonReset(curr,next,opts,false,true);
		opts.animIn.width = next.cycleW;
	});
	opts.cssBefore.left = 0;
	opts.cssBefore.top = 0;
	opts.cssBefore.width = 0;
	opts.animIn.width = 'show';
	opts.animOut.width = 0;
};
$.fn.cycle.transitions.slideY = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$(opts.elements).not(curr).hide();
		$.fn.cycle.commonReset(curr,next,opts,true,false);
		opts.animIn.height = next.cycleH;
	});
	opts.cssBefore.left = 0;
	opts.cssBefore.top = 0;
	opts.cssBefore.height = 0;
	opts.animIn.height = 'show';
	opts.animOut.height = 0;
};

// shuffle
$.fn.cycle.transitions.shuffle = function($cont, $slides, opts) {
	var i, w = $cont.css('overflow', 'visible').width();
	$slides.css({left: 0, top: 0});
	opts.before.push(function(curr,next,opts) {
		$.fn.cycle.commonReset(curr,next,opts,true,true,true);
	});
	// only adjust speed once!
	if (!opts.speedAdjusted) {
		opts.speed = opts.speed / 2; // shuffle has 2 transitions
		opts.speedAdjusted = true;
	}
	opts.random = 0;
	opts.shuffle = opts.shuffle || {left:-w, top:15};
	opts.els = [];
	for (i=0; i < $slides.length; i++)
		opts.els.push($slides[i]);

	for (i=0; i < opts.currSlide; i++)
		opts.els.push(opts.els.shift());

	// custom transition fn (hat tip to Benjamin Sterling for this bit of sweetness!)
	opts.fxFn = function(curr, next, opts, cb, fwd) {
		if (opts.rev)
			fwd = !fwd;
		var $el = fwd ? $(curr) : $(next);
		$(next).css(opts.cssBefore);
		var count = opts.slideCount;
		$el.animate(opts.shuffle, opts.speedIn, opts.easeIn, function() {
			var hops = $.fn.cycle.hopsFromLast(opts, fwd);
			for (var k=0; k < hops; k++) {
				if (fwd)
					opts.els.push(opts.els.shift());
				else
					opts.els.unshift(opts.els.pop());
			}
			if (fwd) {
				for (var i=0, len=opts.els.length; i < len; i++)
					$(opts.els[i]).css('z-index', len-i+count);
			}
			else {
				var z = $(curr).css('z-index');
				$el.css('z-index', parseInt(z,10)+1+count);
			}
			$el.animate({left:0, top:0}, opts.speedOut, opts.easeOut, function() {
				$(fwd ? this : curr).hide();
				if (cb) cb();
			});
		});
	};
	$.extend(opts.cssBefore, { display: 'block', opacity: 1, top: 0, left: 0 });
};

// turnUp/Down/Left/Right
$.fn.cycle.transitions.turnUp = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,true,false);
		opts.cssBefore.top = next.cycleH;
		opts.animIn.height = next.cycleH;
		opts.animOut.width = next.cycleW;
	});
	opts.cssFirst.top = 0;
	opts.cssBefore.left = 0;
	opts.cssBefore.height = 0;
	opts.animIn.top = 0;
	opts.animOut.height = 0;
};
$.fn.cycle.transitions.turnDown = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,true,false);
		opts.animIn.height = next.cycleH;
		opts.animOut.top   = curr.cycleH;
	});
	opts.cssFirst.top = 0;
	opts.cssBefore.left = 0;
	opts.cssBefore.top = 0;
	opts.cssBefore.height = 0;
	opts.animOut.height = 0;
};
$.fn.cycle.transitions.turnLeft = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,false,true);
		opts.cssBefore.left = next.cycleW;
		opts.animIn.width = next.cycleW;
	});
	opts.cssBefore.top = 0;
	opts.cssBefore.width = 0;
	opts.animIn.left = 0;
	opts.animOut.width = 0;
};
$.fn.cycle.transitions.turnRight = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,false,true);
		opts.animIn.width = next.cycleW;
		opts.animOut.left = curr.cycleW;
	});
	$.extend(opts.cssBefore, { top: 0, left: 0, width: 0 });
	opts.animIn.left = 0;
	opts.animOut.width = 0;
};

// zoom
$.fn.cycle.transitions.zoom = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,false,false,true);
		opts.cssBefore.top = next.cycleH/2;
		opts.cssBefore.left = next.cycleW/2;
		$.extend(opts.animIn, { top: 0, left: 0, width: next.cycleW, height: next.cycleH });
		$.extend(opts.animOut, { width: 0, height: 0, top: curr.cycleH/2, left: curr.cycleW/2 });
	});
	opts.cssFirst.top = 0;
	opts.cssFirst.left = 0;
	opts.cssBefore.width = 0;
	opts.cssBefore.height = 0;
};

// fadeZoom
$.fn.cycle.transitions.fadeZoom = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,false,false);
		opts.cssBefore.left = next.cycleW/2;
		opts.cssBefore.top = next.cycleH/2;
		$.extend(opts.animIn, { top: 0, left: 0, width: next.cycleW, height: next.cycleH });
	});
	opts.cssBefore.width = 0;
	opts.cssBefore.height = 0;
	opts.animOut.opacity = 0;
};

// blindX
$.fn.cycle.transitions.blindX = function($cont, $slides, opts) {
	var w = $cont.css('overflow','hidden').width();
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts);
		opts.animIn.width = next.cycleW;
		opts.animOut.left   = curr.cycleW;
	});
	opts.cssBefore.left = w;
	opts.cssBefore.top = 0;
	opts.animIn.left = 0;
	opts.animOut.left = w;
};
// blindY
$.fn.cycle.transitions.blindY = function($cont, $slides, opts) {
	var h = $cont.css('overflow','hidden').height();
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts);
		opts.animIn.height = next.cycleH;
		opts.animOut.top   = curr.cycleH;
	});
	opts.cssBefore.top = h;
	opts.cssBefore.left = 0;
	opts.animIn.top = 0;
	opts.animOut.top = h;
};
// blindZ
$.fn.cycle.transitions.blindZ = function($cont, $slides, opts) {
	var h = $cont.css('overflow','hidden').height();
	var w = $cont.width();
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts);
		opts.animIn.height = next.cycleH;
		opts.animOut.top   = curr.cycleH;
	});
	opts.cssBefore.top = h;
	opts.cssBefore.left = w;
	opts.animIn.top = 0;
	opts.animIn.left = 0;
	opts.animOut.top = h;
	opts.animOut.left = w;
};

// growX - grow horizontally from centered 0 width
$.fn.cycle.transitions.growX = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,false,true);
		opts.cssBefore.left = this.cycleW/2;
		opts.animIn.left = 0;
		opts.animIn.width = this.cycleW;
		opts.animOut.left = 0;
	});
	opts.cssBefore.top = 0;
	opts.cssBefore.width = 0;
};
// growY - grow vertically from centered 0 height
$.fn.cycle.transitions.growY = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,true,false);
		opts.cssBefore.top = this.cycleH/2;
		opts.animIn.top = 0;
		opts.animIn.height = this.cycleH;
		opts.animOut.top = 0;
	});
	opts.cssBefore.height = 0;
	opts.cssBefore.left = 0;
};

// curtainX - squeeze in both edges horizontally
$.fn.cycle.transitions.curtainX = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,false,true,true);
		opts.cssBefore.left = next.cycleW/2;
		opts.animIn.left = 0;
		opts.animIn.width = this.cycleW;
		opts.animOut.left = curr.cycleW/2;
		opts.animOut.width = 0;
	});
	opts.cssBefore.top = 0;
	opts.cssBefore.width = 0;
};
// curtainY - squeeze in both edges vertically
$.fn.cycle.transitions.curtainY = function($cont, $slides, opts) {
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,true,false,true);
		opts.cssBefore.top = next.cycleH/2;
		opts.animIn.top = 0;
		opts.animIn.height = next.cycleH;
		opts.animOut.top = curr.cycleH/2;
		opts.animOut.height = 0;
	});
	opts.cssBefore.height = 0;
	opts.cssBefore.left = 0;
};

// cover - curr slide covered by next slide
$.fn.cycle.transitions.cover = function($cont, $slides, opts) {
	var d = opts.direction || 'left';
	var w = $cont.css('overflow','hidden').width();
	var h = $cont.height();
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts);
		opts.cssAfter.display = '';
		if (d == 'right')
			opts.cssBefore.left = -w;
		else if (d == 'up')
			opts.cssBefore.top = h;
		else if (d == 'down')
			opts.cssBefore.top = -h;
		else
			opts.cssBefore.left = w;
	});
	opts.animIn.left = 0;
	opts.animIn.top = 0;
	opts.cssBefore.top = 0;
	opts.cssBefore.left = 0;
};

// uncover - curr slide moves off next slide
$.fn.cycle.transitions.uncover = function($cont, $slides, opts) {
	var d = opts.direction || 'left';
	var w = $cont.css('overflow','hidden').width();
	var h = $cont.height();
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,true,true,true);
		if (d == 'right')
			opts.animOut.left = w;
		else if (d == 'up')
			opts.animOut.top = -h;
		else if (d == 'down')
			opts.animOut.top = h;
		else
			opts.animOut.left = -w;
	});
	opts.animIn.left = 0;
	opts.animIn.top = 0;
	opts.cssBefore.top = 0;
	opts.cssBefore.left = 0;
};

// toss - move top slide and fade away
$.fn.cycle.transitions.toss = function($cont, $slides, opts) {
	var w = $cont.css('overflow','visible').width();
	var h = $cont.height();
	opts.before.push(function(curr, next, opts) {
		$.fn.cycle.commonReset(curr,next,opts,true,true,true);
		// provide default toss settings if animOut not provided
		if (!opts.animOut.left && !opts.animOut.top)
			$.extend(opts.animOut, { left: w*2, top: -h/2, opacity: 0 });
		else
			opts.animOut.opacity = 0;
	});
	opts.cssBefore.left = 0;
	opts.cssBefore.top = 0;
	opts.animIn.left = 0;
};

// wipe - clip animation
$.fn.cycle.transitions.wipe = function($cont, $slides, opts) {
	var w = $cont.css('overflow','hidden').width();
	var h = $cont.height();
	opts.cssBefore = opts.cssBefore || {};
	var clip;
	if (opts.clip) {
		if (/l2r/.test(opts.clip))
			clip = 'rect(0px 0px '+h+'px 0px)';
		else if (/r2l/.test(opts.clip))
			clip = 'rect(0px '+w+'px '+h+'px '+w+'px)';
		else if (/t2b/.test(opts.clip))
			clip = 'rect(0px '+w+'px 0px 0px)';
		else if (/b2t/.test(opts.clip))
			clip = 'rect('+h+'px '+w+'px '+h+'px 0px)';
		else if (/zoom/.test(opts.clip)) {
			var top = parseInt(h/2,10);
			var left = parseInt(w/2,10);
			clip = 'rect('+top+'px '+left+'px '+top+'px '+left+'px)';
		}
	}

	opts.cssBefore.clip = opts.cssBefore.clip || clip || 'rect(0px 0px 0px 0px)';

	var d = opts.cssBefore.clip.match(/(\d+)/g);
	var t = parseInt(d[0],10), r = parseInt(d[1],10), b = parseInt(d[2],10), l = parseInt(d[3],10);

	opts.before.push(function(curr, next, opts) {
		if (curr == next) return;
		var $curr = $(curr), $next = $(next);
		$.fn.cycle.commonReset(curr,next,opts,true,true,false);
		opts.cssAfter.display = 'block';

		var step = 1, count = parseInt((opts.speedIn / 13),10) - 1;
		(function f() {
			var tt = t ? t - parseInt(step * (t/count),10) : 0;
			var ll = l ? l - parseInt(step * (l/count),10) : 0;
			var bb = b < h ? b + parseInt(step * ((h-b)/count || 1),10) : h;
			var rr = r < w ? r + parseInt(step * ((w-r)/count || 1),10) : w;
			$next.css({ clip: 'rect('+tt+'px '+rr+'px '+bb+'px '+ll+'px)' });
			(step++ <= count) ? setTimeout(f, 13) : $curr.css('display', 'none');
		})();
	});
	$.extend(opts.cssBefore, { display: 'block', opacity: 1, top: 0, left: 0 });
	opts.animIn	   = { left: 0 };
	opts.animOut   = { left: 0 };
};

})(jQuery);



