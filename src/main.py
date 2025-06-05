from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from app.router import router1 as process_router_transactions
from app.router import router2 as process_router_prices

app = FastAPI()
app.include_router(process_router_transactions)
app.include_router(process_router_prices)

mcp = FastApiMCP(app)

# Mount the MCP server directly to your FastAPI app
mcp.mount()

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)