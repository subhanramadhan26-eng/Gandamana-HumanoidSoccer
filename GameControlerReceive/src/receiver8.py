#!/usr/bin/env python3.7
#-*- coding:utf-8 -*-

#from __future__ import unicode_literals, print_function

"""
This module shows how the GameController Communication protocol can be used
in python and also allows to be changed such that every team using python to
interface with the GC can utilize the new protocol.

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>
.. moduleauthor:: Robert Kessler <8kessler@informatik.uni-hamburg.de>

"""

import rospy
from std_msgs.msg import String
from protocolgc.msg import GameControllerState

import socket
import time
import logging
import argparse
import sys

# Requires construct==2.5.3
from construct import Container, ConstError
from gamestate8 import GameState, ReturnData, GAME_CONTROLLER_RESPONSE_VERSION, TeamInfo


logger = logging.getLogger('game_controller')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
logger.addHandler(console_handler)

DEFAULT_LISTENING_HOST = '255.255.255.255'
GAME_CONTROLLER_LISTEN_PORT = 3838
GAME_CONTROLLER_ANSWER_PORT =3838

TEAM = 10 #ID KAMPUS
PLAYER = 1 #NOMOR ROBOT
JERSEY = ""
KICKOFF = False
TEAMS_INDEX = PLAYERS_INDEX = 0

if PLAYER == 1:
    NAME = "GANDA"
elif PLAYER == 2:
    NAME = "DAMA"
elif PLAYER == 3:
    NAME = "MANA"

#Parse berguna untuk memberi masukan melalui cmd
# parser = argparse.ArgumentParser()
# parser.add_argument('--team', type=int, default=TEAM, help="team ID, default is 1")#id tim kampus
# parser.add_argument('--player', type=int, default=PLAYER, help="player ID, default is 1")#id robot berapa
# #parser.add_argument('--goalkeeper', action="store_true", help="if this flag is present, the player takes the role of the goalkeeper")


class GameStateReceiver:
    """ This class puts up a simple UDP Server which receives the
    *addr* parameter to listen to the packages from the game_controller.

    If it receives a package it will be interpreted with the construct data
    structure and the :func:`on_new_gamestate` will be called with the content.

    After this we send a package back to the GC """
    count = 0
    # JERSEY = "magenta"
    def __init__(self, team, player, addr=(DEFAULT_LISTENING_HOST, GAME_CONTROLLER_LISTEN_PORT), answer_port=GAME_CONTROLLER_ANSWER_PORT):
        # Information that is used when sending the answer to the game controller
        self.team = team
        self.player = player
        self.man_penalize = True
        #self.is_goalkeeper = is_goalkeeper

        # The address listening on and the port for sending back the robots meta data
        self.addr = addr
        self.answer_port = answer_port

        # The state and time we received last form the GC
        self.state = None
        self.time = None

        # The socket and whether it is still running
        self.socket = None
        self.running = True

        self._open_socket()

    def _open_socket(self):
        """ Erzeugt das Socket """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.addr)
        self.socket.settimeout(1)
        self.socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#, socket.IPPROTO_UDP)
        self.socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def receive_forever(self):
        """ Waits in a loop that is terminated by setting self.running = False """
        while self.running:
            try:
                self.receive_once()
            except IOError as e:
                logger.debug("Fehler beim Senden des KeepAlive: " + str(e))
    

    def receive_once(self):
        """ -Menerima paket data
            -Kemudian menguraikan data tersebut
            -Kemudian memanggil on_new_gamestate
            -Mengembalikan data ke GC """
        try:
            data, peer = self.socket.recvfrom(GameState.sizeof())
            if len(data) == GameState.sizeof():
                GameStateReceiver.count +=1
                print (f'===={GameStateReceiver.count}!GANDAMANA GAMECONTROLLER STATE!{GameStateReceiver.count}====')
                #print(f"ini length data : {len(data)}")
                
                # .parse = menguraikan paket binary dari GC menjadi bisa dibaca menggunakan gamestate
                parsed_state = GameState.parse(data)
                # state = paket yang telah diuraikan
                self.state = parsed_state
                self.time = time.time()
                # memanggil objek yang betugas mengolah atau mmengatur state
                self.on_new_gamestate(self.state)
                # Menjawab Game Controller
                self.answer_to_gamecontroller(peer)    
        except AssertionError as ae:
            logger.error(ae.message)
        except socket.timeout:
            logger.warning("Socket timeout")
            print("coba")
        except ConstError:
            logger.warning("Parse Error: Probably using an old protocol!")
        except Exception as e:
            logger.exception(e)
            pass

    def answer_to_gamecontroller(self, peer):
        """ Sends a life sign to the game controller """
        return_message = 0 if self.man_penalize else 2
        #if self.is_goalkeeper:
        #    return_message = 3

        data = Container(
            header=b"RGrt",
            version=GAME_CONTROLLER_RESPONSE_VERSION,
            team=self.team,
            player=self.player,
            message=return_message)
        try:
            destination = peer[0], GAME_CONTROLLER_ANSWER_PORT
            self.socket.sendto(ReturnData.build(data), destination)
        except Exception as e:
            logger.log("Network Error: %s" % str(e))

    def on_new_gamestate(self, state):
        global JERSEY, KICKOFF, TEAMS_INDEX, PLAYERS_INDEX
        PLAYERS_INDEX = PLAYER - 1 #menentukan robot berapa
        #Determain our jersey color
        if state.teams[1].team_number == TEAM:
            TEAMS_INDEX = 1 #MAGENTA
        else :
            TEAMS_INDEX = 0 #CYAN
        JERSEY = state.teams[TEAMS_INDEX].team_color
        #Determain who take the kick off
        if state.kick_of_team == JERSEY :
            KICKOFF = True
        else: 
            KICKOFF = False
        
        print(f"Gandamana Player Name  : {NAME} (ROBOT{PLAYER})")
        print(f"Gandamana Score        : {state.teams[TEAMS_INDEX].score}")
        print(f"Gandamana Jersey Color : {JERSEY}")
        print(f"Gandamana 'Kick-off'   : {KICKOFF} ")
        print(f"Gandamana State        : {state.game_state}")
        print(f"Gandamana Pinalty      : {state.teams[TEAMS_INDEX].players[PLAYERS_INDEX]}")
        # print(state)
        info = GameControllerState()
        info.ID_Robot = PLAYER
        info.jersey = JERSEY
        info.kickoff = KICKOFF
        info.state = state.game_state
        info.penalty = state.teams[TEAMS_INDEX].players[PLAYERS_INDEX].penalty
        info.penalty_time = state.teams[TEAMS_INDEX].players[PLAYERS_INDEX].secs_till_unpenalized
        pub.publish(info)
        print("__________________________________________")
        # print("\n")
        #return state.game_state
       

    def get_last_state(self):
        return self.state, self.time

    def get_time_since_last_package(self):
        return time.time() - self.time

    def stop(self):
        self.running = False

    def set_manual_penalty(self, flag):
        self.man_penalize = flag


if __name__ == '__main__':
    try:
        rospy.init_node('GameController')
        rate = rospy.Rate(1)
        # args = parser.parse_args(sys.argv[1:])
        rec = GameStateReceiver(TEAM, PLAYER)#(team = args.team, player = args.player)#, is_goalkeeper = args.goalkeeper)
        #print (rec)
        pub = rospy.Publisher('/DEWO/GameController/allstate', GameControllerState, queue_size=1)
        while not rospy.is_shutdown():
            rec.receive_once()  
    except rospy.ROSInterruptException:
        pass
