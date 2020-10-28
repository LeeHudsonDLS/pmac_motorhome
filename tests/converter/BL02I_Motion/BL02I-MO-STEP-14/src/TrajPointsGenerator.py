# type: ignore
from pkg_resources import require
require('cothread')
require('numpy')
from cothread import *
from cothread.catools import *
from numpy import *
import numpy as np
import sys


CHOPPER_START = 0
CHOPPER_INCREMENT = 22.5

CHOPPER_TIME_MS = 5

OMEGA_STOP_DISTANCE = 1 # found by experiment

TRAJ_MILLISECOND = 1000
TRAJ_SECOND = 1000 * TRAJ_MILLISECOND

VEL_PREV_TO_NEXT = 0
VEL_PREV_TO_CURRENT = 1
VEL_CURRENT_TO_NEXT = 2
VEL_STOP = 3

OMEGA_POINTS = "omega_points"
CHOPPER_POINTS = "chopper_points"
TIME_POINTS = "time_points"
VELOCITY_POINTS = "velocity_points"
X_POINTS = "x_points"
Y_POINTS = "y_points"


def rotation_points(count, omega_start, omega_step, time_interval):
    """
    Args:
        count : number of triggers
        omega_start : first "scan" position
        omega_step : step size
        time_interval : acquire time (seconds)
    """
    omega_positions = np.fromfunction(lambda i: omega_start + omega_step * i, (count + 1,), dtype=np.float64)
    time_to_first = 0.5 * TRAJ_SECOND
    time_to_stop = 1 * TRAJ_SECOND
    time_us = time_interval * TRAJ_SECOND

    omega_veloc = (omega_positions[-1] - omega_positions[0]) / (time_us * count)
    time_for_chopper = CHOPPER_TIME_MS * TRAJ_MILLISECOND

    omega_positions = np.concatenate((
            [omega_positions[0] - time_for_chopper * omega_veloc],
            omega_positions,
            [omega_positions[-1] + time_for_chopper * omega_veloc],
            [omega_positions[-1] + (time_for_chopper * omega_veloc) + OMEGA_STOP_DISTANCE]))

    chopper_positions = np.concatenate((
            [CHOPPER_START],
            [CHOPPER_START + CHOPPER_INCREMENT] * (count + 1),
            [CHOPPER_START + CHOPPER_START * 2] * 2))

    velocity_profile = np.concatenate((
            [VEL_CURRENT_TO_NEXT],
            [VEL_PREV_TO_NEXT] * (count + 1),
            [VEL_PREV_TO_CURRENT, VEL_STOP]))

    time_profile = np.concatenate((
            [time_to_first, time_for_chopper],
            [time_us] * count,
            [time_for_chopper, time_to_stop]))

    params = {OMEGA_POINTS : omega_positions,
            CHOPPER_POINTS : chopper_positions,
            TIME_POINTS : time_profile,
            VELOCITY_POINTS : velocity_profile}
    return params



def grid_points(rows, columns, time_interval, x_start, y_start, x_step, y_step):
    """
    Args:
        rows : number of rows
        columns : number of columns
        time_interval : acquire time in seconds
        x_start : x position of first scan point
        y_start : y position of first scan point (scan points are mid-point of rows, so actual position will be y_start + y_step/2.)
        x_step : x step size
        y_step : y step size
    """
    time_us = time_interval * TRAJ_SECOND

    y_positions = [y_start + y_step * (i + 0.5) for i in xrange(rows)] # scan midpoint of rows

    x_end = x_start + x_step * columns
    x_veloc = (x_end - x_start) / (time_us * columns)

    time_for_chopper = CHOPPER_TIME_MS * TRAJ_MILLISECOND
    distance_for_chopper = x_veloc * time_for_chopper

    time_row_start = 2. * TRAJ_SECOND
    time_to_stop = 1 * TRAJ_SECOND
    stop_distance = 0.5

    x_rows = []
    y_rows = []
    chopper_rows = []
    velocity_rows = []
    time_rows = []

    direction = -1
    chopper_closed = CHOPPER_START
    for i in xrange(rows):
        direction *= -1
        chopper_open = chopper_closed + CHOPPER_INCREMENT
        chopper_closed_end = chopper_open + CHOPPER_INCREMENT
        if direction > 0:
            row_start, row_end = x_start, x_end
        else:
            row_start, row_end = x_end, x_start
        for_chopper_open, for_chopper_close = \
                (row_start - distance_for_chopper * direction, row_end + distance_for_chopper * direction)

        x_row = np.concatenate((
            [for_chopper_open],
            np.linspace(row_start, row_end, num=columns+1, endpoint=True),
            [for_chopper_close]))

        y_row = np.repeat([y_positions[i]], len(x_row))

        chopper_row = np.concatenate((
            [chopper_closed],
            np.repeat([chopper_open], columns + 1),
            [chopper_closed_end]))

        time_row = np.concatenate((
            [time_row_start, time_for_chopper],
            [time_us] * columns,
            [time_for_chopper]))

        velocity_row = np.concatenate((
            [VEL_CURRENT_TO_NEXT],
            np.repeat([VEL_PREV_TO_NEXT], columns + 1),
            [VEL_PREV_TO_CURRENT]))

        x_rows.append(x_row)
        y_rows.append(y_row)
        chopper_rows.append(chopper_row)
        time_rows.append(time_row)
        velocity_rows.append(velocity_row)

    time_profile = np.concatenate(time_rows)
    velocity_profile = np.concatenate(velocity_rows)
    chopper_points = np.concatenate(chopper_rows)
    x_points = np.concatenate(x_rows)
    y_points = np.concatenate(y_rows)
    print (time_profile)
    print (list(x_points))
    print (list(y_points))
    print (list(velocity_profile))

    caput("BL02I-MO-TEST-14:X:Positions", list(x_points))
    caput("BL02I-MO-TEST-14:Y:Positions", list(y_points))
    caput("BL02I-MO-TEST-14:ProfilePointsToBuild", len(y_points))
    caput("BL02I-MO-TEST-14:ProfileTimeArray", list(time_profile))

    params = {
            X_POINTS : x_points,
            Y_POINTS : y_points,
            CHOPPER_POINTS : chopper_points,
            TIME_POINTS : time_profile,
            VELOCITY_POINTS : velocity_profile
    }
    print ("Done")
    return params


#cmd_line_params = [int(x) for x in sys.argv[1:5]]
#rotation_params = rotation_points(600, -30, 0.1, 1/500.)
#chopper_start = rotation_params[CHOPPER_POINTS][0]
#omega_start = rotation_params[OMEGA_POINTS][0]
#print "passing in: rows:", 5, "cols", 10, "x start", 1/500., "y_start", 0, "x_step", 0, "y_step", 0.01
grid_params = grid_points(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7]))
#chopper_start = grid_params[CHOPPER_POINTS][0]
y_start = grid_params[Y_POINTS][0]
x_params = grid_params[X_POINTS][0] - (grid_params[X_POINTS][1] - grid_params[X_POINTS][0]) # wind back by the step amount



