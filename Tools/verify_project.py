"""Check imported references, scene wiring, callbacks, and project configuration.

This reads files only. It does not launch Unity or claim to verify gameplay.
"""
from collections import defaultdict
from pathlib import Path
import json
import re
from remap_flying_lighting import external_references

PROJECT = Path(__file__).resolve().parents[1]
ASSETS = PROJECT / 'Assets'
errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def read_guid(meta):
    match = re.search(r'^guid: ([a-f0-9]{32})', meta.read_text(), re.M)
    return match[1] if match else None


def is_builtin(identity):
    return identity.startswith('0000000000000000')


def blocks(text):
    return {int(match[2]): match[3] for match in re.finditer(
        r'^--- !u!(\d+) &(-?\d+)[^\n]*\n(.*?)(?=^--- !u!|\Z)', text, re.M | re.S)}


identities = defaultdict(list)
for meta in ASSETS.rglob('*.meta'):
    identity = read_guid(meta)
    check(identity is not None, f'Metadata has no GUID: {meta}')
    identities[identity].append(Path(str(meta)[:-5]))
for identity, paths in identities.items():
    check(len(paths) == 1, f'Duplicate GUID {identity}: {paths}')
assets_by_guid = {identity: paths[0] for identity, paths in identities.items()}

package_guids = set()
for meta in (PROJECT / 'Library/PackageCache').rglob('*.meta'):
    identity = read_guid(meta)
    if identity:
        package_guids.add(identity)

text_assets = {}
for asset in ASSETS.rglob('*'):
    if not asset.is_file() or asset.suffix == '.meta' or asset.name == '.DS_Store':
        continue
    check(Path(str(asset)+'.meta').exists(), f'Missing metadata: {asset}')
    if asset.suffix not in {'.unity', '.prefab', '.mat', '.asset', '.physicMaterial'}:
        continue
    try:
        text_assets[asset] = asset.read_text()
    except UnicodeDecodeError:
        # Binary source assets are preserved in their native format.
        continue

external_refs = 0
for asset, text in text_assets.items():
    local = blocks(text)
    check(len(local) == len(re.findall(r'^--- !u!\d+ &', text, re.M)),
          f'Duplicate serialized object IDs: {asset}')
    for match in re.finditer(r'\{fileID: (-?\d+)([^}]*)\}', text, re.S):
        file_id, rest = int(match[1]), match[2]
        if file_id == 0:
            continue
        guid_match = re.search(r'guid: ([a-f0-9]{32})', rest)
        if not guid_match:
            check(file_id in local, f'Unresolved local fileID {file_id}: {asset}')
            continue
        identity = guid_match[1]
        external_refs += 1
        check(is_builtin(identity) or identity in assets_by_guid or identity in package_guids,
              f'Unresolved GUID {identity}: {asset}')
        target = assets_by_guid.get(identity)
        if target in text_assets and target.suffix in {'.prefab', '.mat', '.physicMaterial'}:
            check(file_id in blocks(text_assets[target]) or
                  (target.suffix == '.prefab' and file_id == 100100000),
                  f'Unresolved external fileID {file_id} in {target}: {asset}')

# Check persistent menu callbacks against the actual C# types and methods.
callback_count = 0
for asset in [ASSETS/'Scenes/MainMenu.unity', ASSETS/'Prefabs/InGameMenu.prefab']:
    text = text_assets[asset]
    local = blocks(text)
    for call in re.finditer(r'- m_Target: \{fileID: (\d+)\}\s+'
                            r'm_TargetAssemblyTypeName: ([^\n]+)\s+'
                            r'm_MethodName: (\w+)', text):
        target_id, qualified_type, method = int(call[1]), call[2], call[3]
        callback_count += 1
        controller = local.get(target_id, '')
        script_ref = re.search(r'm_Script: .*?guid: (\w+)', controller)
        check(script_ref is not None, f'Button has no target controller: {asset} {method}')
        if script_ref is None:
            continue
        script = assets_by_guid.get(script_ref[1])
        check(script is not None and script.suffix == '.cs', f'Invalid script for {method}')
        if script is None:
            continue
        code = script.read_text()
        namespace = re.search(r'namespace ([\w.]+)', code)[1]
        class_name = re.search(r'public sealed class (\w+)', code)[1]
        check(qualified_type == f'{namespace}.{class_name}, Assembly-CSharp',
              f'Wrong callback type for {method}: {qualified_type}')
        check(re.search(r'public void ' + method + r'\(', code), f'Missing public callback {method}')
    # Serialized controller references must resolve to nonzero local objects.
    for field in re.finditer(r'^  (firstSelected|pauseCanvas|hudCanvas|controlsText): \{fileID: (\d+)\}', text, re.M):
        check(int(field[2]) in local, f'Unassigned {field[1]}: {asset}')
check(callback_count == 8, f'Expected 8 menu and HUD callbacks, found {callback_count}')

