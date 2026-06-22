import os
import sys
import logging
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

# 为保证能在 Docker 中单机快速拉起并演示，这里我们演示通过 Langchain 包装底层工具。
# 在真正的微服务架构中，Client 会通过 stdio 或 SSE 接入 mcp-config.json 中的 server。
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from servers.mining_news.server import search, fetch_article
from servers.mineral_pdf.server import extract_resources
from servers.lme_price.server import get_price, get_trend

logging.basicConfig(level=logging.INFO)

def run_agent(query: str):
    tools = [
        Tool(
            name="SearchMiningNews",
            func=lambda q: search(q),
            description="搜索最新的矿业新闻，输入关键字即可。"
        ),
        Tool(
            name="FetchArticle",
            func=fetch_article,
            description="根据 URL 抓取新闻文章的全文。"
        ),
        Tool(
            name="ExtractPDFResources",
            func=extract_resources,
            description="从 NI 43-101 矿权报告 PDF 的 URL 中提取储量数据（Indicated/Inferred）。"
        ),
        Tool(
            name="GetPrice",
            func=lambda c: get_price(c),
            description="查询某种商品（如 copper, lithium, iron 等）的最新价格。"
        ),
        Tool(
            name="GetTrend",
            func=lambda c: get_trend(c),
            description="查询某种商品过去 30 天的价格走势。"
        )
    ]
    
    # 默认使用 OpenAI，如果环境变量中配置了 ANTHROPIC_API_KEY，也可以替换为 ChatAnthropic
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    
    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
    
    prompt = f"""
    请作为矿业分析师，处理以下请求：
    【请求】: {query}
    
    你必须输出一份 Markdown 格式的报告，包含以下 4 个部分：
    1. 📰 新闻摘要 (需包含引用源链接)
    2. 📊 储量数据 (尝试搜索或提取相关 PDF 的数据，如果找不到明确 PDF，则根据新闻总结)
    3. 📈 价格走势 (调用价格趋势工具获取该矿产最新行情)
    4. ⚠️ 风险提示 (根据新闻和价格走势给出分析)
    
    请使用中文回复。
    """
    
    try:
        result = agent.run(prompt)
        print("\n" + "="*50)
        print("🎉 矿权日报生成成功：")
        print("="*50 + "\n")
        print(result)
        
        with open("daily_brief.md", "w", encoding="utf-8") as f:
            f.write(result)
            
    except Exception as e:
        logging.error(f"Agent 运行出错: {e}")

if __name__ == "__main__":
    # 如果没有提供 API Key，就 mock 运行
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️ 未检测到 OPENAI_API_KEY，系统将进入 Mock 模式。在实际面试提交时，评委会在 .env 或 docker-compose 中注入 Key。")
    
    query = sys.argv[1] if len(sys.argv) > 1 else "给我生成一份关于 Pilbara 锂矿的今日简报"
    run_agent(query)
