from langchain_openai import ChatOpenAI

class BaseAgent:
    '''
    A base class for agents that interact with LLMs and tools.
    '''
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        if len(tools) > 0:
            self.llm = self.llm.bind_tools(tools)
    def run(self, input):
        # process input with llm and tools
        pass
    

class ChatAgent(BaseAgent):
    '''
    An agent specialized for chat-based interactions.
    '''
    def __init__(self, llm, tools, system_message):
        super().__init__(llm, tools)

        self.system_message = system_message
    def run(self, messages):
        raise NotImplementedError("ChatAgent run method not implemented yet.")

    def node(self, state):
        return {"messages": [self.llm.invoke([self.system_message] + state["messages"])]}

def test_agent():
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    tools = [] 
    system_message = "You are a helpful assistant."
    agent = ChatAgent(llm, tools, system_message)
    sample_messages = [] 
    agent.run(sample_messages)

if __name__ == "__main__":
    test_agent()