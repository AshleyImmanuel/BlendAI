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

    def resolve(self, session_id: str, user_prompt: str):
        """
        Executes the autonomous agent dialogue loop with Skill Injection and Evolution.
        """
        # Load persistent context and skill catalog (Sanitized)
        history = persistent_memory.get_history_context(session_id)
        catalog = skill_manager.get_skills_catalog()
        
        # Wrap history in a safety perimeter
        if history and "No previous interaction" not in history:
            history = f"[UNTRUSTED_HISTORY_DATA_START]\n{history}\n[UNTRUSTED_HISTORY_DATA_END]\n"

        # 1. Decision: Spawn expertise OR specialized library skills
        new_skill_request = ""
        try:
            roles, skills = self.manager.identify_roles_and_skills(user_prompt, catalog)
            # Check for manual 'Save as Skill' intent
            for role in roles:
                if "SAVE_AS_SKILL" in role:
                    new_skill_request = role.split(":")[1].strip()
                    roles.remove(role)
        except Exception as e:
            logger.error(f"Manager Agent decision failure: {e}")
            roles, skills = [], []
            
        # Load the actual code for any identified skills
        skills_context = ""
        for skill_file in skills:
            content = skill_manager.get_skill_code(skill_file)
            skills_context += f"\n[UNTRUSTED_SKILL_DATA_START: {skill_file}]\n{content}\n[UNTRUSTED_SKILL_DATA_END]\n"

        if roles or skills:
            logger.info(f"Swarm Activated: {', '.join(roles)} | Skills: {', '.join(skills)}")
        
        # 2. Architect the collective plan
        plan = self.planner.plan(user_prompt, history, roles)
        
        current_code = ""
        current_feedback = ""
        
        # 3. Collaborative Loop: Execute (with Skills) -> Critique -> Repeat
        for i in range(self.max_iterations):
            logger.info(f"Dialogue Loop Turn {i+1}...")
            
            # Developer attempt
            current_code = self.executor.execute(
                user_prompt, plan, history, current_feedback, skills_context
            )
            
            # Auditor review
            critic_result = self.critic.review(user_prompt, current_code)
            
            # Security Hard-Stop
            if "SECURITY_ALERT" in critic_result.upper():
                logger.error(f"SECURITY BLOCKADE: {critic_result}")
                return {
                    "code": "# SECURITY ERROR: " + critic_result,
                    "report": critic_result,
                    "new_skill": None
                }
            
            # Success convergence & Evolution Check
            if "OK" in critic_result.upper():
                logger.info(f"Mission Accomplished on turn {i+1}.")
                persistent_memory.add_turn(session_id, user_prompt, current_code)
                
                # Handle Skill Creation (Manual or Autonomous)
                new_skill_name = None
                if new_skill_request or "[PROMOTABLE" in critic_result.upper():
                    # Extract name/description for autonomous promotion
                    desc = f"Specialized tool generated for: {user_prompt}"
                    name = new_skill_request or "auto_skill"
                    
                    if "[PROMOTABLE" in critic_result:
                        try:
                            # Parse [PROMOTABLE: name, description]
                            meta = critic_result.split("[PROMOTABLE:")[1].split("]")[0]
                            name = meta.split(",")[0].strip()
                            desc = meta.split(",")[1].strip()
                        except: pass
                    
                    new_skill_name = skill_manager.save_skill(name, current_code, desc)
                    logger.info(f"Evolution promotion: New Skill Learned -> {new_skill_name}")

                return {
                    "code": current_code,
                    "report": "OK",
                    "new_skill": new_skill_name
                }
            
            # Continue the dialogue with feedback
            current_feedback = critic_result
            logger.info(f"Applying Critic feedback for optimization: {current_feedback[:50]}...")

        # Final exit if no convergence
        return {
            "code": current_code,
            "report": f"Unresolved after {self.max_iterations} turns: " + current_feedback,
            "new_skill": None
        }
