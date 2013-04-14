atv.config = { 
    "doesJavaScriptLoadRoot": true,
    "DEBUG_LEVEL": 4,
    "ROOT_URL": "http://trailers.apple.com/plexconnect.xml"
};

atv.onAppEntry = function()
{
    atv.loadURL(atv.config.ROOT_URL);
}
