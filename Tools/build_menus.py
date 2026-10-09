"""Build editable Unity menu assets without opening the editor.

Run from any directory with Python 3. This only replaces the generated menu scene,
pause prefab, their metadata, and the final project's build-scene list.
"""
from pathlib import Path
import json
import re
import uuid

PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[1]
ASSETS = PROJECT / 'Assets'
PACKAGE = next((PROJECT / 'Library/PackageCache').glob('com.unity.ugui@*'))
HEADER = '%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n'
NAVY = (0.055, 0.09, 0.13, 1)
PANEL = (0.085, 0.14, 0.19, 1)
CREAM = (0.94, 0.95, 0.9, 1)
MUTED = (0.65, 0.75, 0.76, 1)
ORANGE = (1, 0.60, 0.32, 1)


def guid(path):
    return uuid.uuid5(uuid.NAMESPACE_URL, 'CSX4515/ThreeInOne/' + path).hex


def package_guid(filename):
    matches = list((PACKAGE / 'Runtime/UGUI').rglob(filename + '.meta'))
    assert len(matches) == 1, matches
    return re.search(r'^guid: (\w+)', matches[0].read_text(), re.M)[1]


def script_guid(name):
    return guid(f'Assets/Scripts/Menus/{name}.cs')


def color(rgba):
    return '{' + ', '.join(f'{key}: {value}' for key, value in zip('rgba', rgba)) + '}'


def ref(value):
    return f'{{fileID: {value}}}'


