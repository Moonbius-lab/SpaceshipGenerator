bl_info = {
    "name": "Spaceship Generator",
    "author": "Michael Davies",
    "version": (1, 1, 6),
    "blender": (5, 2, 0),
    "location": "View3D > Add > Mesh; Sidebar > Spaceship",
    "description": "Procedurally generate 3D spaceships from a random seed.",
    "wiki_url": "https://github.com/Moonbius-lab/SpaceshipGenerator/blob/master/README.md",
    "tracker_url": "https://github.com/Moonbius-lab/SpaceshipGenerator/issues",
    "category": "Add Mesh"
}

if "bpy" in locals():
    # reload logic (magic)
    import importlib
    importlib.reload(spaceship_generator)
else:
    from . import spaceship_generator

import bpy
import uuid
from bpy.props import StringProperty, BoolProperty, IntProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup


SETTING_NAMES = (
    'random_seed',
    'num_hull_segments_min',
    'num_hull_segments_max',
    'create_asymmetry_segments',
    'num_asymmetry_segments_min',
    'num_asymmetry_segments_max',
    'create_face_detail',
    'allow_horizontal_symmetry',
    'allow_vertical_symmetry',
    'apply_bevel_modifier',
    'assign_materials',
)


ZH_HANS = {
    'Spaceship Generator': '飞船生成器',
    'Spaceship': '飞船',
    'Procedurally generate 3D spaceships from a random seed.': '通过随机种子程序化生成三维飞船。',
    'View3D > Add > Mesh; Sidebar > Spaceship': '三维视图 > 添加 > 网格；侧栏 > 飞船',
    'Generate Spaceship': '生成飞船',
    'Regenerate Spaceship': '重新生成飞船',
    'Seed': '种子',
    'Hull': '船体',
    'Details': '细节',
    'Finish': '收尾',
    'Min. Hull Segments': '船体最少段数',
    'Max. Hull Segments': '船体最多段数',
    'Create Asymmetry Segments': '生成不对称结构',
    'Min. Asymmetry Segments': '不对称结构最少段数',
    'Max. Asymmetry Segments': '不对称结构最多段数',
    'Create Face Detail': '生成表面细节',
    'Allow Horizontal Symmetry': '允许水平对称',
    'Allow Vertical Symmetry': '允许垂直对称',
    'Apply Bevel Modifier': '添加倒角修改器',
    'Assign Materials': '添加材质',
    'Max. Hull Segments must be at least Min. Hull Segments': '船体最大段数不能小于最小段数',
    'Max. Asymmetry Segments must be at least Min. Asymmetry Segments': '不对称结构最大段数不能小于最小段数',
}
TRANSLATIONS = {
    'zh_HANS': {
        (context, english): chinese
        for context in ('*', 'Operator')
        for english, chinese in ZH_HANS.items()
    }
}


def settings_error(settings):
    if settings.num_hull_segments_max < settings.num_hull_segments_min:
        return 'Max. Hull Segments must be at least Min. Hull Segments'
    if (settings.create_asymmetry_segments and
            settings.num_asymmetry_segments_max < settings.num_asymmetry_segments_min):
        return 'Max. Asymmetry Segments must be at least Min. Asymmetry Segments'
    return None


def update_hull_min(self, context):
    if self.num_hull_segments_min > self.num_hull_segments_max:
        self.num_hull_segments_max = self.num_hull_segments_min


def update_hull_max(self, context):
    if self.num_hull_segments_max < self.num_hull_segments_min:
        self.num_hull_segments_min = self.num_hull_segments_max


def update_asymmetry_min(self, context):
    if self.num_asymmetry_segments_min > self.num_asymmetry_segments_max:
        self.num_asymmetry_segments_max = self.num_asymmetry_segments_min


def update_asymmetry_max(self, context):
    if self.num_asymmetry_segments_max < self.num_asymmetry_segments_min:
        self.num_asymmetry_segments_min = self.num_asymmetry_segments_max


def generate_from_settings(settings):
    if not settings.random_seed:
        settings.random_seed = uuid.uuid4().hex[:12]
    values = {name: getattr(settings, name) for name in SETTING_NAMES}
    return spaceship_generator.generate_spaceship(**values)


def save_settings(obj, settings):
    obj['spaceship_generator'] = True
    for name in SETTING_NAMES:
        setattr(obj.spaceship_settings, name, getattr(settings, name))


def is_spaceship(obj):
    return obj is not None and obj.type == 'MESH' and (
        obj.get('spaceship_generator', False) or obj.name.startswith('Spaceship'))


class SpaceshipSettings(PropertyGroup):
    random_seed: StringProperty(default='', name='Seed')
    num_hull_segments_min: IntProperty(default=3, min=0, soft_max=16, name='Min. Hull Segments', update=update_hull_min)
    num_hull_segments_max: IntProperty(default=6, min=0, soft_max=16, name='Max. Hull Segments', update=update_hull_max)
    create_asymmetry_segments: BoolProperty(default=True, name='Create Asymmetry Segments')
    num_asymmetry_segments_min: IntProperty(default=1, min=1, soft_max=16, name='Min. Asymmetry Segments', update=update_asymmetry_min)
    num_asymmetry_segments_max: IntProperty(default=5, min=1, soft_max=16, name='Max. Asymmetry Segments', update=update_asymmetry_max)
    create_face_detail: BoolProperty(default=True, name='Create Face Detail')
    allow_horizontal_symmetry: BoolProperty(default=True, name='Allow Horizontal Symmetry')
    allow_vertical_symmetry: BoolProperty(default=False, name='Allow Vertical Symmetry')
    apply_bevel_modifier: BoolProperty(default=True, name='Apply Bevel Modifier')
    assign_materials: BoolProperty(default=True, name='Assign Materials')

