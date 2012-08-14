#
# Copyright 2008 Orbitz WorldWide
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import struct
import time
import operator
import itertools
import re

from whisper.exceptions import InvalidConfiguration, \
    InvalidAggregationMethod, InvalidTimeInterval, TimestampNotCovered, \
    CorruptWhisperFile

try:
    import fcntl
    CAN_LOCK = True
except ImportError:
    CAN_LOCK = False


class Whisper(object):

    """This module is an implementation of the Whisper database API.
    Here is the basic layout of a whisper data file:

    file = header, data
        header = metadata, archive_info
            metadata = aggregation_type, max_retention, x_files_factor, archive_count
            archiveInfo = offset, seconds_per_point, points
        data = archive
            archive = point
                point = timestamp, value
    """

    CAN_LOCK = CAN_LOCK
    LOCK = False
    CACHE_HEADERS = False
    AUTOFLUSH = False

    LONG_FORMAT = "!L"
    LONG_SIZE = struct.calcsize(LONG_FORMAT)
    FLOAT_FORMAT = "!f"
    FLOAT_SIZE = struct.calcsize(FLOAT_FORMAT)
    VALUE_FORMAT = "!d"
    VALUE_SIZE = struct.calcsize(VALUE_FORMAT)
    POINT_FORMAT = "!Ld"
    POINT_SIZE = struct.calcsize(POINT_FORMAT)
    METADATA_FORMAT = "!2LfL"
    METADATA_SIZE = struct.calcsize(METADATA_FORMAT)
    ARCHIVE_INFO_FORMAT = "!3L"
    ARCHIVE_INFO_SIZE = struct.calcsize(ARCHIVE_INFO_FORMAT)

    AGGREGATION_TYPE_TO_METHOD = {1: 'average',
                                  2: 'sum',
                                  3: 'last',
                                  4: 'max',
                                  5: 'min'}
    AGGREGATION_METHOD_TO_TYPE = \
        dict((v, k) for k, v in AGGREGATION_TYPE_TO_METHOD.iteritems())
    AGGREGATION_METHODS = AGGREGATION_TYPE_TO_METHOD.values()

    UNIT_MULTIPLIERS = {'seconds': 1,
                        'minutes': 60,
                        'hours': 3600,
                        'days': 86400,
                        'weeks': 86400 * 7,
                        'years': 86400 * 365}

    _header_cache = {}

    @staticmethod
    def get_unit_string(s):
        if 'seconds'.startswith(s):
            return 'seconds'
        if 'minutes'.startswith(s):
            return 'minutes'
        if 'hours'.startswith(s):
            return 'hours'
        if 'days'.startswith(s):
            return 'days'
        if 'weeks'.startswith(s):
            return 'weeks'
        if 'years'.startswith(s):
            return 'years'
        raise ValueError("Invalid unit '%s'" % s)

    @staticmethod
    def parse_retention_def(retention_def):
        (precision, points) = retention_def.strip().split(':')

        if precision.isdigit():
            precision = int(precision) * \
                Whisper.UNIT_MULTIPLIERS[Whisper.get_unit_string('s')]
        else:
            precision_re = re.compile(r'^(\d+)([a-z]+)$')
            match = precision_re.match(precision)
            if match:
                precision = int(match.group(1)) * \
                    Whisper.UNIT_MULTIPLIERS[Whisper.get_unit_string(match.group(2))]
            else:
                raise ValueError(
                    "Invalid precision specification '%s'" % precision)

        if points.isdigit():
            points = int(points)
        else:
            points_re = re.compile(r'^(\d+)([a-z]+)$')
            match = points_re.match(points)
            if match:
                points = int(match.group(1)) * \
                    Whisper.UNIT_MULTIPLIERS[Whisper.get_unit_string(match.group(2))] / precision
            else:
                raise ValueError("Invalid retention specification '%s'" %
                                 points)

        return (precision, points)

    @staticmethod
    def _read_header(fh):
        info = Whisper._header_cache.get(fh.name)
        if info:
            return info

        original_offset = fh.tell()
        fh.seek(0)
        packed_metadata = fh.read(Whisper.METADATA_SIZE)

        try:
            (aggregation_type, max_retention, xff, archive_count) = \
                struct.unpack(Whisper.METADATA_FORMAT, packed_metadata)
        except:
            raise CorruptWhisperFile("Unable to read header", fh.name)

        archives = []

        for i in xrange(archive_count):
            packed_archive_info = fh.read(Whisper.ARCHIVE_INFO_SIZE)
            try:
                (offset, seconds_per_point, points) = \
                    struct.unpack(Whisper.ARCHIVE_INFO_FORMAT,
                                  packed_archive_info)
            except:
                raise CorruptWhisperFile("Unable to read archive%d metadata" %
                                         i, fh.name)

            archive_info = {'offset': offset,
                            'seconds_per_point': seconds_per_point,
                            'points': points,
                            'retention': seconds_per_point * points,
                            'size': points * Whisper.POINT_SIZE}
            archives.append(archive_info)

        fh.seek(original_offset)
        aggregation_method = \
            Whisper.AGGREGATION_TYPE_TO_METHOD.get(aggregation_type,
                                                   'average')
        info = {'aggregation_method': aggregation_method,
                'max_retention': max_retention,
                'x_files_factor': xff,
                'archives': archives}
        if Whisper.CACHE_HEADERS:
            Whisper._header_cache[fh.name] = info

        return info

    @staticmethod
    def set_aggregation_method(path, aggregation_method):
        """
        path -- a string
        aggregation_method -- specifies the method to use when propogating data
        (see ``whisper.AGGREGATION_METHODS``)
        """
        with open(path, 'r+b') as fh:
            if Whisper.LOCK:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)

            packed_metadata = fh.read(Whisper.METADATA_SIZE)

            try:
                (aggregation_type, max_retention, xff, archive_count) = \
                    struct.unpack(Whisper.METADATA_FORMAT, packed_metadata)
            except:
                raise CorruptWhisperFile("Unable to read header", fh.name)

            try:
                new_aggregation_type = \
                    Whisper.AGGREGATION_METHOD_TO_TYPE[aggregation_method]
                new_aggregation_type = struct.pack(Whisper.LONG_FORMAT,
                                                   new_aggregation_type)
            except KeyError:
                err_message = "Unrecognized aggregation method: %s" % \
                    aggregation_method
                raise InvalidAggregationMethod(err_message)

            fh.seek(0)
            fh.write(new_aggregation_type)

            if Whisper.AUTOFLUSH:
                fh.flush()
                os.fsync(fh.fileno())

            if Whisper.CACHE_HEADERS and fh.name in Whisper._header_cache:
                del Whisper._header_cache[fh.name]

            return Whisper.AGGREGATION_TYPE_TO_METHOD.get(aggregation_type,
                                                          'average')

    @staticmethod
    def validate_archive_list(archive_list):
        """Validates an archive_list.
        An ArchiveList must:
        1. Have at least one archive config. Example: (60, 86400)
        2. No archive may be a duplicate of another.
        3. Higher precision archives' precision must evenly divide all lower
        precision archives' precision.
        4. Lower precision archives must cover larger time intervals than
        higher precision archives.
        5. Each archive must have at least enough points to consolidate to the
        next archive

        Returns True or False
        """

        if not archive_list:
            raise InvalidConfiguration("You must specify at least one archive"
                                       "configuration!")

        archive_list.sort(
            key=lambda a: a[0])  # sort by precision (seconds_per_point)

        for i, archive in enumerate(archive_list):
            if i == len(archive_list) - 1:
                break

            next_archive = archive_list[i + 1]
            if not archive[0] < next_archive[0]:
                err_message = "A Whisper database may not configured having " \
                              "two archives with the same precision " \
                              "(archive%d: %s, archive%d: %s)" % \
                              (i, archive, i + 1, next_archive)
                raise InvalidConfiguration(err_message)

            if next_archive[0] % archive[0] != 0:
                err_message = "Higher precision archives must evenly divide " \
                              "all lower precision archives precision " \
                              "(archive%d: %s, archive%d: %s)" % \
                              (i, archive[0], i + 1, next_archive[0])
                raise InvalidConfiguration(err_message)

            retention = archive[0] * archive[1]
            next_retention = next_archive[0] * next_archive[1]

            if not next_retention > retention:
                err_message = "Lower precision archives must cover larger " \
                              "time intervals than higher precision archives" \
                              "(archive%d: %s seconds, archive%d: %s " \
                              "seconds)" % \
                              (i, archive[1], i + 1, next_archive[1])
                raise InvalidConfiguration(err_message)

            archive_points = archive[1]
            points_per_consolidation = next_archive[0] / archive[0]
            if not archive_points >= points_per_consolidation:
                err_message = "Each archive must have at least enough points" \
                              "to consolidate to the next archive " \
                              "(archive%d consolidates %d of archive%d's " \
                              "points but it has only %d total points)" % \
                              (i + 1, points_per_consolidation, i,
                              archive_points)
                raise InvalidConfiguration(err_message)

    @staticmethod
    def create(path, archive_list, x_files_factor=None,
               aggregation_method=None, sparse=False):
        """
        path -- a string

        archive_list -- a list of archives, each of which is of the form
        (seconds_per_point,number_of_points).

        x_files_factor -- specifies the fraction of data points in a
        propagation interval that must have known values for a propagation to
        occur.

        aggregation_method -- specifies the function to use when propogating
        data (see ``whisper.AGGREGATION_METHODS``)
        """
        # Set default params
        if x_files_factor is None:
            x_files_factor = 0.5
        if aggregation_method is None:
            aggregation_method = 'average'

        #Validate archive configurations...
        Whisper.validate_archive_list(archive_list)

        #Looks good, now we create the file and write the header
        if os.path.exists(path):
            raise InvalidConfiguration("File %s already exists!" % path)

        with open(path, 'wb') as fh:
            if Whisper.LOCK:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)

            aggregation_type = \
                Whisper.AGGREGATION_METHOD_TO_TYPE.get(aggregation_method, 1)
            aggregation_type = struct.pack(Whisper.LONG_FORMAT,
                                           aggregation_type)
            oldest = max(seconds_per_point * points
                         for seconds_per_point, points in archive_list)
            max_retention = struct.pack(Whisper.LONG_FORMAT, oldest)
            x_files_factor = struct.pack(
                Whisper.FLOAT_FORMAT, float(x_files_factor))
            archive_count = struct.pack(Whisper.LONG_FORMAT, len(archive_list))
            packed_metadata = aggregation_type + max_retention + \
                x_files_factor + archive_count
            fh.write(packed_metadata)
            header_size = Whisper.METADATA_SIZE + \
                (Whisper.ARCHIVE_INFO_SIZE * len(archive_list))
            archive_offset_pointer = header_size

            for seconds_per_point, points in archive_list:
                archive_info = struct.pack(Whisper.ARCHIVE_INFO_FORMAT,
                                           archive_offset_pointer,
                                           seconds_per_point, points)
                fh.write(archive_info)
                archive_offset_pointer += (points * Whisper.POINT_SIZE)

            if sparse:
                fh.seek(archive_offset_pointer - header_size - 1)
                fh.write("\0")
            else:
                # If not creating the file sparsely, then fill the rest of the
                # file
                # with zeroes.
                remaining = archive_offset_pointer - header_size
                chunksize = 16384
                zeroes = '\x00' * chunksize
                while remaining > chunksize:
                    fh.write(zeroes)
                    remaining -= chunksize
                fh.write(zeroes[:remaining])

            if Whisper.AUTOFLUSH:
                fh.flush()
                os.fsync(fh.fileno())

    @staticmethod
    def aggregate(aggregation_method, known_values):
        if aggregation_method == 'average':
            return float(sum(known_values)) / float(len(known_values))
        elif aggregation_method == 'sum':
            return float(sum(known_values))
        elif aggregation_method == 'last':
            return known_values[len(known_values) - 1]
        elif aggregation_method == 'max':
            return max(known_values)
        elif aggregation_method == 'min':
            return min(known_values)
        else:
            err_message = "Unrecognized aggregation method %s" % \
                aggregation_method
            raise InvalidAggregationMethod(err_message)

    @staticmethod
    def _propagate(fh, header, timestamp, higher, lower):
        aggregation_method = header['aggregation_method']
        xff = header['x_files_factor']

        lower_interval_start = timestamp - (timestamp % lower[
            'seconds_per_point'])
        lower_interval_end = lower_interval_start + lower['seconds_per_point']

        fh.seek(higher['offset'])
        packed_point = fh.read(Whisper.POINT_SIZE)
        (higher_base_interval, higher_base_value) = \
            struct.unpack(Whisper.POINT_FORMAT, packed_point)

        if higher_base_interval == 0:
            higher_first_offset = higher['offset']
        else:
            time_distance = lower_interval_start - higher_base_interval
            point_distance = time_distance / higher['seconds_per_point']
            byte_distance = point_distance * Whisper.POINT_SIZE
            higher_first_offset = higher['offset'] + \
                byte_distance % higher['size']

        higher_points = lower['seconds_per_point'] / \
            higher['seconds_per_point']
        higher_size = higher_points * Whisper.POINT_SIZE
        relative_first_offset = higher_first_offset - higher['offset']
        relative_last_offset = (
            relative_first_offset + higher_size) % higher['size']
        higher_last_offset = relative_last_offset + higher['offset']
        fh.seek(higher_first_offset)

        if higher_first_offset < higher_last_offset:
            # we don't wrap the archive
            series_string = fh.read(higher_last_offset - higher_first_offset)
        else:  # We do wrap the archive
            higher_end = higher['offset'] + higher['size']
            series_string = fh.read(higher_end - higher_first_offset)
            fh.seek(higher['offset'])
            series_string += fh.read(higher_last_offset - higher['offset'])

        #Now we unpack the series data we just read
        byte_order, point_types = Whisper.POINT_FORMAT[
            0], Whisper.POINT_FORMAT[1:]
        points = len(series_string) / Whisper.POINT_SIZE
        series_format = byte_order + (point_types * points)
        unpacked_series = struct.unpack(series_format, series_string)

        #And finally we construct a list of values
        neighbor_values = [None] * points
        current_interval = lower_interval_start
        step = higher['seconds_per_point']

        for i in xrange(0, len(unpacked_series), 2):
            point_time = unpacked_series[i]
            if point_time == current_interval:
                neighbor_values[i / 2] = unpacked_series[i + 1]
            current_interval += step

        # Propagate aggregate_value to propagate from neighbor_values if we
        # have enough known points
        known_values = [v for v in neighbor_values if v is not None]
        if not known_values:
            return False

        known_percent = float(len(known_values)) / float(len(neighbor_values))
        if known_percent >= xff:  # we have enough data to propagate a value!
            aggregate_value = Whisper.aggregate(aggregation_method,
                                                known_values)
            my_packed_point = struct.pack(Whisper.POINT_FORMAT,
                                          lower_interval_start,
                                          aggregate_value)
            fh.seek(lower['offset'])
            packed_point = fh.read(Whisper.POINT_SIZE)
            (lower_base_interval, lower_base_value) = \
                struct.unpack(Whisper.POINT_FORMAT, packed_point)

            # First propagated update to this lower archive
            if lower_base_interval == 0:
                fh.seek(lower['offset'])
                fh.write(my_packed_point)
            else:  # Not our first propagated update to this lower archive
                time_distance = lower_interval_start - lower_base_interval
                point_distance = time_distance / lower['seconds_per_point']
                byte_distance = point_distance * Whisper.POINT_SIZE
                lower_offset = lower['offset'] + \
                    (byte_distance % lower['size'])
                fh.seek(lower_offset)
                fh.write(my_packed_point)

            return True

        else:
            return False

    @staticmethod
    def update(path, value, timestamp=None):
        """
        path -- a string
        value -- a float
        timestamp -- either an int or float
        """
        value = float(value)
        with open(path, 'r+b') as fh:
            return Whisper.file_update(fh, value, timestamp)

    @staticmethod
    def file_update(fh, value, timestamp):
        if Whisper.LOCK:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)

        header = Whisper._read_header(fh)
        now = int(time.time())
        if timestamp is None:
            timestamp = now

        timestamp = int(timestamp)
        diff = now - timestamp
        if not ((diff < header['max_retention']) and diff >= 0):
            err_message = "Timestamp not covered by any archives in this " \
                "database."
            raise TimestampNotCovered(err_message)

        # Find the highest-precision archive that covers timestamp
        for i, archive in enumerate(header['archives']):
            if archive['retention'] < diff:
                continue
            #We'll pass on the update to these lower precision archives later
            lower_archives = header['archives'][i + 1:]
            break

        #First we update the highest-precision archive
        my_interval = timestamp - (timestamp % archive['seconds_per_point'])
        my_packed_point = struct.pack(Whisper.POINT_FORMAT, my_interval, value)
        fh.seek(archive['offset'])
        packed_point = fh.read(Whisper.POINT_SIZE)
        (base_interval, base_value) = struct.unpack(Whisper.
                                                    POINT_FORMAT, packed_point)

        if base_interval == 0:  # This file's first update
            fh.seek(archive['offset'])
            fh.write(my_packed_point)
            base_interval, base_value = my_interval, value
        else:  # Not our first update
            time_distance = my_interval - base_interval
            point_distance = time_distance / archive['seconds_per_point']
            byte_distance = point_distance * Whisper.POINT_SIZE
            my_offset = archive['offset'] + (byte_distance % archive['size'])
            fh.seek(my_offset)
            fh.write(my_packed_point)

        #Now we propagate the update to lower-precision archives
        higher = archive
        for lower in lower_archives:
            if not Whisper._propagate(fh, header, my_interval, higher, lower):
                break
            higher = lower

        if Whisper.AUTOFLUSH:
            fh.flush()
            os.fsync(fh.fileno())

        fh.close()

    @staticmethod
    def update_many(path, points):
        """
        path -- a string
        points -- a list of (timestamp, value) points
        """
        if not points:
            return
        points = [(int(t), float(v)) for (t, v) in points]
        points.sort(key=lambda p: p[0], reverse=True)
            #order points by timestamp, newest first
        with open(path, 'r+b') as fh:
            return Whisper.file_update_many(fh, points)

    @staticmethod
    def file_update_many(fh, points):
        if Whisper.LOCK:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)

        header = Whisper._read_header(fh)
        now = int(time.time())
        archives = iter(header['archives'])
        current_archive = archives.next()
        current_points = []

        for point in points:
            age = now - point[0]

            # we can't fit any more points in this archive
            while current_archive['retention'] < age:
                # commit all the points we've found that it can fit
                if current_points:
                    # put points in chronological order
                    current_points.reverse()
                    Whisper._archive_update_many(
                        fh, header, current_archive, current_points)
                    current_points = []
                try:
                    current_archive = archives.next()
                except StopIteration:
                    current_archive = None
                    break

            if not current_archive:
                break  # drop remaining points that don't fit in the database

            current_points.append(point)
        # don't forget to commit after we've checked all the archives
        if current_archive and current_points:
            current_points.reverse()
            Whisper._archive_update_many(
                fh, header, current_archive, current_points)

        if Whisper.AUTOFLUSH:
            fh.flush()
            os.fsync(fh.fileno())

        fh.close()

    @staticmethod
    def _archive_update_many(fh, header, archive, points):
        step = archive['seconds_per_point']
        aligned_points = [(timestamp - (timestamp % step), value)
                          for (timestamp, value) in points]
        #Create a packed string for each contiguous sequence of points
        packed_strings = []
        previous_interval = None
        current_string = ""
        for (interval, value) in aligned_points:
            if interval == previous_interval:
                continue
            if (not previous_interval) or \
                    (interval == previous_interval + step):
                current_string += struct.pack(Whisper.POINT_FORMAT,
                                              interval, value)
                previous_interval = interval
            else:
                number_of_points = len(current_string) / Whisper.POINT_SIZE
                start_interval = previous_interval - \
                    step * (number_of_points - 1)
                packed_strings.append((start_interval, current_string))
                current_string = struct.pack(Whisper.POINT_FORMAT, interval,
                                             value)
                previous_interval = interval
        if current_string:
            number_of_points = len(current_string) / Whisper.POINT_SIZE
            start_interval = previous_interval - step * (number_of_points - 1)
            packed_strings.append((start_interval, current_string))

        #Read base point and determine where our writes will start
        fh.seek(archive['offset'])
        packed_base_point = fh.read(Whisper.POINT_SIZE)
        (base_interval, base_value) = struct.unpack(Whisper.POINT_FORMAT,
                                                    packed_base_point)
        if base_interval == 0:  # This file's first update
            #use our first string as the base, so we start at the start
            base_interval = packed_strings[0][0]

        # Write all of our packed strings in locations determined by the
        # base_interval
        for (interval, packed_string) in packed_strings:
            time_distance = interval - base_interval
            point_distance = time_distance / step
            byte_distance = point_distance * Whisper.POINT_SIZE
            my_offset = archive['offset'] + (byte_distance % archive['size'])
            fh.seek(my_offset)
            archive_end = archive['offset'] + archive['size']
            bytes_beyond = (my_offset + len(packed_string)) - archive_end

            if bytes_beyond > 0:
                fh.write(packed_string[:-bytes_beyond])
                message = "archive_end=%d fh.tell=%d bytes_beyond=%d " \
                    "len(packed_string)=%d" % (archive_end, fh.tell(),
                                               bytes_beyond,
                                               len(packed_string))
                assert fh.tell() == archive_end, message
                fh.seek(archive['offset'])
                # safe because it can't exceed the archive (retention checking
                # logic above)
                fh.write(packed_string[-bytes_beyond:])
            else:
                fh.write(packed_string)

        #Now we propagate the updates to lower-precision archives
        higher = archive
        lower_archives = [arc for arc in header['archives'] if arc[
            'seconds_per_point'] > archive['seconds_per_point']]

        for lower in lower_archives:
            fit = lambda i: i - (i % lower['seconds_per_point'])
            lower_intervals = [fit(p[0]) for p in aligned_points]
            unique_lower_intervals = set(lower_intervals)
            propagate_further = False
            for interval in unique_lower_intervals:
                if Whisper._propagate(fh, header, interval, higher, lower):
                    propagate_further = True

            if not propagate_further:
                break
            higher = lower

    @staticmethod
    def info(path):
        with open(path, 'rb') as fh:
            return Whisper._read_header(fh)

    @staticmethod
    def fetch(path, from_time, until_time=None):
        """
        path -- a string
        from_time -- an epoch time
        until_time -- also an epoch time, but defaults to now
        """
        with open(path, 'rb') as fh:
            return Whisper.file_fetch(fh, from_time, until_time)

    @staticmethod
    def file_fetch(fh, from_time, until_time):
        header = Whisper._read_header(fh)
        now = int(time.time())
        if until_time is None:
            until_time = now
        from_time = int(from_time)
        until_time = int(until_time)

        oldest_time = now - header['max_retention']
        if from_time < oldest_time:
            from_time = oldest_time

        if not (from_time < until_time):
            raise InvalidTimeInterval("Invalid time interval")
        if until_time > now:
            until_time = now
        if until_time < from_time:
            until_time = now

        diff = now - from_time
        for archive in header['archives']:
            if archive['retention'] >= diff:
                break

        from_interval = int(from_time - (from_time % archive[
            'seconds_per_point'])) + archive['seconds_per_point']
        until_interval = int(until_time -
                             until_time % archive['seconds_per_point'])
        until_interval += archive['seconds_per_point']
        fh.seek(archive['offset'])
        packed_point = fh.read(Whisper.POINT_SIZE)
        (base_interval, base_value) = struct.unpack(Whisper.POINT_FORMAT,
                                                    packed_point)

        if base_interval == 0:
            step = archive['seconds_per_point']
            points = (until_interval - from_interval) / step
            time_info = (from_interval, until_interval, step)
            value_list = [None] * points
            return (time_info, value_list)

        #Determine from_offset
        time_distance = from_interval - base_interval
        point_distance = time_distance / archive['seconds_per_point']
        byte_distance = point_distance * Whisper.POINT_SIZE
        from_offset = archive['offset'] + (byte_distance % archive['size'])

        #Determine until_offset
        time_distance = until_interval - base_interval
        point_distance = time_distance / archive['seconds_per_point']
        byte_distance = point_distance * Whisper.POINT_SIZE
        until_offset = archive['offset'] + (byte_distance % archive['size'])

        #Read all the points in the interval
        fh.seek(from_offset)
        if from_offset < until_offset:  # If we don't wrap around the archive
            series_string = fh.read(until_offset - from_offset)
        else:  # We do wrap around the archive, so we need two reads
            archive_end = archive['offset'] + archive['size']
            series_string = fh.read(archive_end - from_offset)
            fh.seek(archive['offset'])
            series_string += fh.read(until_offset - archive['offset'])

        # Now we unpack the series data we just read (anything faster than
        # unpack?)
        byte_order, point_types = Whisper.POINT_FORMAT[
            0], Whisper.POINT_FORMAT[1:]
        points = len(series_string) / Whisper.POINT_SIZE
        series_format = byte_order + (point_types * points)
        unpacked_series = struct.unpack(series_format, series_string)

        #And finally we construct a list of values (optimize this!)
        value_list = [None] * points  # pre-allocate entire list for speed
        current_interval = from_interval
        step = archive['seconds_per_point']

        for i in xrange(0, len(unpacked_series), 2):
            point_time = unpacked_series[i]
            if point_time == current_interval:
                point_value = unpacked_series[i + 1]
                # in-place reassignment is faster than append()
                value_list[i / 2] = point_value
            current_interval += step

        fh.close()
        time_info = (from_interval, until_interval, step)
        return (time_info, value_list)

    @staticmethod
    def merge(path_from, path_to, step=1 << 12):
        header_from = Whisper.info(path_from)

        archives = header_from['archives']
        archives.sort(key=operator.itemgetter('retention'), reverse=True)

        # Start from max_retention of the oldest file, and skip forward at max
        # 'step'
        # points at a time.
        from_time = int(time.time()) - header_from['max_retention']
        for archive in archives:
            points_remaining = archive['points']
            while points_remaining:
                points_to_read = step
                if points_remaining < step:
                    points_to_read = points_remaining
                points_remaining -= points_to_read
                until_time = from_time + (points_to_read *
                                          archive['seconds_per_point'])
                (time_info, values) = Whisper.fetch(path_from, from_time,
                                                    until_time)
                (start, end, archive_step) = time_info
                points_to_write = list(itertools.ifilter(
                                       lambda points: points[1] is not None,
                                       itertools.izip(xrange(start, end,
                                                             archive_step),
                                                      values)))
                # order points by timestamp,newest first
                points_to_write.sort(key=lambda p: p[0],
                                     reverse=True)
                Whisper.update_many(path_to, points_to_write)
                from_time = until_time
