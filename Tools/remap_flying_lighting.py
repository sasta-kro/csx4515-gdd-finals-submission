"""Preserve the source Unity lighting bake and remap its binary asset references.

Unity's text GUID order swaps the nibbles of each byte compared with this native
serialized file. Only metadata external GUID entries are modified. Object data,
including the ambient probe and embedded reflection data, stays unchanged.
"""
from pathlib import Path
import json
import re
import struct

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[1]
SOURCE = WORKSPACE/'w6_Prototype1_v2/Assets/Challenge 1/Challenge 1/LightingData.asset'
TARGET = PROJECT/'Assets/Games/Flying/Challenge 1/Challenge 1/LightingData.asset'


def native_guid(text):
    return bytes.fromhex(''.join(text[i+1]+text[i] for i in range(0, 32, 2)))


def text_guid(raw):
    text = raw.hex()
    return ''.join(text[i+1]+text[i] for i in range(0, 32, 2))


def external_references(data):
    """Read metadata for the Unity 6000.5 format used by the source LightingData.

    Validate and skip complete type-tree and object tables rather than searching
    arbitrary binary payloads for sequences resembling GUIDs.
    """
    assert struct.unpack_from('>I', data, 8)[0] == 23, 'Expected serialized format 23'
    assert data[16] == 0, 'Expected little-endian metadata'
    metadata_size, file_size, data_offset = struct.unpack_from('>Iqq', data, 20)
    assert file_size == len(data)
    pos = 48

    def take(fmt):
        nonlocal pos
        values = struct.unpack_from('<'+fmt, data, pos)
        pos += struct.calcsize('<'+fmt)
        return values[0] if len(values) == 1 else values

    def skip_string():
        nonlocal pos
        pos = data.index(b'\0', pos)+1

    skip_string()  # Editor version.
    take('i')  # Target platform.
    assert take('?'), 'Expected included type trees'
    types = take('i')
    for _ in range(types):
        class_id, stripped, script_index = take('i?h')
        if class_id == 114:
            pos += 16
        pos += 16  # Original type hash.
        pos += 16  # Type-tree information hash.
        tree_size = take('I')
        pos += tree_size
        dependencies = take('i')
        pos += 4*dependencies
    objects = take('i')
    for _ in range(objects):
        pos = (pos+3) & ~3
        take('qqIi')  # Path ID, data offset, data size, type index.
    scripts = take('i')
    for _ in range(scripts):
        take('i')
        pos = (pos+3) & ~3
        take('q')
    count = take('i')
    entries = []
    for _ in range(count):
        skip_string()
        offset = pos
        raw_guid = data[pos:pos+16]
        pos += 16
        asset_type = take('i')
        skip_string()
        entries.append((offset, text_guid(raw_guid), asset_type))
    assert take('i') == 0, 'Unexpected reference type table'
    skip_string()  # User information.
    assert pos == 48+metadata_size, (pos, metadata_size)
    return entries, data_offset


def main():
    manifest = json.loads((PROJECT/'Tools/import-manifest.json').read_text())
    remap = manifest['Flying']['guidRemap']
    original = SOURCE.read_bytes()
    entries, data_offset = external_references(original)
    assert len(entries) == 2, f'Expected scene and reflection references, got {entries}'
    scene_meta = WORKSPACE/'w6_Prototype1_v2/Assets/Challenge 1/Challenge 1.unity.meta'
    reflection_meta = SOURCE.with_name('ReflectionProbe-0.exr.meta')
    expected = {re.search(r'^guid: (\w+)', meta.read_text(), re.M)[1]
                for meta in [scene_meta, reflection_meta]}
    assert {identity for _, identity, _ in entries} == expected
    updated = bytearray(original)
    for offset, old, asset_type in entries:
        assert old in remap and asset_type == 3
        updated[offset:offset+16] = native_guid(remap[old])
    assert updated[data_offset:] == original[data_offset:], 'Lighting payload changed'
    TARGET.write_bytes(updated)
    parsed, _ = external_references(updated)
    assert {identity for _, identity, _ in parsed} == {remap[old] for old in expected}
    print('Remapped binary scene and reflection GUIDs; preserved the complete bake payload.')


if __name__ == '__main__':
    main()
