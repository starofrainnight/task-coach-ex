"""
Task Coach - Your friendly task manager
Copyright (C) 2004-2016 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from taskcoachlib.i18n import _


snoozeChoices = [
    (0, _("Don't snooze")),
    (5, _("5 minutes")),
    (10, _("10 minutes")),
    (15, _("15 minutes")),
    (20, _("20 minutes")),
    (30, _("30 minutes")),
    (45, _("45 minutes")),
    (60, _("1 hour")),
    (90, _("1.5 hour")),
    (120, _("2 hours")),
    (3 * 60, _("3 hours")),
    (4 * 60, _("4 hours")),
    (6 * 60, _("6 hours")),
    (8 * 60, _("8 hours")),
    (12 * 60, _("12 hours")),
    (18 * 60, _("18 hours")),
    (24 * 60, _("24 hours")),
    (48 * 60, _("48 hours")),
    (72 * 60, _("72 hours")),
    (7 * 24 * 60, _("1 week")),
    (2 * 7 * 24 * 60, _("2 weeks")),
]
