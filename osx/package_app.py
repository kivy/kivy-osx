#!/usr/bin/python
# -*- coding: utf-8 -*-
'''package_app

Usage:
    package-app <path_to_app> [--icon=<icon_path> --author=<copyright>\
        --appname=<appname> --source-app=<source_app> --deps=<dep_list>\
        --bundleid=<bundle_id> --displayname=<displayname>\
        --bundlename=<bundle_name> --bundleversion=<bundleversion>\
        --strip=<true_false>]
    package-app -h | --help
    package-app --version

Options:
    -h  --help                      Show this screen.
    --icon=<icon_path>              Path to source icon
                                    [default: data/logo/kivy-icon-512.png].
    --author=<copyright>            Copyright attribution
                                    [default: © 2015 Kivy team].
    --appname=<app_name>            Name of the resulting .app file.
    --source-app=<source_app>       Path to the Kivy.app to use as base
                                    [default: ./Kivy.app].
    --entrypoint=<entrypoint>       Entry point module to your application
                                    [default: main].
    --displayname=<displayname>     Bundle display name of the application.
                                    [default: Kivy].
    --bundleid=<bundleid>           Bundle identifier eg:org.kivy.launcher
                                    [default: org.kivy.launcher].
    --bundlename=<bundle_name>      Bundle name eg: `showcase`
                                    [default: kivy]
    --bundleversion=<version>       Bundle Version eg: 1.2.0
                                    [default: 0.0.1]
    --strip=<True_False>            Greatly reduce app size, by removing a
                                    lot of unneeded files. [default: True].
    --deps=<deplist>                Dependencies list.
'''

__version__ = '0.1'
__author__ = 'the kivy team'

from docopt import docopt
try:
    import sh
except ImportError:
    print('Please install sh `pip install sh --user`')
from os.path import exists, abspath, dirname, join
from subprocess import check_call
from os import walk, unlink
from compileall import compile_dir
from os.path import exists
from subprocess import check_call

try:
    input = raw_input
except NameError:
    pass


def error(message):
    print(message)
    exit(-1)


def bootstrap(source_app, appname, confirm):
    # remove mypackage.app if it already exists
    print('Copy Kivy.app/source.app if it exists')
    if exists(appname):
        print('{} already exists removing it...'.format(appname))
        sh.rm('-rf', appname)

    # check if Kivy.app exists and copy it
    if not exists(source_app):
        error("source app {} doesn't exist")
    print('copying {} to {}'.format(source_app, appname))
    sh.cp('-a', source_app, appname)


def insert_app(path_to_app, appname):
    # insert appname into our source_app
    sh.cp('-a', path_to_app, appname+'/Contents/Resources/myapp')

def cleanup(appname, strip, whitelist=None, blacklist=None):
    if not strip:
        return
    print("stripping app")
    from subprocess import call
    call(["sh", "-x", "cleanup_app.sh" , "./"+appname])
    print("Stripping complete")

def fill_meta(appname, arguments):
    print('Editing info.plist')
    bundleversion = arguments.get('--bundleversion')
    import plistlib
    info_plist = appname+'/Contents/info.plist'
    rootObject = plistlib.readPlist(info_plist)
    rootObject['NSHumanReadableCopyright'] = arguments.get('--author')
    rootObject['Bundle Display Name'] = arguments.get('--displayname')
    rootObject['Bundle Identifier'] = arguments.get('--bundleid')
    rootObject['Bundle Name'] = arguments.get('--bundlename')
    rootObject['Bundle Version'] = arguments.get('--bundleversion')
    plistlib.writePlist(rootObject, info_plist)

def setup_icon(path_to_app, path_to_icon):
    # check icon file
    from subprocess import check_output
    if path_to_icon.startswith('http'):
        print('Downloading ' + path_to_icon)
        check_output(['curl', '-O', '-L', path_to_icon])
        path_to_icon = path_to_icon.split('/')[-1]
    height = check_output(['sips', '-g', 'pixelHeight', path_to_icon])[-5:]
    width = check_output(['sips', '-g', 'pixelHeight', path_to_icon])[-5:]
    if height != width:
        print('The height and width of the image must be same')
        import sys
        sys.exit()

    # icon file is Finder
    sh.command('sips', '-s', 'format', 'icns', path_to_icon, '--out',
        path_to_app + "/Contents/Resources/appIcon.icns")
    print('Icon set to {}'.format(path_to_icon))

def compile_app(appname):
    #check python Versions
    print('Compiling app...')
    py3 = appname + '/Contents/Frameworks/python/3.5.0/bin/python'
    pypath = appname + '/Contents/Resources'
    if exists(py3):
        print('python3 detected...')
        check_call(
            [pypath + '/script -OO -m compileall -b ' + pypath],
            shell=True)
     	print("Remove all __pycache__")
     	check_call(
            ['find -E {} -regex "(.*)\.py" | xargs rm'.format(pypath)],
             shell=True)
     	check_call(
            ['find -E {}/Contents/'.format(appname) +\
             '-name "__pycache__"| xargs rm -rf'],
            shell=True)
    else:
        print('using system python...')
     	check_call(
            [pypath + '/script -OO -m compileall ' + appname],
            shell=True)
     	print("-- Remove all py/pyc")
     	check_call(
            ['find -E {} -regex "(.*)\.pyc" | xargs rm'.format(appname)],
            shell=True)
     	check_call(
            ['find -E {} -regex "(.*)\.py" | xargs rm'.format(appname)],
            shell=True)
    sh.command('mv', pypath + '/myapp', pypath + '/yourapp')

def install_deps(appname, deps):
    print('managing dependencies {}'.format(deps))
    for dep in deps.split(','):
        print('Installing {} into {}'.format(dep, appname))
        check_call(
            (appname + '/Contents/Resources/script -m' +\
             ' pip install --upgrade --force-reinstall ' + dep),
            shell=True)


def main(arguments):
    path_to_app = arguments.get('<path_to_app>')
    source_app = arguments.get('--source_app', dirname(abspath(__file__)) + '/kivy.app')
    confirm = arguments.get('-y')
    appname = arguments.get('--appname')
    if not appname:
        appname = path_to_app.split('/')[-1] + '.app'
    else:
        appname = appname + '.app'
    icon = arguments.get('--icon', appname + '/Contents/Resources/kivy/kivy/data/logo/kivy-icon-512.png')
    strip = arguments.get('--strip', True)
    deps = arguments.get('--deps', [])

    bootstrap(source_app, appname, confirm)
    insert_app(path_to_app, appname)
    install_deps(appname, deps)
    compile_app(appname)
    setup_icon(appname, icon)
    fill_meta(appname, arguments)
    cleanup(appname, strip)
    print("All done!")


if __name__ == '__main__':
    arguments = docopt(__doc__, version='package app {}'.format(__version__))
    print(arguments)
    main(arguments)
