<?php
$image = $_GET['image'];
$gradient = $_GET['gradient'];
$hd = $_GET['hd'];
$text = $_GET['title'];

if (isset($image) ) {
    
    // No Fanart
    if (!empty($image)) {
        $image = $_GET['image'];
    } else {
        $image = "blank.jpg";
    }

    $base_image = imagecreatefromjpeg($image);
    $top_image = imagecreatefrompng("gradient".$gradient.".png");
    $linefile = "line".$gradient.$hd.".png";
    $line_image = imagecreatefrompng($linefile);
 
    imagealphablending($top_image, true);
    imagesavealpha($top_image, true);    
    imagealphablending($line_image, true);
    imagesavealpha($line_image, true);
    
    // Size Handling:
    if ($hd == "720") {
        $destWidth = 1280;
        $destHeight = 720;
    } else {
        $destWidth = 1920;
        $destHeight = 1080;
    }
    
    list($sourceWidth, $sourceHeight) = getimagesize($image);
    // Image must be 1080, fanart will be overlayed in 720p
    
    $sized_image = imagecreatetruecolor(1920, 1080);
    imagecopyresized($sized_image, $base_image, 0, 0, 0, 0, $destWidth, $destHeight, $sourceWidth, $sourceHeight);

    imagecopyresized($sized_image, $top_image, 0, 0, 0, 0, $destWidth, $destHeight, 1920, 1080);
    
    //Blur effect for TV Shows
    if ($gradient == 'tv') {
        //imagefilter($sized_image, IMG_FILTER_GAUSSIAN_BLUR);
        //imagefilter($sized_image, IMG_FILTER_SMOOTH, -4);
        //imagefilter($sized_image, IMG_FILTER_GAUSSIAN_BLUR);
        //imagefilter($sized_image, IMG_FILTER_GAUSSIAN_BLUR);
        
       	imagecopy($sized_image, $line_image, 0, 0, 0, 0, $destWidth, $destHeight);
        $white = imagecolorallocate($sized_image, 255, 255, 255);
        $font = 'HelveticaBold.ttf';
        $h = $destHeight / 7.2;
        $w = $destWidth / 3.66;
        $fs = $destHeight / 36;
        imagettftext($sized_image, $fs, 0, $w, $h, $white, $font, $text);
    
    
    } else if ($gradient == 'seasons') {
        //imagefilter($sized_image, IMG_FILTER_GAUSSIAN_BLUR);
        //imagefilter($sized_image, IMG_FILTER_SMOOTH, -4);
        //imagefilter($sized_image, IMG_FILTER_GAUSSIAN_BLUR);
        //imagefilter($sized_image, IMG_FILTER_GAUSSIAN_BLUR);
        /*$white = imagecolorallocate($sized_image, 255, 255, 255);
        $font = 'HelveticaBold.ttf';
        $h = $destHeight / 7.2;
        $fs = $destHeight / 28;
        
        $fontSize = imageloadfont($font);
        $xsize = imagefontwidth($fs) * imagefontwidth($fontSize) * strlen($text);
        $w = ($destWidth - $xsize) / 2;
        imagettftext($sized_image, $fs, 0, $w, $h, $white, $font, $text);*/
    } else {
        imagecopy($sized_image, $line_image, 0, 0, 0, 0, $destWidth, $destHeight);
        $white = imagecolorallocate($sized_image, 255, 255, 255);
        $font = 'HelveticaBold.ttf';
        $h = $destHeight / 2.25;
        $w = $destWidth / 3.66;
        $fs = $destHeight / 36;
        imagettftext($sized_image, $fs, 0, $w, $h, $white, $font, $text); 
    }

    header("Content-type: image/png");
    imagepng($sized_image);
} else {
    die("error");
}

        

?>