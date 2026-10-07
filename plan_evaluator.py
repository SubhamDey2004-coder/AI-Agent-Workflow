def evaluate_plan_step(plan_step, tool_name, arguments, result):
    """
    Determine whether a tool execution successfully
    completed the current plan step.

    Returns:
        True  -> plan step completed
        False -> plan step not completed
    """

    step = plan_step.lower()

    # -----------------------------------------
    # READ FILE
    # -----------------------------------------

    if step.startswith("read "):

        if tool_name != "read_file":
            return False

        expected_filename = step.replace(
            "read ",
            "",
            1
        ).strip()

        actual_filename = str(
            arguments.get("filename", "")
        ).lower().strip()

        return expected_filename == actual_filename


    # -----------------------------------------
    # CREATE / GENERATE FILE
    # -----------------------------------------

    if (
        "create " in step
        or "generate " in step
        or "save " in step
    ):

        if tool_name != "write_file":
            return False

        if isinstance(result, str):
            if result.startswith("Error:"):
                return False

            if "written successfully" not in result.lower():
                return False

        return True


    # -----------------------------------------
    # VERIFY
    # -----------------------------------------

    if "verify " in step:

        if tool_name not in ("list_files", "read_file"):
            return False

        return True


    # -----------------------------------------
    # Unknown step
    # -----------------------------------------

    return False