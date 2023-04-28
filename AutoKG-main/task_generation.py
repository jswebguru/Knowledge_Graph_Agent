import multiprocessing
import os

from camel.agents import ChatAgent
from camel.generators import (
    AISocietyTaskPromptGenerator,
    SystemMessageGenerator,
)
from camel.messages import UserChatMessage
from camel.typing import RoleType, TaskType


def generate_tasks(role_names: str, task_generator_prompt: str,
                   start_token: str = "1.", num_tasks: int = 10) -> None:
    sys_msg_generator = SystemMessageGenerator(task_type=TaskType.DEFAULT)

    assistant_sys_msg = sys_msg_generator.from_dict(
        dict(), role_tuple=("Task Generator", RoleType.DEFAULT))
    assistant_agent = ChatAgent(assistant_sys_msg)

    user_msg = UserChatMessage(role_name="Task Generator",
                               content=task_generator_prompt)

    assistant_msgs, _, _ = assistant_agent.step(user_msg)
    assistant_msg = assistant_msgs[0]

    tasks = assistant_msg.content.split("\n")

    # Filter out the generated response to include the tasks only
    for i, task in enumerate(tasks):
        if start_token in task:
            tasks = tasks[i:i + num_tasks]
            break

    # Ensure exact number of tasks is generated
    assert str(num_tasks) in tasks[-1], print(tasks)

    with open(f"./tasks/{'_'.join(role_names)}.txt", "w") as file:
        file.write("\n".join(tasks))


def main() -> None:
    num_tasks = 10
    start_token = "1."

    task_generator_prompt_generator = AISocietyTaskPromptGenerator(
        num_tasks=num_tasks).from_role_files()

    pool = multiprocessing.Pool()

    for task_generator_prompt, role_names in task_generator_prompt_generator:
        if not os.path.exists(f"./tasks/{'_'.join(role_names)}.txt"):
            print(f"Generating tasks for {role_names}")
            pool.apply_async(
                generate_tasks,
                (role_names, task_generator_prompt, start_token, num_tasks))

    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