class GenerateSpaceship(Operator):
    """Procedurally generate 3D spaceships from a random seed."""
    bl_idname = "mesh.generate_spaceship"
    bl_label = "Spaceship"
    bl_options = {'REGISTER', 'UNDO'}

    random_seed : StringProperty(default='', name='Seed')
    num_hull_segments_min      : IntProperty (default=3, min=0, soft_max=16, name='Min. Hull Segments', update=update_hull_min)
    num_hull_segments_max      : IntProperty (default=6, min=0, soft_max=16, name='Max. Hull Segments', update=update_hull_max)
    create_asymmetry_segments  : BoolProperty(default=True, name='Create Asymmetry Segments')
    num_asymmetry_segments_min : IntProperty (default=1, min=1, soft_max=16, name='Min. Asymmetry Segments', update=update_asymmetry_min)
    num_asymmetry_segments_max : IntProperty (default=5, min=1, soft_max=16, name='Max. Asymmetry Segments', update=update_asymmetry_max)
    create_face_detail         : BoolProperty(default=True,  name='Create Face Detail')
    allow_horizontal_symmetry  : BoolProperty(default=True,  name='Allow Horizontal Symmetry')
    allow_vertical_symmetry    : BoolProperty(default=False, name='Allow Vertical Symmetry')
    apply_bevel_modifier       : BoolProperty(default=True,  name='Apply Bevel Modifier')
    assign_materials           : BoolProperty(default=True,  name='Assign Materials')

    def execute(self, context):
        error = settings_error(self)
        if error:
            self.report({'ERROR'}, bpy.app.translations.pgettext_iface(error))
            return {'CANCELLED'}
        obj = generate_from_settings(self)
        save_settings(obj, self)
        return {'FINISHED'}


class RegenerateSpaceship(Operator):
    bl_idname = 'mesh.regenerate_spaceship'
    bl_label = 'Regenerate Spaceship'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return is_spaceship(context.object)

    def execute(self, context):
        old_obj = context.object
        settings = old_obj.spaceship_settings
        error = settings_error(settings)
        if error:
            self.report({'ERROR'}, bpy.app.translations.pgettext_iface(error))
            return {'CANCELLED'}

        old_name = old_obj.name
        old_matrix = old_obj.matrix_world.copy()
        old_collections = tuple(old_obj.users_collection)
        old_mesh = old_obj.data
        old_materials = tuple(
            mat for mat in old_mesh.materials
            if mat is not None and mat.get('spaceship_generator', False))

        new_obj = generate_from_settings(settings)
        save_settings(new_obj, settings)
        new_obj.matrix_world = old_matrix
        for collection in old_collections:
            if collection not in new_obj.users_collection:
                collection.objects.link(new_obj)
        for collection in tuple(new_obj.users_collection):
            if collection not in old_collections:
                collection.objects.unlink(new_obj)

        bpy.data.objects.remove(old_obj, do_unlink=True)
        if old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)
        for material in old_materials:
            if material.users == 0:
                bpy.data.materials.remove(material)
        new_obj.name = old_name
        return {'FINISHED'}


class SpaceshipPanel(Panel):
    bl_idname = 'VIEW3D_PT_spaceship_generator'
    bl_label = 'Spaceship Generator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Spaceship'

    def draw(self, context):
        layout = self.layout
        if not is_spaceship(context.object):
            layout.operator(GenerateSpaceship.bl_idname, text='Generate Spaceship', icon='MESH_ICOSPHERE')
            return

        settings = context.object.spaceship_settings
        layout.prop(settings, 'random_seed')

        hull = layout.column(align=True)
        hull.label(text='Hull')
        hull.prop(settings, 'num_hull_segments_min')
        hull.prop(settings, 'num_hull_segments_max')

        asymmetry = layout.column(align=True)
        asymmetry.prop(settings, 'create_asymmetry_segments')
        if settings.create_asymmetry_segments:
            asymmetry.prop(settings, 'num_asymmetry_segments_min')
            asymmetry.prop(settings, 'num_asymmetry_segments_max')

        detail = layout.column(align=True)
        detail.label(text='Details')
        detail.prop(settings, 'create_face_detail')
        detail.prop(settings, 'allow_horizontal_symmetry')
        detail.prop(settings, 'allow_vertical_symmetry')

        finish = layout.column(align=True)
        finish.label(text='Finish')
        finish.prop(settings, 'apply_bevel_modifier')
        finish.prop(settings, 'assign_materials')
        layout.operator(RegenerateSpaceship.bl_idname, icon='FILE_REFRESH')


def menu_func(self, context):
    self.layout.operator(GenerateSpaceship.bl_idname, text="Spaceship")


CLASSES = (SpaceshipSettings, GenerateSpaceship, RegenerateSpaceship, SpaceshipPanel)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.app.translations.register(__name__, TRANSLATIONS)
    bpy.types.Object.spaceship_settings = PointerProperty(type=SpaceshipSettings)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    del bpy.types.Object.spaceship_settings
    bpy.app.translations.unregister(__name__)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
