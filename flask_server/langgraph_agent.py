from common_imports import *
from generic_engines import *
from pydantic_schemas import *
from agent_utils import *


class MyAgent:
    def __init__(self,thread_id):
        self.config = None
        self.app = None
        self.build(thread_id)

    def draw_workflow(self):
        display(Image(self.app.get_graph(xray=True).draw_mermaid_png()))
    
    def build(self,thread_id):
        workflow = StateGraph(AgentState)
        workflow.add_node("welcome", welcome)
        workflow.add_node("human", human_node)
        workflow.add_node("ask_ai_first_level_requirements", ask_ai_first_level_requirements)
        workflow.add_node("exit_from_first_level_requirements", exit_from_requirements)

        workflow.add_node("iteration_start", iteration_start)
        workflow.add_node("welcome_secondary", secondary_welcome)
        workflow.add_node("human_secondary", human_node_secondary)
        workflow.add_node("human_secondary_new_prod", human_node_secondary)
        workflow.add_node("ask_ai_secondary_level_requirements", ask_ai_secondary_level_requirements)
        workflow.add_node("exit_from_requirements_secondary", exit_from_requirements_secondary)


        workflow.add_node("new_product_handler", new_product_handler)
        workflow.add_node("product_search", product_search)
        # workflow.add_node("dummy_secondary_req_handler", dummy_secondary_req_handler)
        workflow.add_node("final_exit", final_exit)

        

        workflow.add_edge("welcome", "human")
        workflow.add_conditional_edges(
            "human", 
            check_statisfied,
            {
                True: "exit_from_first_level_requirements",
                False: "ask_ai_first_level_requirements"
            }
        )
        workflow.add_edge("ask_ai_first_level_requirements", "human")

        workflow.add_edge("exit_from_first_level_requirements", "iteration_start")
        workflow.add_conditional_edges(
            "iteration_start", 
            req_iterator,
            {
                True: "welcome_secondary",
                False: "final_exit"
            }
        )

        workflow.add_edge("welcome_secondary", "human_secondary")
        workflow.add_conditional_edges(
            "human_secondary", 
            check_statisfied_secondary,
            {
                "new requirement": "ask_ai_secondary_level_requirements",
                "completed": "product_search"
            }
        )

        workflow.add_edge("ask_ai_secondary_level_requirements", "human_secondary")    

        workflow.add_edge("product_search", "exit_from_requirements_secondary")
        workflow.add_edge("exit_from_requirements_secondary", "new_product_handler")
        workflow.add_edge("new_product_handler", "human_secondary_new_prod")
        workflow.add_conditional_edges(
            "human_secondary_new_prod", 
            check_asking_for_new_product_secondary,
            {
                'asking for new product': "welcome_secondary",
                'completed': "iteration_start"
            }
        )
        workflow.add_edge("final_exit", langgraph.graph.END)

        
        workflow.set_entry_point("welcome")
        with SqliteSaver.from_conn_string(":memory:") as memory:
            app = workflow.compile(
                checkpointer=memory,
                interrupt_before=["human","human_secondary","human_secondary_new_prod"],
            )
        
        self.app = app
        self.config = {"configurable": {"thread_id": str(thread_id)}}
        return app
    

      

    
    def get_recent_state_snap(self):
        return self.app.get_state(config=self.config).values.copy()
    
    def get_last_message(self):
        if self.get_recent_state_snap()["mode"] == "secondary":
            return self.get_last_secondary_message()
        snap = self.get_recent_state_snap()
        return snap["messages"][-1]
    
    def get_last_secondary_message(self):
        snap = self.get_recent_state_snap()
        return snap["requirements"][snap["cur_state"]]["thread_conversation"][-1]

    def continue_flow(self, state):
        self.app.invoke(state, config=self.config)
        return self.get_recent_state_snap()

    def resume_with_user_input(self, user_input:str):
        print("Keys!!",self.get_recent_state_snap().keys())
        if self.get_recent_state_snap()["mode"] == "secondary":
            print("<<<<<<<<<<<<<<<<< Resuming secondary ...")
            return self.resume_with_user_input_secondary(user_input)
        snap = self.get_recent_state_snap()
        snap["messages"].append(HumanMessage(user_input))
        self.app.update_state(self.config, snap)
        return self.continue_flow(None)
    
    def resume_with_user_input_secondary(self, user_input:str):
        snap = self.get_recent_state_snap()
        snap["requirements"][snap["cur_state"]]["thread_conversation"].append(HumanMessage(user_input))
        self.app.update_state(self.config, snap)
        return self.continue_flow(None)