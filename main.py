import os
import time
import math
import random
import multiprocessing
from threading import Thread
from tqdm import tqdm
from urllib import request, error
from utils import wgs_to_tile

USER_AGENT = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.62'
]

TDT_KEY = [
    '98390210b003e812656026ef694bbbee',
    'e7baa690c03a5ed235a671ec2cce4123',
    '6f2d1fdbd539ee0c34a7adbe0cf31174',
    'ead285c52abf82507e0472e092a5cded',
    'bfd6908081d54d7ae6ebde9a003aab0b',
    '53375a007eafae52264f34444de11922',
    'a3bac08f4e22fb64a082d9cc69808bc2',
    '7666c190624c3192a9ff430e570dda26',
    'fa100ee8c3113e17317a119198ec3166',
    '83570f7bc2f2a642f30362542eec6882'
]


def save_img(tile):
    """
    保存瓦片文件
    :param tile: url 和文件名 {'url': '', 'file': ''}
    :return:
    """
    url = tile['url']
    file_path = tile['file']
    req = request.Request(url)
    req.add_header('User-Agent', random.choice(USER_AGENT))

    try:
        data = request.urlopen(req, timeout=5).read()
        file = open(file_path, 'wb')
        file.write(data)
        file.close()
    except error.HTTPError as he:
        print(he)
        time.sleep(30)
    except Exception as e:
        print(e)


class Downloader(Thread):
    # multiple threads downloader
    def __init__(self, index, count, tiles):
        # index represents the number of threads
        # count represents the total number of threads
        # tiles represents the list of tiles need to be downloaded
        super().__init__()
        self.tiles = tiles
        self.index = index
        self.count = count

    def run(self):
        for i, tile in enumerate(self.tiles):
            if i % self.count != self.index:
                continue

            # 概率分布睡眠
            secs = random.normalvariate(0, 0.5)
            secs = math.fabs(secs)
            time.sleep(secs)
            save_img(tile)


def get_tiles(extent, zoom, url, root_path):
    """
    获取瓦片
    :param extent:
    :param zoom:
    :param root_path:
    :param url:
    :return:
    """
    pos1x, pos1y = wgs_to_tile(extent[0], extent[1], zoom)
    pos2x, pos2y = wgs_to_tile(extent[2], extent[3], zoom)
    lenx = pos2x - pos1x + 1
    leny = pos2y - pos1y + 1
    print('瓦片总数：{x} X {y}'.format(x=lenx, y=leny))

    if not os.path.exists(root_path):
        os.mkdir(root_path)
    # 创建zoom文件夹
    zoom_path = os.path.join(root_path, str(zoom))
    if not os.path.isdir(zoom_path):
        os.mkdir(zoom_path)
    tiles = []
    for x in tqdm(range(pos1x, pos1x + lenx), desc='瓦片地址'):
        # 创建x文件夹
        x_path = os.path.join(zoom_path, str(x))
        if not os.path.isdir(x_path):
            os.mkdir(x_path)
        for y in range(pos1y, pos1y + leny):
            # y文件
            file_name = os.path.join(x_path, str(y) + '.png')
            if not os.path.exists(file_name):
                tiles.append({
                    'url': url.format(z=zoom, x=x, y=y,
                                      key=random.choice(TDT_KEY),
                                      subdomain=random.randint(0, 7)),
                    'file': file_name
                })
    return tiles


def download_tiles(tiles, multi=4):
    if multi < 1 or multi > 20 or not isinstance(multi, int):
        raise Exception("multi of Downloader should be int and between 1 to 20.")
    tasks = [Downloader(i, multi, tiles) for i in range(multi)]
    for i in tasks:
        i.start()
    for i in tasks:
        i.join()


def main(extent, zoom, url, root_path):
    """
    :param extent: 下载范围
    :param zoom: zoom
    :param root_path: 下载瓦片根目录
    :param url: url
    :return:
    """
    tiles = get_tiles(extent=extent, zoom=zoom, url=url, root_path=root_path)
    print('获取瓦片下载地址完成，待下载瓦片数量：{len}'.format(len=len(tiles)))
    if len(tiles) > 0:
        tiles_group = [tiles[i:i + math.ceil(len(tiles) / multiprocessing.cpu_count())]
                       for i in range(0, len(tiles), math.ceil(len(tiles) / multiprocessing.cpu_count()))]

        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        with tqdm(total=len(tiles_group), desc='瓦片下载') as t:
            for i, x in enumerate(pool.imap(download_tiles, tiles_group)):
                t.update()
        pool.close()
        pool.join()
        print('瓦片下载完成')
    else:
        print('当前瓦片已下载完成，无需重复下载')


if __name__ == '__main__':
    start_time = time.time()
    # [-180, 90, 180, -90]
    # [73.536163, 53.558094, 135.084259, 7.397329]
    # [105.317233, 32.203410, 110.158904, 28.164785]

    tdt_img_url = ('https://t{subdomain}.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0'
                   '&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles'
                   '&TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk={key}')

    main(extent=[105.317233, 32.203410, 110.158904, 28.164785],
         zoom=6,
         url=tdt_img_url,
         root_path='E:\\test')
    end_time = time.time()
    print('总耗时： {:.2f}秒'.format(end_time - start_time))
