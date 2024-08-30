from common_imports import *

class SituationalRequirement1(BaseModel):
    clothing: bool = Field(description="Whether clothing products are relevant to the user's situation.")
    bags_wallets_belts: bool = Field(description="Whether bags, wallets, and belts are relevant to the user's situation.")
    jewellery: bool = Field(description="Whether jewellery products are relevant to the user's situation.")
    beauty_and_personal_care: bool = Field(description="Whether beauty and personal care products are relevant to the user's situation.")
    watches: bool = Field(description="Whether watches are relevant to the user's situation.")
    sunglasses: bool = Field(description="Whether sunglasses are relevant to the user's situation.")
    sports_fitness: bool = Field(description="Whether sports and fitness products are relevant to the user's situation.")
    health_personal_care_appliances: bool = Field(description="Whether health and personal care appliances are relevant to the user's situation.")
    home_decor_festive_needs: bool = Field(description="Whether home decor and festive needs are relevant to the user's situation.")
    home_furnishing: bool = Field(description="Whether home furnishing products are relevant to the user's situation.")
    kithen_dining: bool = Field(description="Whether kitchen and dining products are relevant to the user's situation.")
    homes_kitchen: bool = Field(description="Whether home and kitchen products are relevant to the user's situation.")

class SituationalRequirement2(BaseModel):
    furniture: bool = Field(description="Whether furniture products are relevant to the user's situation.")
    pet_supplies: bool = Field(description="Whether pet supplies are relevant to the user's situation.")
    pens_stationery: bool = Field(description="Whether pens and stationery products are relevant to the user's situation.")
    automotive: bool = Field(description="Whether automotive products are relevant to the user's situation.")
    tools_hardware: bool = Field(description="Whether tools and hardware products are relevant to the user's situation.")
    baby_care: bool = Field(description="Whether baby care products are relevant to the user's situation.")
    mobile_accessories: bool = Field(description="Whether mobile accessories are relevant to the user's situation.")
    computers: bool = Field(description="Whether computer products are relevant to the user's situation.")
    cameras_accessories: bool = Field(description="Whether cameras and accessories are relevant to the user's situation.")
    gaming: bool = Field(description="Whether gaming products are relevant to the user's situation.")
    home_improvement: bool = Field(description="Whether home improvement products are relevant to the user's situation.")
    home_entertainment: bool = Field(description="Whether home entertainment products are relevant to the user's situation.")
    budget_value : float = Field(description="The budget value, the user has for the products. If the user has not specified any budget, then the value is 10000.00")

class UserRequirement(BaseModel):
    requirement_list: List[str] = Field(description="List of requirements that the user has. Each requirement should be detailed and unique.")
    price_lower_bound: float = Field(description="The lower bound of the price range that the user is looking for in INR. Default: 0")
    price_upper_bound: float = Field(description="The upper bound of the price range that the user is looking for in INR. Default: 100000")

class RequirementFullfilled(BaseModel):
    is_fullfilled: bool = Field(description="Whether the user's requirements are fullfilled.")

class RequirementStatus(BaseModel):
    satisfaction_status: bool = Field(description="Whether the user is very satisfied with all the requirements.")

class AskingsForNewProduct(BaseModel):
    asking_for_new_product: bool = Field(description="Whether the user is asking for a new/another type of product.")


class MoveToPlace(BaseModel):
    move_to_place: bool = Field(description="Whether the user wants to move to a new place.")

class NewPlaceNameAndRequirement(BaseModel):
    new_place_name: str = Field(description="The name of the new place where the user wants to move to.")
    meidcal_store_keys: str = Field(description="Default: Any essential medical store where the user can get medical supplies.")
    grocery_store_keys: str = Field(description="Default: Any grocery store where the user can get groceries.")
    resturants_keys: str = Field(description="Any special cuisine resturants where the user can get food. Default: Any resturants.")


class AgentState(TypedDict):
    cur_state: str
    messages: Annotated[list, add_messages]
    requirements: dict = {}
    first_level_chosen: List[str] = []
    first_level_not_chosen: List[str] = []
    mode: str = "idle"
    recently_added: List[str] = []
    CATEGORY_WISE_VECTOR_STORE: dict
    budget: float = 10000.00
    new_place_req:dict = {}