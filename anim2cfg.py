# Copyright (C) 2019 4d4a5852
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

bl_info = {
    "name": "anim2cfg: Animation to model.cfg",
    "author": "4d4a5852",
    "version": (0, 1, 1),
    "blender": (2, 80, 0),
    "location": "File -> Export",
    "description": "Export animations to Arma 3 model.cfg",
    "warning": "",
    "wiki_url": "https://github.com/4d4a5852/anim2cfg",
    "tracker_url": "https://github.com/4d4a5852/anim2cfg/issues",
    "category": "Import-Export",
    }

import bpy
import bpy_extras
from bpy.utils import register_class, unregister_class
from math import degrees
from mathutils import Matrix, Vector
import re

def sanitize_classname(text):
    return re.sub('[^A-Za-z0-9_]', '_', text)

def export_anim(file, obj, selection_name='', source_name='', parent_name='',
                frame_start=0, frame_end=0, min_value=0.1, max_value=1.0,
                precision=7):
    if frame_start > frame_end:
        frames = range(frame_start, frame_end - 1, -1)
    else:
        frames = range(frame_start, frame_end + 1)
    last = None
    i = 0
    if selection_name == '':
        selection_name = obj.name
    if source_name == '':
        source_name = 'foobar'
    parent_object = None
    parent_matrix = Matrix()
    if parent_name != '':
        try:
            parent_object = bpy.context.scene.objects[parent_name]
        except KeyError:
            return (-1, 0)
    with open(file, 'w') as cfg:
        for f in frames:
            bpy.context.scene.frame_set(f)
            if parent_object is not None:
                parent_matrix = parent_object.matrix_world
            curr = parent_matrix.inverted() @ obj.matrix_world
            if last is not None:
                p = curr.to_translation()
                q = (curr @ last.inverted()).to_quaternion()
                d = p - last.to_translation()
                length = d.length
                if round(length, precision) == 0:
                    d = Vector((1, 0, 0))
                dn = d.normalized()
                q_axis = q.axis.normalized()
                q_angle = degrees(q.angle)
                if round(q_angle, precision) == 0:
                    q_axis = Vector((1, 0, 0))
                curr_min_value = min_value + i*(max_value - min_value)/(len(frames) - 1)
                curr_max_value = min_value + (i + 1)*(max_value - min_value)/(len(frames) - 1)
                cfg.write(f"class {sanitize_classname(selection_name)}_trans_{i} {{\n"
                          f"    type       = direct;\n"
                          f"    source     = {source_name};\n"
                          f"    selection  = {selection_name};\n"
                          f"    axisPos[]  = {{0, 0, 0}};\n"
                          f"    axisDir[]  = {{{dn.x:.{precision}f}, {dn.z:.{precision}f}, {dn.y:.{precision}f}}};\n"
                          f"    angle      = 0;\n"
                          f"    axisOffset = {length:.{precision}f};\n"
                          f"    minValue   = {curr_min_value:.{precision}f};\n"
                          f"    maxValue   = {curr_max_value:.{precision}f};\n"
                          f"}};\n"
                          f"class {sanitize_classname(selection_name)}_rot_{i} {{\n"
                          f"    type       = direct;\n"
                          f"    source     = {source_name};\n"
                          f"    selection  = {selection_name};\n"
                          f"    axisPos[]  = {{{p.x:.{precision}f}, {p.z:.{precision}f}, {p.y:.{precision}f}}};\n"
                          f"    axisDir[]  = {{{q_axis.x:.{precision}f}, {q_axis.z:.{precision}f}, {q_axis.y:.{precision}f}}};\n"
                          f"    angle      = {q_angle:.{precision}f};\n"
                          f"    axisOffset = 0;\n"
                          f"    minValue   = {curr_min_value:.{precision}f};\n"
                          f"    maxValue   = {curr_max_value:.{precision}f};\n"
                          f"}};\n")
                i += 1
            last = curr.copy()
    return (0, i)

class ANIM2CFG_OT_ModelCfgExport(bpy.types.Operator,
                                 bpy_extras.io_utils.ExportHelper):
    bl_idname = "anim2cfg.modelcfgexport"
    bl_label = "Export model.cfg"
    bl_description = "Export model.cfg"
    filename_ext = ".hpp"
    filter_glob: bpy.props.StringProperty(
        default="*.cfg;*.hpp",
        options={'HIDDEN'})
    selection_name: bpy.props.StringProperty(
        name="Selection Name",
        description=("Selection name to be used in the model.cfg.\n"
                     "Defaults to the name of the object"),
        default='')
    source_name: bpy.props.StringProperty(
        name="Source Name",
        description="Source name to be used in the model.cfg",
        default='')
    parent_name: bpy.props.StringProperty(
        name="Parent Object",
        description=("Animations will be exported relative to this object.\n"
                     "When not set the origin will be used"),
        default='')
    frame_start: bpy.props.IntProperty(
        name="Start Frame",
        description="Starting frame to export",
        default=0)
    frame_end: bpy.props.IntProperty(
        name="End Frame",
        description="End frame to export",
        default=0)
    min_value: bpy.props.FloatProperty(
        name = "minValue",
        description="minValue to be used in the model.cfg for the first animation",
        default=0.0)
    max_value: bpy.props.FloatProperty(
        name = "maxValue",
        description="maxValue to be used in the model.cfg for the last animation",
        default=1.0)
    precision: bpy.props.IntProperty(
        name="Precision",
        description="Number of decimal places",
        min=0,
        default=7)

    def invoke(self, context, event):
        self.selection_name = bpy.context.active_object.name
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        return super().invoke(context, event)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column()
        col.prop_search(self, "parent_name", scene, "objects")
        col.prop(self, "frame_start")
        col.prop(self, "frame_end")
        col.label(text="model.cfg")
        col.prop(self, "selection_name")
        col.prop(self, "source_name")
        col.prop(self, "min_value")
        col.prop(self, "max_value")
        col.prop(self, "precision")

    def execute(self, context):
        result, nAnims = export_anim(self.filepath,
                                     bpy.context.active_object,
                                     selection_name=self.selection_name,
                                     source_name=self.source_name,
                                     parent_name=self.parent_name,
                                     frame_start=self.frame_start,
                                     frame_end=self.frame_end,
                                     min_value=self.min_value,
                                     max_value=self.max_value,
                                     precision=self.precision)
        if result == 0:
            self.report({'INFO'}, f"{nAnims + 1} frames exported as {nAnims} animation pairs")
        elif result != 0:
            self.report({'ERROR'}, "Unknown Error")
        return {'FINISHED'}

def ModelCfgExportMenuFunc(self, context):
    self.layout.operator(ANIM2CFG_OT_ModelCfgExport.bl_idname,
                         text="Arma 3 model.cfg (.cfg/.hpp)")

classes = (
    ANIM2CFG_OT_ModelCfgExport,
    )

def register():
    for cls in classes:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(ModelCfgExportMenuFunc)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(ModelCfgExportMenuFunc)
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == '__main__':
    register()
