atv.config = { 
    "doesJavaScriptLoadRoot": true,
    "DEBUG_LEVEL": 4,
    "ROOT_URL": "http://trailers.apple.com/appletv/index.xml"
};

atv.onAppEntry = function()
{
    atv.loadURL('http://trailers.apple.com/index.xml');
}
