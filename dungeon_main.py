import sys
import os
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))
if os.path.join(os.path.dirname(__file__), 'loader') not in sys.path:
    # get sys.path set up to run from anywheres
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'loader'))
import dungeon_settings
import dungeon_logger as logger


def parse_options():
    ret = {'path': dungeon_settings.BASEPATH}
    options = sys.argv[1:]
    for index, option in enumerate(options):
        if option == '-path' and index != len(options)-1:
            ret['path'] = options[index+1]
    return ret


def main():
    options = parse_options()  # parse the options
    dungeon_settings.load(options['path'])
    logger.info('Starting Game.')  # starting the game now
    # pass the options to dungeon_game (which does pretty much everything, but weird logs pop up if we run it directly)
    import dungeon_game
    dungeon_game.main(options)


if __name__ == '__main__':
    main()  # run the game
