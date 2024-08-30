from pydantic_schemas import *
from generic_engines import *
from cc_utils import *


def welcome(state:AgentState)->AgentState:
    msg = SystemMessage("Welcome to the AI assistant. I am here to help you with your shopping needs. Tell me about your situation and I will suggest products accordingly. You may also suggest a budget of your cart ...")
    print(msg.content)
    state['messages'].append(msg)
    # print(f"Current messages: {state['messages']}")
    return state


def secondary_welcome(state:AgentState)->AgentState:
    msg = SystemMessage(f"Hi looks like you are looking for some {state['cur_state']} products. I can help you with that. Tell me about your requirements and I will suggest products accordingly. You may also suggest a price range.")
    print(msg.content)
    print("state['requirements'][state['cur_state']]: ",state['requirements'][state['cur_state']])
    state['requirements'][state['cur_state']]['thread_conversation'].append(msg)
    return state







def exit_from_requirements(state:AgentState)->AgentState:
    msg = SystemMessage(f"Final requirements:{state['first_level_chosen']}")
    print(msg.content)
    state['messages'].append(msg)

    print(f"Requirements: {state['requirements']}")
    for req in state['first_level_chosen']:
        state['requirements'][req] = {
            "secondary_status": "new requirement",
            "list_of_requirements": [[]],
            "list_of_products": [],
            "thread_conversation":[],
            "price_lower_bounds": [0.],
            "price_upper_bounds": [100000.]
        }
        print(f"Added {req} to the requirements list.")

    return state

def exit_from_requirements_secondary(state:AgentState)->AgentState:
    print(f"Exiting category {state['cur_state']} ...")
    msg = SystemMessage(f"Final requirements:{state['first_level_chosen']}")
    print(msg.content)
    # state['messages'].append(msg)
    state['requirements'][state['cur_state']]['secondary_status'] = "completed"
    return state

def final_exit(state:AgentState)->AgentState: 
    # Clearing all threads
    state["cur_state"] = "completed"
    for key in state['requirements']:
        state['requirements'][key]['thread_conversation'] = []
    msg = SystemMessage(f"So finally we have the following requirements:\n {json.dumps(state['requirements'], indent=4)}")
    print(msg.content)
    state['messages'].append(msg)
    return state





def generate_situational_requirements(user_situation: str,update_mode=False):
    """ 
    This tool generates situational requirements based on the user's situation. 
    """

    systemPromptText = """You are an AI assistant. 
    You are helping a user who is looking for products on an e-commerce platform. 
    He/she will tell you about his/her situation and you will suggest products accordingly those perfectly fit his/her situational requirements.
    You are given a list of possible categories, you have to determine whether products from these categories are relevant to the user's situation or not.
    """

    if not update_mode:
        query = f"""
        User: I am looking for products on an e-commerce platform.
        My current situation is: {user_situation}
        """
    else:
        query=f"""
        User: These are previous conversation messages.
        {user_situation}
        Now determine the situational requirements based on the user's situation.
        """

    engine1 = LangchainJSONEngine(SituationalRequirement1, systemPromptText=systemPromptText)
    engine2 = LangchainJSONEngine(SituationalRequirement2, systemPromptText=systemPromptText)

    result1 = engine1.run(query).dict()
    result2 = engine2.run(query).dict()
    budget_value = result2['budget_value']
    del result2['budget_value']
    result1.update(result2)

    return result1, budget_value


def generate_secondary_requirements(chat_conversation):
    """
    This tool generates secondary requirements based on the user's requirements.
    """

    systemPromptText = """You are an AI assistant. 
    You are helping a user who is looking for products on an e-commerce platform. 
    Your task is to determine the user's requirements based on the conversation.
    Generate a list of detailed requirements that the user has.

    Example: For a clothing product. [Requirement 1: The product should be of a specific brand. Requirement 2: The product should be of a specific color. Requirement 3: The product should be of a specific size.]
    """

    query = f"""
    Chat conversation: {chat_conversation}
    """

    engine = LangchainJSONEngine(UserRequirement, systemPromptText=systemPromptText)
    result = engine.run(query).dict()
    
    return result






def summarize_chosen_categories(first_level_chosen:List[str]):
    systemPromptText = """You are an AI assistant.
    You are helping a user who is looking for products on an e-commerce platform. 
    There are some AI suggested categories that are relevant to the user's situation.
    You have to summarize the chosen categeroies and tell the user about the categories.
    You all also if he/she wants to add or remove any categories. Also mention if there is any budget range available or mentioned by the user.
    Also, you have to ask the user if he/she wants to proceed to the product suggestion phase if the chosen categories are correct.
    """

    query = f"""
    Some AI suggested chosen categories: {first_level_chosen}
    """

    engine = LangchainSimpleEngine(systemPromptText=systemPromptText)
    result = engine.run(query)

    return result.content


