# imageviewer

I have a bunch of images on my hard drive, and some of them are stored in heavily nested folder structures.
This is a script to help me look through them images.
It scans a folder for image files (plus any subfolders), then arranges them in a grid.
I can click any image to go to the original file:

![A collection of images arranged in a grid on a dark background.](screenshot.png)

## Installation

1.  Install Python 3
2.  Clone the repo
3.  Install the requirements (`pip3 install -r requirements.txt`)
4.  (Optional) install [dominant_colours](https://github.com/alexwlchan/dominant_colours)

## Usage

Run the included imageviewer script, passing a path to the folder with images you want to browse, e.g.

```console
$ python3 imageviewer.py ~/repos/alexwlchan.net
```

It will open an HTML file with the image grid in your browser.

## License

Code: MIT.

The background texture is [Memphis Mini Dark by Tomislava Babić](https://www.toptal.com/designers/subtlepatterns/memphis-mini-dark-pattern/), used under a Creative Commons licence.
