function pause(millis) {
  var date = new Date();
  var curDate = null;
  do { curDate = new Date(); } 
  while(curDate-date < millis);
}; 

function reloadPMS_XML() {
  pause(200); // 0.2 second pause to let any images on XML page unload
  var path = atv.sessionStorage['reloadXMLpath'];
  atv.loadAndSwapURL("http://trailers.apple.com" + path);
};
