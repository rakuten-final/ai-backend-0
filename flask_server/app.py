from common_imports import *
from generic_engines import *
from pydantic_schemas import *
from agent_utils import *
from langgraph_agent import *


app = flask.Flask(__name__)
CORS(app)


sessions = {
    10: {
        "agent": None,
        "cart": [], # List of product ids
        "cart_budget":10000.
    }
}

@app.route("/start-session", methods=["POST"])
def start_session():
    thread_id = 10 # Must be integer
    sessions[thread_id] = {
        "agent": MyAgent(thread_id),
        "cart": [],
        "cart_budget":10000.
    }
    return jsonify({"status": "success", "thread_id": thread_id})

@app.route("/chat", methods=["POST"])
def continue_flow():
    try:
        data = request.json
        thread_id = 10
        agent = sessions[thread_id]["agent"]

        if agent is None:
            return jsonify({"status": "error", "message": "no agent found"})

        snap = agent.get_recent_state_snap()

        if len(snap.keys()) == 1:
            # Start the conversation
            snap = agent.continue_flow({
                "cur_state": "Requirement Phase",
                "requirements": {},
                "recently_added": [],
                "mode":"primary",
            })
        else:
            snap = agent.resume_with_user_input(data["user_input"])
            sessions[thread_id]["cart_budget"] = snap["budget"]
        
        recently_added = snap["recently_added"]
        try:
            text_content = agent.get_last_message().content
            return jsonify({"status": "success","cur_state":snap['cur_state'], "text_content": text_content, "product_list": recently_added,"budget":sessions[thread_id]["cart_budget"]})
        except:
            snap = agent.get_recent_state_snap()
            requirements = snap.get("requirements", {})
            # Making agent None
            sessions[thread_id]["agent"] = None
            return jsonify({"status": "success","cur_state":"completed","text_content":f"No messages to show ! Have a good day ! Your requirements are {requirements}", "product_list": [],"budget":sessions[thread_id]["cart_budget"]})
        
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)})
        

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    data = request.json
    thread_id = 10

    proudct_ids = data["product_ids"]
    prices = data["prices"] # default [0]

    for price in prices:
        sessions[thread_id]["cart_budget"] -= price
    sessions[thread_id]["cart"] += proudct_ids
    return jsonify({"status": "success","budget":sessions[thread_id]["cart_budget"]})
    

@app.route("/get-cart", methods=["GET"])
def get_cart():
    thread_id = 10
    cart = sessions[thread_id]["cart"]
    return jsonify({"status": "success", "cart": cart})

@app.route("/force-stop", methods=["POST"])
def force_stop():
    thread_id = 10
    sessions[thread_id]["agent"] = None
    return jsonify({"status": "success"})

if __name__ == "__main__":
    load_dotenv('../.env')
    app.run(host="0.0.0.0", port=8080, debug=False)













