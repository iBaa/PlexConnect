// atv.Element extensions
if(atv.Element)
{
	atv.Element.prototype.getElementsByTagName = function(tagName)
	{
		return this.ownerDocument.evaluateXPath("descendant::" + tagName, this);
	};

	atv.Element.prototype.getElementByTagName = function(tagName)
	{
		var elements = this.getElementsByTagName(tagName);
		if(elements && elements.length > 0)
		{
			return elements[0];
		};
		return undefined;
	};
};

// Load Photo Fullscreen
function onSelectPhoto(ID)
{
	var pArray = createArray(ID);
	loadFSBrowser(pArray.photoDicts, pArray.initialSelection);
};

// Make a collection-array from the photos 
function createArray(photoID)
{
	var initialSelection = 0;
	var photoDicts = [];

	var photos = document.evaluateXPath('//photo');
	for(var i = 0; i < photos.length; ++i)
	{
		var photo = photos[i]
    var type = photo.tagName;
    var collectionArrayName = "assets";
		var photoAssets = photo.getElementsByTagName('photoAsset');

		photoDict = {};

		photoDict.id = photo.getAttribute('id');
		photoDict.type = "photo";
		
		photoDict[collectionArrayName] = [];
		for(var assetIndex = 0; assetIndex < photoAssets.length; ++assetIndex)
		{
			var photoAsset = photoAssets[assetIndex];
			var photoAssetDict = {
				"width": parseInt(photoAsset.getAttribute('width')),
				"height": parseInt(photoAsset.getAttribute('height')),
				"src": photoAsset.getAttribute('src')
			};

			photoDict[collectionArrayName].push(photoAssetDict);
		};

		if(photoDict.id == photoID)
		{
			initialSelection = photoDicts.length;
		};

		photoDicts.push(photoDict);
	};

	var photoArray = {
		"photoDicts": photoDicts,
		"initialSelection": initialSelection
	};

	return photoArray;
};

// OPen the FullScreen browser
function loadFSBrowser(photoDicts, initialSelection)
{
	var fullScreenMediaBrowser = new atv.FullScreenMediaBrowser();
	fullScreenMediaBrowser.show(photoDicts, initialSelection);
};
