import ollama

from tools import tool_registry, get_tool_schemas
from rag import build_context, build_rag_prompt
from agent_state import AgentState
from goal_evaluator import evaluate_goal
from planner import create_plan
from plan_evaluator import evaluate_plan_step


tools = get_tool_schemas()


system_prompt = """
You are an AI agent that solves tasks by using the available tools.

Your job is to:

1. Understand the user's goal.
2. Follow the execution plan.
3. Choose the appropriate tool.
4. Execute one tool at a time.
5. Inspect the result.
6. Continue with the next required plan step.
7. Only give a final answer when the goal is actually complete.

IMPORTANT RULES:

1. If the task requires a tool, ALWAYS call the appropriate tool.
2. Do not merely describe which tool should be called.
3. For multi-step tasks, perform one tool call at a time.
4. After receiving a tool result, inspect it before continuing.
5. Follow the provided execution plan.
6. Do not skip plan steps.
7. Do not claim a task is complete unless all required steps are complete.
8. If a tool fails, do not pretend the task succeeded.
9. Never invent information.
10. Prefer tools over guessing.


MEMORY:

- Use `recall` when the user asks about personal information,
  preferences, or previously saved facts.

- Use `remember` when the user explicitly asks you to save
  something for future conversations.


KNOWLEDGE:

- If the answer could reasonably exist in the user's indexed
  documents, use `search_knowledge`.

- Do not answer document-based questions from general knowledge.

- If relevant results are found, use the retrieved context.

- If no relevant results are found, clearly state that the
  information was not found in the indexed documents.

- Never invent information from documents.


FILES:

- Use `list_files` when the user asks what files exist.
- Use `read_file` when the user asks to inspect a file.
- Use `search_files` when the user asks to find files.
- Use `write_file` when the user asks to create a file.


CALCULATIONS:

- Use `calculator` for mathematical expressions.


GROUNDING:

- When creating content from a source file, use ONLY information
  contained in that source.

- If the user says "based only on" or "using only", strictly
  follow that restriction.

- Do not introduce unsupported information.


VERIFICATION:

- If the plan contains a verification step, verification MUST
  be performed using a tool.

- Never claim a file was verified unless a verification tool
  actually succeeded.


FINAL ANSWER:

- Only provide a final answer after the goal evaluator says
  COMPLETE.

- If the evaluator says CONTINUE, continue using tools.
"""


messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]


print("Agent started. Type 'exit' to stop.")


