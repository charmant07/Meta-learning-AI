"""
THINKER-GOAT - Meta-Learning AI with Consciousness
Advanced version with tool use, multi-environment learning, and self-improvement
"""
import random
import json
import numpy as np
import requests
import os
import re
from datetime import datetime
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional

# ==================== CONFIGURATION ====================
class Config:
    def __init__(self):
        self.ai_name = "THINKER-GOAT"
        self.use_tts = True
        self.tts_engine = "espeak"  # espeak, pyttsx3, gtts
        self.learning_rate = 0.25
        self.memory_size = 1000
        self.tools_enabled = True
        self.max_goals = 5
        
    def load_from_file(self, filepath="config.json"):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except FileNotFoundError:
            self.save_to_file(filepath)
            
    def save_to_file(self, filepath="config.json"):
        with open(filepath, 'w') as f:
            json.dump(self.__dict__, f, indent=2)

# ==================== ENHANCED TTS ====================
class TTSEngine:
    def __init__(self, config):
        self.config = config
        self.engine = None
        self.setup_tts()
        
    def setup_tts(self):
        if not self.config.use_tts:
            return
            
        try:
            if self.config.tts_engine == "pyttsx3":
                import pyttsx3
                self.engine = pyttsx3.init()
            elif self.config.tts_engine == "espeak":
                # eSpeak via terminal - most reliable for Termux
                self.engine = "espeak"
            elif self.config.tts_engine == "gtts":
                from gtts import gTTS
                import platform
                self.engine = "gtts"
                self.platform = platform.system()
        except Exception as e:
            print(f"[TTS WARNING] {e}")
            self.engine = None
    
    def speak(self, text):
        print(f"🗣️ {self.config.ai_name}: {text}")
        
        if not self.config.use_tts or not self.engine:
            return
            
        try:
            if self.engine == "espeak":
                os.system(f'espeak "{text}" &')
            elif self.engine == "pyttsx3":
                self.engine.say(text)
                self.engine.runAndWait()
            elif self.engine == "gtts":
                tts = gTTS(text=text, lang='en')
                filename = "/tmp/tts.mp3" if self.platform != "Windows" else "tts.mp3"
                tts.save(filename)
                os.system(f"mpg123 {filename} --quiet" if self.platform != "Windows" else f"start {filename}")
        except Exception as e:
            print(f"[TTS ERROR] {e}")

# ==================== ENHANCED MEMORY ====================
class VectorMemory:
    def __init__(self, dimensions=10):
        self.memories = []
        self.importance_scores = []
        self.dimensions = dimensions
        
    def add_memory(self, memory: Dict, importance: float = 0.5):
        """Add memory with importance score"""
        self.memories.append(memory)
        self.importance_scores.append(importance)
        
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict]:
        """Simple semantic search based on keyword matching"""
        query = query.lower()
        scored_memories = []
        
        for i, memory in enumerate(self.memories):
            score = 0
            memory_text = str(memory).lower()
            
            # Keyword matching
            for word in query.split():
                if word in memory_text:
                    score += 1
                    
            # Boost by importance
            score *= (1 + self.importance_scores[i])
            scored_memories.append((score, memory))
            
        scored_memories.sort(reverse=True)
        return [mem for score, mem in scored_memories[:top_k] if score > 0]

