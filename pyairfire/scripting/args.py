__author__      = "Joel Dubowy"
__copyright__   = "Copyright (c) 2015 AirFire, PNW, USFS"

import ConfigParser
import datetime
import logging
import re
from argparse import (
    ArgumentTypeError, ArgumentParser, Action, RawTextHelpFormatter
)

from pyairfire.datetime.parsing import parse as parse_datetime
from .utils import exit_with_msg

__all__ = [
    # Argument Parsing
    'parse_args',
    # Argument Action Callbacks
    'SetConfigOptionAction',
    'ExtractAndSetKeyValueAction',
    'ParseDatetimeAction',
    'append_or_split_with_delimiter_and_extend',
    'AppendOrSplitAndExtendAction'
]

##
## 'Public' Interface
##

##  Argument Parsing Methods

def parse_args(required_args, optional_args, positional_args=None, usage=None,
        epilog=None, post_args_outputter=None, pre_validation=None):
    """....

    Arguments:
     - required_args --
     - optional_args --
    Kwargs
     - usage -- usage text to replace default
     - epilog -- additional help text to display after list of args
     - post_args_outputter -- callable object that generates epilog
        (for when itneeds to be dynamically generated)
     - pre_validation -- callable object that performs any tasks that
        should be done before outputing the parsed args

    TODO:
     - support custom positional args
    """
    parser = ArgumentParser(usage=usage)

    if epilog or post_args_outputter:
        parser.epilog = epilog or post_args_outputter()
        parser.formatter_class = RawTextHelpFormatter

    add_arguments(parser, required_args, required=True)
    add_arguments(parser, optional_args)
    if positional_args:
        add_arguments(parser, positional_args)

    add_logging_options(parser)

    args = parser.parse_args()

    configure_logging_from_args(args, parser)

    if pre_validation:
        pre_validation(parser, args)

    output_args(args)

    return parser, args

## Callback Actions for add_argument

class SetConfigOptionAction(Action):

    OPTION_EXTRACTOR = re.compile('(\w+)\.(\w+)=(.+)')

    def __call__(self, parser, namespace, value, option_string=None):
        m = self.OPTION_EXTRACTOR.search(value.strip())
        if not m:
            msg = "Invalid value '%s' for option '%s' - value must be of the form 'Section.OPTION=value'" % (
                value, option_string)
            raise OptionValueError(msg)
        config = getattr(namespace, self.dest)
        if not config:
            config = ConfigParser.ConfigParser()
            setattr(namespace, self.dest, config)
        if not config.has_section(m.group(1)):
            config.add_section(m.group(1))
        config.set(m.group(1), m.group(2), m.group(3))

class ExtractAndSetKeyValueAction(Action):

    KEY_VALUE_EXTRACTER = re.compile('^([^=]+)=([^=]+)$')

    def __call__(self, parser, namespace, value, option_string=None):
        """Splits value into key/value, and set in destination dict

        Note: Expects value to be of the format 'key=value'.  Also expects
        destination (i.e. parser.value's self.dest attribute), to be
        initialized as an empty dict.
        """
        m = self.KEY_VALUE_EXTRACTER.search(value.strip())
        if not m:
            msg = "Invalid value '%s' for option '%s' - value must be of the form 'key=value'" % (
                value, opt)
            raise ArgumentTypeError(msg)
        d = getattr(namespace, self.dest)
        d[m.group(1)] = m.group(2)

class ParseDatetimeAction(Action):

    def __call__(self, parser, namespace, value, option_string=None):
        """Parses datetime from string value

        Note: Expects value to be of one of the formats listed in
        pyairfire.datetime.parsing.RECOGNIZED_DATETIME_FORMATS
        """
        try:
            dt = parse_datetime(value)
        except ValueError:
            # If we got here, none of them matched, so raise error
            raise ArgumentTypeError("Invalid datetime format '%s' for option %s" % (
                value, option_string))
        setattr(namespace, self.dest, dt)


def append_or_split_with_delimiter_and_extend(dilimiter):
    """Generates a callback function that augments the append action with the
    ability to split a string and extend the redsulting values to the option array

    Args:
     - delimiter -- character used to to split the string string
    """
    class C(Action):
        def __call__(self, parser, namespace, values, option_string=None):
            d = getattr(namespace, self.dest)
            d.extend(values.split(dilimiter))
    return C
AppendOrSplitAndExtendAction = append_or_split_with_delimiter_and_extend(',')
"""For convenience, returns callback generated by
append_or_split_with_delimiter_and_extend with comma as the dilimiter
"""

##
## Helper Methods
##

## Argument Parsing

def add_arguments(parser, argument_hashes, required=False):
    for o in argument_hashes:
        opt_strs = [e for e in [o.get('short'), o.get('long')] if e]
        kwargs = dict([(k,v) for k,v in o.items() if k not in ('short', 'long')])
        if required:
            kwargs.update(required=True)
        parser.add_argument(*opt_strs, **kwargs)

def output_args(args):
    for k,v in args.__dict__.items():
        logging.info("%s: %s" % (' '.join(k.split('_')), v))

## Logging Related Options

LOG_LEVELS = [
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL'
]

def add_logging_options(parser):
    add_arguments(parser, [
        {
            'long': "--log-level",
            'dest': "log_level",
            'action': "store",
            'default': None,
            'help': "python log level (%s)" % (','.join(LOG_LEVELS))
        },
        {
            'long': "--log-file",
            'dest': "log_file",
            'action': "store",
            'default': None,
            'help': "log file"
        },
        {
            'long': "--log-message-format",
            'dest': "log_message_format",
            'action': "store",
            'default': None,
            'help': "log message format"
        },
    ])

def configure_logging_from_args(args, parser):
    level = logging.WARNING  # default
    if args.log_level:
        log_level = args.log_level.upper()
        if log_level not in LOG_LEVELS:
            exit_with_msg(
                'Invalid log level: %s' % (log_level))
        level = getattr(logging, log_level)

    log_message_format = args.log_message_format or '%(asctime)s %(levelname)s: %(message)s'

    logging.basicConfig(format=log_message_format, level=level, filename=args.log_file)
