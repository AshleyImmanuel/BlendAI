import bpy # type: ignore # noqa: F401
import requests
import threading
import json
import time
import subprocess
import sys
import os

bl_info = {
    "name": "BlendAI Swarm",
    "author": "Ashley Immanuel",
    "version": (1, 7, 0),
    "blender": (3, 0, 0),
    "location": "Edit > Preferences > Addons > BlendAI | View3D > Sidebar",
    "description": "EXPERIMENTAL: Use at your own risk. The author (Ashley Immanuel) is not responsible for data loss. Sorry for any trouble caused. (v1.7.0 Swarm)",
    "category": "Object",
}

# --- PREFERENCES & SETTINGS ---
class BLENDAI_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    api_key: bpy.props.StringProperty(  # type: ignore
        name="API Key",
        description="Enter your OpenAI-compatible API Key",
        default="",
        subtype='PASSWORD'
    )
    custom_base_url: bpy.props.StringProperty(  # type: ignore
        name="API Base URL",
        description="Custom endpoint for local AI (e.g. http://localhost:11434/v1 for Ollama)",
        default="https://api.openai.com/v1",
    )
    model: bpy.props.StringProperty(  # type: ignore
        name="Model",
        description="Select AI Model",
        default="gpt-4o"
    )
    server_url: bpy.props.StringProperty(  # type: ignore
        name="Server URL",
        description="Backend URL (leave as default unless customized)",
        default="http://localhost:8000"
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Master Configuration", icon='SETTINGS')
        
        column = layout.column(align=True)
        column.prop(self, "api_key")
        column.prop(self, "model")
        column.prop(self, "server_url")
        
        layout.separator()
        layout.label(text="Environment Management", icon='PREFERENCES')
        row = layout.row()
        row.operator("blendai.install_deps", icon='FILE_REFRESH', text="Prepare Environment")
        row.operator("blendai.start_server", icon='PLAY', text="Launch AI Backend")

# --- OPERATORS ---
class BLENDAI_OT_InstallDeps(bpy.types.Operator):
    """Automatically installs necessary libraries into Blender's Python"""
    bl_idname = "blendai.install_deps" # type: ignore
    bl_label = "Install Dependencies" # type: ignore
    
    def execute(self, context):
        self.report({'INFO'}, "[INFO] BlendAI: Initializing environment install...")
        try:
            python_path = sys.executable
            # Ensure we're using the correct internal python binary
            if hasattr(bpy.app, "binary_path_python"):
                python_path = bpy.app.binary_path_python

            subprocess.check_call([python_path, "-m", "pip", "install", "fastapi", "uvicorn", "openai", "requests", "pydantic", "python-multipart"])
            self.report({'INFO'}, "[SUCCESS] BlendAI: Environment is READY!")
        except Exception as e:
            self.report({'ERROR'}, f"[ERROR] BlendAI: Install Failed: {str(e)}")
        return {'FINISHED'}

class BLENDAI_OT_StartServer(bpy.types.Operator):
    """Launches the BlendAI Backend in a detached background process"""
    bl_idname = "blendai.start_server" # type: ignore
    bl_label = "Start Backend" # type: ignore
    
    def execute(self, context):
        try:
            # Locate main.py relative to this file
            addon_dir = os.path.dirname(os.path.abspath(__file__))
            backend_path = os.path.join(addon_dir, "backend", "main.py")
            
            # Search parent if not in subfolder
            if not os.path.exists(backend_path):
                backend_path = os.path.join(os.path.dirname(addon_dir), "backend", "main.py")

            if not os.path.exists(backend_path):
                self.report({'ERROR'}, f"[ERROR] BlendAI: backend/main.py not found at {backend_path}")
                return {'CANCELLED'}

            # Launch detached
            subprocess.Popen([sys.executable, backend_path], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            self.report({'INFO'}, "[STARTING] BlendAI: Backend launched in the background.")
        except Exception as e:
            self.report({'ERROR'}, f"[ERROR] BlendAI: Failed to start server: {str(e)}")
        return {'FINISHED'}

class BLENDAI_Properties(bpy.types.PropertyGroup):
    """Local scene properties for the session"""
    prompt: bpy.props.StringProperty(name="Prompt", default="") # type: ignore
    is_running: bpy.props.BoolProperty(default=False) # type: ignore
    last_error: bpy.props.StringProperty(default="") # type: ignore
    session_id: bpy.props.StringProperty(default="user_scene") # type: ignore

class BLENDAI_OT_RunSwarm(bpy.types.Operator):
    """The Master Execution Operator with UX Toasts"""
    bl_idname = "blendai.run_swarm" # type: ignore
    bl_label = "Invoke Swarm" # type: ignore
    
    _timer = None
    _thread = None
    _result = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            if self._result is not None:
                self.process_result(context)
                context.scene.blendai_props.is_running = False
                return {'FINISHED'}
            if not self._thread.is_alive():
                context.scene.blendai_props.is_running = False
                self.report({'WARNING'}, "[WARNING] BlendAI: Swarm communication lost.")
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        props = context.scene.blendai_props
        
        # UI Safety Guard
        if props.is_running:
            self.report({'WARNING'}, "Wait for the current Swarm to finish!")
            return {'CANCELLED'}

        prefs = context.preferences.addons[__package__ if __package__ else __name__].preferences
        
        if not prefs.api_key:
            self.report({'ERROR'}, "[ERROR] API Key missing! Check Addon Preferences.")
            return {'CANCELLED'}

        if not props.prompt:
            self.report({'WARNING'}, "Please enter a command first.")
            return {'CANCELLED'}

        props.is_running = True
        props.last_error = ""
        self.report({'INFO'}, "BlendAI: Swarm is collaborating...")
        
        self._thread = threading.Thread(target=self.call_backend, args=(props, prefs))
        self._thread.start()
        
        self._timer = context.window_manager.event_timer_add(0.2, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def call_backend(self, props, prefs):
        try:
            payload = {
                "prompt": props.prompt,
                "api_key": prefs.api_key,
                "session_id": props.session_id,
                "model": prefs.model,
                "base_url": prefs.custom_base_url
            }
            # Extended timeout for complex swarm discussion turns
            response = requests.post(f"{prefs.server_url}/run", json=payload, timeout=180) 
            if response.status_code == 200:
                self._result = response.json()
            elif response.status_code == 429:
                props.last_error = "Rate Limit Exceeded. Please wait 60s."
                self._result = False
            else:
                props.last_error = f"Error {response.status_code}: {response.text}"
                self._result = False
        except Exception as e:
            props.last_error = "Server Offline. Click 'Launch AI Backend' in Preferences."
            self._result = False

    def process_result(self, context):
        props = context.scene.blendai_props
        if self._result and "code" in self._result:
            code = self._result["code"]
            
            # Evolution Notification
            if "new_skill" in self._result and self._result["new_skill"]:
                skill_name = self._result["new_skill"]
                self.report({'INFO'}, f"[EVOLUTION] New Skill Learned: {skill_name}")

            try:
                # Security Audit should have happened in the Swarm Manager
                exec_globals = {"bpy": bpy, "math": __import__('math'), "mathutils": __import__('mathutils')}
                exec(code, exec_globals)
                self.report({'INFO'}, "[SUCCESS] BlendAI: Swarm Task Completed!")
            except Exception as e:
                self.report({'ERROR'}, f"[ERROR] Python Error: {str(e)}")
                props.last_error = str(e)
        context.window_manager.event_timer_remove(self._timer)

class VIEW3D_PT_blendai_panel(bpy.types.Panel):
    bl_label = "BlendAI"
    bl_idname = "VIEW3D_PT_blendai_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendAI'

    def draw(self, context):
        layout = self.layout
        props = context.scene.blendai_props
        
        box = layout.box()
        box.prop(props, "prompt", text="Command")
        
        row = layout.row()
        row.scale_y = 1.6
        if props.is_running:
            row.label(text="Collaborating...", icon='URL')
        else:
            row.operator("blendai.run_swarm", icon='PLAY', text="Run BlendAI Swarm")

        if props.last_error:
            err = layout.box()
            err.label(text="Troubleshooting:", icon='ERROR')
            err.label(text=props.last_error)

classes = (
    BLENDAI_AddonPreferences,
    BLENDAI_OT_InstallDeps,
    BLENDAI_OT_StartServer,
    BLENDAI_Properties,
    BLENDAI_OT_RunSwarm,
    VIEW3D_PT_blendai_panel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blendai_props = bpy.props.PointerProperty(type=BLENDAI_Properties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.blendai_props

if __name__ == "__main__":
    register()
