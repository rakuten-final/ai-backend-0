from generic_engines import *
from pydantic import BaseModel, Field

class RevieParemeters(BaseModel):
    review_params : List[str] = Field("All different parameters that can be used to describe a review to analyze the goodness of the product")


def generate_category_wise_params(product_cat):

    systemPromptText = """You are an AI assistant. 
    You are an AI tool that helps users analyze the goodness of a product based on the reviews.
    You are given with a product category. 
    You need to generate the detailed parameters that can be used to describe a review to analyze the goodness of the product.
    Example: for a technology product, the parameters can be [performance of a product, durabilty of product, battery life of product(camera, mobile etc.)].
    """

    query = f"""
    Product category: {product_cat}
    """

    engine = LangchainJSONEngine(RevieParemeters, systemPromptText=systemPromptText)
    result = engine.run(query).dict()

    
    return result




def generate_category_wise_params_all_cats(all_cats,store_path='./stored-result/cat-wise-params.json',use_stored=True):

    if use_stored and os.path.exists(store_path):
        print("Using stored result")
        return get_stored_result(store_path, "json")
    
    result = {}
    for _,cat in all_cats[0].items():
        params = generate_category_wise_params(cat)
        result[cat] = params["review_params"]

    save_result(result, store_path, "json")
    return result




class ToolsAndHardwareScores(BaseModel):
    Durability: int = Field("Durability of the product. 0 means negative, 1 means neutral, 2 means positive")
    EaseOfUse: int = Field("Ease of use of the product. 0 means negative, 1 means neutral, 2 means positive")
    Versatility: int = Field("Versatility of the product. 0 means negative, 1 means neutral, 2 means positive")
    QualityofMaterials: int = Field("Quality of materials used in the product. 0 means negative, 1 means neutral, 2 means positive")
    Portability: int = Field("Portability of the product. 0 means negative, 1 means neutral, 2 means positive")
    ValueforMoney: int = Field("Value for money of the product. 0 means negative, 1 means neutral, 2 means positive")



def analyze_review(review_text_date,pydanaic_model):
    systemPromptText = """You are an AI assistant. 
    You are an AI tool that helps users analyze the goodness of a product based on the reviews.
    You are given with a review text.
    You need to analyze the review and provide scores for different parameters.
    Example: for a review text "The product is good and durable", the scores can be [Durability: 2, Ease of use: 2, Versatility: 1, Quality of materials: 2, Portability: 1, Value for money: 2].
    """

    query = f"""
    Review text: {review_text_date[0]}
    """

    engine = LangchainJSONEngine(pydanaic_model, systemPromptText=systemPromptText)
    result = engine.run(query).dict()
    datetime = review_text_date[1]
    final_result = [
       result,datetime
    ]
    return final_result








def analyze_product_id(product_id, firs_level_cat, reviews_map, store_path='./stored-result/product-reviews-parmas.json', use_stored=True):

    cat_to_pydatnic_model = {
        "tools_hardware": ToolsAndHardwareScores
    }

    pydanaic_model = cat_to_pydatnic_model[firs_level_cat]

    if use_stored and os.path.exists(store_path):
        print("Using stored result")
        stored_data = get_stored_result(store_path, "json")
        if product_id in stored_data:
            return stored_data[product_id]
    reviews = reviews_map[product_id]
    results = []
    for _,review in tqdm(reviews.items()):
        result = analyze_review(review,pydanaic_model)
        results.append(result)

    final_result = {
             product_id:results
        }
    if os.path.exists(store_path):
        stored_result = get_stored_result(store_path, "json")
        stored_result.update(final_result)
        save_result(stored_result, store_path, "json")
    else:
        save_result(final_result, store_path, "json")
    return final_result





def calculate_monthly_averages(data):
    # Initialize dictionaries to store sums and counts for each month
    monthly_sums = defaultdict(lambda: defaultdict(float))
    monthly_counts = defaultdict(int)
    
    for item in data:
        parameters, date_str = item
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        month_key = date.strftime("%Y-%m")
        
        # Update sums and counts
        for key, value in parameters.items():
            monthly_sums[month_key][key] += value
        monthly_counts[month_key] += 1
    
    # Calculate averages
    monthly_averages = []
    for month, sums in monthly_sums.items():
        count = monthly_counts[month]
        averages = {f"Avg {key}": (value / count) for key, value in sums.items()}
        # All parameter avg
        averages["Aggregated Score"] = sum(averages.values()) / len(averages)
        averages["No interactions"] = count
        monthly_averages.append([averages, month])

    # last three months avg of aggregated score

    last_three_months_avg = sum([item[0]["Aggregated Score"] for item in monthly_averages[-3:]]) / 3   
    
    return monthly_averages,last_three_months_avg




def calculate_review_details(product_id,first_level_cat, reviews_map_path, use_stored=True, store_path = './stored-result/product-reviews-parmas.json'):
    fake_reviews = get_stored_result(reviews_map_path, "json")
    final_result = analyze_product_id(product_id, firs_level_cat = first_level_cat,reviews_map=fake_reviews, use_stored=use_stored, store_path=store_path)
    monthly_averages,last_three_months_avg = calculate_monthly_averages(final_result)
    return monthly_averages,last_three_months_avg