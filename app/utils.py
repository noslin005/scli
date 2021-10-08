def normalize_serial(system_serial: str):
    """
    This is a quick fix to deal with system serial number on the scheduler.
    A single system with serial number '1098591' is stored on the scheduler
    as '1098591-1'. If theres multiple systems, it just keep increment the
    last digit. It's common in the SCC production to use leading zeros on
    the system serial number, for example '1098591-01'.
    This format is not recognized by the scheduler API. This means, the
    leading zero after the '-' on system serial number needs to be removed
    in order to query the scheduler for that particular system.
    """
    if '-' not in system_serial:
        "if it's a single system, append 'dash one' (-1)"
        system_serial = '{}-1'.format(system_serial)
    else:
        " remove the leading zeros "
        first, last = system_serial.split('-')
        system_serial = "{0}-{1}".format(first, last.lstrip('0'))

    return system_serial


def format_fru(system_serial: str):
    first, last = system_serial.split('-')
    last = int(last)
    first = int(first)
    system_serial = "{0}-{1:02}".format(first, last)

    return system_serial
