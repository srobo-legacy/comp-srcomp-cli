from __future__ import print_function

from datetime import timedelta
from enum import Enum
import time

import mido

from sr.comp.comp import SRComp


__description__ = 'MIDI Show Control Interface to control lights and other ' \
                  'things at a competition.'


class State(Enum):
    idle = 0
    match = 1
    match_ending = 2
    pre_match = 3


class CompetitionStateMachine:
    def __init__(self, comp):
        self.comp = comp

    @property
    def now(self):
        return self.comp.schedule.datetime_now

    def wait_until(self, date):
        while True:
            delta = date - self.now
            s = delta.total_seconds()
            if s <= 0:
                break
            time.sleep(s)

    @property
    def current_match(self):
        current_matches = list(self.comp.schedule.matches_at(self.now))
        if current_matches:
            return current_matches[0]
        else:
            return None

    @property
    def next_match(self):
        # assumes list is in time order
        now = self.now
        for slot in self.comp.schedule.matches:
            for match in slot.values():
                if self.get_game_end_time(match) >= now:
                    return match
        return None

    def get_game_start_time(self, match):
        match_slot_lengths = self.comp.schedule.match_slot_lengths
        return match.start_time + match_slot_lengths['pre']

    def get_game_end_time(self, match):
        match_slot_lengths = self.comp.schedule.match_slot_lengths
        return match.end_time - match_slot_lengths['post']

    def is_match_in_game(self, match):
        a = self.get_game_start_time(match)
        b = self.get_game_end_time(match)
        return a <= self.now <= b

    @property
    def current_state(self):
        current_match = self.current_match

        if current_match is not None and self.is_match_in_game(current_match):
            game_end_time = self.get_game_end_time(current_match)
            game_ending_time = game_end_time - timedelta(seconds=10)
            if self.now <= game_ending_time:
                return State.match, game_ending_time
            if self.now <= game_end_time:
                return State.match_ending, game_end_time

        next_match = self.next_match

        if next_match is None:
            return State.idle, self.now + timedelta(days=100)

        game_start_time = self.get_game_start_time(next_match)
        game_starting_time = game_start_time - timedelta(seconds=5)
        if game_starting_time <= self.now <= game_start_time:
            return State.pre_match, game_start_time

        return State.idle, game_starting_time

    def transition(self):
        prev_state = None
        while True:
            state, transition_date = self.current_state
            yield prev_state, state, transition_date
            self.wait_until(transition_date)
            prev_state = state


class LightingController:
    tracks = {
        State.idle: 0,
        State.match: 1,
        State.pre_match: 2,
        State.match_ending: 3,
    }

    def __init__(self, comp, midi):
        self.comp = comp
        self.state = CompetitionStateMachine(comp)
        self.midi = midi
        self.cur_playback = None

    def note_on(self, note, velocity):
        msg = mido.Message('note_on', note=note, velocity=velocity)
        self.midi.send(msg)

    def start_playback(self, note, velocity=127):
        self.note_on(note, velocity)

    def stop_playback(self, note):
        self.note_on(note, 0)

    def run(self):
        for _, state, transition_date in self.state.transition():
            if self.cur_playback is not None:
                self.stop_playback(self.cur_playback)

            playback = self.tracks[state]
            self.start_playback(playback)
            self.cur_playback = playback

            print(state, 'until', transition_date)


class PrintOutput(mido.ports.BaseOutput):
    def _send(self, message):
        print(message)


def command(args):
    comp = SRComp(args.compstate)

    if args.dry_run:
        output = PrintOutput()
    else:
        output = mido.open_output(args.output)

    LightingController(comp, output).run()


def add_subparser(subparsers):
    parser = subparsers.add_parser('midi-show-control-interface',
                                   help=__description__,
                                   description=__description__)
    parser.add_argument('compstate', help='Competition state repository.')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--port', help='The MIDI port to use.')
    group.add_argument('--dry-run', action='store_true', help='Dry run.')

    parser.set_defaults(func=command)
