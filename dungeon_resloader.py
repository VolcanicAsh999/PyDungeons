import os
import shutil

path = os.path.join(os.path.dirname(__file__), 'backres')
path2 = os.path.join(os.environ['APPDATA'], '.pydungeons', 'resources')

def check():
    import dungeon_logger as logger
    logger.info('Checking for unavailable/unused resources!', 'ResourceLoader')
    logger.info('Resource path is: ' + path2, 'ResourceLoader')
    count = 0
    for name in os.listdir(path):
        if not os.path.exists(os.path.join(path2, name)):
            if os.path.isdir(os.path.join(path, name)):
                logger.warn('Found directory to add: ' + name, 'ResourceLoader')
                shutil.copytree(os.path.join(path, name), os.path.join(path2, name))
                count += 1
                for i in os.listdir(os.path.join(path, name)):
                    count += 1
                    if os.path.isdir(os.path.join(path, name, i)):
                        for j in os.listdir(os.path.join(path, name, i)):
                            count += 1
                            if os.path.isdir(os.path.join(path, name, i, j)):
                                for k in os.listdir(os.path.join(path, name, i, j)):
                                    count += 1
                                    if os.path.isdir(os.path.join(path, name, i, j, k)):
                                        for l in os.listdir(os.path.join(path, name, i, j, k)):
                                            count += 1
            else:
                shutil.copy(os.path.join(path, name), os.path.join(path2, name))
                count += 1
                logger.warn('Found file to add: ' + name, 'ResourceLoader')
    count2 = 0
    for name in os.listdir(path2):
        if not os.path.exists(os.path.join(path, name)):
            if os.path.isdir(os.path.join(path2, name)):
                logger.warn('Found directory to remove: ' + name, 'ResourceLoader')
                count2 += 1
                for i in os.listdir(os.path.join(path2, name)):
                    count2 += 1
                    if os.path.isdir(os.path.join(path2, name, i)):
                        for j in os.listdir(os.path.join(path2, name, i)):
                            count2 += 1
                            if os.path.isdir(os.path.join(path2, name, i, j)):
                                for k in os.listdir(os.path.join(path2, name, i, j)):
                                    count2 += 1
                                    if os.path.isdir(os.path.join(path2, name, i, j, k)):
                                        for l in os.listdir(os.path.join(path2, name, i, j, k)):
                                            count2 += 1
                shutil.rmtree(os.path.join(path2, name))
            else:
                os.remove(os.path.join(path2, name))
                count2 += 1
                logger.warn('Found file to remove: ' + name, 'ResourceLoader')
    logger.info('Added ' + str(count) + ' files/directories.', 'ResourceLoader')
    logger.info('Removed ' + str(count2) + ' files/directories.', 'ResourceLoader')
