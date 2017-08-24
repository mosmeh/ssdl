#!/usr/bin/env python3

import sys
import urllib.request
import tempfile
import re
import os
import subprocess
import bs4
import tqdm

def download(url):
    img_url_re = re.compile('https?://image.slidesharecdn.com/[^/]+/[^/]+/.+-([0-9]+)-[0-9]+\..+')

    print('retrieving image list')
    doc = bs4.BeautifulSoup(urllib.request.urlopen(url), 'lxml')
    img_urls = list(map(lambda n: n.attrs['data-full'], doc.find_all('img', class_='slide_image')))
    num_imgs = len(img_urls)

    # sort by page number
    img_urls.sort(key=lambda img_url: int(img_url_re.match(img_url).group(1)))

    with tempfile.TemporaryDirectory() as dirname:
        img_filenames = []

        for i, img_url in tqdm.tqdm(enumerate(img_urls), desc='downloading', total=num_imgs):
            # no need to include extensions in filenames since ImageMagick determines file types from signatures
            filename = os.path.join(dirname, str(i))
            urllib.request.urlretrieve(img_url, filename)
            img_filenames.append(filename)

        print('converting to PDF')
        # if |url| points at specific page, get title of parent slide
        title_elem = doc.find('a', class_='j-parent-title')
        if title_elem is None:
            # if no, just get title of slide
            title_elem = doc.find('span', class_='j-title-breadcrumb')

        # ImageMagick uses filename as PDF title
        dest_filename = os.path.join(dirname, '{}.pdf'.format(title_elem.string))
        subprocess.call(['convert'] + img_filenames + [dest_filename])

        # then rename to sanitized title in |url|
        author, title = re.match('https?://www.slideshare.net/([^/]+)/([^/]+)(?:/.+)?', url).groups()
        final_filename = '{}_{}.pdf'.format(author, title)
        os.rename(dest_filename, os.path.join(os.curdir, final_filename))
        print('saved to {}'.format(final_filename))

if __name__ == '__main__':
    download(sys.argv[1])