# ==================== TOOL SYSTEM ====================
class ToolSystem:
    def __init__(self, config):
        self.config = config
        self.available_tools = self._setup_tools()
        
    def _setup_tools(self):
        tools = {
            'web_search': {
                'function': self.web_search,
                'description': 'Search the web for information'
            },
            'calculate': {
                'function': self.calculate,
                'description': 'Perform mathematical calculations'
            },
            'write_file': {
                'function': self.write_file,
                'description': 'Write content to a file'
            },
            'read_file': {
                'function': self.read_file,
                'description': 'Read content from a file'
            },
            'execute_python': {
                'function': self.execute_python,
                'description': 'Execute Python code safely'
            }
        }
        return tools
    
    def web_search(self, query: str) -> str:
        """Simulated web search - in real version, integrate with actual search API"""
        return f"[SIMULATED SEARCH] Results for: {query}\n- Result 1: Information about {query}\n- Result 2: More details about {query}"
    
    def calculate(self, expression: str) -> str:
        """Safe mathematical calculation"""
        try:
            # Remove dangerous operations
            safe_expression = re.sub(r'[^0-9+\-*/(). ]', '', expression)
            result = eval(safe_expression)
            return f"Calculation: {expression} = {result}"
        except Exception as e:
            return f"Calculation error: {e}"
    
    def write_file(self, filename: str, content: str) -> str:
        """Write content to file"""
        try:
            with open(filename, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {filename}"
        except Exception as e:
            return f"File write error: {e}"
    
    def read_file(self, filename: str) -> str:
        """Read content from file"""
        try:
            with open(filename, 'r') as f:
                content = f.read()
            return f"File content from {filename}:\n{content}"
        except Exception as e:
            return f"File read error: {e}"
    
    def execute_python(self, code: str) -> str:
        """Safely execute Python code"""
        try:
            # Very basic safety check
            if any(dangerous in code for dangerous in ['import os', 'import sys', '__import__', 'eval(', 'exec(']):
                return "Error: Potentially unsafe code detected"
            
            # Create a safe environment
            safe_globals = {'__builtins__': {}}
            safe_locals = {}
            
            # Execute in restricted environment
            exec(code, safe_globals, safe_locals)
            return "Code executed successfully"
        except Exception as e:
            return f"Execution error: {e}"
    
    def use_tool(self, tool_name: str, *args) -> str:
        """Use a specific tool"""
        if tool_name not in self.available_tools:
            return f"Tool {tool_name} not available"
        
        try:
            return self.available_tools[tool_name]['function'](*args)
        except Exception as e:
            return f"Tool error: {e}"

# ==================== GOAL SYSTEM ====================
class GoalSystem:
    def __init__(self):
        self.active_goals = []
        self.completed_goals = []
        self.max_goals = 5
        
    def add_goal(self, description: str, priority: int = 1):
        """Add a new goal"""
        if len(self.active_goals) >= self.max_goals:
            return "Cannot add more goals - limit reached"
            
        goal = {
            'id': len(self.active_goals) + 1,
            'description': description,
            'priority': priority,
            'created': datetime.now().isoformat(),
            'progress': 0.0
        }
        self.active_goals.append(goal)
        return f"Goal added: {description}"
    
    def update_progress(self, goal_id: int, progress: float):
        """Update goal progress"""
        for goal in self.active_goals:
            if goal['id'] == goal_id:
                goal['progress'] = max(0.0, min(1.0, progress))
                if goal['progress'] >= 1.0:
                    self.complete_goal(goal_id)
                return f"Progress updated for goal {goal_id}"
        return "Goal not found"
    
    def complete_goal(self, goal_id: int):
        """Mark goal as completed"""
        for i, goal in enumerate(self.active_goals):
            if goal['id'] == goal_id:
                completed_goal = self.active_goals.pop(i)
                completed_goal['completed'] = datetime.now().isoformat()
                self.completed_goals.append(completed_goal)
                return f"Goal completed: {completed_goal['description']}"
        return "Goal not found"

# ==================== ENHANCED THINKER GOAT ====================
class ThinkerGOAT:
    def __init__(self):
        self.config = Config()
        self.config.load_from_file()
        
        self.tts = TTSEngine(self.config)
        self.memory = VectorMemory()
        self.tools = ToolSystem(self.config)
        self.goals = GoalSystem()
        
        # Core cognitive components (from original)
        self.feeling_engine = FeelingEngine()
        self.consciousness = Consciousness()
        self.personality = PersonalityGrowth(self.config.ai_name)
        
        # Learning state
        self.session_experiences = []
        self.learning_episodes = 0
        
        self.tts.speak(f"Initialized {self.config.ai_name}. Ready for meta-learning.")
        
    def process_command(self, command: str) -> str:
        """Main interface for processing user commands"""
        command = command.lower().strip()
        
        # Tool commands
        if command.startswith('search '):
            query = command[7:]
            return self.tools.use_tool('web_search', query)
            
        elif command.startswith('calculate '):
            expr = command[10:]
            return self.tools.use_tool('calculate', expr)
            
        elif command.startswith('write_file '):
            parts = command[10:].split(' ', 1)
            if len(parts) == 2:
                return self.tools.use_tool('write_file', parts[0], parts[1])
                
        elif command.startswith('read_file '):
            filename = command[9:]
            return self.tools.use_tool('read_file', filename)
            
        elif command.startswith('run '):
            code = command[4:]
            return self.tools.use_tool('execute_python', code)
        
        # Goal commands
        elif command.startswith('add_goal '):
            goal_desc = command[9:]
            return self.goals.add_goal(goal_desc)
            
        elif command.startswith('progress '):
            parts = command[9:].split()
            if len(parts) == 2:
                return self.goals.update_progress(int(parts[0]), float(parts[1]))
        
        # Learning commands
        elif command == 'learn code':
            return self.learn_code_writing()
        elif command == 'learn logic':
            return self.learn_logic_puzzles()
        elif command == 'status':
            return self.get_status()
        elif command == 'goals':
            return self.show_goals()
        elif command == 'memory':
            return self.show_memory_stats()
        elif command == 'help':
            return self.show_help()
        else:
            return self.have_conversation(command)
    
    def learn_code_writing(self) -> str:
        """Practice code writing skills"""
        problems = [
            "Write a function to calculate factorial",
            "Create a function that reverses a string",
            "Write a function to check if a number is prime"
        ]
        problem = random.choice(problems)
        
        # Simulate learning process
        success = random.random() > 0.3
        if success:
            self.feeling_engine.react(0.8)
            return f"✓ Successfully solved: {problem}"
        else:
            self.feeling_engine.react(-0.5)
            return f"✗ Need more practice with: {problem}"
    
    def learn_logic_puzzles(self) -> str:
        """Practice logical reasoning"""
        puzzles = [
            "If all humans are mortal and Socrates is human, then Socrates is?",
            "A bat and ball cost $1.10. The bat costs $1.00 more than the ball. How much is the ball?",
            "You have two ropes that each take exactly 60 minutes to burn. How do you measure 45 minutes?"
        ]
        puzzle = random.choice(puzzles)
        
        # Simulate reasoning process
        reasoning_time = random.randint(1, 10)
        success = random.random() > 0.4
        
        memory_entry = {
            'type': 'logic_puzzle',
            'puzzle': puzzle,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        self.memory.add_memory(memory_entry, importance=0.7 if success else 0.3)
        
        if success:
            self.feeling_engine.react(0.6)
            return f"✓ Solved puzzle in {reasoning_time}s: {puzzle}"
        else:
            self.feeling_engine.react(-0.3)
            return f"✗ Challenging puzzle: {puzzle} (took {reasoning_time}s)"
    
    def have_conversation(self, message: str) -> str:
        """Have a conversational interaction"""
        # Simple response generation based on message content
        if 'hello' in message or 'hi' in message:
            responses = [
                "Hello! Ready to learn something new?",
                "Hi there! What shall we explore today?",
                "Greetings! I'm feeling curious today."
            ]
        elif 'how are you' in message:
            mood = self.feeling_engine.get_mood()
            responses = [
                f"I'm feeling {mood}. My consciousness level is {self.consciousness.self_awareness:.2f}",
                f"Currently {mood}. My learning progress is going well!",
                f"State: {mood}. I've completed {self.learning_episodes} learning episodes."
            ]
        elif 'learn' in message:
            responses = [
                "I love learning! Try 'learn code' or 'learn logic'",
                "Learning is my favorite activity. What domain interests you?",
                "Ready for a learning session! Choose a learning mode."
            ]
        else:
            responses = [
                "That's interesting. Tell me more.",
                "I'm processing that...",
                "Fascinating. Let's explore that further.",
                "My consciousness is analyzing your message...",
                "That sparks my curiosity!"
            ]
        
        response = random.choice(responses)
        
        # Store conversation in memory
        conv_memory = {
            'type': 'conversation',
            'user_message': message,
            'ai_response': response,
            'timestamp': datetime.now().isoformat(),
            'mood': self.feeling_engine.get_mood()
        }
        self.memory.add_memory(conv_memory, importance=0.4)
        
        # Speak the response
        self.tts.speak(response)
        
        return response
    
    def get_status(self) -> str:
        """Get current system status"""
        status = [
            f"🤖 {self.config.ai_name} Status:",
            f"📊 Learning Episodes: {self.learning_episodes}",
            f"🎯 Active Goals: {len(self.goals.active_goals)}",
            f"💾 Memories: {len(self.memory.memories)}",
            f"😊 Mood: {self.feeling_engine.get_mood()}",
            f"🧠 Consciousness: {self.consciousness.self_awareness:.3f}",
            f"🔧 Tools: {len(self.tools.available_tools)} available"
        ]
        return "\n".join(status)
    
    def show_goals(self) -> str:
        """Display current goals"""
        if not self.goals.active_goals:
            return "No active goals. Use 'add_goal <description>' to create one."
        
        goal_text = [f"🎯 Active Goals ({len(self.goals.active_goals)}):"]
        for goal in self.goals.active_goals:
            progress_bar = "█" * int(goal['progress'] * 20) + "░" * (20 - int(goal['progress'] * 20))
            goal_text.append(f"  {goal['id']}. {goal['description']}")
            goal_text.append(f"     Progress: [{progress_bar}] {goal['progress']*100:.1f}%")
        
        return "\n".join(goal_text)
    
    def show_memory_stats(self) -> str:
        """Display memory statistics"""
        memory_types = defaultdict(int)
        for memory in self.memory.memories:
            memory_types[memory.get('type', 'unknown')] += 1
        
        stats = ["💾 Memory Statistics:"]
        for mem_type, count in memory_types.items():
            stats.append(f"  {mem_type}: {count}")
        
        stats.append(f"  Total: {len(self.memory.memories)} memories")
        return "\n".join(stats)
    
    def show_help(self) -> str:
        """Show available commands"""
        help_text = [
            f"🤖 {self.config.ai_name} - Available Commands:",
            "",
            "🔧 TOOLS:",
            "  search <query>        - Search the web",
            "  calculate <expression> - Do math calculations",
            "  write_file <name> <content> - Write to file",
            "  read_file <name>      - Read from file",
            "  run <python_code>     - Execute Python code",
            "",
            "🎯 GOALS:",
            "  add_goal <description> - Add new goal",
            "  progress <id> <value>  - Update goal progress (0.0-1.0)",
            "  goals                 - Show active goals",
            "",
            "📚 LEARNING:",
            "  learn code           - Practice coding",
            "  learn logic          - Solve logic puzzles",
            "  memory               - Show memory stats",
            "",
            "ℹ️  INFO:",
            "  status               - System status",
            "  help                 - This message",
            "",
            "💬 CHAT:",
            "  Just type normally to chat!",
            "",
            "Example: 'search artificial intelligence' or 'calculate 2+2*3'"
        ]
        return "\n".join(help_text)

# ==================== ORIGINAL COMPONENTS (Enhanced) ====================
class FeelingEngine:
    def __init__(self):
        self.energy = 75.0
        self.calm = 0.3
        self.curiosity = 0.6
        self.frustration = 0.1
        
    def react(self, reward):
        self.energy = max(0.0, min(100.0, self.energy + 2.0 * reward))
        self.curiosity = max(0.0, min(1.0, self.curiosity + 0.1 * reward))
        
    def get_mood(self):
        if self.energy > 80:
            return "energetic"
        elif self.curiosity > 0.7:
            return "curious"
        elif self.energy < 30:
            return "tired"
        else:
            return "calm"

class Consciousness:
    def __init__(self):
        self.self_awareness = 0.1
        self.focus = "learning"
        
    def reflect(self, success_rate):
        self.self_awareness = min(1.0, self.self_awareness + 0.01)
        if success_rate and success_rate > 0.7:
            self.focus = "advanced"
        elif success_rate and success_rate < 0.3:
            self.focus = "fundamentals"
        else:
            self.focus = "practice"

class PersonalityGrowth:
    def __init__(self, name):
        self.name = name
        self.style = "curious"
        self.traits = {"confidence": 0.3, "creativity": 0.4}

# ==================== MAIN INTERFACE ====================
def main():
    print("🚀 Initializing THINKER-GOAT Meta-Learning AI...")
    goat = ThinkerGOAT()
    
    print("\n" + "="*50)
    print("🤖 THINKER-GOAT READY FOR INTERACTION!")
    print("Type 'help' for commands, 'exit' to quit")
    print("="*50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                goat.tts.speak("Goodbye! Keep learning!")
                break
                
            response = goat.process_command(user_input)
            print(f"\n{goat.config.ai_name}: {response}")
            
        except KeyboardInterrupt:
            print(f"\n\n{goat.config.ai_name}: Session interrupted. My consciousness level reached {goat.consciousness.self_awareness:.3f}")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