def summarize_secondary_requirements(requirement_list:List[str]):
    systemPromptText = """You are an AI assistant.
    You are helping a user who is looking for products on an e-commerce platform. 
    There are some AI suggested requirements that based on the user's chat conversation with the AI.

    You have to summarize the chosen requirements and tell the user about the requirements.
    You also tell if he/she wants to add or remove any requirements. Tell the user if he/she wants to modify the price range.
    Also, you have to ask the user if he/she wants to 
        1. Add a new product under same category
        2. Completed with this category and move to the next category

    """

    query = f"""
    Some AI suggested chosen requirements: {requirement_list}
    """

    engine = LangchainSimpleEngine(systemPromptText=systemPromptText)
    result = engine.run(query)

    return result.content









def check_statisfied(state:AgentState)->AgentState:
    chat = "\n".join([f"{msg.type} : {msg.content}" for msg in state['messages']])
    systemPromptText = """You are an AI assistant.
    You are helping a user who is looking for products on an e-commerce platform.
    You read the user's previous conversations and determine whether the user has described all his/her requirements and ready to proceed with the product suggestions.
    """

    query = f"""
    Previous messages: {chat}
    Now tell me, are all the user's requirements fullfilled?
    """

    engine = LangchainJSONEngine(RequirementFullfilled, systemPromptText=systemPromptText)
    result = engine.run(query).dict()
    state['is_fullfilled'] = result['is_fullfilled']

    print(f"Is fullfilled ??????? : {state['is_fullfilled']}")

    return state['is_fullfilled']
    




def check_statisfied_secondary(state:AgentState)->AgentState:
    chat = "\n".join([f"{msg.type} : {msg.content}" for msg in state['requirements'][state['cur_state']]['thread_conversation']])

    print("(Sec) Chat: ",chat)
    systemPromptText = f"""You are an AI assistant.
    You are helping a human who is looking for {"clothing"} products on an e-commerce platform.
    You read the human's previous conversations and determine the status of the conversation.
    You have to determine whether the user is asking for a new requirement or he/she is satisfied with the current requirements.
    """

    query = f"""
    Previous conversations: {chat}
    What is the status of the conversation?
    """

    engine = LangchainJSONEngine(RequirementStatus, systemPromptText=systemPromptText)
    result = engine.run(query).dict()

    state['requirements'][state['cur_state']]['secondary_done'] = "completed" if result['satisfaction_status'] else "new requirement"
    print(f"Is fullfilled (secondary) ??????? : {result}")
    return state['requirements'][state['cur_state']]['secondary_done']


def check_asking_for_new_product_secondary(state:AgentState)->AgentState:
    chat = "\n".join([f"{msg.type} : {msg.content}" for msg in state['requirements'][state['cur_state']]['thread_conversation']])
    print("----------------------> >  >> > .",chat)
    print("----!----"*21)
    systemPromptText = """You are an AI assistant.
    You are helping a user who is looking for products on an e-commerce platform.
    You read the user's previous conversations and determine whether the user is interested in a new product.
    """

    query = f"""
    Previous messages: {chat}
    Now tell me, is the user asking for a new product?
    """

    engine = LangchainJSONEngine(AskingsForNewProduct, systemPromptText=systemPromptText)
    result = engine.run(query).dict()

    print(f"Is asking for new product ??????? : {result}")

    if result['asking_for_new_product']:
        state['requirements'][state['cur_state']]['secondary_done'] = "new requirement"

    return 'asking for new product' if result['asking_for_new_product'] else 'completed'













def human_node(state:AgentState)->AgentState:
    print("Human node ...")
    # print(f"Current messages: {state['messages']}")
    return state

def human_node_secondary(state:AgentState)->AgentState:
    print("Human node (secondary) ...")
    print("Flusing receently added ...")
    state['recently_added'] = []
    # print(f"Current messages: {state[state['cur_state']]['thread_conversation']}")
    return state









def refine_requirement(reqs:dict):
    chosen = []
    not_chosen = []
    for key, value in reqs.items():
        if value == True:
            chosen.append(key)
        else:
            not_chosen.append(key)
    return chosen, not_chosen


def ask_ai_first_level_requirements(state:AgentState)->AgentState:
    previous_messages = state['messages']
    chat = "\n".join([f"{msg.type} : {msg.content}" for msg in previous_messages])
    first_level_requirements,budget_value = generate_situational_requirements(chat,update_mode=True)
    # state['requirements'] = first_level_requirements
    first_level_chosen, first_level_not_chosen = refine_requirement(first_level_requirements)
    state['budget'] = budget_value
    state['first_level_chosen'] = first_level_chosen
    state['first_level_not_chosen'] = first_level_not_chosen
    summarized_ans = summarize_chosen_categories(first_level_chosen)
    print(summarized_ans)
    state['messages'].append(SystemMessage(summarized_ans))
    return state


