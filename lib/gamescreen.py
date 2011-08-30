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

import ui
import client
import pygame
import pygame.gfxdraw
import functools

from client import freeciv

import citydlg
import gamemenu

SELECT_POPUP = 0

class ScreenClient(client.Client):
    def __init__(self):
        client.Client.__init__(self)
        self.init_ui()
    
    def init_ui(self):
        self.ui = ScreenWidget(self)
    
    #def console_line(self, line):
    #    self.ui.console.line(line)
    
    def update_meswin(self, lines):
        self.ui.console.clear()
        for line, attrs, tile in lines:
            self.ui.console.line(line)
    
    def popup_city_dialog(self, city):
        dialog = citydlg.Dialog(self, city)
        ui.set(dialog.ui)
    
    def overview_size_changed(self, w, h):
        self.ui.resize_left_pane(self.ui.overview.size[0])
    
    def update_menus(self, unit):
        actions = unit.get_actions()
        self.ui.menu.update(actions)
    
    def disable_menus(self):
        self.ui.menu.update(None)
    
    def popup_unit_select_dialog(self, units):
        def focus(unit):
            unit.focus()
            ui.back()
        
        panel = ui.LinearLayoutWidget()
        for unit in units:
            name = unit.get_name()
            callback = functools.partial(focus, unit)
            panel.add(ui.Label(name, callback))
        ui.set(ui.ScrollWrapper(panel))

class ScreenWidget(ui.HorizontalLayoutWidget):
    def __init__(self, client):
        super(ScreenWidget, self).__init__()
        self.client = client
        
        self.map = MapWidget(client)
        self.overview = OverviewWidget(client)
        self.console = ConsoleWidget(client)
        self.menu = gamemenu.Menu(client)
        self.end_turn_button = ui.Button('End turn', self.client.end_turn)
        
        self.left_panel = ui.LinearLayoutWidget(spacing=0)
        self.map_wrapper = ui.AbsoluteLayoutWidget()
        
        self.add(self.left_panel)
        self.add(self.map_wrapper)
        
        self.map_wrapper.add(self.map, (0, 0))
        self.map_wrapper.add(self.menu, (0, 0), align=ui.BOTTOM)
        
        self.left_panel.add(self.overview)
        self.left_panel.add(self.console.scroll)
        self.left_panel.add(self.end_turn_button)
        
        # key_end_turn()
        
        self.focus = self.map
    
    def resize_left_pane(self, width):
        self.console.width = width
        self.console.scroll.width = width
        self.console.scroll.height = 100
    
    def tick(self):
        self.map.size = ui.screen_width - self.overview.size[0], ui.screen_height
        self.client.tick()
        super(ScreenWidget, self).tick()
    
    def back(self):
        self.map.back()

class OverviewWidget(object):
    def __init__(self, client):
        self.client = client
        self.scale_width = 150
    
    @property
    def size(self):
        w, h = self.client.get_overview_size()
        ratio = h / float(w)
        return (self.scale_width, int(ratio * self.scale_width))
    
    def tick(self):
        pass
    
    def event(self, ev):
        pass
    
    def draw(self, surf, pos):
        self.client.draw_overview(surf, pos, scale=self.size)
        pygame.draw.rect(surf, (255,255,255), pos + self.size, 1)

class ConsoleWidget(ui.LinearLayoutWidget):
    def __init__(self, client):
        super(ConsoleWidget, self).__init__(spacing=0)
        self.client = client
        self.width = 0
        self.scroll = ConsoleScrollWrapper(self)
    
    @property
    def size(self):
        return (self.width, self._size[1])
    
    def line(self, text):
        self.add(ui.Label(text, font=ui.consolefont))
    
    def clear(self):
        self.items = []
    
    def draw(self, surf, pos):
        #clip = surf.get_clip()
        #surf.set_clip(pos + self._size)
        pygame.gfxdraw.box(surf, pos + self._size, (255, 255, 255, 170))
        super(ConsoleWidget, self).draw(surf, pos)
        #surf.set_clip(clip)
    
    def event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN:
            myabspos = ui._subpoints(ev.abs_pos, ev.pos)
            ui.add_overlay(self.scroll, myabspos)
        elif ev.type == pygame.MOUSEBUTTONUP:
            if self.scroll in ui.overlays:
                ui.overlays.remove(self.scroll)

class ConsoleScrollWrapper(ui.ScrollWrapper):
    def get_clip(self, pos):
        return pos + (self.item._size[0], self.size[1])
    
    def canceled_event(self, event):
        self.item.event(event)

class MapWidget(object):
    def __init__(self, client):
        self.client = client
        self.last_size = (0, 0)
        self.size = (0, 0)
        
        self.last_recentered_at = None
        self.start_drag = None
        self.last_drag_pos = None
        self.was_dragged = False
    
    def tick(self):
        pass
    
    def draw(self, surf, pos):
        if self.size != self.last_size:
            self.client.set_map_size(self.size)
            self.last_size = self.size
        
            self.client.update_map_canvas_visible()
        
        self.client.draw_map(surf, pos)
    
    def back(self):
        self.client.key_event(pygame.KEYDOWN, pygame.K_ESCAPE)
    
    def event(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            if self.start_drag:
                if not self.was_dragged:
                    x, y = ev.pos
                    ox, oy = self.start_drag
                    dist = ((x - ox)**2 + (y - oy)**2) ** 0.5
                    if dist > 15:
                        self.was_dragged = True
                        #print 'was_dragged', dist
                if self.was_dragged:
                    self.drag(ev.pos)
                    return
            self.client.mouse_motion(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            x, y = ev.pos
            if ev.button == 3:
                self.recenter_at(x, y)
            else:
                #print 'start_drag'
                self.start_drag = ev.pos
        elif ev.type == pygame.MOUSEBUTTONUP:
            if self.was_dragged:
                self.drag(ev.pos)
                self.was_dragged = False
            elif ev.button == 1:
                x, y = ev.pos
                freeciv.func.action_button_pressed(x, y, SELECT_POPUP)
            self.start_drag = None
            self.last_drag_pos = None
        elif ev.type in (pygame.KEYDOWN, pygame.KEYUP):
            self.client.key_event(ev.type, ev.key)
    
    def recenter_at(self, x, y):
        self.last_recentered_at = freeciv.func.canvas_pos_to_nearest_tile_id(x, y)
        freeciv.func.recenter_button_pressed(x, y)
    
    def drag(self, pos):
        if not self.last_drag_pos:
            self.last_drag_pos = self.start_drag
        delta = ui._subpoints(self.last_drag_pos, pos)
        x, y = freeciv.func.get_map_view_origin()
        #print 'drag', x + delta[0], y + delta[1]
        freeciv.func.set_mapview_origin(x + delta[0], y + delta[1])
        self.last_drag_pos = pos

def init():
    gamemenu.init()