build = (PROJECT/'ProjectSettings/EditorBuildSettings.asset').read_text()
entries = re.findall(r'- enabled: 1\s+path: ([^\n]+)\s+guid: (\w+)', build)
check(len(entries) == 4, f'Expected four enabled scenes, found {len(entries)}')
check(entries and entries[0][0] == 'Assets/Scenes/MainMenu.unity', 'MainMenu must be first')
check([Path(path).stem for path, _ in entries] == ['MainMenu', 'Driving', 'Flying', 'Sumo'],
      'Unexpected build-scene names or order')
for path, identity in entries:
    target = PROJECT/path
    check(target.exists(), f'Build scene missing: {path}')
    check(read_guid(Path(str(target)+'.meta')) == identity, f'Build scene GUID mismatch: {path}')

prefab_guid = read_guid(ASSETS/'Prefabs/InGameMenu.prefab.meta')
for path, _ in entries[1:]:
    text = (PROJECT/path).read_text()
    check(len(re.findall(r'm_SourcePrefab: \{[^}]*guid: '+prefab_guid, text)) == 1,
          f'Expected one shared pause-menu instance in {path}')
    if Path(path).stem == 'Flying':
        lighting = ASSETS/'Games/Flying/Challenge 1/Challenge 1/LightingData.asset'
        check(lighting.exists(), 'Flying baked lighting is missing')
        if lighting.exists():
            lighting_guid = read_guid(Path(str(lighting)+'.meta'))
            check(f'm_LightingDataAsset: {{fileID: 112000000, guid: {lighting_guid}, type: 2}}' in text,
                  'Flying is not connected to its preserved lighting bake')
            binary_refs, _ = external_references(lighting.read_bytes())
            for _, identity, _ in binary_refs:
                check(identity in assets_by_guid, f'Unresolved binary lighting GUID: {identity}')
            check({assets_by_guid[identity].suffix for _, identity, _ in binary_refs
                   if identity in assets_by_guid} == {'.unity', '.exr'},
                  'Flying bake must reference its imported scene and reflection probe')

mist = ASSETS/'Games/Sumo/Course Library/_Source_Files/Materials/FX_Mist.prefab'
check('  m_IsActive: 1' in text_assets[mist], 'Sumo mist must stay enabled')
for game in ['Driving', 'Flying', 'Sumo']:
    sky = next((ASSETS/'Games'/game).rglob('SkyDome.prefab'))
    decoration_count = 0
    for obj in blocks(text_assets[sky]).values():
        if re.search(r'^  m_Name: (Sun|Moon|Stars)$', obj, re.M):
            decoration_count += 1
            check('  m_IsActive: 0' in obj, f'Square sky decoration enabled in {sky}')
    check(decoration_count == 3, f'Expected three sky-decoration roots in {sky}')

for script in (ASSETS/'Games').rglob('*.cs'):
    code = script.read_text()
    for body in re.finditer(r'void (Update|LateUpdate)\(\)\s*\{([^}]+)', code):
        check(body[2].lstrip().startswith('if (Time.timeScale == 0f) return;'),
              f'Gameplay update has no pause guard: {script}')
settings = (PROJECT/'ProjectSettings/ProjectSettings.asset').read_text()
check('activeInputHandler: 0' in settings, 'Legacy input is not enabled')
graphics = (PROJECT/'ProjectSettings/GraphicsSettings.asset').read_text()
check('m_CustomRenderPipeline: {fileID: 0}' in graphics, 'Default renderer is not built-in')
check('m_LightsUseLinearIntensity: 0' in graphics and 'm_LightsUseColorTemperature: 0' in graphics,
      'Lighting intensity conventions differ from the tutorial projects')
quality = (PROJECT/'ProjectSettings/QualitySettings.asset').read_text()
check(all(value.strip() == 'fileID: 0' for value in re.findall(r'customRenderPipeline: \{([^}]+)\}', quality)),
      'A quality level still enables an SRP renderer')
tags = (PROJECT/'ProjectSettings/TagManager.asset').read_text()
for tag in ['Enemy', 'Powerup', 'Projectile']:
    check(f'  - {tag}\n' in tags, f'Missing sumo tag: {tag}')

manifest = json.loads((PROJECT/'Tools/import-manifest.json').read_text())
old_guids = {identity for info in manifest.values() for identity in info['guidRemap']}
for asset, text in text_assets.items():
    if 'Games' in asset.parts:
        check(not old_guids.intersection(re.findall(r'guid: (\w+)', text)),
              f'An imported asset still references a source GUID: {asset}')

if errors:
    print('\n'.join(errors))
    raise SystemExit(f'FAIL: {len(errors)} problems')
print(f'PASS: {len(identities)} unique asset GUIDs; {external_refs} external references resolved.')
print('PASS: native object references, eight callbacks, four build scenes, and three pause instances.')
print('PASS: legacy input, built-in renderer, sumo tags, imported GUIDs, and pause guards.')
