markdowner
==========

A markdown viewer/reader and editor written with Python GTK.

## Installation

    git clone git://github.com/aviddiviner/markdowner

You'll need Python installed. My system came bundled with v2.6.5, but if you don't have it, a quick `sudo apt-get install python` or similar should fix things.

After that, you'll need to install the *markdown* library. I did this as follows:

    git clone git://github.com/waylan/Python-Markdown.git
    cd Python-Markdown/
    sudo python setup.py install

(See [http://www.freewisdom.org/projects/python-markdown/](http://www.freewisdom.org/projects/python-markdown/) for more info.)

### Create a Symlink

You may now want to create a symlink in your bin folder or something similar:

    sudo ln -s /path/to/your/markdowner.py /usr/local/bin/markdowner

Once you've done this, you can edit files by typing in your console `markdowner <filename>`

### Associate Files in Nautilus

This is also easy. Right click on a markdown file, such as this README.md file and choose:

    Properties > Open With > Add > Custom Command > markdowner


## Credits
This is based off a script I found at [http://www.jezra.net](http://www.jezra.net) so thanks go out to him for the base of this.

