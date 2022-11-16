import sys, os
if os.path.dirname(__file__) not in sys.path: sys.path.insert(0, os.path.dirname(__file__))
if os.path.join(os.path.dirname(__file__), 'loader') not in sys.path: sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'loader')) #get sys.path set up to run from anywheres
import dungeon_settings
import dungeons_game
import logger #imports (dungeon_settings is actually not needed yet... TODO: comment it/figure out a use)

def parse_options():
    return None #no options yet

def main():
    options = parse_options() #parse the options
    logger.info('Starting Game.') #starting the game now
    dungeons_game.main(options) #pass the options to dungeons_game (which does pretty much everything, but weird logs pop up if we run it directly)

if __name__ == '__main__':
    main() #run the game
