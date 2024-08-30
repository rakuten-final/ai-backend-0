from common_imports import *
from generic_engines import *
from pydantic_schemas import *
from agent_utils import *
from langgraph_agent import *
from prod_review_utils import *
from MongoUtils import utils


app = flask.Flask(__name__)
CORS(app)


sessions = {
    10: {
        "agent": None,
        "cart": [], # List of product ids
        "cart_budget":10000.,
        "user_id": "user_1"
    }
}

@app.route("/api/v1/products", methods=["GET"])
def getProducts():
    products = utils.fetchAll()
    return jsonify(products), 200


@app.route("/api/v1/products/<id>", methods=["GET"])
def getProductById(id):
    product = utils.fetchById(id)
    return jsonify(product), 200

@app.route("/api/v1/products/paginated/<int:page_number>/<int:page_size>", methods=["GET"])
def get_paginated_products(page_number, page_size):
    try:
        # Assuming fetchPaginated is a function that retrieves products based on pagination
        products = utils.fetchPaginated(page_size, page_number)
        return jsonify(products), 200
    except ValueError as e:
        # Handle the case where conversion to integer fails or other errors occur
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

@app.route("/start-session", methods=["POST"])
def start_session():
    thread_id = 10 # Must be integer
    sessions[thread_id] = {
        "agent": MyAgent(thread_id),
        "cart": [],
        "cart_budget":10000.,
        "user_id": "user_1"
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
                "user_id": sessions[thread_id]["user_id"]
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

@app.route("/fetch-product", methods=["POST"])
def fetch_product():
    product_id = request.json["product_id"]
    MONGO_HOSTED_URL = os.getenv("MONGO_HOSTED_URL")
    total_url = f"{MONGO_HOSTED_URL}/api/v1/products/{product_id}"
    print(total_url)
    response = requests.get(total_url)
    return jsonify(response.json())


@app.route("/get-product-review-scores", methods=["POST"])
def get_product_review_scores():
    data = request.json
    product_id = data["product_id"]  # 0513ab340eced913dce82594bd118ff0
    first_level_cat = data["first_level_cat"] # tools_hardware , clothing
    
    if product_id not in ["0513ab340eced913dce82594bd118ff0"]:
        return jsonify({"status": "error", "message": "Product not found"})
    
    
    monthly_averages,last_three_months_avg = calculate_review_details(
        product_id, 
        first_level_cat, 
        reviews_map_path = "../stored-result-git/user-reviews-fake.json",
        use_stored=True, 
        store_path = '../stored-result-git/product-reviews-parmas.json')
    
    result = {
        "monthly_averages": monthly_averages,
        "last_three_months_avg": last_three_months_avg,
        "product_id": product_id
    }
    return jsonify(result)


if __name__ == "__main__":
    load_dotenv('../.env')
    app.run(host="0.0.0.0", port=8080, debug=False)













