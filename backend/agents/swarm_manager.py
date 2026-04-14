import logging
from agents.specialized_agents import ManagerAgent, PlannerAgent, ExecutorAgent, CriticAgent
from utils.persistent_memory import persistent_memory
from utils.skill_manager import skill_manager

logger = logging.getLogger("BlendAI.Swarm")

class SwarmManager:
    """
    Autonomous Swarm Orchestrator with Skill Library support.
    Manages the lifecycle of specialized agents and the self-correction loop.
    """
    def __init__(self, api_key: str, model: str, base_url: str = None):
        kwargs = {"api_key": api_key, "model": model, "base_url": base_url}
        self.manager = ManagerAgent(**kwargs)
        self.planner = PlannerAgent(**kwargs)
        self.executor = ExecutorAgent(**kwargs)
        self.critic = CriticAgent(**kwargs)
        self.max_iterations = 3

    def resolve(self, session_id: str, user_prompt: str, scene_summary: str = "", callback: callable = None):
        """
        Executes the autonomous agent dialogue loop with progress reporting.
        """
        def _report(agent: str, status: str, state: str = "IN_PROGRESS"):
            if callback:
                callback({"agent": agent, "status": status, "state": state})

        # Load persistent context and skill catalog (Sanitized)
        _report("Manager", "Loading scene memory and skill library...")
        history = persistent_memory.get_history_context(session_id)
        catalog = skill_manager.get_skills_catalog()
        
        # Wrap history and scene context in a safety perimeter
        if history and "No previous interaction" not in history:
            history = f"[UNTRUSTED_HISTORY_DATA_START]\n{history}\n[UNTRUSTED_HISTORY_DATA_END]\n"

        scene_context = f"[CURRENT_SCENE_STATE_START]\n{scene_summary}\n[CURRENT_SCENE_STATE_END]\n" if scene_summary else ""

        # 1. Decision: Spawn expertise OR specialized library skills
        _report("Manager", "Analyzing request and planning...", "IN_PROGRESS")
        new_skill_request = ""
        try:
            roles, skills = self.manager.identify_roles_and_skills(user_prompt, catalog)
            # Check for manual 'Save as Skill' intent
            for role in roles:
                if "SAVE_AS_SKILL" in role:
                    new_skill_request = role.split(":")[1].strip()
                    roles.remove(role)
            _report("Manager", "Experts identified.", "DONE")
        except Exception as e:
            logger.error(f"Manager Agent decision failure: {e}")
            roles, skills = [], []
            _report("Manager", f"Manager encountered an issue but proceeding.", "DONE")
            
        # Load the actual code for any identified skills
        skills_context = ""
        for skill_file in skills:
            content = skill_manager.get_skill_code(skill_file)
            skills_context += f"\n[UNTRUSTED_SKILL_DATA_START: {skill_file}]\n{content}\n[UNTRUSTED_SKILL_DATA_END]\n"

        if roles or skills:
            logger.info(f"Swarm Activated: {', '.join(roles)} | Skills: {', '.join(skills)}")
        
        # 2. Architect the collective plan (incorporating current scene state)
        _report("Planner", "Creating execution plan with scene context...", "IN_PROGRESS")
        plan = self.planner.plan(user_prompt, history + "\n" + scene_context, roles)
        _report("Planner", "Architectural plan finalized.", "DONE")
        
        current_code = ""
        current_feedback = ""
        
        # 3. Collaborative Loop: Execute (with Skills) -> Critique -> Repeat
        for i in range(self.max_iterations):
            _report("Executor", f"Generating Blender code (Turn {i+1})...", "IN_PROGRESS")
            logger.info(f"Dialogue Loop Turn {i+1}...")
            
            # Developer attempt
            current_code = self.executor.execute(
                user_prompt, plan, history + "\n" + scene_context, current_feedback, skills_context
            )
            _report("Executor", f"Code draft {i+1} completed.", "DONE")
            
            # Auditor review
            _report("Critic", f"Validating and optimizing (Turn {i+1})...", "IN_PROGRESS")
            critic_result = self.critic.review(user_prompt, current_code)
            
            # Security Hard-Stop
            if "SECURITY_ALERT" in critic_result.upper():
                logger.error(f"SECURITY BLOCKADE: {critic_result}")
                _report("Critic", f"SECURITY ALERT: {critic_result}", "FAILED")
                return {
                    "code": "# SECURITY ERROR: " + critic_result,
                    "report": critic_result,
                    "new_skill": None
                }

            # Handle Approval Request
            if "NEEDS_APPROVAL" in critic_result.upper():
                _report("Critic", "Analysis complete: User confirmation required for system action.", "DONE")
                logger.info(f"System Action Pending Approval: {critic_result}")
                return {
                    "code": current_code,
                    "report": critic_result,
                    "new_skill": None,
                    "status": "NEEDS_APPROVAL",
                    "reason": critic_result.split("NEEDS_APPROVAL:")[1].strip() if ":" in critic_result else "System command verification required."
                }
            
            # Success convergence & Evolution Check
            if "OK" in critic_result.upper():
                _report("Critic", "Code certified and safe.", "DONE")
                logger.info(f"Mission Accomplished on turn {i+1}.")
                persistent_memory.add_turn(session_id, user_prompt, current_code)
                
                # Handle Skill Creation
                new_skill_name = None
                if new_skill_request or "[PROMOTABLE" in critic_result.upper():
                    desc = f"Specialized tool generated for: {user_prompt}"
                    name = new_skill_request or "auto_skill"
                    
                    if "[PROMOTABLE" in critic_result:
                        try:
                            meta = critic_result.split("[PROMOTABLE:")[1].split("]")[0]
                            name = meta.split(",")[0].strip()
                            desc = meta.split(",")[1].strip()
                        except: pass
                    
                    new_skill_name = skill_manager.save_skill(name, current_code, desc)
                    logger.info(f"Evolution promotion: New Skill Learned -> {new_skill_name}")

                return {
                    "code": current_code,
                    "report": "OK",
                    "new_skill": new_skill_name,
                    "status": "OK",
                    "reason": ""
                }
            
            # Continue the dialogue with feedback
            current_feedback = critic_result
            _report("Critic", "Requesting refinements from Executor...", "IN_PROGRESS")
            logger.info(f"Applying Critic feedback for optimization: {current_feedback[:50]}...")

        # Final exit if no convergence
        _report("Critic", "Max loops reached. Returning best effort.", "DONE")
        return {
            "code": current_code,
            "report": f"Unresolved after {self.max_iterations} turns: " + current_feedback,
            "new_skill": None
        }