while True:

    user_goal = input("\nYou: ")

    if user_goal.lower() == "exit":
        print("Agent stopped.")
        break


    # --------------------------------------------------
    # Add user goal
    # --------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": user_goal
        }
    )


    # --------------------------------------------------
    # Create state
    # --------------------------------------------------

    state = AgentState(user_goal)


    # --------------------------------------------------
    # Create execution plan
    # --------------------------------------------------

    plan = create_plan(user_goal)
    state.set_plan(plan)


    print("\n========== PLAN ==========")

    if not plan:

        print("Planner failed to create a plan.")

    else:

        for i, plan_step in enumerate(plan, start=1):

            print(
                f"{i}. {plan_step}"
            )

    print("==========================\n")


    # --------------------------------------------------
    # Give the plan to the model
    # --------------------------------------------------

    if plan:

        plan_text = "\n".join(
            f"{i}. {step}"
            for i, step in enumerate(plan, start=1)
        )

        messages.append(
            {
                "role": "system",
                "content": (
                    "Execution plan for the current goal:\n\n"
                    f"{plan_text}\n\n"
                    "Follow this plan in order. "
                    "Do not skip steps."
                )
            }
        )


    # --------------------------------------------------
    # Agent loop
    # --------------------------------------------------

    max_steps = 10
    step = 0


    while step < max_steps:

        step += 1

        state.next_step()


        # ----------------------------------------------
        # Tell the model to continue the plan
        # ----------------------------------------------

        # ----------------------------------------------
        # Tell the model which plan step to execute
        # ----------------------------------------------

        if state.plan and state.current_plan_step < len(state.plan):
        
            current_plan_step = state.plan[
                state.current_plan_step
            ]

            messages.append(
                {
                    "role": "system",
                    "content": (
                        f"Current plan step:\n"
                        f"{state.current_plan_step + 1}. "
                        f"{current_plan_step}\n\n"

                        "Execute this plan step now.\n"
                        "Do not skip it.\n"
                        "Use the appropriate tool.\n"
                        "Do not execute a later plan step yet."
                    )
                }
            )


        response = ollama.chat(
            model="qwen3:4b",
            messages=messages,
            tools=tools
        )


        # ----------------------------------------------
        # Model produced no tool call
        # ----------------------------------------------

        if not response.message.tool_calls:

            evaluation = evaluate_goal(state)


            if evaluation == "complete":

                print(
                    "Agent:",
                    response.message.content
                )

                messages.append(
                    response.message
                )

                state.complete()

                print(
                    "\nGoal evaluator: COMPLETE"
                )

                state.show()

                break


            elif evaluation == "failed":

                print(
                    "Agent:",
                    response.message.content
                )

                state.fail()

                print(
                    "\nGoal evaluator: FAILED"
                )

                state.show()

                break


            else:

                # Model answered too early.
                messages.append(
                    response.message
                )

                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "You attempted to answer before the "
                            "goal was complete. Continue executing "
                            "the remaining plan steps using tools."
                        )
                    }
                )

                continue


        # ----------------------------------------------
        # Store assistant tool-call message
        # ----------------------------------------------

        messages.append(
            response.message
        )


        # ----------------------------------------------
        # Execute tool calls
        # ----------------------------------------------

        for tool_call in response.message.tool_calls:

            tool_name = tool_call.function.name

            arguments = tool_call.function.arguments


            print(
                "Agent selected tool:",
                tool_name
            )

            print(
                "Arguments:",
                arguments
            )


            state.record_tool_call(
                tool_name,
                arguments
            )


            # ------------------------------------------
            # Unknown tool
            # ------------------------------------------

            if tool_name not in tool_registry:

                result = (
                    f"Unknown tool: {tool_name}"
                )

                print(
                    "Tool result:",
                    result
                )


                state.record_result(
                    result,
                    success=False
                )


                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": result
                    }
                )

                state.fail()

                break


            # ------------------------------------------
            # Execute known tool
            # ------------------------------------------

            function = tool_registry[tool_name]


            try:

                result = function(**arguments)


                success = not (
                    isinstance(result, str)
                    and result.startswith("Error:")
                )


                print(
                    "Tool result:",
                    result
                )


            except Exception as e:

                result = (
                    f"Tool error: {str(e)}"
                )

                success = False


                print(result)


            # ------------------------------------------
            # Record result
            # ------------------------------------------

            state.record_result(
                result,
                success=success
            )
            
            # -----------------------------------------
            # Evaluate current plan step
            # -----------------------------------------

            if success and state.plan:

                current_step_index = state.current_plan_step

                if current_step_index < len(state.plan):

                    current_plan_step = state.plan[
                        current_step_index
                    ]

                    step_completed = evaluate_plan_step(
                        current_plan_step,
                        tool_name,
                        arguments,
                        result
                    )

                    print(
                        "Plan step:",
                        current_plan_step
                    )

                    print(
                        "Plan step result:",
                        "COMPLETED" if step_completed else "NOT COMPLETED"
                    )

                    if step_completed:
                    
                        state.complete_plan_step(
                            current_step_index
                        )
                        
                        state.advance_plan_step()


            # ------------------------------------------
            # Send result back to model
            # ------------------------------------------

            messages.append(
                {
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": str(result)
                }
            )


            # ------------------------------------------
            # Handle failure
            # ------------------------------------------

            if not success:

                state.fail()

                print(
                    "Agent: The task could not be completed "
                    "because the tool operation failed."
                )

                break


            # ------------------------------------------
            # RAG handling
            # ------------------------------------------

            if tool_name == "search_knowledge":

                if (
                    isinstance(result, dict)
                    and result.get("found")
                ):

                    context = build_context(
                        result["results"]
                    )


                    print(
                        "RAG context constructed."
                    )


                    rag_prompt = build_rag_prompt(
                        user_goal,
                        context
                    )


                    messages.append(
                        {
                            "role": "user",
                            "content": rag_prompt
                        }
                    )


                else:

                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "No relevant information was "
                                "found in the user's indexed "
                                "documents. Do not invent an "
                                "answer."
                            )
                        }
                    )


        # ----------------------------------------------
        # Stop after failure
        # ----------------------------------------------

        if state.status == "failed":

            print(
                "\nGoal evaluator: FAILED"
            )

            state.show()

            break


        # ----------------------------------------------
        # Evaluate current progress
        # ----------------------------------------------

        evaluation = evaluate_goal(
            state
        )


        if evaluation == "complete":

            state.complete()


            print(
                "\nGoal evaluator: COMPLETE"
            )


            # Ask model for final response
            final_response = ollama.chat(
                model="qwen3:4b",
                messages=messages
            )


            print(
                "Agent:",
                final_response.message.content
            )


            messages.append(
                final_response.message
            )


            state.show()

            break


        elif evaluation == "failed":

            state.fail()


            print(
                "\nGoal evaluator: FAILED"
            )


            print(
                "Agent: The task could not be completed."
            )


            state.show()

            break


        else:

            print(
                "Goal evaluator: CONTINUE"
            )


    # --------------------------------------------------
    # Maximum steps reached
    # --------------------------------------------------

    else:

        state.fail()


        print(
            "\nAgent stopped: maximum number of steps reached."
        )


        print(
            "Goal evaluator: FAILED"
        )


        state.show()