from common_imports import *

def get_reason_for_product_offer(input: Dict[str, Any],cc_prod_path:str) -> List[Dict[str, str]]:
    with open(cc_prod_path, 'r') as file:
        cc_prod_offer = json.load(file)
    
    prod_list = [fetch_product_handler(item) for item in input["prod_list"]]

    output = []
    for cc in input["user"]["cc_list"]:
        for prod in prod_list:
            for cc_prod in cc_prod_offer["credit_card_to_products_list"]:
                if cc_prod["credit_card_name"].lower() == cc.lower():
                    # print(cc_prod)
                    for prod_offer in cc_prod["product_offer_list"]:
                        if prod["brand"].lower() in prod_offer["product_brand_name"].lower():
                            output.append({"prod_id": prod["uniq_id"], "reason": f"The {cc} offers discounts for {prod['brand']} products with {prod_offer['offer_details']}"})
    return output


def fetch_product_handler(product_id):
    MONGO_HOSTED_URL = os.getenv("MONGO_HOSTED_URL")
    total_url = f"{MONGO_HOSTED_URL}/api/v1/products/{product_id}"
    # print(total_url)
    response = requests.get(total_url)
    return response.json()