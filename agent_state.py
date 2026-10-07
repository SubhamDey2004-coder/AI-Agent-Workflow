class AgentState:

    def __init__(self, goal):
        self.goal = goal
        
        # Execution Plan
        self.plan = []
        self.completed_plan_steps = []
        self.current_plan_step = 0

        self.status = "running"

        # Number of agent loop iterations
        self.current_step = 0

        # Tool execution statistics
        self.total_tool_calls = 0
        self.successful_tools = 0
        self.failed_tools = 0

        # History of all tool executions
        self.tool_history = []

    def next_step(self):
        self.current_step += 1

    def set_plan(self, plan):
        self.plan = plan
        self.completed_plan_steps = []
        
    def complete_plan_step(self, step_index):
        if step_index not in self.completed_plan_steps:
            self.completed_plan_steps.append(step_index)
            
    def advance_plan_step(self):
        self.current_plan_step += 1

    def record_tool_call(self, tool_name, arguments):
        self.total_tool_calls += 1

        self.tool_history.append(
            {
                "tool": tool_name,
                "arguments": arguments,
                "status": "pending"
            }
        )

    def record_result(self, result, success=True):

        if success:
            self.successful_tools += 1
            status = "success"
        else:
            self.failed_tools += 1
            status = "error"

        # Update the most recent pending tool call
        if self.tool_history:
            self.tool_history[-1]["status"] = status

    def complete(self):
        self.status = "completed"

    def fail(self):
        self.status = "failed"

    def show(self):

        print("\n========== AGENT STATE ==========")

        print(f"Goal: {self.goal}")
        print(f"Status: {self.status}")
        print(f"Steps: {self.current_step}")
        print(f"Plan progress: "
              f"{len(self.completed_plan_steps)}/{len(self.plan)}"
        )
        print(f"Total tool calls: {self.total_tool_calls}")
        print(f"Successful tools: {self.successful_tools}")
        print(f"Failed tools: {self.failed_tools}")

        print("\nTool history:")

        if not self.tool_history:
            print("  No tools executed.")

        else:
            for i, entry in enumerate(self.tool_history, start=1):

                print(
                    f"  {i}. "
                    f"{entry['tool']} | "
                    f"{entry['status']}"
                )

        print("=================================\n")