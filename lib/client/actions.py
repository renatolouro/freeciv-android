# Copyright (C) 2011 Michal Zielinski (michal@zielinscy.org.pl)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import freeciv

import client

ACTIVITY_IDLE = 0
ACTIVITY_POLLUTION = 1
ACTIVITY_ROAD = 2
ACTIVITY_MINE = 3
ACTIVITY_IRRIGATE = 4
ACTIVITY_FORTIFIED = 5
ACTIVITY_FORTRESS = 6
ACTIVITY_SENTRY = 7
ACTIVITY_RAILROAD = 8
ACTIVITY_PILLAGE = 9
ACTIVITY_GOTO = 10
ACTIVITY_EXPLORE = 11
ACTIVITY_TRANSFORM = 12
# ACTIVITY_UNKNOWN = 13
ACTIVITY_AIRBASE = 14
ACTIVITY_FORTIFYING = 15
ACTIVITY_FALLOUT = 16
# ACTIVITY_PATROL_UNUSED = 17
ACTIVITY_BASE = 18

ACTIVITY_DISBAND = 1001
ACTIVITY_WAIT = 1002
ACTIVITY_DONE = 1003
ACTIVITY_ADD_TO_CITY = 1004
ACTIVITY_BUILD_CITY = 1005
ACTIVITY_HELP_BUILD_WONDER = 1006
ACTIVITY_PARADROP = 1007
ACTIVITY_CHANGE_HOMECITY = 1008
ACTIVITY_LOAD = 1009
ACTIVITY_UNLOAD = 1010

activities = dict( (k,v) for k,v in globals().items() if k.startswith('ACTIVITY_' ) )
activity_names = dict( (v, k) for k,v in activities.items() )

action_names = {
    'done': 'no orders',
    'fortyfing': 'fortify',
    'explore': 'auto explore',
}

class Unit(object):
    def __init__(self, unit_id):
        self.unit_id = unit_id
    
    def get_properties(self):
        return freeciv.func.get_unit_properties(self.unit_id)
    
    def iter_actions(self):
        id, tileid, city, terrain_name = self.get_properties()
        
        yield ACTIVITY_GOTO
        yield ACTIVITY_DISBAND
        yield ACTIVITY_WAIT
        yield ACTIVITY_DONE
        
        if freeciv.func.can_unit_add_or_build_city(id):
            if city:
                yield ACTIVITY_ADD_TO_CITY
            else:
                yield ACTIVITY_BUILD_CITY
        
        if freeciv.func.unit_can_help_build_wonder_here(id):
            yield ACTIVITY_HELP_BUILD_WONDER
        
        if freeciv.func.can_unit_paradrop(id):
            yield ACTIVITY_PARADROP
        
        if freeciv.func.can_unit_change_homecity(id):
            yield ACTIVITY_CHANGE_HOMECITY
        
        # TODO: unload transporter
        
        #if freeciv.func.units_can_load(id):
        #    yield ACTIVITY_LOAD
        #
        #if freeciv.func.units_can_unload(id):
        #    yield ACTIVITY_UNLOAD
        
        # TODO: wakup others
        # TODO: autosettlers
        # TODO: nuke
        # TODO: airlift
        
        
        standard_activities = [
            ACTIVITY_RAILROAD,
            ACTIVITY_ROAD,
            ACTIVITY_IRRIGATE,
            ACTIVITY_MINE,
            ACTIVITY_TRANSFORM,
            #BASE_GUI_FORTRESS,
            ACTIVITY_FORTIFYING,
            ACTIVITY_POLLUTION,
            ACTIVITY_FALLOUT,
            ACTIVITY_SENTRY,
            ACTIVITY_PILLAGE,
            ACTIVITY_EXPLORE
        ]
        
        for a_ident in standard_activities:
            if freeciv.func.can_unit_do_activity(id, a_ident):
                yield a_ident
    
    def get_actions(self):
        return [ (ident, self.get_action_name(ident), self.get_action_time(ident)) for ident in self.iter_actions() ]
    
    def get_action_time(self, type):
        if type > 1000:
            return 0
        else:
            return freeciv.func.tile_activity_time(type, self.get_tile())
    
    def get_action_name(self, type):
        def_name = activity_names[type][len('ACTIVITY_'):].lower().replace('_', ' ')
        if def_name in action_names:
            return action_names[def_name]
        return def_name
    
    def get_tile(self):
        id, tileid, city, terrain_name = self.get_properties()
        return tileid
    
    def get_terrain_name(self):
        id, tileid, city, terrain_name = self.get_properties()
        return terrain_name
    
    def get_name(self):
        return freeciv.func.get_unit_name(self.unit_id)
    
    def focus(self):
        freeciv.func.request_new_unit_activity(self.unit_id, ACTIVITY_IDLE)
        freeciv.func.set_unit_focus(self.unit_id)
    
    def perform_activity(self, ident):
        if ident == ACTIVITY_GOTO:
            freeciv.func.key_unit_goto()
        elif ident == ACTIVITY_ROAD:
            freeciv.func.key_unit_road()
        elif ident == ACTIVITY_RAILROAD:
            freeciv.func.key_unit_road()
        elif ident == ACTIVITY_BUILD_CITY:
            freeciv.func.key_unit_build_city()
        #elif ident == ACTIVITY_:
        #    freeciv.func.key_unit_trade_route()
        elif ident == ACTIVITY_IRRIGATE:
            freeciv.func.key_unit_irrigate()
        elif ident == ACTIVITY_MINE:
            freeciv.func.key_unit_mine()
        elif ident == ACTIVITY_TRANSFORM:
            freeciv.func.key_unit_transform()
        elif ident == ACTIVITY_FORTRESS:
            freeciv.func.key_unit_fortress()
        elif ident == ACTIVITY_FORTIFYING:
            freeciv.func.key_unit_fortify()
        elif ident == ACTIVITY_AIRBASE:
            freeciv.func.key_unit_airbase()
        elif ident == ACTIVITY_POLLUTION:
            freeciv.func.key_unit_pollution()
        elif ident == ACTIVITY_PARADROP:
            freeciv.func.key_unit_paradrop()
        elif ident == ACTIVITY_FALLOUT:
            freeciv.func.key_unit_fallout()
        elif ident == ACTIVITY_SENTRY:
            freeciv.func.key_unit_sentry()
        elif ident == ACTIVITY_PILLAGE:
            freeciv.func.key_unit_pillage()
        #elif ident == ACTIVITY_:
        #    freeciv.func.key_unit_homecity()
        #elif ident == ACTIVITY_:
        #    freeciv.func.key_unit_unload_all()
        elif ident == ACTIVITY_WAIT:
            freeciv.func.key_unit_wait()
        elif ident == ACTIVITY_DONE:
            freeciv.func.key_unit_done()
        elif ident == ACTIVITY_DISBAND:
            freeciv.func.key_unit_disband()
        else:
            print 'Unsupported action ', ident

def get_unit_in_focus():
    units = freeciv.func.get_units_in_focus()
    if units:
        return Unit(units[0])
    else:
        return None

@freeciv.register
def update_menus():
    units = freeciv.func.get_units_in_focus()
    if not units:
        client.client.disable_menus()
    else:
        first_unit = Unit(units[0])
        client.client.update_menus(first_unit)