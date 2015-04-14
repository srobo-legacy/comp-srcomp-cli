# -*- coding: utf-8 -*-
import argparse
import yaml


class ScheduleGenerator(object):
    def __init__(self, target, arenas, state):
        from reportlab.pdfgen import canvas

        self.canvas = canvas.Canvas(target)
        self.state = state
        self.width = 595
        self.height = 842
        self.margin = 50
        self.page_number = 0
        self.arenas = arenas
        self.columns = 2 + 4*len(arenas)

    def start_page(self, title='Match Schedule'):
        self.row_height = 800
        if self.page_number != 0:
            self.canvas.showPage()
        self.page_number += 1

        self.draw_header(title)
        self.draw_footer()
        self.draw_vertical_bars()
        self.draw_column_headings()

    def draw_header(self, text):
        self.canvas.setFont('Helvetica', 12)
        self.canvas.drawCentredString(self.width * 0.5, 820, text)

    def draw_footer(self):
        self.canvas.setFont("Helvetica", 8)
        self.canvas.drawCentredString(self.width*0.5, 10,
                "Page {} • Generated from state {}".format(self.page_number,
                                                           self.state[:7]))

    def draw_vertical_bars(self):
        for x in (134, 353):
            self.canvas.line(x, 30, x, 810)

    def draw_column_headings(self):
        headings = ['**Number**', '**Time**']
        for arena in self.arenas.values():
            headings += ['**{}**'.format(arena.display_name), '', '', '']
        self.add_line(headings)

    def add_line(self, line):
        if len(line) != self.columns:
            raise ValueError("Incorrect column count")
        for i, cell in enumerate(line):
            self.canvas.setFont("Helvetica", 10)

            if isinstance(cell, tuple):
                text = cell[0]
                colour = cell[1]
            else:
                text = cell
                colour = '#000000'

            self.canvas.setFillColor(colour)
            self.canvas.drawCentredString(self.margin + i * (self.width - 2*self.margin) / (self.columns - 1),
                                          self.row_height, text)
            self.canvas.setFillColor('black')
        self.canvas.line(self.margin*0.5, self.row_height - 3.5,
                         self.width-(self.margin*0.5), self.row_height - 3.5)
        self.row_height -= 14

    def _generate(self, competition, shepherds=None):
        current_period = None

        team_colours = {}
        if shepherds:
            for shepherd in shepherds:
                for team in shepherd['teams']:
                    team_colours[team] = shepherd['colour']

        for n, slot in enumerate(competition.schedule.matches):
            first_match = next(iter(slot.values()))
            period = competition.schedule.period_at(first_match.start_time)
            if period != current_period:
                current_period = period
                self.start_page(str(period))
                n = 0

            cells = ['', '']
            for arena in self.arenas:
                match = slot.get(arena)
                if match is not None:
                    for team in match.teams:
                        colour = team_colours.get(team, '#000000')
                        cells.append((team if team else '–', colour))
                    cells[0] = str(match.num)
                    cells[1] = str(match.start_time.strftime('%H:%M'))
                else:
                    cells += ['–', '–', '–', '–']
            self.add_line(cells)

            if n % 65 == 65:
                self.start_page(str(current_period))

    def generate(self, competition, shepherds=None):
        if shepherds is None:
            self._generate(competition)
        else:
            self._generate(competition, None)

            for shepherd in shepherds:
                self._generate(competition, [shepherd])

            self._generate(competition, shepherds)

    def write(self):
        self.canvas.save()


def command(settings):
    import os.path

    from sr.comp.comp import SRComp


    comp = SRComp(os.path.realpath(settings.compstate))

    generator = ScheduleGenerator(settings.output, arenas=comp.arenas,
                                  state=comp.state)

    if settings.shepherds:
        shepherds = yaml.load(settings.shepherds)['shepherds']
    else:
        shepherds = None

    generator.generate(comp, shepherds=shepherds)
    generator.write()


def add_subparser(subparsers):
    parser = subparsers.add_parser('print-schedule',
                                   help='print a shepherding sheet')
    parser.add_argument('compstate', help='competition state repository')
    parser.add_argument('-o', '--output', help='output file',
                        type=argparse.FileType('wb'), required=True)
    parser.add_argument('-s', '--shepherds', help='shepherds file',
                        type=argparse.FileType('r'))
    parser.set_defaults(func=command)
