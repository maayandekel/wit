# Upload 170


import os


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def create_activated(path):
    activated_path = os.path.join(path, '.wit/activated.txt')
    with open(activated_path, 'w') as active_file:
        active_file.write('master')


def init():
    home_path = os.getcwd()
    folders = ['.wit', '.wit/images', '.wit/staging_area']
    for folder in folders:
        folder_path = '/'.join([home_path, folder])
        create_folder(folder_path)
    create_activated(home_path)


# init()