def metadata(path, kind):
    identity = guid(str(path.relative_to(PROJECT)))
    Path(str(path) + '.meta').write_text(
        f'fileFormatVersion: 2\nguid: {identity}\n{kind}:\n'
        '  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
    return identity


class UnityAsset:
    def __init__(self):
        self.next_id = 700000000
        self.nodes = []
        self.components = []

    def allocate(self):
        self.next_id += 1
        return self.next_id

    def node(self, name, parent=None, rect=True, pos=(0, 0), size=(0, 0),
             anchors=((0.5, 0.5), (0.5, 0.5)), pivot=(0.5, 0.5), active=True):
        node = dict(go=self.allocate(), transform=self.allocate(), name=name,
                    parent=parent, rect=rect, pos=pos, size=size, anchors=anchors,
                    pivot=pivot, active=active, children=[], components=[])
        self.nodes.append(node)
        if parent:
            parent['children'].append(node)
        return node

    def component(self, node, class_id, type_name, fields):
        identity = self.allocate()
        item = dict(identity=identity, node=node, class_id=class_id,
                    type_name=type_name, fields=fields)
        self.components.append(item)
        node['components'].append(identity)
        return item

    def mono(self, node, script, fields):
        return self.component(node, 114, 'MonoBehaviour',
            f'  m_Enabled: 1\n  m_EditorHideFlags: 0\n'
            f'  m_Script: {{fileID: 11500000, guid: {script}, type: 3}}\n'
            f'  m_Name: \n  m_EditorClassIdentifier: \n{fields}')

    def canvas(self, name, parent=None, order=0, active=True):
        node = self.node(name, parent, active=active, anchors=((0, 0), (1, 1)))
        self.component(node, 223, 'Canvas',
            '  m_Enabled: 1\n  serializedVersion: 3\n  m_RenderMode: 0\n'
            '  m_Camera: {fileID: 0}\n  m_PlaneDistance: 100\n  m_PixelPerfect: 0\n'
            '  m_ReceivesEvents: 1\n  m_OverrideSorting: 1\n'
            '  m_OverridePixelPerfect: 0\n  m_SortingBucketNormalizedSize: 0\n'
            '  m_VertexColorAlwaysGammaSpace: 0\n  m_AdditionalShaderChannelsFlag: 25\n'
            f'  m_SortingLayerID: 0\n  m_SortingOrder: {order}\n  m_TargetDisplay: 0\n')
        self.mono(node, package_guid('CanvasScaler.cs'),
            '  m_UiScaleMode: 1\n  m_ReferencePixelsPerUnit: 100\n  m_ScaleFactor: 1\n'
            '  m_ReferenceResolution: {x: 1280, y: 720}\n  m_ScreenMatchMode: 0\n'
            '  m_MatchWidthOrHeight: 0.5\n  m_PhysicalUnit: 3\n'
            '  m_FallbackScreenDPI: 96\n  m_DefaultSpriteDPI: 96\n'
            '  m_DynamicPixelsPerUnit: 1\n  m_PresetInfoIsWorld: 0\n')
        self.mono(node, package_guid('GraphicRaycaster.cs'),
            '  m_IgnoreReversedGraphics: 1\n  m_BlockingObjects: 0\n'
            '  m_BlockingMask:\n    serializedVersion: 2\n    m_Bits: 4294967295\n')
        return node

    def graphic_fields(self, rgba, raycast):
        return ('  m_Material: {fileID: 0}\n' + f'  m_Color: {color(rgba)}\n'
                f'  m_RaycastTarget: {int(raycast)}\n'
                '  m_RaycastPadding: {x: 0, y: 0, z: 0, w: 0}\n'
                '  m_Maskable: 1\n  m_OnCullStateChanged:\n'
                '    m_PersistentCalls:\n      m_Calls: []\n')

    def image(self, node, rgba, raycast=False):
        self.component(node, 222, 'CanvasRenderer', '  m_CullTransparentMesh: 1\n')
        return self.mono(node, package_guid('Image.cs'), self.graphic_fields(rgba, raycast) +
            '  m_Sprite: {fileID: 0}\n  m_Type: 0\n  m_PreserveAspect: 0\n'
            '  m_FillCenter: 1\n  m_FillMethod: 4\n  m_FillAmount: 1\n'
            '  m_FillClockwise: 1\n  m_FillOrigin: 0\n  m_UseSpriteMesh: 0\n'
            '  m_PixelsPerUnitMultiplier: 1\n')

    def text(self, name, parent, value, pos, size, font_size=24, rgba=CREAM,
             alignment=4, bold=False, anchors=((0.5, 0.5), (0.5, 0.5)), pivot=(0.5, 0.5)):
        node = self.node(name, parent, pos=pos, size=size, anchors=anchors, pivot=pivot)
        self.component(node, 222, 'CanvasRenderer', '  m_CullTransparentMesh: 1\n')
        item = self.mono(node, package_guid('Text.cs'), self.graphic_fields(rgba, False) +
            '  m_FontData:\n'
            '    m_Font: {fileID: 12800000, guid: 0000000000000000e000000000000000, type: 0}\n'
            f'    m_FontSize: {font_size}\n    m_FontStyle: {int(bold)}\n'
            '    m_BestFit: 0\n    m_MinSize: 10\n    m_MaxSize: 60\n'
            f'    m_Alignment: {alignment}\n    m_AlignByGeometry: 0\n'
            '    m_RichText: 0\n    m_HorizontalOverflow: 0\n'
            '    m_VerticalOverflow: 0\n    m_LineSpacing: 1\n'
            f'  m_Text: {json.dumps(value)}\n')
        return node, item

    def button(self, name, parent, label, method, controller, pos, size=(540, 64),
               controller_type='MainMenuController', font_size=26,
               anchors=((0.5, 0.5), (0.5, 0.5)), pivot=(0.5, 0.5)):
        node = self.node(name, parent, pos=pos, size=size, anchors=anchors, pivot=pivot)
        image = self.image(node, CREAM, True)
        item = self.mono(node, package_guid('Button.cs'),
            '  m_Navigation:\n    m_Mode: 4\n    m_WrapAround: 1\n'
            '    m_SelectOnUp: {fileID: 0}\n    m_SelectOnDown: {fileID: 0}\n'
            '    m_SelectOnLeft: {fileID: 0}\n    m_SelectOnRight: {fileID: 0}\n'
            '  m_Transition: 1\n  m_Colors:\n'
            '    m_NormalColor: {r: 1, g: 1, b: 1, a: 1}\n'
            '    m_HighlightedColor: {r: 0.56, g: 0.94, b: 0.85, a: 1}\n'
            '    m_PressedColor: {r: 0.38, g: 0.72, b: 0.65, a: 1}\n'
            '    m_SelectedColor: {r: 0.56, g: 0.94, b: 0.85, a: 1}\n'
            '    m_DisabledColor: {r: 0.5, g: 0.5, b: 0.5, a: 0.5}\n'
            '    m_ColorMultiplier: 1\n    m_FadeDuration: 0.1\n'
            '  m_SpriteState:\n    m_HighlightedSprite: {fileID: 0}\n'
            '    m_PressedSprite: {fileID: 0}\n    m_SelectedSprite: {fileID: 0}\n'
            '    m_DisabledSprite: {fileID: 0}\n'
            '  m_AnimationTriggers:\n    m_NormalTrigger: Normal\n'
            '    m_HighlightedTrigger: Highlighted\n    m_PressedTrigger: Pressed\n'
            '    m_SelectedTrigger: Selected\n    m_DisabledTrigger: Disabled\n'
            f'  m_Interactable: 1\n  m_TargetGraphic: {ref(image["identity"])}\n'
            '  m_OnClick:\n    m_PersistentCalls:\n      m_Calls:\n'
            f'      - m_Target: {ref(controller["identity"])}\n'
            f'        m_TargetAssemblyTypeName: ThreeInOne.Menus.{controller_type}, Assembly-CSharp\n'
            f'        m_MethodName: {method}\n        m_Mode: 1\n'
            '        m_Arguments:\n          m_ObjectArgument: {fileID: 0}\n'
            '          m_ObjectArgumentAssemblyTypeName: UnityEngine.Object, UnityEngine\n'
            '          m_IntArgument: 0\n          m_FloatArgument: 0\n'
            '          m_StringArgument: \n          m_BoolArgument: 0\n'
            '        m_CallState: 2\n')
        self.text('Label', node, label, (0, 0), (size[0] - 24, size[1] - 8),
                  font_size=font_size, rgba=NAVY, bold=True)
        return node, item

    def navigation(self, buttons):
        for i, (_, item) in enumerate(buttons):
            for direction, destination in [('Up', buttons[(i-1) % len(buttons)][1]),
                                           ('Down', buttons[(i+1) % len(buttons)][1])]:
                item['fields'] = item['fields'].replace(
                    f'm_SelectOn{direction}: {{fileID: 0}}',
                    f'm_SelectOn{direction}: {ref(destination["identity"])}')

    def event_system(self, parent=None, first=None):
        node = self.node('EventSystem', parent, rect=False)
        self.mono(node, package_guid('EventSystem.cs'),
            f'  m_FirstSelected: {ref(first["go"] if first else 0)}\n'
            '  m_sendNavigationEvents: 1\n  m_DragThreshold: 10\n')
        self.mono(node, package_guid('StandaloneInputModule.cs'),
            '  m_SendPointerHoverToParent: 1\n  m_HorizontalAxis: Horizontal\n'
            '  m_VerticalAxis: Vertical\n  m_SubmitButton: Submit\n'
            '  m_CancelButton: Cancel\n  m_InputActionsPerSecond: 10\n'
            '  m_RepeatDelay: 0.5\n  m_ForceModuleActive: 0\n')

    def serialize(self):
        output = ''
        def block(class_id, identity, name, fields, go=None):
            common = ('  m_ObjectHideFlags: 0\n  m_CorrespondingSourceObject: {fileID: 0}\n'
                      '  m_PrefabInstance: {fileID: 0}\n  m_PrefabAsset: {fileID: 0}\n')
            if go:
                common += f'  m_GameObject: {ref(go)}\n'
            return f'--- !u!{class_id} &{identity}\n{name}:\n' + common + fields
        for node in self.nodes:
            components = [node['transform']] + node['components']
            output += block(1, node['go'], 'GameObject',
                '  serializedVersion: 6\n  m_Component:\n' +
                ''.join(f'  - component: {ref(c)}\n' for c in components) +
                f'  m_Layer: {5 if node["rect"] else 0}\n  m_Name: {json.dumps(node["name"])}\n'
                '  m_TagString: Untagged\n  m_Icon: {fileID: 0}\n'
                '  m_NavMeshLayer: 0\n  m_StaticEditorFlags: 0\n'
                f'  m_IsActive: {int(node["active"])}\n')
            children = ''.join(f'  - {ref(c["transform"])}\n' for c in node['children'])
            fields = ('  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}\n'
                      '  m_LocalPosition: {x: 0, y: 0, z: 0}\n'
                      '  m_LocalScale: {x: 1, y: 1, z: 1}\n'
                      '  m_ConstrainProportionsScale: 0\n' +
                      ('  m_Children:\n' + children if children else '  m_Children: []\n') +
                      f'  m_Father: {ref(node["parent"]["transform"] if node["parent"] else 0)}\n'
                      '  m_RootOrder: 0\n  m_LocalEulerAnglesHint: {x: 0, y: 0, z: 0}\n')
            if node['rect']:
                lo, hi = node['anchors']; x, y = node['pos']; w, h = node['size']; px, py = node['pivot']
                fields += (f'  m_AnchorMin: {{x: {lo[0]}, y: {lo[1]}}}\n'
                           f'  m_AnchorMax: {{x: {hi[0]}, y: {hi[1]}}}\n'
                           f'  m_AnchoredPosition: {{x: {x}, y: {y}}}\n'
                           f'  m_SizeDelta: {{x: {w}, y: {h}}}\n'
                           f'  m_Pivot: {{x: {px}, y: {py}}}\n')
            output += block(224 if node['rect'] else 4, node['transform'],
                            'RectTransform' if node['rect'] else 'Transform', fields, node['go'])
        for item in self.components:
            output += block(item['class_id'], item['identity'], item['type_name'],
                            item['fields'], item['node']['go'])
        return output


# Main menu is a saved scene with native uGUI objects and persistent button actions.
main = UnityAsset()
canvas = main.canvas('Main Menu')
controller = main.mono(canvas, script_guid('MainMenuController'), '')
background = main.node('Background', canvas, anchors=((0, 0), (1, 1)))
main.image(background, NAVY, True)
main.text('Course', canvas, 'THREE-IN-ONE GAME', (0, 278), (880, 30), 18, ORANGE, bold=True)
main.text('Title', canvas, 'Three Ways to Play', (0, 225), (960, 74), 54, bold=True)
main.text('Subtitle', canvas, 'Drive the road. Fly the course. Survive the arena.', (0, 168), (900, 38), 22, MUTED)
line = main.node('Accent', canvas, pos=(0, 130), size=(64, 4))
main.image(line, ORANGE)
buttons = []
for i, (name, label, action) in enumerate([
    ('Driving Button', 'Mad Driver', 'PlayDriving'),
    ('Flying Button', 'Fly Like a Bird', 'PlayFlying'),
    ('Sumo Button', "I'm a Sumo and a Ball", 'PlaySumo'),
    ('Exit Button', 'Exit', 'ExitGame'),
]):
    buttons.append(main.button(name, canvas, label, action, controller, (0, 70 - 78*i)))
main.navigation(buttons)
controller['fields'] += f'  firstSelected: {ref(buttons[0][0]["go"])}\n'
main.text('Navigation Hint', canvas, 'Click to select  |  Up/Down + Enter', (30, 26), (600, 40), 17,
          MUTED, alignment=3, anchors=((0, 0), (0, 0)), pivot=(0, 0))
main.text('Author', canvas, 'By Sai Aike Shwe Tun Aung', (-30, 26), (520, 40), 18,
          CREAM, alignment=5, anchors=((1, 0), (1, 0)), pivot=(1, 0))
main.event_system(first=buttons[0][0])
scene = ASSETS / 'Scenes/MainMenu.unity'
base_scene = (WORKSPACE / 'w6_Prototype1_v2/Assets/Scenes/SampleScene.unity').read_text()
scene.write_text(base_scene + main.serialize())
main_guid = metadata(scene, 'DefaultImporter')

# One shared prefab contains the HUD, hidden pause canvas, and its EventSystem.
pause = UnityAsset()
root = pause.node('In-Game Menu', rect=False)
controller = pause.mono(root, script_guid('GameMenuController'), '')
hud = pause.canvas('Game HUD', root, order=10)
controls, controls_component = pause.text('Controls', hud, 'Game controls', (24, 18), (990, 58), 17,
    CREAM, alignment=3, anchors=((0, 0), (0, 0)), pivot=(0, 0))
# A dark backing keeps controls readable against the sky and terrain.
backing = pause.node('Controls Background', hud, pos=(16, 18), size=(1000, 58),
                     anchors=((0, 0), (0, 0)), pivot=(0, 0))
pause.image(backing, (0.035, 0.06, 0.09, 0.86))
hud['children'].remove(backing)
hud['children'].insert(0, backing)
pause.button('Pause Button', hud, 'Pause [Esc]', 'PauseGame', controller, (-24, -24),
    size=(176, 44), controller_type='GameMenuController', font_size=20,
    anchors=((1, 1), (1, 1)), pivot=(1, 1))
overlay = pause.canvas('Pause Menu', root, order=100, active=False)
scrim = pause.node('Dim Background', overlay, anchors=((0, 0), (1, 1)))
pause.image(scrim, (0.015, 0.025, 0.04, 0.86), True)
panel = pause.node('Pause Panel', overlay, size=(600, 478))
pause.image(panel, PANEL, True)
line = pause.node('Accent', panel, pos=(0, 222), size=(600, 4))
pause.image(line, ORANGE)
pause.text('Pause Title', panel, 'PAUSED', (0, 152), (520, 70), 48, bold=True)
pause.text('Pause Subtitle', panel, 'Take a breath. Pick your next move.', (0, 99), (530, 36), 20, MUTED)
buttons = []
for i, (name, label, action) in enumerate([
    ('Resume Button', 'Resume', 'ResumeGame'),
    ('Restart Button', 'Restart', 'RestartGame'),
    ('Main Menu Button', 'Back to Main Menu', 'BackToMainMenu'),
]):
    buttons.append(pause.button(name, panel, label, action, controller, (0, 30 - 78*i),
                               size=(480, 62), controller_type='GameMenuController', font_size=25))
pause.navigation(buttons)
pause.text('Resume Hint', panel, 'Esc to resume  |  Up/Down + Enter to select', (0, -197),
           (540, 30), 17, MUTED)
controller['fields'] += (f'  pauseCanvas: {ref(overlay["go"])}\n  hudCanvas: {ref(hud["go"])}\n'
                        f'  firstSelected: {ref(buttons[0][0]["go"])}\n'
                        f'  controlsText: {ref(controls_component["identity"])}\n')
pause.event_system(root)
prefab = ASSETS / 'Prefabs/InGameMenu.prefab'
prefab.write_text(HEADER + pause.serialize())
prefab_guid = metadata(prefab, 'PrefabImporter')

manifest = json.loads((PROJECT / 'Tools/import-manifest.json').read_text())
for game, info in manifest.items():
    target = PROJECT / info['scene']
    text = target.read_text()
    marker = '--- !u!1001 &700090000\n'
    if marker in text:
        text = text.split(marker)[0]
    text += (marker + 'PrefabInstance:\n  m_ObjectHideFlags: 0\n  serializedVersion: 2\n'
             '  m_Modification:\n    serializedVersion: 3\n'
             '    m_TransformParent: {fileID: 0}\n    m_Modifications:\n'
             f'    - target: {{fileID: {root["transform"]}, guid: {prefab_guid}, type: 3}}\n'
             '      propertyPath: m_RootOrder\n      value: 99\n'
             '      objectReference: {fileID: 0}\n'
             '    m_RemovedComponents: []\n    m_RemovedGameObjects: []\n'
             '    m_AddedGameObjects: []\n    m_AddedComponents: []\n'
             f'  m_SourcePrefab: {{fileID: 100100000, guid: {prefab_guid}, type: 3}}\n')
    target.write_text(text)

build = HEADER + '--- !u!1045 &1\nEditorBuildSettings:\n  m_ObjectHideFlags: 0\n  serializedVersion: 2\n  m_Scenes:\n'
for path, identity in [('Assets/Scenes/MainMenu.unity', main_guid)] + [
    (info['scene'], re.search(r'^guid: (\w+)', Path(str(PROJECT / info['scene']) + '.meta').read_text(), re.M)[1])
    for info in manifest.values()
]:
    build += f'  - enabled: 1\n    path: {path}\n    guid: {identity}\n'
build += '  m_configObjects: {}\n  m_UseUCBPForAssetBundles: 0\n'
(PROJECT / 'ProjectSettings/EditorBuildSettings.asset').write_text(build)

# All newly created folders receive stable metadata, including imported game roots.
for folder in sorted((p for p in ASSETS.rglob('*') if p.is_dir()), key=str):
    meta = Path(str(folder) + '.meta')
    if not meta.exists():
        meta.write_text(f'fileFormatVersion: 2\nguid: {guid(str(folder.relative_to(PROJECT)))}\n'
                        'folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n'
                        '  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
print('Created MainMenu.unity, InGameMenu.prefab, and four enabled build scenes.')
