import struct


def OSType(s):
    return 0 + (ord(s[0]) << 24) + (ord(s[1]) << 16) + (ord(s[2]) << 8) + ord(s[3])


def OSTypeString(n):
    return chr((n & 0xFF000000) >> 24) + chr((n & 0x00FF0000) >> 16) + chr((n & 0x0000FF00) >> 8) + chr(n & 0x000000FF)


def pstring(data, pos, padded=True):
    length = data[pos]
    b = data[pos + 1:pos + 1 + length]
    if padded and length % 2 == 0:
        length += 1
    return b.decode('macroman'), pos + 1 + length


def parse_resources(data):
    data_offset, map_offset, data_len, map_len = struct.unpack('!4L', data[:16])
    # resource map
    fork_attrs, type_list_offset, name_list_offset, num_types = struct.unpack('!4H', data[map_offset + 22:map_offset + 30])
    offset = map_offset + type_list_offset + 2  # already read num_types above
    for i in range(num_types + 1):
        # type list entry
        rsrc_type, num_resources, rsrc_list_offset = struct.unpack('!LHH', data[offset:offset + 8])
        rsrc_offset = map_offset + type_list_offset + rsrc_list_offset
        for k in range(num_resources + 1):
            # reference list entry
            rsrc_id, name_offset, rsrc_info = struct.unpack('!HhL', data[rsrc_offset:rsrc_offset + 8])
            rsrc_attrs = rsrc_info >> 24  # noqa
            rsrc_data_offset = data_offset + (rsrc_info & 0x00FFFFFF)
            rsrc_data_len = struct.unpack('!L', data[rsrc_data_offset:rsrc_data_offset + 4])[0]
            rsrc_data = data[rsrc_data_offset + 4:rsrc_data_offset + 4 + rsrc_data_len]
            if name_offset >= 0:
                rsrc_name_offset = map_offset + name_list_offset + name_offset
                namelen = data[rsrc_name_offset]
                name = data[rsrc_name_offset + 1:rsrc_name_offset + 1 + namelen].decode('macroman')
            else:
                name = ''
            yield rsrc_type, rsrc_id, name, rsrc_data
            rsrc_offset += 12
        offset += 8


def parse_ledi(data):
    set_tag, num_levels = struct.unpack('!LH', data[:6])
    pos = 6
    for i in range(num_levels):
        level_tag = struct.unpack('!L', data[pos:pos + 4])[0]
        pos += 4
        name, pos = pstring(data, pos)
        intro, pos = pstring(data, pos)
        rsrc_name, pos = pstring(data, pos)
        enables, from_file, rsvd, count_enables = struct.unpack('!hHLh', data[pos:pos + 10])
        pos += 10
        count_enables = min(count_enables, 64)
        pos += 4 * count_enables
        yield set_tag, level_tag, name, intro, rsrc_name
