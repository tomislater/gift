gift (get images from tumblr)
=============================

Script for downloading images from tumblr blogs. All images are stored in **images/blog-name**.

Install
-------
    pip install -r requirements.txt

How to use
----------
You must have application on tumblr. You can register [here](http://www.tumblr.com/oauth/apps).
If you created application, you need paste **OAuth Consumer Key** in config.

###### config.cfg
    [tumblr]
    consumer_key = your_consumer_key

###### Usage
    Usage: gift.py NAME [-l NUMBER]

    Examples:
        gift.py perfectboard
        gift.py perfectboard -l 100
        gift.py perfectboard --limit=1000

    Arguments:
        NAME    Name of the blog

    Options:
        -l NUMBER --limit=NUMBER    limit for posts which will be downloaded

Screenshots
-----------

![1](http://2.bp.blogspot.com/-dBeDbBXDM6s/UZ0wUSXotjI/AAAAAAAAArM/pBFgSh2Q3DE/s1600/-bin-bash_023.png)

![2](http://1.bp.blogspot.com/-W1WG6DHoYCk/UZ0wUQi0MII/AAAAAAAAArQ/lrY7PTL3Cug/s1600/-bin-bash_024.png)

![2](http://4.bp.blogspot.com/-GPCgf6FYDic/UZ0wUXmXPBI/AAAAAAAAArU/Qxb0Luh5Zx8/s1600/-bin-bash_026.png)