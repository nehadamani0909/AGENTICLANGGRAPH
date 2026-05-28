import os
from typing import Annotated

from langchain_core.tools import tool as lc_tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from env_helper import load_project_env


class State(TypedDict):
    messages: Annotated[list, add_messages]


@lc_tool("tavily_search")
def tavily_search(query: str) -> dict:
    """Search recent AI news. Do not pass start_date or end_date."""
    search = TavilySearch(
        max_results=2,
        topic="news",
        time_range="day",
        tavily_api_key=os.environ["TAVILY_API_KEY"],
    )
    return search.invoke(query)


@lc_tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


def build_graph(model: str = "llama-3.3-70b-versatile"):
    env = load_project_env()
    if not env.get("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY was not loaded from .env")
    if not env.get("TAVILY_API_KEY"):
        raise RuntimeError("TAVILY_API_KEY was not loaded from .env")

    llm = ChatGroq(model=model)
    tools = [tavily_search, multiply]
    llm_with_tool = llm.bind_tools(tools)

    def tool_calling_llm(state: State):
        return {"messages": [llm_with_tool.invoke(state["messages"])]}

    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges("tool_calling_llm", tools_condition)
    builder.add_edge("tools", END)

    return builder.compile(), llm, tools


def run_demo(prompt: str = "Give me the recent ai news and then multiply 5 by 10"):
    graph, _, _ = build_graph()
    response = graph.invoke({"messages": [("user", prompt)]})
    for message in response["messages"]:
        message.pretty_print()
    return response
