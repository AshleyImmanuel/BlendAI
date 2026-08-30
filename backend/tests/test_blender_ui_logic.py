import unittest
import ast
import os

class TestBlenderUILogic(unittest.TestCase):
    def setUp(self):
        # Locate the addon script correctly relative to the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.addon_path = os.path.join(base_dir, "blender_ai_agent.py")
        with open(self.addon_path, "r", encoding="utf-8") as f:
            self.content = f.read()
            self.tree = ast.parse(self.content)

    def test_bl_info_structure(self):
        """Verify that bl_info is present and correctly structured."""
        found_bl_info = False
        for node in self.tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "bl_info":
                        found_bl_info = True
                        break
        self.assertTrue(found_bl_info, "bl_info metadata is missing from the addon script.")

    def test_registration_integrity(self):
        """Ensure register() and unregister() functions are defined."""
        functions = [n.name for n in self.tree.body if isinstance(n, ast.FunctionDef)]
        self.assertIn("register", functions, "Mandatory register() function is missing.")
        self.assertIn("unregister", functions, "Mandatory unregister() function is missing.")

    def test_class_naming_protocols(self):
        """Ensure Blender-specific naming protocols are followed."""
        class_names = [n.name for n in self.tree.body if isinstance(n, ast.ClassDef)]
        
        # We check for the presence of standard prefix patterns
        # Operators should have _OT_, Panels should have _PT_
        has_operator = any("_OT_" in name for name in class_names)
        has_panel = any("_PT_" in name for name in class_names)
        has_prefs = any("AddonPreferences" in name for name in class_names)

        self.assertTrue(has_operator, "No standard Blender Operator class (_OT_) found.")
        self.assertTrue(has_panel, "No standard Blender Panel class (_PT_) found.")
        self.assertTrue(has_prefs, "No AddonPreferences class found for API key storage.")

    def test_ui_logic_dependencies(self):
        """Verify that mandatory UI logic components exist."""
        # Check for props pointer in register
        register_found = False
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "register":
                register_found = True
                # Look for scene property registration
                content = ast.dump(node)
                self.assertIn("PointerProperty", content, "Scene property registration logic is missing or malformed.")
        self.assertTrue(register_found)

if __name__ == "__main__":
    unittest.main()
