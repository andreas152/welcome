#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(filename)s : %(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import sys
import getopt

BASEDIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
app = Flask(__name__)

root = BASEDIR
port = 8080

'''
@app.route('/', methods=['GET'])
def main(path=None):
    logger.info(f'{BASEDIR}/index.html')
    with open(os.path.join(BASEDIR, 'index.html'), 'r') as fp:
        return fp.read(), 200
'''

@app.route('/', methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def assets(path=''):
    path_elems = [elem for elem in path.split('/') if elem]
    logger.info(path_elems)

    if len(path_elems) > 0 and len(path_elems) <= 2 and path_elems[-1] == 'components':
        components_root = f'{root}/{"/".join([elem for elem in path_elems[:path_elems.index("components")+1]])}'
        logger.info(components_root)
        if os.path.exists(components_root) and os.path.isdir(components_root):
            _, _, files = next(os.walk(components_root))
            return {'files': files}, 200, {'Content-type': 'application/json'}
        else:
            # return 'Not found', 404
            return {'files': []}, 200, {'Content-type': 'application/json'}

    for idx in range(2):
        if len(path_elems) > idx and path_elems[idx] in ('css', 'js', 'components'):
            content_path = f'{root}/{"/".join([elem for elem in path_elems[:idx+2]])}'
            logger.info(content_path)
            return send_from_directory(f'{root}/{"/".join(path_elems[:idx+1])}', path_elems[idx+1], as_attachment=False), 200 
    
    content_path = f'{root}/{"/".join(path_elems)}'
    logger.info(f'{content_path} {os.path.isfile(content_path)}')
    
    if os.path.exists(content_path) and os.path.isfile(content_path):
        return send_from_directory(f'{root}/{"/".join(path_elems[:-1])}', path_elems[-1], as_attachment=False), 200 

    #elif content_path.endswith('.md') or path in ('config.json', 'config.yaml') or path_elems[0] in ('images,'):
    #    return 'Not found', 404
    
    if os.path.exists(content_path) and os.path.isdir(content_path) or os.path.exists(f'{content_path}.md'):
        content_path = f'{root}{"/" + path_elems[0] if len(path_elems) > 0 else ""}/index.html'
        logger.info(content_path)
        with open(content_path, 'r') as fp:
            return fp.read(), 200
    
    content_path = f'{root}/index.html'
    if os.path.exists(content_path):
        logger.info(content_path)
        with open(content_path, 'r') as fp:
            return fp.read(), 200

    logger.info(content_path)

    return 'Not found', 404

def usage():
    print(f'{sys.argv[0]} [hl:r:p:]')
    print(f'   -h --help        Print help message')
    print(f'   -l --loglevel    Logging level (default=warning)')
    print(f'   -r --root        Content root (default={root})')
    print(f'   -p --port        Use port (default={port})')

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hl:r:p:', ['help', 'loglevel', 'root', 'port'])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ('-l', '--loglevel'):
            loglevel = a.lower()
            if loglevel in ('error',): logger.setLevel(logging.ERROR)
            elif loglevel in ('warn','warning'): logger.setLevel(logging.INFO)
            elif loglevel in ('info',): logger.setLevel(logging.INFO)
            elif loglevel in ('debug',): logger.setLevel(logging.DEBUG)
        elif o in ('-r', '--root'):
            root = os.path.abspath(a)
        elif o in ('-p', '--port'):
            port = int(a)
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, 'unhandled option'

    logger.info(f'Serving content from {root}')
    app.run(debug=True, host='0.0.0.0', port=port)