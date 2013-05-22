#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Usage: gift.py NAME [-l NUMBER]

Examples:
    gift.py perfectboard
    gift.py perfectboard -l 100
    gift.py perfectboard --limit=1000

Arguments:
    NAME    Name of the blog

Options:
    -l NUMBER --limit=NUMBER    limit for posts which will be downloaded
"""

import os
import Queue
import urllib2
import pytumblr
import threading
import ConfigParser

from docopt import docopt
from progressbar import ProgressBar, Bar, Percentage, SimpleProgress

MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
IMAGES_DIR = os.path.join(MAIN_DIR, 'images')

config = ConfigParser.RawConfigParser()
config.read(os.path.join(MAIN_DIR, 'config.cfg'))

client = pytumblr.TumblrRestClient(config.get('tumblr', 'consumer_key'))


def get_image_name(photo_url):
    return photo_url[photo_url.rfind('/') + 1:]


class ThreadCheckImage(threading.Thread):
    """
        Checks if image exists in dir.
    """
    def __init__(self, q_to_check, q_content, image_dir, pbar):
        """
            :param Queue.Queue q_to_check: queue for images to check
            :param Queue.Queue q_content: queue for images to download
            :param str image_dir: image dir
            :param ProgressBar pbar: instance of progress bar
        """
        threading.Thread.__init__(self)
        self.queue_to_check = q_to_check
        self.queue_content = q_content
        self.image_dir = image_dir
        self.pbar = pbar

    def run(self):
        while True:
            photo_url, image_name = self.queue_to_check.get()

            if not self.check_image_in_dir(image_name, self.image_dir):
                self.queue_content.put((photo_url, image_name))
            else:
                self.pbar.update(self.pbar.currval + 1)

            self.queue_to_check.task_done()

    def check_image_in_dir(self, image_name, image_dir):
        """
            :param str image_name: name of image
            :param str image_dir: image dir
            :return: True or False
            :rtype: bool
        """
        return image_name in os.listdir(image_dir)


class ThreadGetContent(threading.Thread):
    def __init__(self, q_content, q_save):
        """
            :param Queue.Queue q_content: queue for images to download
            :param Queue.Queue q_save: queue for content from images
        """
        threading.Thread.__init__(self)
        self.queue_content = q_content
        self.queue_save = q_save

    def run(self):
        while True:
            photo_url, image_name = self.queue_content.get()
            self.queue_save.put(
                (urllib2.urlopen(photo_url).read(), image_name)
            )
            self.queue_content.task_done()


class ThreadSave(threading.Thread):
    def __init__(self, q_save, image_dir, pbar):
        """
            :param Queue.Queue q_save: queue with content to save
            :param str image_dir: image dir
            :param ProgressBar pbar: progress bar
        """
        threading.Thread.__init__(self)
        self.queue_save = q_save
        self.image_dir = image_dir
        self.pbar = pbar

    def run(self):
        while True:
            content, image_name = self.queue_save.get()

            with open(
                self.image_dir + '/{0}'.format(image_name), 'wb'
            ) as f:
                f.write(content)

            self.pbar.update(self.pbar.currval + 1)
            self.queue_save.task_done()


def get_urls_from_tumblr(queue, limit, blog_name, pbar):
    """
        Gets URL to photos.

        :param Queue.Queue queue: queue ;)
        :param int limit: limit for posts
        :param str blog_name: name of blog
        :param ProgressBar pbar: progress bar
        :return: queue with tuple(url, image_name)
        :rtype: queue with tuples
    """

    if limit < 20:
        for post in client.posts(blog_name, limit=limit)["posts"]:
            if post["type"] == "photo":
                url = post["photos"][0]["original_size"]["url"]
                queue.put((url, get_image_name(url)))
            pbar.update(pbar.currval + 1)
    else:
        for offset in xrange(0, limit, 20):
            limoff = limit - offset
            for post in client.posts(blog_name,
                                     offset=offset,
                                     limit=limoff if limoff < 20 else 20)["posts"]:
                if post["type"] == "photo":
                    url = post["photos"][0]["original_size"]["url"]
                    queue.put((url, get_image_name(url)))
                pbar.update(pbar.currval + 1)
    return queue


if __name__ == "__main__":
    arguments = docopt(__doc__)
    blog_name = arguments["NAME"]

    if arguments["--limit"]:
        limit = int(arguments["--limit"])
    else:
        limit = client.blog_info(blog_name)["blog"]["posts"]

    image_dir = IMAGES_DIR + '/{0}'.format(blog_name)

    try:
        os.listdir(image_dir)
    except OSError:
        os.makedirs(image_dir)

    queue_to_check = Queue.Queue()
    queue_content = Queue.Queue()
    queue_save = Queue.Queue()

    print("Collecting data from tumblr...")
    pbar_tumblr = ProgressBar(
        widgets=[Percentage(),
                 ' ', Bar(),
                 ' ', SimpleProgress()],
        maxval=limit).start()

    queue_to_check = get_urls_from_tumblr(
        queue_to_check,
        limit,
        blog_name,
        pbar_tumblr
    )
    pbar_tumblr.finish()

    print("Downloading images...")
    pbar = ProgressBar(
        widgets=[Percentage(),
                 ' ', Bar(),
                 ' ', SimpleProgress()],
        maxval=queue_to_check.qsize()).start()

    for x in xrange(16):
        tci = ThreadCheckImage(queue_to_check, queue_content, image_dir, pbar)
        tci.daemon = True
        tci.start()

        tgc = ThreadGetContent(queue_content, queue_save)
        tgc.daemon = True
        tgc.start()

    for x in xrange(4):
        ts = ThreadSave(queue_save, image_dir, pbar)
        ts.daemon = True
        ts.start()

    queue_to_check.join()
    queue_content.join()
    queue_save.join()
    pbar.finish()