def ask_ai_secondary_level_requirements(state:AgentState)->AgentState:
    previous_messages = state['requirements'][state['cur_state']]['thread_conversation']
    chat = "\n".join([f"{msg.type} : {msg.content}" for msg in previous_messages])
    secondary_level_requirements = generate_secondary_requirements(chat)
    state['requirements'][state['cur_state']]['list_of_requirements'][-1]=(secondary_level_requirements['requirement_list'])
    state['requirements'][state['cur_state']]['price_lower_bounds'][-1] = secondary_level_requirements['price_lower_bound']
    state['requirements'][state['cur_state']]['price_upper_bounds'][-1] = secondary_level_requirements['price_upper_bound']

    print("-"*20)
    print("price lower bounds: ",state['requirements'][state['cur_state']]['price_lower_bounds'])
    print("price upper bounds: ",state['requirements'][state['cur_state']]['price_upper_bounds'])
    print(secondary_level_requirements['requirement_list'])
    print("-"*20)

    # state['requirements'][state['cur_state']]['thread_conversation'].append(HumanMessage(content=secondary_level_requirements['requirement_list']))
    summarized_ans = summarize_secondary_requirements(secondary_level_requirements['requirement_list'])
    print(summarized_ans)
    state['requirements'][state['cur_state']]['thread_conversation'].append(SystemMessage(summarized_ans))
    return state











def iteration_start(state:AgentState)->AgentState:
    print("Iteration start. Activating the levels one by one ...")
    state['mode'] = "secondary"
    for req in state['requirements']:
        if state['requirements'][req]['secondary_status'] == "new requirement":
            print(f"Activating {req} ...")
            state['cur_state'] = req
            break;
    return state

def req_iterator(state:AgentState)->AgentState:
    print("Req iterator ...")
    
    for req in state['requirements']:
        if state['requirements'][req]['secondary_status'] == "new requirement":
            return True

    state['cur_state'] = "exit"   
    return False





def dummy_secondary_req_handler(state:AgentState)->AgentState:
    print("Dummy secondary req handler ...")
    print(f"Requirements: {state['requirements']}")
    state['requirements'][state['cur_state']]['secondary_status'] = "completed"
    return state



def new_product_handler(state:AgentState)->AgentState:
    print("New product handler ...")
    state['requirements'][state['cur_state']]['thread_conversation'] = []
    state['requirements'][state['cur_state']]['list_of_requirements'].append([])
    state['requirements'][state['cur_state']]['price_lower_bounds'].append(0.)
    state['requirements'][state['cur_state']]['price_upper_bounds'].append(100000.)
    msg = SystemMessage(f"Do you want to add a new product under the same category or move to the next category?")
    state['requirements'][state['cur_state']]['thread_conversation'].append(msg)
    print("%"*12)
    print(f"Requirements: {state['requirements']}")
    print("%"*12)
    return state

def sort_by_price_relevance(product_doc_list, price_lower_bound, price_upper_bound):
    product_doc_list = product_doc_list.copy()
    # Calculate the midpoint of the price range
    price_midpoint = (price_lower_bound + price_upper_bound) / 2
    def relevance(product_doc):
        price = product_doc.metadata['discounted_price']
        return abs(price - price_midpoint)
    sorted_product_doc_list = sorted(product_doc_list, key=relevance)
    # sorted_product_doc_list.reverse()

    return sorted_product_doc_list


def product_search(state:AgentState)->AgentState:
    cur_reqs = state['requirements'][state['cur_state']]['list_of_requirements'][-1]
    price_lower_bound = state['requirements'][state['cur_state']]['price_lower_bounds'][-1]
    price_upper_bound = state['requirements'][state['cur_state']]['price_upper_bounds'][-1]
    # Elastic search for products based on the requirements
    # Currently dummy random products
    # product_list = [f"{state['cur_state']}_{len(state['requirements'][state['cur_state']]['list_of_requirements'])}_{i}" for i in range(5)]
    global CATEGORY_WISE_VECTOR_STORE
    print("Searching products with reqs: ","\n- ".join(cur_reqs))
    product_doc_list = CATEGORY_WISE_VECTOR_STORE[state['cur_state']].similarity_search("\n- ".join(cur_reqs),k=10)
    if not(price_lower_bound==0. and price_upper_bound==100000.):
        print("!!!! User is looking for a specific price range !!!!")
        product_doc_list = sort_by_price_relevance(product_doc_list, price_lower_bound, price_upper_bound)
    # discounted_price is the key for each doc for the price
    # Sort the doclist based on the relevanve of price range
    print(f"Showing products for {state['cur_state']} Price range: {price_lower_bound} - {price_upper_bound}")
    print("Product list: ",product_doc_list)
    product_list = [doc.metadata['uniq_id'] for doc in product_doc_list]

    # Credit card offer
    cc_payload = {
        "user":{"cc_list" : ["Amazon pay ICICI credit card", "HDFC Bank Credit Card"]}, # To be feched from mongo
        "prod_list":product_list
    }
    cc_prod_path = "../stored-result-git/cc_prod_offer.json"

    product_list = get_reason_for_product_offer(cc_payload,cc_prod_path)

    state['requirements'][state['cur_state']]['list_of_products'].append(product_list)
    state['recently_added'] = product_list
    return state
