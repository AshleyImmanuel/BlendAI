import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.swarm_manager import SwarmManager
from utils.persistent_memory import persistent_memory

class TestSwarmArchitecture(unittest.TestCase):
    """
    Simulates a full Swarm lifecycle:
    1. Manager identifies roles.
    2. Planner creates plan.
    3. Executor fails first attempt.
    4. Critic catches error and gives feedback.
    5. Executor fixes code in 2nd iteration.
    6. System converges and saves to memory.
    """
    
    @patch('utils.llm_client.LLMClient.completion')
    def test_swarm_iteration_convergence(self, mock_completion):
        print("\n[Audit] Starting Autonomous Swarm Architecture Test...")
        
        # Define simulation responses
        responses = [
            "MaterialExpert, GeometryExpert", # Manager: Spawns roles
            "1. Create mesh, 2. Add material", # Planner: Creates plan
            "bpy.ops.mesh.primitive_cube_add()", # Executor (Attempt 1): Buggy code (missing material)
            "FAIL: You forgot the material instructions.", # Critic (Attempt 1): Feedback
            "bpy.ops.mesh.primitive_cube_add()\n# Material added", # Executor (Attempt 2): Fixed code
            "OK" # Critic (Attempt 2): Approval
        ]
        mock_completion.side_effect = responses
        
        swarm = SwarmManager(api_key="mock_key", model="gpt-4o")
        session_id = "audit_test_session"
        
        # Run the swarm
        code, status = swarm.resolve(session_id, "Make a cube with materials")
        
        print(f"[Audit] Final Status: {status}")
        print(f"[Audit] Code Convergence:\n{code}")
        
        # ASSERTIONS
        # 1. Did it identify roles?
        self.assertEqual(mock_completion.call_count, 6, "Swarm should have iterated exactly 6 times (Manager, Plan, Exec1, Crit1, Exec2, Crit2)")
        
        # 2. Did it converge?
        self.assertEqual(status, "OK")
        self.assertIn("Material added", code)
        
        # 3. Did it persist?
        memory_path = persistent_memory._get_file_path(session_id)
        self.assertTrue(os.path.exists(memory_path), "Memory file should have been created")
        
        # Cleanup
        persistent_memory.clear_session(session_id)
        print("[Audit] Cleanup complete. System Logic is VERIFIED.")

if __name__ == "__main__":
    unittest.main()
