import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        TODO: Implement the system prompt that instructs the agent to follow ReAct.
        Should include:
        1.  Available tools and their descriptions.
        2.  Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
        You are an intelligent assistant. You have access to the following tools:
        {tool_descriptions}

        Use the following format:
        Thought: your line of reasoning.
        Action: tool_name(arguments)
        Observation: result of the tool call.
        ... (repeat Thought/Action/Observation if needed)
        Final Answer: your final response.
        """

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        current_prompt = user_input
        steps = 0

        while steps < self.max_steps:
            # Generate LLM response
            response = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            result = response.get("content", "")
            
            logger.log_event("AGENT_STEP", {"step": steps, "response": result})
            
            print(f"\n[Bước {steps + 1}]")
            print(result.strip())
            
            # If Final Answer found -> Break loop
            final_answer_match = re.search(r"Final Answer:\s*(.*)", result, re.DOTALL)
            if final_answer_match:
                final_answer = final_answer_match.group(1).strip()
                logger.log_event("AGENT_END", {"steps": steps + 1, "status": "success", "answer": final_answer})
                return final_answer
            
            # Parse Thought/Action from result
            action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", result)
            
            # If Action found -> Call tool -> Append Observation
            if action_match:
                tool_name = action_match.group(1)
                tool_args = action_match.group(2)
                
                observation = self._execute_tool(tool_name, tool_args)
                print(f"Observation: {observation}")
                
                # Append to prompt for next iteration
                current_prompt += f"\n{result}\nObservation: {observation}\n"
                logger.log_event("AGENT_ACTION", {"tool": tool_name, "args": tool_args, "observation": observation})
            else:
                # Nếu LLM không xuất ra format Action hay Final Answer (VD: đang tán gẫu)
                # Thay vì báo lỗi và lặp vô hạn, ta lấy luôn câu nói đó làm Final Answer
                fallback_answer = result.strip()
                logger.log_event("AGENT_END", {"steps": steps + 1, "status": "success_fallback", "answer": fallback_answer})
                return fallback_answer
            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps, "status": "max_steps_reached"})
        return "I could not find the answer within the maximum number of steps."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                # TODO: Implement dynamic function calling or simple if/else
                if 'func' in tool:
                    try:
                        # Try to parse arguments dynamically
                        if not args.strip():
                            return str(tool['func']())
                        try:
                            # Evaluate as tuple
                            parsed_args = eval(f"({args},)")
                            return str(tool['func'](*parsed_args))
                        except Exception:
                            # Fallback: pass as string
                            return str(tool['func'](args))
                    except Exception as e:
                        return f"Error executing {tool_name}: {e}"
                else:
                    return f"Result of {tool_name} with args: {args}"
        return f"Tool {tool_name} not found."
