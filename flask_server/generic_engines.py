from common_imports import *

class LangchainJSONEngine:
    def __init__(self, sampleBaseModel: BaseModel, systemPromptText: str=None, humanPromptText: str=None):
        self.llm = llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.structured_llm = llm.with_structured_output(sampleBaseModel)
        
        if systemPromptText is None:
            self.systemPromptText = """
            You are an AI assistant. You are helping a user with a task. The user is asking you questions and you are answering them.
            """
        else:
            self.systemPromptText = systemPromptText

        if humanPromptText is None:
            self.HumanPromptText = """
            Human: {query}
            """
        else:
            self.humanPromptText = humanPromptText

        self.prompt = ChatPromptTemplate.from_messages(
            [("system", self.systemPromptText), ("human", "Query:\n\n {query}")])
        
        self.micro_agent = self.prompt | self.structured_llm

    def run(self, query: str):
        result = self.micro_agent.invoke({
            "query": query
        }) 
        return result
    

class LangchainSimpleEngine:
    def __init__(self, tools:List[tool]=[], systemPromptText: str=None, humanPromptText: str=None):
        self.llm = llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.tools = tools
        
        if len(tools) == 0:
            self.llm_with_tools = llm
        else:
            self.llm_with_tools = llm.bind_tools(tools)
            
        if systemPromptText is None:
            self.systemPromptText = """
            You are an AI assistant. You are helping a user with a task. The user is asking you questions and you are answering them.
            """
        else:
            self.systemPromptText = systemPromptText

        if humanPromptText is not None: 
            print("Skipping human prompt text ...")

    def run(self, query: str):
        messages = [
            SystemMessage(self.systemPromptText),
            HumanMessage(content=query)
        ]
        level1_result = self.llm_with_tools.invoke(messages)
        if len(level1_result.tool_calls) == 0:
            print("No tools to run ...")
            return level1_result
        else:
            print("Running tools ...")
            for tool_call in level1_result.tool_calls:
                tool_output = tool_call.invoke()
                messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
            level2_result = self.llm_with_tools.invoke(messages)
            return level2_result