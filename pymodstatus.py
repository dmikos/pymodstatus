'''
pymodstatus - An interface to remote Apache mod_status data.  This is a rewrite of pyserverstatus written by Mark Caudill.  The original version required the requests module to be installed.  This should run on a vanilla python 2.4+ installation.
'''
import httplib

__all__ = ['server_status', 'recreate']


def server_status(url):
    '''
    Fetch the mod_status output from `url` and parse it into
    something beautiful (or at least useful.)

    >>> status = server_status('server.tld')
    >>> print status
    {'idle_cleanup_of_worker': 0, 'uptime': 234140, 'logging': 0, 'total_accesses': 34326, 'open_slots': 247, 'idle_workers': 8, 'reading_request': 0, 'requests_per_second': 0.14660500000000001, 'starting_up': 0, 'bytes_per_second': 425.03800000000001, 'cpuload': 0.11558, 'closing_connection': 0, 'waiting_for_connection': 8, 'sending_reply': 1, 'dns_lookup': 0, 'total_kbytes': 97186, 'gracefully_finishing': 0, 'keepalive': 0, 'bytes_per_request': 2899.2199999999998, 'busy_workers': 1}

    :param url: URL to fetch from.
    :type  url: string
    :return: Dictionary containing parsed data.
    :rtype: dict
    :raises ValueError: If unable to fetch any data.
    '''
    # Get the raw output. Raise a ValueError on anything other than a 200
    # Use httplib instead of requests for out-of-date businesses like mine.
    cn = httplib.HTTPConnection(url)
    cn.request("GET", "/server-status?auto")
    resp = cn.getresponse()
    if resp.status != 200:
        cn.close()
        raise ValueError('HTTP %s received from %s.' % (resp.status, url))
    raw = resp.read()
    cn.close()

    # Initialize with None because mod_status has different levels of
    # verbosity. So if it doesn't respond with a value, we'll just have
    # a None instead which is nicer than getting unpredictable exceptions
    # when accessing the output later on.
    parsed = {'total_accesses': None,
              'total_kbytes': None,
              'cpuload': None,
              'uptime': None,
              'requests_per_second': None,
              'bytes_per_second': None,
              'bytes_per_request': None,
              'busy_workers': None,
              'idle_workers': None,
              'waiting_for_connection': None,
              'starting_up': None,
              'reading_request': None,
              'sending_reply': None,
              'keepalive': None,
              'dns_lookup': None,
              'closing_connection': None,
              'logging': None,
              'gracefully_finishing': None,
              'idle_cleanup_of_worker': None,
              'open_slots': None}

    # Do the nasty parsing. Doing this programatically may be
    # more extensible but it's much rougher looking.
    for line in raw.splitlines():
        (key, value) = line.split(': ')
        if key == 'Total Accesses':
            parsed['total_accesses'] = int(value)
        if key == 'Total kBytes':
            parsed['total_kbytes'] = int(value)
        if key == 'CPULoad':
            parsed['cpuload'] = float(value)
        if key == 'Uptime':
            parsed['uptime'] = int(value)
        if key == 'ReqPerSec':
            parsed['requests_per_second'] = float(value)
        if key == 'BytesPerSec':
            parsed['bytes_per_second'] = float(value)
        if key == 'BytesPerReq':
            parsed['bytes_per_request'] = float(value)
        if key == 'BusyWorkers':
            parsed['busy_workers'] = int(value)
        if key == 'IdleWorkers':
            parsed['idle_workers'] = int(value)
        if key == 'Scoreboard':
            parsed['waiting_for_connection'] = value.count('_')
            parsed['starting_up'] = value.count('S')
            parsed['reading_request'] = value.count('R')
            parsed['sending_reply'] = value.count('W')
            parsed['keepalive'] = value.count('K')
            parsed['dns_lookup'] = value.count('D')
            parsed['closing_connection'] = value.count('C')
            parsed['logging'] = value.count('L')
            parsed['gracefully_finishing'] = value.count('G')
            parsed['idle_cleanup_of_worker'] = value.count('I')
            parsed['open_slots'] = value.count('.')

    return parsed


def recreate(parsed):
    '''
    Recreate the statistics portion of the mod_status output.

    >>> status = server_status('http://server.tld/server-status?auto')
    >>> print recreate(status)
    Total Accesses: 34326
    Total kBytes: 97186
    CPULoad: 0.11558
    Uptime: 234140
    ReqPerSec: 0.146605
    BytesPerSec: 425.038
    BytesPerReq: 2899.22
    BusyWorkers: 1
    IdleWorkers: 8
    Scoreboard: ________W.......................................................................................................................................................................................................................................................
    
    :param parsed: Parsed mod_status data.
    :type  parsed: dict
    :returns: A string formatted the same as generated by /server-status?auto.
    :rtype: string
    '''
    scoreboard = '%s%s%s%s%s%s%s%s%s%s%s' % (
        '_' * parsed['waiting_for_connection'],
        'S' * parsed['starting_up'],
        'R' * parsed['reading_request'],
        'W' * parsed['sending_reply'],
        'K' * parsed['keepalive'],
        'D' * parsed['dns_lookup'],
        'C' * parsed['closing_connection'],
        'L' * parsed['logging'],
        'G' * parsed['gracefully_finishing'],
        'I' * parsed['idle_cleanup_of_worker'],
        '.' * parsed['open_slots'])
    output = 'Total Accesses: %s\n' % parsed['total_accesses']
    output += 'Total kBytes: %s\n' % parsed['total_kbytes']
    output += 'CPULoad: %s\n' % parsed['cpuload']
    output += 'Uptime: %s\n' % parsed['uptime']
    output += 'ReqPerSec: %s\n' % parsed['requests_per_second']
    output += 'BytesPerSec: %s\n' % parsed['bytes_per_second']
    output += 'BytesPerReq: %s\n' % parsed['bytes_per_request']
    output += 'BusyWorkers: %s\n' % parsed['busy_workers']
    output += 'IdleWorkers: %s\n' % parsed['idle_workers']
    output += 'Scoreboard: %s\n' % scoreboard
    return output
