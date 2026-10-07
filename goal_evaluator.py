def evaluate_goal(state):
    """
    Evaluate whether the agent's goal is complete.

    Returns:
        "failed"   -> a tool operation failed
        "complete" -> all required plan steps are satisfied
        "continue" -> more work is required
    """

    # --------------------------------------------------
    # 1. Failure has highest priority
    # --------------------------------------------------

    if state.failed_tools > 0 or state.status == "failed":
        return "failed"


    # --------------------------------------------------
    # 2. No tools have been executed yet
    # --------------------------------------------------

    if state.total_tool_calls == 0:
        return "continue"


    # --------------------------------------------------
    # 3. Use the execution plan when available
    # --------------------------------------------------

    if state.plan:

        if (
            len(state.completed_plan_steps) == len(state.plan)
            and state.current_plan_step >= len(state.plan)
        ):
            return "complete"

        return "continue"


    # --------------------------------------------------
    # 4. Fallback when there is no plan
    # --------------------------------------------------

    goal = state.goal.lower()


    # Simple read
    if goal.startswith("read "):

        if "read_file" in [
            item["tool"]
            for item in state.tool_history
            if item["status"] == "success"
        ]:
            return "complete"

        return "continue"


    # Simple creation
    if "create" in goal:

        if "write_file" in [
            item["tool"]
            for item in state.tool_history
            if item["status"] == "success"
        ]:
            return "complete"

        return "continue"


    return "continue"