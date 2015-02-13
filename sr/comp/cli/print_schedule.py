# -*- coding: utf-8 -*-

from sr.comp.comp import SRComp

import argparse
import os.path
import sys
from reportlab.pdfgen import canvas

class ScheduleGenerator(object):
    def __init__(self, target, arenas, state):
        self.canvas = canvas.Canvas(target)
        self.state = state
        self.width = 595
        self.height = 842
        self.margin = 40
        self.page_number = 0
        self.arenas = arenas
        self.columns = 2 + 4*len(arenas)
        self.start_page()

    def start_page(self):
        self.row_height = 815
        if self.page_number != 0:
            self.canvas.showPage()
        self.page_number += 1

        self.draw_header()
        self.draw_footer()
        self.draw_vertical_bars()
        self.draw_column_headings()

    def draw_header(self):
        self.canvas.setFont("Helvetica", 12)
        self.canvas.drawCentredString(self.width*0.5, 825, "Match Schedule")

    def draw_footer(self):
        self.canvas.setFont("Helvetica", 8)
        self.canvas.drawCentredString(self.width*0.5, 10,
                "Page {} • Generated from state {}".format(self.page_number,
                                                           self.state[:7]))

    def draw_vertical_bars(self):
        for x in (140, 368):
            self.canvas.line(x, 20, x, 825)

    def draw_column_headings(self):
        headings = ['**Number**', '**Time**']
        for arena, config in self.arenas.items():
            headings += ['**{}**'.format(config.display_name), '', '', '']
        self.add_line(headings)

    def add_line(self, line):
        if len(line) != self.columns:
            raise ValueError("Incorrect column count")
        for i, cell in enumerate(line):
            if cell.startswith('**') and cell.endswith('**'):
                cell = cell[2:-2]
                self.canvas.setFont("Helvetica-Bold", 10)
            else:
                self.canvas.setFont("Helvetica", 9)
            self.canvas.drawCentredString(self.margin + i * (self.width - 2*self.margin) / (self.columns - 1),
                                          self.row_height, cell)
        self.canvas.line(self.margin*0.7, self.row_height - 3.5,
                         self.width-(self.margin*0.7), self.row_height - 3.5)
        self.row_height -= 12

    def generate(self, competition, highlight=()):
        def display(team):
            if team is None:
                return '–'
            if team in highlight:
                return '**' + team + '**'
            else:
                return team

        for n, match in enumerate(competition.schedule.matches):
            cells = ['', '']
            for arena in self.arenas:
                match_arena = match.get(arena)
                if match_arena is not None:
                    cells += [display(team) for team in match_arena.teams]
                    cells[0] = str(match_arena.num)
                    cells[1] = str(match_arena.start_time.strftime('%a %H:%M'))
                else:
                    cells += ['–', '–', '–', '–']
            if any(x.startswith('**') for x in cells):
                cells[0] = '**' + cells[0] + '**'
            self.add_line(cells)
            if n % 66 == 65:
                self.start_page()

    def write(self):
        self.canvas.save()

def command(settings):
    comp = SRComp(os.path.realpath(settings.compstate))

    generator = ScheduleGenerator(settings.output,
                                  arenas=comp.arenas,
                                  state=comp.state)
    generator.generate(comp,
                       highlight=settings.highlight if settings.highlight is not None else ())
    generator.write()

def add_subparser(subparsers):
    parser = subparsers.add_parser('print-schedule',
                                   help='print a shepherding sheet')
    parser.add_argument('compstate', help='competition state repository')
    parser.add_argument('-o', '--output', help='output file',
                        type=argparse.FileType('wb'),
                        required=True)
    parser.add_argument('-H', '--highlight', help='highlight specific team\'s matches',
                        nargs='+')
    parser.set_defaults(func=command)
