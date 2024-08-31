from common_imports import *
from MongoUtils import utils

def get_reason_for_product_offer(input: Dict[str, Any],cc_prod_path:str) -> List[Dict[str, str]]:
    with open(cc_prod_path, 'r') as file:
        cc_prod_offer = json.load(file)
    
    prod_list = [fetch_product_handler(item) for item in input["prod_list"]]

    output = []
    for cc in input["user"]["cc_list"]:
        for prod in prod_list:
            for cc_prod in cc_prod_offer["credit_card_to_products_list"]:
                if cc_prod["credit_card_name"].lower() == cc.lower():
                    for prod_offer in cc_prod["product_offer_list"]:
                        if prod["brand"].lower() in prod_offer["product_brand_name"].lower():
                            found = False
                            for item in output:
                                if item["prod_id"] == prod["uniq_id"]:
                                    item["reason"] += f" The {cc} offers discounts for {prod['brand']} products with {prod_offer['offer_details']}"
                                    found = True
                                    break
                            if not found:
                                output.append({"prod_id": prod["uniq_id"], "reason": f"The {cc} offers discounts for {prod['brand']} products with {prod_offer['offer_details']}"})
    
    # Add unmatched products to the output
    for prod in prod_list:
        found = False
        for item in output:
            if item["prod_id"] == prod["uniq_id"]:
                found = True
                break
        if not found:
            output.append({"prod_id": prod["uniq_id"], "reason": ""})
    
    return output


def fetch_product_handler(product_id):
    response = utils.fetchById(product_id)
    return response