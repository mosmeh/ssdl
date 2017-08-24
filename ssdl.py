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
    img_url_re = re.compile('.+/.+-([0-9]+)-1024\..+\?cb=.+$')

    print('retrieving image list')
    doc = bs4.BeautifulSoup(urllib.request.urlopen(url), 'lxml')
    img_urls = list(map(lambda n: n.attrs['data-full'], doc.find_all('img', class_='slide_image')))
    num_imgs = len(img_urls)
    img_urls.sort(key=lambda img_url: int(img_url_re.match(img_url).group(1)))

    with tempfile.TemporaryDirectory() as dirname:
        img_filenames = []

        for i, img_url in tqdm.tqdm(enumerate(img_urls), desc='downloading', total=num_imgs):
            filename = os.path.join(dirname, str(i))
            urllib.request.urlretrieve(img_url, filename)
            img_filenames.append(filename)

        print('converting to PDF')
        dest_filename = os.path.join(dirname, doc.title.string + '.pdf')
        subprocess.call(['convert'] + img_filenames + [dest_filename])

        author, title = re.match('.+/(.+)/(.+)/?', url).groups()
        final_filename = '{}_{}.pdf'.format(author, title)
        os.rename(dest_filename, os.path.join(os.curdir, final_filename))
        print('saved to {}'.format(final_filename))

if __name__ == '__main__':
    download(sys.argv[1])
