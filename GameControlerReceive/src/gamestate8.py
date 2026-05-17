#!/usr/bin/env python
# -*- coding:utf-8 -*-

from construct import Byte, Struct, Enum, Bytes, Const, Array, Int16ul, Int32ul, PaddedString, Flag, Int16sl

Short = Int16ul

RobotInfo = "robot_info" / Struct(
    # define NONE                        0
    #define HL_BALL_MANIPULATION                30
    #define HL_PHYSICAL_CONTACT                 31
    #define HL_ILLEGAL_ATTACK                   32
    #define HL_ILLEGAL_DEFENSE                  33
    #define HL_PICKUP_OR_INCAPABLE              34
    #define HL_SERVICE                          35
    "penalty" / Enum(Byte, 
                     Play = 0,
                     Ball_Manipulation = 1,
                     Physical_Contact = 2,
                     Illegal_Attack = 3,
                     Illegal_Defence = 4,
                     Pickup = 5,
                     Service = 6,
                     Substitute = 7,
                     Not_Play = 14),
    "secs_till_unpenalized" / Byte,
    #"number_of_warnings" / Byte,
    #"number_of_yellow_cards" / Byte,
    #"number_of_red_cards" / Byte,
    #"goalkeeper" / Flag
)

TeamInfo = "team" / Struct(
    "team_number" / Byte,
    "team_color" / Enum(Byte,
                        #BLUE=0,
                        CYAN=0,
                       # RED=1,
                        MAGENTA=1
                        #YELLOW=2,
                        #BLACK=3,
                        #WHITE=4,
                        #GREEN=5,
                        #ORANGE=6,
                        #PURPLE=7,
                        #BROWN=8,
                        #GRAY=9
                        ),
    "score" / Byte,
    "penalty_shot" / Byte,  # penalty shot counter
    "single_shots" / Short,  # bits represent penalty shot success
    #"coach_sequence" / Byte,
    "coach_message" / PaddedString(40, 'utf8'),
    "coach" / RobotInfo,
    "players" / Array(11, "robot_info"/RobotInfo)
)

GameState = "gamedata" / Struct(
    "header" / Const(b'RGme'),
    "version" / Const(8, Byte),
    "packet_number" / Byte,
    "players_per_team" / Byte,
    #"game_type" / Byte,
    "game_state" / Enum(Byte,
                        STATE_INITIAL=0,
                        # auf startposition gehen
                        STATE_READY=1,
                        # bereithalten
                        STATE_SET=2,
                        # spielen
                        STATE_PLAYING=3,
                        # spiel zu ende
                        STATE_FINISHED=4
                        ),
    "first_half" / Flag,
    "kick_of_team" / Enum(Byte, CYAN =0, MAGENTA = 1),
    "secondary_state" / Enum(Byte,
                             STATE_NORMAL=0,
                             STATE_PENALTYSHOOT=1,
                             STATE_OVERTIME=2,
                             STATE_TIMEOUT=3,
                             #STATE_DIRECT_FREEKICK=4,
                             #STATE_INDIRECT_FREEKICK=5,
                             #STATE_PENALTYKICK=6,
                             #STATE_CORNERKICK=7,
                             #STATE_GOALKICK=8,
                             #STATE_THROWIN=9,
                             DROPBALL=2,
                             #UNKNOWN=255
                             ),
    #"secondary_state_info" / Bytes(4),
    "drop_in_team" / Flag,
    "drop_in_time" / Short,
    "seconds_remaining" / Short,
    "secondary_seconds_remaining" / Short,
    "teams" / Array(2, "team" / TeamInfo)
)

GAME_CONTROLLER_RESPONSE_VERSION = 2

ReturnData = Struct(
    "header" / Const(b"RGrt"),
    "version" / Const(2, Byte),
    "team" / Byte,
    "player" / Byte,
    "message" / Byte
)
